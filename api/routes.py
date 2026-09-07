from flask import Blueprint, request, jsonify, send_file, Response
from database.db import (
    get_config, update_config,
    get_all_teachers, get_teacher, save_teacher, delete_teacher,
    get_all_subjects, get_subject, save_subject, delete_subject,
    get_all_rooms, get_room, save_room, delete_room,
    get_all_sections, get_section, save_section, delete_section,
    get_timetable, save_timetable, update_entry_lock, unlock_all_entries,
    get_all_lectures, save_lecture, delete_lecture,
    seed_default_data
)
from models.teacher import Teacher
from models.subject import Subject
from models.room import Room
from models.section import Section
from models.timetable_entry import TimetableEntry
from solver.cp_sat_solver import TimetableSolver
from solver.manual_assist import ManualAssistEngine
from api.export_service import ExportService
from api.import_service import ImportService

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/data", methods=["GET"])
def get_all_data():
    teachers = get_all_teachers()
    subjects = get_all_subjects()
    rooms = get_all_rooms()
    sections = get_all_sections()
    config = get_config()
    timetable = get_timetable()
    lectures = get_all_lectures()
    
    # Calculate stats
    total_assigned = len(timetable)
    locked_count = sum(1 for e in timetable if e.get("is_locked"))
    
    # Build departments list with counts
    from database.vtu_syllabus import VTU_DEPARTMENTS
    dept_counts = {}
    for s in subjects:
        br = s.get("branch", "GENERAL")
        dept_counts[br] = dept_counts.get(br, 0) + 1
        
    departments = []
    for d in VTU_DEPARTMENTS:
        d_copy = dict(d)
        d_copy["subject_count"] = dept_counts.get(d["code"], 0)
        departments.append(d_copy)
        
    return jsonify({
        "status": "success",
        "teachers": teachers,
        "subjects": subjects,
        "rooms": rooms,
        "sections": sections,
        "departments": departments,
        "config": config,
        "timetable": timetable,
        "lectures": lectures,
        "stats": {
            "num_teachers": len(teachers),
            "num_subjects": len(subjects),
            "num_rooms": len(rooms),
            "num_sections": len(sections),
            "num_departments": len(departments),
            "num_entries": total_assigned,
            "num_locked": locked_count,
            "num_lectures": len(lectures)
        }
    })

