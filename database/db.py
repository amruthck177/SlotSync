import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "timetable.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def generate_default_time_slots(
    start_time: str = "09:00",
    period_duration: int = 55,
    periods_count: int = 7,
    short_break_after: int = 2,
    short_break_duration: int = 15,
    lunch_break_after: int = 4,
    lunch_break_duration: int = 50
) -> List[Dict[str, Any]]:
    """
    Auto-computes start and end times for all teaching periods and breaks.
    """
    try:
        cur_time = datetime.strptime(start_time, "%H:%M")
    except ValueError:
        cur_time = datetime.strptime("09:00", "%H:%M")

    slots = []
    p_num = 1

    while p_num <= periods_count:
        # Teaching period
        end_time = cur_time + timedelta(minutes=period_duration)
        slots.append({
            "period": p_num,
            "type": "teaching",
            "label": f"Period {p_num}",
            "start_time": format_time(cur_time),
            "end_time": format_time(end_time),
            "duration": period_duration
        })
        cur_time = end_time

        # Check for Short Break
        if short_break_after > 0 and p_num == short_break_after and short_break_duration > 0:
            break_end = cur_time + timedelta(minutes=short_break_duration)
            slots.append({
                "period": 0,
                "type": "break",
                "label": "Short Break",
                "start_time": format_time(cur_time),
                "end_time": format_time(break_end),
                "duration": short_break_duration
            })
            cur_time = break_end

        # Check for Lunch Break
        if lunch_break_after > 0 and p_num == lunch_break_after and lunch_break_duration > 0:
            lunch_end = cur_time + timedelta(minutes=lunch_break_duration)
            slots.append({
                "period": 0,
                "type": "lunch",
                "label": "Lunch Break",
                "start_time": format_time(cur_time),
                "end_time": format_time(lunch_end),
                "duration": lunch_break_duration
            })
            cur_time = lunch_end

        p_num += 1

    return slots