# Config
@api_bp.route("/config", methods=["POST"])
def update_system_config():
    data = request.json or {}
    days = data.get("days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    periods = int(data.get("periods_per_day", 7))
    start_time = data.get("start_time", "09:00")
    period_duration = int(data.get("period_duration", 55))
    short_break_after = int(data.get("short_break_after", 2))
    short_break_duration = int(data.get("short_break_duration", 15))
    lunch_break_after = int(data.get("lunch_break_after", 4))
    lunch_break_duration = int(data.get("lunch_break_duration", 50))
    time_slots = data.get("time_slots")
    
    update_config(
        days=days,
        periods_per_day=periods,
        start_time=start_time,
        period_duration=period_duration,
        short_break_after=short_break_after,
        short_break_duration=short_break_duration,
        lunch_break_after=lunch_break_after,
        lunch_break_duration=lunch_break_duration,
        time_slots=time_slots
    )
    return jsonify({
        "status": "success",
        "message": "Academic grid and timing configuration updated successfully.",
        "config": get_config()
    })

@api_bp.route("/config/preview-slots", methods=["POST"])
def preview_time_slots():
    data = request.json or {}
    start_time = data.get("start_time", "09:00")
    period_duration = int(data.get("period_duration", 55))
    periods = int(data.get("periods_per_day", 7))
    short_break_after = int(data.get("short_break_after", 2))
    short_break_duration = int(data.get("short_break_duration", 15))
    lunch_break_after = int(data.get("lunch_break_after", 4))
    lunch_break_duration = int(data.get("lunch_break_duration", 50))
    
    from database.db import generate_default_time_slots
    slots = generate_default_time_slots(
        start_time=start_time,
        period_duration=period_duration,
        periods_count=periods,
        short_break_after=short_break_after,
        short_break_duration=short_break_duration,
        lunch_break_after=lunch_break_after,
        lunch_break_duration=lunch_break_duration
    )
    return jsonify({"status": "success", "time_slots": slots})

# Seed Data
@api_bp.route("/seed", methods=["POST"])
def seed_data():
    seed_default_data()
    return jsonify({"status": "success", "message": "Demo college dataset loaded successfully!"})

# Teachers CRUD
@api_bp.route("/teachers", methods=["POST"])
def create_teacher():
    data = request.json or {}
    if not data.get("id") or not data.get("name") or not data.get("branch"):
        return jsonify({"status": "error", "message": "ID, Name, and Branch are required."}), 400
    save_teacher(data)
    return jsonify({"status": "success", "message": f"Teacher {data['id']} saved."})

@api_bp.route("/teachers/<teacher_id>", methods=["GET"])
def get_single_teacher(teacher_id):
    t = get_teacher(teacher_id)
    if not t:
        return jsonify({"status": "error", "message": f"Teacher {teacher_id} not found."}), 404
    return jsonify({"status": "success", "teacher": t})

@api_bp.route("/teachers/<teacher_id>", methods=["DELETE"])
def remove_teacher(teacher_id):
    delete_teacher(teacher_id)
    return jsonify({"status": "success", "message": f"Teacher {teacher_id} deleted."})

# Departments & VTU Curriculum
@api_bp.route("/departments", methods=["GET"])
def get_departments():
    from database.vtu_syllabus import VTU_DEPARTMENTS
    subjects = get_all_subjects()
    
    # Calculate subject counts per department
    dept_counts = {}
    for s in subjects:
        br = s.get("branch", "GENERAL")
        dept_counts[br] = dept_counts.get(br, 0) + 1
        
    result = []
    for d in VTU_DEPARTMENTS:
        d_copy = dict(d)
        d_copy["subject_count"] = dept_counts.get(d["code"], 0)
        result.append(d_copy)
        
    return jsonify({
        "status": "success",
        "departments": result
    })

@api_bp.route("/departments/<dept_code>/subjects", methods=["GET"])
def get_department_subjects(dept_code):
    semester = request.args.get("semester")
    sem_int = int(semester) if semester and semester.isdigit() else None
    subjects = get_all_subjects(branch=dept_code, semester=sem_int)
    return jsonify({
        "status": "success",
        "department": dept_code,
        "semester": sem_int,
        "subjects": subjects
    })

@api_bp.route("/departments/quick-create-section", methods=["POST"])
def quick_create_section_from_semester():
    data = request.json or {}
    branch = data.get("branch", "CSE")
    semester = int(data.get("semester", 5))
    section_name = data.get("section_id") or f"{branch}-{semester}A"
    
    # Fetch all subjects for this branch and semester
    dept_subjects = get_all_subjects(branch=branch, semester=semester)
    if not dept_subjects:
        return jsonify({"status": "error", "message": f"No subjects found for {branch} Semester {semester}."}), 404
        
    core_subjects = []
    elective_options = []
    
    for s in dept_subjects:
        if "elective" in s["name"].lower():
            elective_options.append(s["id"])
        else:
            core_subjects.append(s["id"])
            
    electives_payload = []
    if elective_options:
        electives_payload.append({
            "group": f"Elective-Sem{semester}",
            "options": elective_options
        })
        
    section_data = {
        "id": section_name,
        "branch": branch,
        "semester": semester,
        "subjects": core_subjects,
        "electives": electives_payload
    }
    
    save_section(section_data)
    return jsonify({
        "status": "success",
        "message": f"Section {section_name} created with {len(core_subjects)} core subjects and {len(elective_options)} elective options.",
        "section": section_data
    })

# Subjects CRUD
@api_bp.route("/subjects/import-vtu", methods=["POST"])
def import_vtu_subjects_endpoint():
    from database.vtu_syllabus import import_vtu_syllabus
    result = import_vtu_syllabus()
    return jsonify({
        "status": "success",
        "message": f"VTU Syllabus imported: {result['added']} new subjects added, {result.get('updated', 0)} existing updated.",
        "result": result
    })

@api_bp.route("/subjects", methods=["POST"])
def create_subject():
    data = request.json or {}
    if not data.get("id") or not data.get("name") or not data.get("branch"):
        return jsonify({"status": "error", "message": "ID, Name, and Branch are required."}), 400
    save_subject(data)
    return jsonify({"status": "success", "message": f"Subject {data['id']} saved."})

@api_bp.route("/subjects/<subject_id>", methods=["GET"])
def get_single_subject(subject_id):
    s = get_subject(subject_id)
    if not s:
        return jsonify({"status": "error", "message": f"Subject {subject_id} not found."}), 404
    return jsonify({"status": "success", "subject": s})

@api_bp.route("/subjects/<subject_id>", methods=["DELETE"])
def remove_subject(subject_id):
    delete_subject(subject_id)
    return jsonify({"status": "success", "message": f"Subject {subject_id} deleted."})

# Rooms CRUD
@api_bp.route("/rooms", methods=["POST"])
def create_room():
    data = request.json or {}
    if not data.get("id"):
        return jsonify({"status": "error", "message": "Room ID is required."}), 400
    save_room(data)
    return jsonify({"status": "success", "message": f"Room {data['id']} saved."})

@api_bp.route("/rooms/<room_id>", methods=["GET"])
def get_single_room(room_id):
    r = get_room(room_id)
    if not r:
        return jsonify({"status": "error", "message": f"Room {room_id} not found."}), 404
    return jsonify({"status": "success", "room": r})

@api_bp.route("/rooms/<room_id>", methods=["DELETE"])
def remove_room(room_id):
    delete_room(room_id)
    return jsonify({"status": "success", "message": f"Room {room_id} deleted."})

# Sections CRUD
@api_bp.route("/sections", methods=["POST"])
def create_section():
    data = request.json or {}
    if not data.get("id") or not data.get("branch"):
        return jsonify({"status": "error", "message": "Section ID and Branch are required."}), 400
    save_section(data)
    return jsonify({"status": "success", "message": f"Section {data['id']} saved."})

@api_bp.route("/sections/<section_id>", methods=["GET"])
def get_single_section(section_id):
    sec = get_section(section_id)
    if not sec:
        return jsonify({"status": "error", "message": f"Section {section_id} not found."}), 404
    return jsonify({"status": "success", "section": sec})

@api_bp.route("/sections/<section_id>", methods=["DELETE"])
def remove_section(section_id):
    delete_section(section_id)
    return jsonify({"status": "success", "message": f"Section {section_id} deleted."})

# Full Solve Generator
@api_bp.route("/generate", methods=["POST"])
def generate_timetable():
    req_data = request.json or {}
    preserve_locked = req_data.get("preserve_locked", True)
    
    teachers = [Teacher.from_dict(t) for t in get_all_teachers()]
    subjects = [Subject.from_dict(s) for s in get_all_subjects()]
    rooms = [Room.from_dict(r) for r in get_all_rooms()]
    sections = [Section.from_dict(sec) for sec in get_all_sections()]
    config = get_config()
    
    locked_entries = []
    if preserve_locked:
        locked_entries = [e for e in get_timetable() if e.get("is_locked")]
    
    solver = TimetableSolver(
        teachers=teachers,
        subjects=subjects,
        rooms=rooms,
        sections=sections,
        days=config["days"],
        periods_per_day=config["periods_per_day"],
        lunch_break_period=config.get("lunch_break_period", 4),
        locked_entries=locked_entries
    )
    
    success, entries, stats = solver.solve()
    if not success:
        return jsonify({
            "status": "error",
            "message": stats.get("error", "Solver could not find a feasible schedule."),
            "stats": stats
        }), 422
    
    # Save to DB
    dict_entries = [e.to_dict() for e in entries]
    save_timetable(dict_entries, preserve_locked=preserve_locked)
    
    return jsonify({
        "status": "success",
        "message": f"Timetable generated successfully in {stats['time_taken_seconds']}s with {stats['num_entries']} entries.",
        "stats": stats,
        "timetable": dict_entries
    })

# Lock / Pin Toggle
@api_bp.route("/timetable/lock", methods=["POST"])
def toggle_lock():
    data = request.json or {}
    day = data.get("day")
    period = int(data.get("period", 0))
    section_id = data.get("section_id")
    subject_id = data.get("subject_id")
    is_locked = bool(data.get("is_locked", True))
    
    update_entry_lock(day, period, section_id, subject_id, is_locked)
    return jsonify({"status": "success", "message": f"Lock status updated to {is_locked}."})

@api_bp.route("/timetable/unlock-all", methods=["POST"])
def unlock_all():
    unlock_all_entries()
    return jsonify({"status": "success", "message": "All locked slots have been unpinned."})

# Manual Assist (Permutations & Patch Mode)
@api_bp.route("/manual-assist/candidates", methods=["POST"])
def get_manual_candidates():
    data = request.json or {}
    teacher_id = data.get("teacher_id")
    section_id = data.get("section_id")
    subject_id = data.get("subject_id")
    
    if not teacher_id or not section_id or not subject_id:
        return jsonify({"status": "error", "message": "Teacher, Section, and Subject IDs are required."}), 400
        
    teachers = [Teacher.from_dict(t) for t in get_all_teachers()]
    subjects = [Subject.from_dict(s) for s in get_all_subjects()]
    rooms = [Room.from_dict(r) for r in get_all_rooms()]
    sections = [Section.from_dict(sec) for sec in get_all_sections()]
    config = get_config()
    current_tt = get_timetable()
    
    engine = ManualAssistEngine(
        teachers=teachers,
        subjects=subjects,
        rooms=rooms,
        sections=sections,
        days=config["days"],
        periods_per_day=config["periods_per_day"],
        current_timetable=current_tt
    )
    
    options = engine.get_valid_placements_for_teacher(
        teacher_id=teacher_id,
        section_id=section_id,
        subject_id=subject_id,
        max_options=8
    )
    
    return jsonify({
        "status": "success",
        "num_options": len(options),
        "options": options
    })

@api_bp.route("/manual-assist/apply", methods=["POST"])
def apply_manual_slots():
    data = request.json or {}
    slots = data.get("slots", [])
    resolve_remainder = data.get("resolve_remainder", True)
    
    if not slots:
        return jsonify({"status": "error", "message": "No slots provided."}), 400
        
    # Remove existing entries for this (section_id, subject_id) and insert the new pinned slots
    sample = slots[0]
    section_id = sample["section_id"]
    subject_id = sample["subject_id"]
    
    current_tt = get_timetable()
    filtered_tt = [
        e for e in current_tt
        if not (e["section_id"] == section_id and e["subject_id"] == subject_id)
    ]
    
    for s in slots:
        s["is_locked"] = True
        filtered_tt.append(s)
        
    save_timetable(filtered_tt, preserve_locked=False)
    
    if resolve_remainder:
        # Re-trigger solver with locked slots preserved
        teachers = [Teacher.from_dict(t) for t in get_all_teachers()]
        subjects = [Subject.from_dict(s) for s in get_all_subjects()]
        rooms = [Room.from_dict(r) for r in get_all_rooms()]
        sections = [Section.from_dict(sec) for sec in get_all_sections()]
        config = get_config()
        locked = [e for e in get_timetable() if e.get("is_locked")]
        
        solver = TimetableSolver(
            teachers=teachers,
            subjects=subjects,
            rooms=rooms,
            sections=sections,
            days=config["days"],
            periods_per_day=config["periods_per_day"],
            lunch_break_period=config.get("lunch_break_period", 4),
            locked_entries=locked
        )
        success, entries, stats = solver.solve()
        if success:
            dict_entries = [e.to_dict() for e in entries]
            save_timetable(dict_entries, preserve_locked=True)
            return jsonify({
                "status": "success",
                "message": "Manual slots pinned and entire timetable successfully re-aligned!",
                "stats": stats
            })
        else:
            return jsonify({
                "status": "warning",
                "message": "Manual slots were pinned, but remaining timetable could not be fully resolved without clashes. Try another permutation.",
                "stats": stats
            }), 422
            
    return jsonify({"status": "success", "message": "Manual slots pinned successfully."})

# Export Routes
@api_bp.route("/export/csv", methods=["GET"])
def export_csv():
    entries = get_timetable()
    csv_data = ExportService.generate_csv(entries)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=timetable_schedule.csv"}
    )

@api_bp.route("/export/excel", methods=["GET"])
def export_excel():
    entries = get_timetable()
    config = get_config()
    teachers_map = {t["id"]: t for t in get_all_teachers()}
    subjects_map = {s["id"]: s for s in get_all_subjects()}
    sections = get_all_sections()
    periods = list(range(1, config["periods_per_day"] + 1))
    
    excel_stream = ExportService.generate_excel(
        entries=entries,
        days=config["days"],
        periods=periods,
        teachers_map=teachers_map,
        subjects_map=subjects_map,
        sections=sections,
        time_slots=config.get("time_slots")
    )
    return send_file(
        excel_stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="SlotSync_Timetable.xlsx"
    )

# Lectures CRUD
@api_bp.route("/lectures", methods=["GET"])
def list_lectures():
    lectures = get_all_lectures()
    return jsonify({"status": "success", "lectures": lectures})

@api_bp.route("/lectures", methods=["POST"])
def create_lecture():
    data = request.json or {}
    if not data.get("subject_id") or not data.get("teacher_id") or not data.get("section_id"):
        return jsonify({"status": "error", "message": "Subject, Teacher, and Section are required."}), 400
    save_lecture(data)
    return jsonify({"status": "success", "message": f"Lecture assignment saved: {data['teacher_id']} → {data['subject_id']} for {data['section_id']}."})