def init_db():
    conn = get_db_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    
    # Check config columns and migrate if necessary
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(config)")
    columns = [row["name"] for row in cur.fetchall()]

    new_cols = [
        ("start_time", "TEXT NOT NULL DEFAULT '09:00'"),
        ("period_duration", "INTEGER NOT NULL DEFAULT 55"),
        ("short_break_after", "INTEGER NOT NULL DEFAULT 2"),
        ("short_break_duration", "INTEGER NOT NULL DEFAULT 15"),
        ("lunch_break_after", "INTEGER NOT NULL DEFAULT 4"),
        ("lunch_break_duration", "INTEGER NOT NULL DEFAULT 50"),
        ("time_slots_json", "TEXT NOT NULL DEFAULT '[]'")
    ]

    for col_name, col_def in new_cols:
        if col_name not in columns:
            try:
                cur.execute(f"ALTER TABLE config ADD COLUMN {col_name} {col_def}")
            except Exception as ex:
                print(f"Migration note for {col_name}: {ex}")

    # Check subjects columns and migrate if necessary
    cur.execute("PRAGMA table_info(subjects)")
    subj_columns = [row["name"] for row in cur.fetchall()]
    if "semester" not in subj_columns:
        try:
            cur.execute("ALTER TABLE subjects ADD COLUMN semester INTEGER NOT NULL DEFAULT 5")
        except Exception as ex:
            print(f"Migration note for subjects.semester: {ex}")

    # Check if row 1 exists
    cur.execute("SELECT COUNT(*) as count FROM config WHERE id = 1")
    if cur.fetchone()["count"] == 0:
        default_slots = generate_default_time_slots()
        cur.execute("""
            INSERT INTO config (
                id, days, periods_per_day, start_time, period_duration,
                short_break_after, short_break_duration,
                lunch_break_after, lunch_break_duration, time_slots_json
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(["Mon", "Tue", "Wed", "Thu", "Fri"]),
            7, "09:00", 55, 2, 15, 4, 50, json.dumps(default_slots)
        ))
    else:
        # Verify if time_slots_json is populated
        cur.execute("SELECT time_slots_json FROM config WHERE id = 1")
        row = cur.fetchone()
        if not row or not row["time_slots_json"] or row["time_slots_json"] == "[]":
            default_slots = generate_default_time_slots()
            cur.execute("UPDATE config SET time_slots_json = ? WHERE id = 1", (json.dumps(default_slots),))

    conn.commit()
    conn.close()

# Config
def get_config() -> Dict[str, Any]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM config WHERE id = 1")
    row = cur.fetchone()
    conn.close()

    if row:
        slots = json.loads(row["time_slots_json"]) if "time_slots_json" in row.keys() and row["time_slots_json"] else []
        if not slots:
            slots = generate_default_time_slots(
                start_time=row["start_time"] if "start_time" in row.keys() else "09:00",
                period_duration=row["period_duration"] if "period_duration" in row.keys() else 55,
                periods_count=row["periods_per_day"],
                short_break_after=row["short_break_after"] if "short_break_after" in row.keys() else 2,
                short_break_duration=row["short_break_duration"] if "short_break_duration" in row.keys() else 15,
                lunch_break_after=row["lunch_break_after"] if "lunch_break_after" in row.keys() else 4,
                lunch_break_duration=row["lunch_break_duration"] if "lunch_break_duration" in row.keys() else 50,
            )

        return {
            "days": json.loads(row["days"]),
            "periods_per_day": row["periods_per_day"],
            "start_time": row["start_time"] if "start_time" in row.keys() else "09:00",
            "period_duration": row["period_duration"] if "period_duration" in row.keys() else 55,
            "short_break_after": row["short_break_after"] if "short_break_after" in row.keys() else 2,
            "short_break_duration": row["short_break_duration"] if "short_break_duration" in row.keys() else 15,
            "lunch_break_after": row["lunch_break_after"] if "lunch_break_after" in row.keys() else 4,
            "lunch_break_duration": row["lunch_break_duration"] if "lunch_break_duration" in row.keys() else 50,
            "time_slots": slots
        }

    default_slots = generate_default_time_slots()
    return {
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "periods_per_day": 7,
        "start_time": "09:00",
        "period_duration": 55,
        "short_break_after": 2,
        "short_break_duration": 15,
        "lunch_break_after": 4,
        "lunch_break_duration": 50,
        "time_slots": default_slots
    }

def update_config(
    days: List[str],
    periods_per_day: int,
    start_time: str = "09:00",
    period_duration: int = 55,
    short_break_after: int = 2,
    short_break_duration: int = 15,
    lunch_break_after: int = 4,
    lunch_break_duration: int = 50,
    time_slots: Optional[List[Dict[str, Any]]] = None
):
    if not time_slots:
        time_slots = generate_default_time_slots(
            start_time=start_time,
            period_duration=period_duration,
            periods_count=periods_per_day,
            short_break_after=short_break_after,
            short_break_duration=short_break_duration,
            lunch_break_after=lunch_break_after,
            lunch_break_duration=lunch_break_duration
        )

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE config SET 
            days = ?,
            periods_per_day = ?,
            start_time = ?,
            period_duration = ?,
            short_break_after = ?,
            short_break_duration = ?,
            lunch_break_after = ?,
            lunch_break_duration = ?,
            time_slots_json = ?
        WHERE id = 1
    """, (
        json.dumps(days),
        periods_per_day,
        start_time,
        period_duration,
        short_break_after,
        short_break_duration,
        lunch_break_after,
        lunch_break_duration,
        json.dumps(time_slots)
    ))
    conn.commit()
    conn.close()

# Teachers
def get_all_teachers() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teachers ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        subj = json.loads(r["subjects_json"])
        cb = json.loads(r["cross_branch_json"])
        result.append({
            "id": r["id"],
            "name": r["name"],
            "branch": r["branch"],
            "subjects": subj,
            "cross_branch_subjects": cb,
            "num_subjects": len(subj) + len(cb),
            "max_hours_per_day": r["max_hours_per_day"],
            "max_hours_per_week": r["max_hours_per_week"],
        })
    return result