@api_bp.route("/lectures/<int:lecture_id>", methods=["DELETE"])
def remove_lecture(lecture_id):
    delete_lecture(lecture_id)
    return jsonify({"status": "success", "message": f"Lecture #{lecture_id} removed."})


# Conflict Diagnostics Engine
@api_bp.route("/diagnostics", methods=["GET"])
def get_diagnostics():
    entries = get_timetable()
    teachers = {t["id"]: t for t in get_all_teachers()}
    rooms = {r["id"]: r for r in get_all_rooms()}
    sections = {s["id"]: s for s in get_all_sections()}
    subjects = {s["id"]: s for s in get_all_subjects()}
    lectures = get_all_lectures()

    issues = []
    
    if not entries:
        return jsonify({
            "status": "success",
            "summary": {
                "health_score": 100,
                "total_issues": 0,
                "critical_count": 0,
                "warning_count": 0,
                "info_count": 0
            },
            "issues": []
        })

    # 1. Teacher Double Booking (Hard Conflict)
    teacher_slots = {}
    for e in entries:
        t_id = e.get("teacher_id")
        if not t_id:
            continue
        key = (e.get("day"), e.get("period"), t_id)
        teacher_slots.setdefault(key, []).append(e)

    for (day, period, t_id), slot_entries in teacher_slots.items():
        if len(slot_entries) > 1:
            sec_names = ", ".join([se.get("section_id", "N/A") for se in slot_entries])
            teacher_name = teachers.get(t_id, {}).get("name", t_id)
            issues.append({
                "id": f"tc_{day}_{period}_{t_id}",
                "type": "teacher_clash",
                "severity": "critical",
                "title": f"Teacher Double-Booked: {teacher_name}",
                "message": f"{teacher_name} is simultaneously scheduled for sections ({sec_names}) on {day}, Period {period}.",
                "day": day,
                "period": period,
                "target_type": "teacher",
                "target_id": t_id
            })

    # 2. Room Double Booking (Hard Conflict)
    room_slots = {}
    for e in entries:
        r_id = e.get("room_id")
        if not r_id:
            continue
        key = (e.get("day"), e.get("period"), r_id)
        room_slots.setdefault(key, []).append(e)

    for (day, period, r_id), slot_entries in room_slots.items():
        if len(slot_entries) > 1:
            sec_names = ", ".join([se.get("section_id", "N/A") for se in slot_entries])
            issues.append({
                "id": f"rc_{day}_{period}_{r_id}",
                "type": "room_clash",
                "severity": "critical",
                "title": f"Room Clash: Room {r_id}",
                "message": f"Room {r_id} is simultaneously occupied by sections ({sec_names}) on {day}, Period {period}.",
                "day": day,
                "period": period,
                "target_type": "room",
                "target_id": r_id
            })

    # 3. Section Multiple Classes (unless elective)
    section_slots = {}
    for e in entries:
        s_id = e.get("section_id")
        if not s_id:
            continue
        key = (e.get("day"), e.get("period"), s_id)
        section_slots.setdefault(key, []).append(e)

    for (day, period, s_id), slot_entries in section_slots.items():
        if len(slot_entries) > 1:
            # Check if all are electives (parallel elective slots)
            all_electives = all(
                bool(se.get("is_elective")) or bool(se.get("elective_group")) for se in slot_entries
            )
            if not all_electives:
                subj_codes = ", ".join([se.get("subject_id", "N/A") for se in slot_entries])
                issues.append({
                    "id": f"sc_{day}_{period}_{s_id}",
                    "type": "section_clash",
                    "severity": "critical",
                    "title": f"Section Overlap: {s_id}",
                    "message": f"Section {s_id} has overlapping classes ({subj_codes}) on {day}, Period {period}.",
                    "day": day,
                    "period": period,
                    "target_type": "section",
                    "target_id": s_id
                })

    # 4. Room Capacity Overflow (Warning)
    for e in entries:
        r_id = e.get("room_id")
        s_id = e.get("section_id")
        room_obj = rooms.get(r_id)
        section_obj = sections.get(s_id)
        if room_obj and section_obj:
            cap = room_obj.get("capacity", 0)
            students = section_obj.get("student_count", 0)
            if students > cap and cap > 0:
                issues.append({
                    "id": f"cap_{e.get('day')}_{e.get('period')}_{r_id}_{s_id}",
                    "type": "capacity_overflow",
                    "severity": "warning",
                    "title": f"Capacity Overflow: {s_id} in {r_id}",
                    "message": f"Section {s_id} ({students} students) exceeds room {r_id} capacity ({cap} seats) on {e.get('day')}, Period {e.get('period')}.",
                    "day": e.get("day"),
                    "period": e.get("period"),
                    "target_type": "room",
                    "target_id": r_id
                })

    # 5. Teacher Weekly Workload Overload (Warning)
    teacher_hour_counts = {}
    for e in entries:
        t_id = e.get("teacher_id")
        if t_id:
            teacher_hour_counts[t_id] = teacher_hour_counts.get(t_id, 0) + 1

    for t_id, count in teacher_hour_counts.items():
        t_obj = teachers.get(t_id, {})
        max_daily = t_obj.get("max_hours_per_day", 4)
        max_weekly = max_daily * 5  # assuming 5 working days
        if count > max_weekly:
            issues.append({
                "id": f"tover_{t_id}",
                "type": "workload_overload",
                "severity": "warning",
                "title": f"Faculty Workload Exceeded: {t_obj.get('name', t_id)}",
                "message": f"{t_obj.get('name', t_id)} is scheduled for {count} hours/week (recommended max: {max_weekly} hours).",
                "day": "Weekly",
                "period": None,
                "target_type": "teacher",
                "target_id": t_id
            })

    # 6. Curriculum / Lecture Coverage (Info/Warning)
    # Check subjects scheduled vs required hours
    subject_scheduled = {}
    for e in entries:
        subj = e.get("subject_id")
        if subj:
            subject_scheduled[subj] = subject_scheduled.get(subj, 0) + 1

    for subj_id, subj_obj in subjects.items():
        req = subj_obj.get("weekly_hours", 0)
        actual = subject_scheduled.get(subj_id, 0)
        if req > 0 and actual < req:
            issues.append({
                "id": f"deficit_{subj_id}",
                "type": "curriculum_deficit",
                "severity": "info",
                "title": f"Curriculum Shortfall: {subj_id}",
                "message": f"{subj_id} ({subj_obj.get('name')}) has {actual} periods scheduled out of {req} required weekly hours.",
                "day": "Weekly",
                "period": None,
                "target_type": "section",
                "target_id": None
            })

    critical_count = sum(1 for i in issues if i["severity"] == "critical")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    info_count = sum(1 for i in issues if i["severity"] == "info")

    # Health score: 100 minus penalties
    score = 100 - (critical_count * 25) - (warning_count * 5)
    score = max(0, min(100, score))

    return jsonify({
        "status": "success",
        "summary": {
            "health_score": score,
            "total_issues": len(issues),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "info_count": info_count
        },
        "issues": issues
    })