def save_teacher(teacher: Dict[str, Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    subj_json = json.dumps(teacher.get("subjects", []))
    cb_json = json.dumps(teacher.get("cross_branch_subjects", []))
    cur.execute("""
        INSERT INTO teachers (id, name, branch, subjects_json, cross_branch_json, max_hours_per_day, max_hours_per_week)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            branch = excluded.branch,
            subjects_json = excluded.subjects_json,
            cross_branch_json = excluded.cross_branch_json,
            max_hours_per_day = excluded.max_hours_per_day,
            max_hours_per_week = excluded.max_hours_per_week
    """, (
        teacher["id"],
        teacher["name"],
        teacher["branch"],
        subj_json,
        cb_json,
        int(teacher.get("max_hours_per_day", 4)),
        int(teacher.get("max_hours_per_week", 20))
    ))
    conn.commit()
    conn.close()

def delete_teacher(teacher_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()

def get_teacher(teacher_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teachers WHERE id = ?", (teacher_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    subj = json.loads(r["subjects_json"])
    cb = json.loads(r["cross_branch_json"])
    return {
        "id": r["id"],
        "name": r["name"],
        "branch": r["branch"],
        "subjects": subj,
        "cross_branch_subjects": cb,
        "num_subjects": len(subj) + len(cb),
        "max_hours_per_day": r["max_hours_per_day"],
        "max_hours_per_week": r["max_hours_per_week"],
    }

# Subjects
def get_all_subjects(branch: Optional[str] = None, semester: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM subjects WHERE 1=1"
    params = []
    if branch:
        query += " AND branch = ?"
        params.append(branch)
    if semester:
        query += " AND semester = ?"
        params.append(int(semester))
    query += " ORDER BY branch, semester, id"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    from models.subject import extract_semester_from_code
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "branch": r["branch"],
            "weekly_hours": r["weekly_hours"],
            "needs_lab": bool(r["needs_lab"]),
            "consecutive_hours": r["consecutive_hours"],
            "semester": r["semester"] if "semester" in r.keys() and r["semester"] else extract_semester_from_code(r["id"])
        }
        for r in rows
    ]

def save_subject(subject: Dict[str, Any]):
    from models.subject import extract_semester_from_code
    code = subject["id"]
    sem = subject.get("semester")
    if sem is None or not str(sem).isdigit() or int(sem) < 1 or int(sem) > 8:
        sem = extract_semester_from_code(code)
    else:
        sem = int(sem)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subjects (id, name, branch, weekly_hours, needs_lab, consecutive_hours, semester)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            branch = excluded.branch,
            weekly_hours = excluded.weekly_hours,
            needs_lab = excluded.needs_lab,
            consecutive_hours = excluded.consecutive_hours,
            semester = excluded.semester
    """, (
        code,
        subject["name"],
        subject["branch"],
        int(subject.get("weekly_hours", 4)),
        1 if subject.get("needs_lab", False) else 0,
        int(subject.get("consecutive_hours", 1)),
        sem
    ))
    conn.commit()
    conn.close()

def delete_subject(subject_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()

def get_subject(subject_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    from models.subject import extract_semester_from_code
    return {
        "id": r["id"],
        "name": r["name"],
        "branch": r["branch"],
        "weekly_hours": r["weekly_hours"],
        "needs_lab": bool(r["needs_lab"]),
        "consecutive_hours": r["consecutive_hours"],
        "semester": r["semester"] if "semester" in r.keys() and r["semester"] else extract_semester_from_code(r["id"])
    }

# Rooms
def get_all_rooms() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "type": r["type"],
            "capacity": r["capacity"],
            "branch": r["branch"],
            "is_lab": r["type"].lower() == "lab"
        }
        for r in rows
    ]

def save_room(room: Dict[str, Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO rooms (id, type, capacity, branch)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            type = excluded.type,
            capacity = excluded.capacity,
            branch = excluded.branch
    """, (
        room["id"],
        room.get("type", "regular"),
        int(room.get("capacity", 60)),
        room.get("branch", "GENERAL")
    ))
    conn.commit()
    conn.close()

def delete_room(room_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    conn.commit()
    conn.close()

def get_room(room_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r["id"],
        "type": r["type"],
        "capacity": r["capacity"],
        "branch": r["branch"],
        "is_lab": r["type"].lower() == "lab"
    }

# Sections
def get_all_sections() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sections ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "branch": r["branch"],
            "semester": r["semester"],
            "subjects": json.loads(r["subjects_json"]),
            "electives": json.loads(r["electives_json"]),
        })
    return result

def save_section(section: Dict[str, Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sections (id, branch, semester, subjects_json, electives_json)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            branch = excluded.branch,
            semester = excluded.semester,
            subjects_json = excluded.subjects_json,
            electives_json = excluded.electives_json
    """, (
        section["id"],
        section["branch"],
        int(section.get("semester", 5)),
        json.dumps(section.get("subjects", [])),
        json.dumps(section.get("electives", []))
    ))
    conn.commit()
    conn.close()

def delete_section(section_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sections WHERE id = ?", (section_id,))
    conn.commit()
    conn.close()

def get_section(section_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r["id"],
        "branch": r["branch"],
        "semester": r["semester"],
        "subjects": json.loads(r["subjects_json"]),
        "electives": json.loads(r["electives_json"]),
    }

# Timetable Entries
def get_timetable(section_id: Optional[str] = None, teacher_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM timetable_entries WHERE 1=1"
    params = []
    if section_id:
        query += " AND section_id = ?"
        params.append(section_id)
    if teacher_id:
        query += " AND teacher_id = ?"
        params.append(teacher_id)
    query += " ORDER BY day, period"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "day": r["day"],
            "period": r["period"],
            "subject_id": r["subject_id"],
            "teacher_id": r["teacher_id"],
            "room_id": r["room_id"],
            "section_id": r["section_id"],
            "is_elective": bool(r["is_elective"]),
            "elective_group": r["elective_group"],
            "is_locked": bool(r["is_locked"])
        }
        for r in rows
    ]

def save_timetable(entries: List[Dict[str, Any]], preserve_locked: bool = True):
    conn = get_db_connection()
    cur = conn.cursor()
    if not preserve_locked:
        cur.execute("DELETE FROM timetable_entries")
    else:
        cur.execute("DELETE FROM timetable_entries WHERE is_locked = 0")
    
    for e in entries:
        if preserve_locked:
            cur.execute("""
                SELECT id FROM timetable_entries 
                WHERE day = ? AND period = ? AND section_id = ? AND subject_id = ? AND is_locked = 1
            """, (e["day"], e["period"], e["section_id"], e["subject_id"]))
            if cur.fetchone():
                continue
                
        cur.execute("""
            INSERT INTO timetable_entries (day, period, subject_id, teacher_id, room_id, section_id, is_elective, elective_group, is_locked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e["day"],
            e["period"],
            e["subject_id"],
            e["teacher_id"],
            e["room_id"],
            e["section_id"],
            1 if e.get("is_elective", False) else 0,
            e.get("elective_group"),
            1 if e.get("is_locked", False) else 0
        ))
    conn.commit()
    conn.close()

def update_entry_lock(day: str, period: int, section_id: str, subject_id: str, is_locked: bool):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE timetable_entries SET is_locked = ?
        WHERE day = ? AND period = ? AND section_id = ? AND subject_id = ?
    """, (1 if is_locked else 0, day, period, section_id, subject_id))
    conn.commit()
    conn.close()

def unlock_all_entries():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE timetable_entries SET is_locked = 0")
    conn.commit()
    conn.close()

# Lectures CRUD
def get_all_lectures() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.id, l.subject_id, l.teacher_id, l.section_id,
               l.description, l.credits, l.preferred_room_type, l.is_tutorial,
               s.name as subject_name, s.branch as subject_branch, s.weekly_hours,
               s.needs_lab, s.semester,
               t.name as teacher_name, t.branch as teacher_branch,
               sec.branch as section_branch, sec.semester as section_semester
        FROM lectures l
        LEFT JOIN subjects s ON l.subject_id = s.id
        LEFT JOIN teachers t ON l.teacher_id = t.id
        LEFT JOIN sections sec ON l.section_id = sec.id
        ORDER BY l.section_id, l.subject_id
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "subject_id": r["subject_id"],
            "teacher_id": r["teacher_id"],
            "section_id": r["section_id"],
            "description": r["description"] or "",
            "credits": r["credits"],
            "preferred_room_type": r["preferred_room_type"],
            "is_tutorial": bool(r["is_tutorial"]),
            "subject_name": r["subject_name"] or r["subject_id"],
            "subject_branch": r["subject_branch"] or "",
            "weekly_hours": r["weekly_hours"] or 4,
            "needs_lab": bool(r["needs_lab"]) if r["needs_lab"] is not None else False,
            "semester": r["semester"] or r["section_semester"] or 5,
            "teacher_name": r["teacher_name"] or r["teacher_id"],
            "teacher_branch": r["teacher_branch"] or "",
            "section_branch": r["section_branch"] or "",
            "section_semester": r["section_semester"] or 5,
        }
        for r in rows
    ]

def save_lecture(lecture: Dict[str, Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    lecture_id = lecture.get("id")
    if lecture_id:
        cur.execute("""
            UPDATE lectures SET
                subject_id = ?, teacher_id = ?, section_id = ?,
                description = ?, credits = ?, preferred_room_type = ?, is_tutorial = ?
            WHERE id = ?
        """, (
            lecture["subject_id"],
            lecture["teacher_id"],
            lecture["section_id"],
            lecture.get("description", ""),
            int(lecture.get("credits", 4)),
            lecture.get("preferred_room_type", "regular"),
            1 if lecture.get("is_tutorial", False) else 0,
            lecture_id
        ))
    else:
        cur.execute("""
            INSERT INTO lectures (subject_id, teacher_id, section_id, description, credits, preferred_room_type, is_tutorial)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            lecture["subject_id"],
            lecture["teacher_id"],
            lecture["section_id"],
            lecture.get("description", ""),
            int(lecture.get("credits", 4)),
            lecture.get("preferred_room_type", "regular"),
            1 if lecture.get("is_tutorial", False) else 0
        ))
    conn.commit()
    conn.close()