# =========================================================================
# Bulk Data Import & Template Endpoints
# =========================================================================
@api_bp.route("/import/template/<entity_type>", methods=["GET"])
def download_import_template(entity_type):
    file_format = request.args.get("format", "csv").lower()
    try:
        buffer = ImportService.generate_template(entity_type, file_format)
        if entity_type == "workbook" or file_format in ["excel", "xlsx"]:
            filename = f"SlotSync_{entity_type.capitalize()}_Template.xlsx"
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            filename = f"SlotSync_{entity_type.capitalize()}_Template.csv"
            mimetype = "text/csv"

        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to generate template: {str(e)}"}), 400

@api_bp.route("/import/<entity_type>", methods=["POST"])
def import_entity_data(entity_type):
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded. Please attach a file under the 'file' field."}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"status": "error", "message": "No file selected for upload."}), 400

    parsers = {
        "teachers": ImportService.import_teachers,
        "subjects": ImportService.import_subjects,
        "rooms": ImportService.import_rooms,
        "sections": ImportService.import_sections,
        "workbook": ImportService.import_workbook
    }

    parser = parsers.get(entity_type.lower())
    if not parser:
        return jsonify({"status": "error", "message": f"Invalid entity type '{entity_type}'. Allowed types: {list(parsers.keys())}"}), 400

    try:
        result = parser(file)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as ex:
        return jsonify({"status": "error", "message": f"Import failed: {str(ex)}"}), 500