def delete_lecture(lecture_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lectures WHERE id = ?", (lecture_id,))
    conn.commit()
    conn.close()

# Seed default data
def seed_default_data():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Clear existing tables
    cur.execute("DELETE FROM teachers")
    cur.execute("DELETE FROM subjects")
    cur.execute("DELETE FROM rooms")
    cur.execute("DELETE FROM sections")
    cur.execute("DELETE FROM timetable_entries")
    
    # Reset config with default time slots
    default_slots = generate_default_time_slots()
    cur.execute("""
        UPDATE config SET 
            days = ?,
            periods_per_day = 7,
            start_time = '09:00',
            period_duration = 55,
            short_break_after = 2,
            short_break_duration = 15,
            lunch_break_after = 4,
            lunch_break_duration = 50,
            time_slots_json = ?
        WHERE id = 1
    """, (json.dumps(["Mon", "Tue", "Wed", "Thu", "Fri"]), json.dumps(default_slots)))

    # Teachers
    teachers = [
        {
            "id": "T1", "name": "Dr. Suresh", "branch": "CSE",
            "subjects": ["CS301", "CS302"],
            "cross_branch_subjects": [{"code": "IS402", "branch": "ISE"}],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T2", "name": "Prof. Ananya", "branch": "CSE",
            "subjects": ["CS303", "CS304"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T3", "name": "Dr. Ramesh", "branch": "CSE",
            "subjects": ["CS305", "CS301L"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T4", "name": "Prof. Vikram", "branch": "CSE",
            "subjects": ["CS306", "CS302L"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T5", "name": "Prof. Priya", "branch": "CSE",
            "subjects": ["CS307", "CS303"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T6", "name": "Dr. Meenakshi", "branch": "ISE",
            "subjects": ["IS401", "IS402"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T7", "name": "Prof. Rajesh", "branch": "ISE",
            "subjects": ["IS403", "IS404"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T8", "name": "Prof. Kavita", "branch": "ISE",
            "subjects": ["IS405", "IS401"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T9", "name": "Dr. Harish", "branch": "ECE",
            "subjects": ["EC301", "EC302"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        },
        {
            "id": "T10", "name": "Prof. Sneha", "branch": "ECE",
            "subjects": ["EC303", "EC304", "EC301L"],
            "cross_branch_subjects": [],
            "max_hours_per_day": 4, "max_hours_per_week": 18
        }
    ]
    for t in teachers:
        cur.execute("""
            INSERT INTO teachers (id, name, branch, subjects_json, cross_branch_json, max_hours_per_day, max_hours_per_week)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (t["id"], t["name"], t["branch"], json.dumps(t["subjects"]), json.dumps(t["cross_branch_subjects"]), t["max_hours_per_day"], t["max_hours_per_week"]))
        
    # Subjects
    subjects = [
        {"id": "CS301", "name": "Database Management Systems", "branch": "CSE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "CS302", "name": "Operating Systems", "branch": "CSE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "CS303", "name": "Computer Networks", "branch": "CSE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "CS304", "name": "Design & Analysis of Algorithms", "branch": "CSE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "CS301L", "name": "DBMS Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": 1, "consecutive_hours": 2},
        {"id": "CS302L", "name": "OS Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": 1, "consecutive_hours": 2},
        {"id": "CS305", "name": "Artificial Intelligence (Elective)", "branch": "CSE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "CS306", "name": "Cloud Computing (Elective)", "branch": "CSE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "CS307", "name": "Cybersecurity (Elective)", "branch": "CSE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "IS401", "name": "Software Engineering", "branch": "ISE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "IS402", "name": "Web Technologies", "branch": "ISE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "IS403", "name": "Big Data Analytics", "branch": "ISE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "IS404", "name": "Data Mining", "branch": "ISE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "IS405", "name": "DevOps & Cloud (Elective)", "branch": "ISE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "EC301", "name": "Digital Signal Processing", "branch": "ECE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "EC302", "name": "VLSI Design", "branch": "ECE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "EC303", "name": "Microcontrollers & Embedded", "branch": "ECE", "weekly_hours": 4, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "EC304", "name": "Control Systems", "branch": "ECE", "weekly_hours": 3, "needs_lab": 0, "consecutive_hours": 1},
        {"id": "EC301L", "name": "DSP & VLSI Lab", "branch": "ECE", "weekly_hours": 2, "needs_lab": 1, "consecutive_hours": 2},
    ]
    for s in subjects:
        cur.execute("""
            INSERT INTO subjects (id, name, branch, weekly_hours, needs_lab, consecutive_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (s["id"], s["name"], s["branch"], s["weekly_hours"], s["needs_lab"], s["consecutive_hours"]))

    # Rooms
    rooms = [
        {"id": "LH-101", "type": "regular", "capacity": 65, "branch": "CSE"},
        {"id": "LH-102", "type": "regular", "capacity": 65, "branch": "CSE"},
        {"id": "LH-103", "type": "regular", "capacity": 65, "branch": "CSE"},
        {"id": "LH-201", "type": "regular", "capacity": 65, "branch": "ISE"},
        {"id": "LH-202", "type": "regular", "capacity": 65, "branch": "ISE"},
        {"id": "LH-301", "type": "regular", "capacity": 65, "branch": "ECE"},
        {"id": "LAB-1", "type": "lab", "capacity": 35, "branch": "CSE"},
        {"id": "LAB-2", "type": "lab", "capacity": 35, "branch": "CSE"},
        {"id": "LAB-3", "type": "lab", "capacity": 35, "branch": "ECE"},
    ]
    for r in rooms:
        cur.execute("""
            INSERT INTO rooms (id, type, capacity, branch)
            VALUES (?, ?, ?, ?)
        """, (r["id"], r["type"], r["capacity"], r["branch"]))

    # Sections
    sections = [
        {
            "id": "CSE-5A", "branch": "CSE", "semester": 5,
            "subjects": ["CS301", "CS302", "CS303", "CS304", "CS301L"],
            "electives": [{"group": "Elective-1", "options": ["CS305", "CS306", "CS307"]}]
        },
        {
            "id": "CSE-5B", "branch": "CSE", "semester": 5,
            "subjects": ["CS301", "CS302", "CS303", "CS304", "CS302L"],
            "electives": [{"group": "Elective-1", "options": ["CS305", "CS306", "CS307"]}]
        },
        {
            "id": "ISE-5A", "branch": "ISE", "semester": 5,
            "subjects": ["IS401", "IS402", "IS403", "IS404"],
            "electives": [{"group": "Elective-1", "options": ["CS305", "IS405"]}]
        },
        {
            "id": "ECE-5A", "branch": "ECE", "semester": 5,
            "subjects": ["EC301", "EC302", "EC303", "EC304", "EC301L"],
            "electives": []
        }
    ]
    for sec in sections:
        cur.execute("""
            INSERT INTO sections (id, branch, semester, subjects_json, electives_json)
            VALUES (?, ?, ?, ?, ?)
        """, (sec["id"], sec["branch"], sec["semester"], json.dumps(sec["subjects"]), json.dumps(sec["electives"])))

    # Lectures (sample teaching assignments)
    cur.execute("DELETE FROM lectures")
    sample_lectures = [
        {"subject_id": "CS301", "teacher_id": "T1", "section_id": "CSE-5A", "description": "Covers relational model, SQL, normalization, transactions, and indexing.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "CS302", "teacher_id": "T1", "section_id": "CSE-5A", "description": "Process management, memory, file systems, and concurrency.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "CS303", "teacher_id": "T2", "section_id": "CSE-5A", "description": "OSI model, TCP/IP, routing algorithms, and network security.", "credits": 3, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "CS304", "teacher_id": "T2", "section_id": "CSE-5A", "description": "Divide and conquer, greedy, dynamic programming, graph algorithms, NP-completeness.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "CS301L", "teacher_id": "T3", "section_id": "CSE-5A", "description": "Hands-on SQL queries, PL/SQL, schema design, and triggers.", "credits": 2, "preferred_room_type": "lab", "is_tutorial": 0},
        {"subject_id": "CS301", "teacher_id": "T1", "section_id": "CSE-5B", "description": "Covers relational model, SQL, normalization, transactions, and indexing.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "IS401", "teacher_id": "T6", "section_id": "ISE-5A", "description": "SDLC, agile, testing, maintenance, and project management.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "IS402", "teacher_id": "T6", "section_id": "ISE-5A", "description": "HTML, CSS, JavaScript, React/Angular basics, REST APIs.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "EC301", "teacher_id": "T9", "section_id": "ECE-5A", "description": "Z-transform, DFT, FFT, filter design, and spectral analysis.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
        {"subject_id": "EC302", "teacher_id": "T9", "section_id": "ECE-5A", "description": "MOS transistors, CMOS logic, layout design, and FPGA.", "credits": 4, "preferred_room_type": "regular", "is_tutorial": 0},
    ]
    for lec in sample_lectures:
        cur.execute("""
            INSERT INTO lectures (subject_id, teacher_id, section_id, description, credits, preferred_room_type, is_tutorial)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (lec["subject_id"], lec["teacher_id"], lec["section_id"], lec["description"], lec["credits"], lec["preferred_room_type"], lec["is_tutorial"]))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database updated and initialized successfully.")
