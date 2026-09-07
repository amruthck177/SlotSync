import io
import json
import pandas as pd
from typing import Dict, Any, List, Tuple
from database.db import save_teacher, save_subject, save_room, save_section

class ImportService:
    @staticmethod
    def _read_dataframe(file_storage) -> pd.DataFrame:
        filename = file_storage.filename.lower()
        if filename.endswith(".csv"):
            return pd.read_csv(file_storage, keep_default_na=False, dtype=str)
        elif filename.endswith((".xlsx", ".xls")):
            return pd.read_excel(file_storage, keep_default_na=False, dtype=str)
        else:
            raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")

    @staticmethod
    def import_teachers(file_storage) -> Dict[str, Any]:
        df = ImportService._read_dataframe(file_storage)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        # Expected / aliased columns
        # id / teacher_id, name / full_name, branch / department, max_hours_per_day / max_hours, subjects, cross_branch_subjects
        id_col = next((c for c in ["id", "teacher_id", "faculty_id"] if c in df.columns), None)
        name_col = next((c for c in ["name", "faculty_name", "full_name"] if c in df.columns), None)
        branch_col = next((c for c in ["branch", "department", "dept"] if c in df.columns), None)

        if not id_col or not name_col or not branch_col:
            raise ValueError(f"Missing required columns. Teachers file must include: 'id', 'name', and 'branch'. Found: {list(df.columns)}")

        added = 0
        updated = 0
        errors = []

        from database.db import get_all_teachers
        existing_ids = {t["id"] for t in get_all_teachers()}

        for idx, row in df.iterrows():
            row_num = idx + 2
            t_id = str(row[id_col]).strip()
            name = str(row[name_col]).strip()
            branch = str(row[branch_col]).strip().upper()

            if not t_id or not name or not branch:
                errors.append(f"Row {row_num}: Missing id, name, or branch. Skipped.")
                continue

            max_hours = 4
            for h_col in ["max_hours_per_day", "max_hours", "daily_hours"]:
                if h_col in df.columns and str(row[h_col]).strip().isdigit():
                    max_hours = int(str(row[h_col]).strip())
                    break

            # Parse subjects
            subjects = []
            for s_col in ["subjects", "assigned_subjects", "subject_ids"]:
                if s_col in df.columns and str(row[s_col]).strip():
                    raw_sub = str(row[s_col]).replace(";", ",")
                    subjects = [s.strip() for s in raw_sub.split(",") if s.strip()]
                    break

            # Parse cross branch subjects
            cross_branch = []
            for cb_col in ["cross_branch_subjects", "cross_branch", "cross_dept"]:
                if cb_col in df.columns and str(row[cb_col]).strip():
                    raw_cb = str(row[cb_col]).strip()
                    try:
                        if raw_cb.startswith("[") and raw_cb.endswith("]"):
                            cross_branch = json.loads(raw_cb)
                        else:
                            items = [x.strip() for x in raw_cb.replace(";", ",").split(",") if x.strip()]
                            for item in items:
                                if ":" in item:
                                    c_code, c_br = item.split(":", 1)
                                    cross_branch.append({"code": c_code.strip(), "branch": c_br.strip().upper()})
                                else:
                                    cross_branch.append({"code": item.strip(), "branch": branch})
                    except Exception as e:
                        errors.append(f"Row {row_num}: Invalid cross-branch format '{raw_cb}'. Error: {e}")

            teacher_data = {
                "id": t_id,
                "name": name,
                "branch": branch,
                "subjects": subjects,
                "cross_branch_subjects": cross_branch,
                "max_hours_per_day": max_hours,
                "max_hours_per_week": max_hours * 5
            }

            try:
                save_teacher(teacher_data)
                if t_id in existing_ids:
                    updated += 1
                else:
                    added += 1
                    existing_ids.add(t_id)
            except Exception as ex:
                errors.append(f"Row {row_num} ({t_id}): Database save error: {ex}")

        return {"status": "success", "added": added, "updated": updated, "total": len(df), "errors": errors}

    @staticmethod
    def import_subjects(file_storage) -> Dict[str, Any]:
        df = ImportService._read_dataframe(file_storage)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        id_col = next((c for c in ["id", "subject_code", "code", "course_code"] if c in df.columns), None)
        name_col = next((c for c in ["name", "subject_name", "course_name", "title"] if c in df.columns), None)
        branch_col = next((c for c in ["branch", "department", "dept"] if c in df.columns), None)

        if not id_col or not name_col or not branch_col:
            raise ValueError(f"Missing required columns. Subjects file must include: 'id' (or 'code'), 'name', and 'branch'. Found: {list(df.columns)}")

        added = 0
        updated = 0
        errors = []

        from database.db import get_all_subjects
        existing_ids = {s["id"] for s in get_all_subjects()}

        for idx, row in df.iterrows():
            row_num = idx + 2
            s_id = str(row[id_col]).strip()
            name = str(row[name_col]).strip()
            branch = str(row[branch_col]).strip().upper()

            if not s_id or not name or not branch:
                errors.append(f"Row {row_num}: Missing subject ID, name, or branch. Skipped.")
                continue

            weekly_hours = 4
            for wh_col in ["weekly_hours", "hours", "credits", "hours_per_week"]:
                if wh_col in df.columns and str(row[wh_col]).strip().isdigit():
                    weekly_hours = int(str(row[wh_col]).strip())
                    break

            consecutive_hours = 1
            for ch_col in ["consecutive_hours", "block_hours", "block"]:
                if ch_col in df.columns and str(row[ch_col]).strip().isdigit():
                    consecutive_hours = int(str(row[ch_col]).strip())
                    break

            needs_lab = False
            for lab_col in ["needs_lab", "is_lab", "lab"]:
                if lab_col in df.columns:
                    val = str(row[lab_col]).strip().lower()
                    needs_lab = val in ["1", "true", "yes", "y", "t", "lab"]
                    break

            semester = None
            for sem_col in ["semester", "sem"]:
                if sem_col in df.columns and str(row[sem_col]).strip().isdigit():
                    semester = int(str(row[sem_col]).strip())
                    break

            subj_data = {
                "id": s_id,
                "name": name,
                "branch": branch,
                "weekly_hours": weekly_hours,
                "consecutive_hours": consecutive_hours,
                "needs_lab": needs_lab,
                "semester": semester
            }

            try:
                save_subject(subj_data)
                if s_id in existing_ids:
                    updated += 1
                else:
                    added += 1
                    existing_ids.add(s_id)
            except Exception as ex:
                errors.append(f"Row {row_num} ({s_id}): Database save error: {ex}")

        return {"status": "success", "added": added, "updated": updated, "total": len(df), "errors": errors}

    @staticmethod
    def import_rooms(file_storage) -> Dict[str, Any]:
        df = ImportService._read_dataframe(file_storage)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        id_col = next((c for c in ["id", "room_id", "room_number", "room"] if c in df.columns), None)
        if not id_col:
            raise ValueError(f"Missing required column. Rooms file must include 'id' or 'room_id'. Found: {list(df.columns)}")

        added = 0
        updated = 0
        errors = []

        from database.db import get_all_rooms
        existing_ids = {r["id"] for r in get_all_rooms()}

        for idx, row in df.iterrows():
            row_num = idx + 2
            r_id = str(row[id_col]).strip()
            if not r_id:
                errors.append(f"Row {row_num}: Missing room ID. Skipped.")
                continue

            r_type = "regular"
            for t_col in ["type", "room_type", "is_lab"]:
                if t_col in df.columns:
                    val = str(row[t_col]).strip().lower()
                    if val in ["lab", "computer_lab", "laboratory", "true", "1", "yes"]:
                        r_type = "lab"
                    elif val in ["regular", "lecture", "hall", "classroom", "lecture_hall"]:
                        r_type = "regular"
                    break

            capacity = 60
            for cap_col in ["capacity", "seats", "size"]:
                if cap_col in df.columns and str(row[cap_col]).strip().isdigit():
                    capacity = int(str(row[cap_col]).strip())
                    break

            branch = "GENERAL"
            for br_col in ["branch", "department", "dept"]:
                if br_col in df.columns and str(row[br_col]).strip():
                    branch = str(row[br_col]).strip().upper()
                    break

            room_data = {
                "id": r_id,
                "type": r_type,
                "capacity": capacity,
                "branch": branch
            }

            try:
                save_room(room_data)
                if r_id in existing_ids:
                    updated += 1
                else:
                    added += 1
                    existing_ids.add(r_id)
            except Exception as ex:
                errors.append(f"Row {row_num} ({r_id}): Database save error: {ex}")

        return {"status": "success", "added": added, "updated": updated, "total": len(df), "errors": errors}

    @staticmethod
    def import_sections(file_storage) -> Dict[str, Any]:
        df = ImportService._read_dataframe(file_storage)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        id_col = next((c for c in ["id", "section_id", "section"] if c in df.columns), None)
        branch_col = next((c for c in ["branch", "department", "dept"] if c in df.columns), None)

        if not id_col or not branch_col:
            raise ValueError(f"Missing required columns. Sections file must include 'id' and 'branch'. Found: {list(df.columns)}")

        added = 0
        updated = 0
        errors = []

        from database.db import get_all_sections
        existing_ids = {s["id"] for s in get_all_sections()}

        for idx, row in df.iterrows():
            row_num = idx + 2
            sec_id = str(row[id_col]).strip()
            branch = str(row[branch_col]).strip().upper()

            if not sec_id or not branch:
                errors.append(f"Row {row_num}: Missing section ID or branch. Skipped.")
                continue

            semester = 5
            for sem_col in ["semester", "sem"]:
                if sem_col in df.columns and str(row[sem_col]).strip().isdigit():
                    semester = int(str(row[sem_col]).strip())
                    break

            subjects = []
            for s_col in ["subjects", "core_subjects", "subject_ids"]:
                if s_col in df.columns and str(row[s_col]).strip():
                    raw_s = str(row[s_col]).replace(";", ",")
                    subjects = [s.strip() for s in raw_s.split(",") if s.strip()]
                    break

            electives = []
            for el_col in ["electives", "elective_groups", "electives_json"]:
                if el_col in df.columns and str(row[el_col]).strip():
                    raw_el = str(row[el_col]).strip()
                    try:
                        if raw_el.startswith("["):
                            electives = json.loads(raw_el)
                    except Exception as e:
                        errors.append(f"Row {row_num}: Could not parse electives JSON '{raw_el}': {e}")

            sec_data = {
                "id": sec_id,
                "branch": branch,
                "semester": semester,
                "subjects": subjects,
                "electives": electives
            }

            try:
                save_section(sec_data)
                if sec_id in existing_ids:
                    updated += 1
                else:
                    added += 1
                    existing_ids.add(sec_id)
            except Exception as ex:
                errors.append(f"Row {row_num} ({sec_id}): Database save error: {ex}")

        return {"status": "success", "added": added, "updated": updated, "total": len(df), "errors": errors}

    @staticmethod
    def import_workbook(file_storage) -> Dict[str, Any]:
        """
        Imports an all-in-one Excel workbook containing sheets:
        Teachers, Subjects, Rooms, Sections.
        """
        xls = pd.ExcelFile(file_storage)
        sheet_names = [s.strip().lower() for s in xls.sheet_names]
        results = {}
        total_added = 0
        total_updated = 0
        all_errors = []

        mapping = {
            "teachers": ImportService.import_teachers,
            "subjects": ImportService.import_subjects,
            "rooms": ImportService.import_rooms,
            "sections": ImportService.import_sections
        }

        for sheet in xls.sheet_names:
            normalized = sheet.strip().lower()
            target_key = next((k for k in mapping.keys() if k in normalized), None)
            if target_key:
                df = pd.read_excel(xls, sheet_name=sheet, keep_default_na=False, dtype=str)
                # Convert back to an in-memory buffer to reuse parser
                csv_buffer = io.BytesIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                
                class BufferWrapper:
                    def __init__(self, buf, name):
                        self.buf = buf
                        self.filename = name
                    def read(self, *args):
                        return self.buf.read(*args)
                    def seek(self, *args):
                        return self.buf.seek(*args)

                wrapped = BufferWrapper(csv_buffer, f"{target_key}.csv")
                res = mapping[target_key](wrapped)
                results[target_key] = res
                total_added += res.get("added", 0)
                total_updated += res.get("updated", 0)
                all_errors.extend([f"[{sheet}] {e}" for e in res.get("errors", [])])

        return {
            "status": "success",
            "added": total_added,
            "updated": total_updated,
            "sheets_processed": list(results.keys()),
            "errors": all_errors,
            "details": results
        }

    @staticmethod
    def generate_template(entity_type: str, file_format: str = "csv") -> io.BytesIO:
        """
        Generates a sample template for the given entity with example rows.
        """
        templates_data = {
            "teachers": [
                {
                    "id": "T1",
                    "name": "Dr. Ramesh Kumar",
                    "branch": "CSE",
                    "max_hours_per_day": 4,
                    "subjects": "21CS51, 21CS52, 21CSL55",
                    "cross_branch_subjects": "21IS61:ISE, 21EC41:ECE"
                },
                {
                    "id": "T2",
                    "name": "Prof. Priya Sharma",
                    "branch": "CSE",
                    "max_hours_per_day": 4,
                    "subjects": "21CS53, 21CS54",
                    "cross_branch_subjects": ""
                },
                {
                    "id": "T3",
                    "name": "Dr. Anand Rao",
                    "branch": "ISE",
                    "max_hours_per_day": 5,
                    "subjects": "21IS51, 21IS52",
                    "cross_branch_subjects": "21CS51:CSE"
                }
            ],
            "subjects": [
                {
                    "id": "21CS51",
                    "name": "Automata Theory & Computability",
                    "branch": "CSE",
                    "semester": 5,
                    "weekly_hours": 4,
                    "needs_lab": "no",
                    "consecutive_hours": 1
                },
                {
                    "id": "21CS52",
                    "name": "Computer Networks",
                    "branch": "CSE",
                    "semester": 5,
                    "weekly_hours": 4,
                    "needs_lab": "no",
                    "consecutive_hours": 1
                },
                {
                    "id": "21CSL55",
                    "name": "Computer Networks Laboratory",
                    "branch": "CSE",
                    "semester": 5,
                    "weekly_hours": 3,
                    "needs_lab": "yes",
                    "consecutive_hours": 2
                }
            ],
            "rooms": [
                {
                    "id": "LH-101",
                    "type": "regular",
                    "capacity": 70,
                    "branch": "GENERAL"
                },
                {
                    "id": "LH-102",
                    "type": "regular",
                    "capacity": 65,
                    "branch": "CSE"
                },
                {
                    "id": "CS-LAB1",
                    "type": "lab",
                    "capacity": 40,
                    "branch": "CSE"
                },
                {
                    "id": "IS-LAB1",
                    "type": "lab",
                    "capacity": 35,
                    "branch": "ISE"
                }
            ],
            "sections": [
                {
                    "id": "CSE-5A",
                    "branch": "CSE",
                    "semester": 5,
                    "subjects": "21CS51, 21CS52, 21CS53, 21CSL55",
                    "electives": '[{"group": "Elective-1", "options": ["21CS54A", "21CS54B"]}]'
                },
                {
                    "id": "CSE-5B",
                    "branch": "CSE",
                    "semester": 5,
                    "subjects": "21CS51, 21CS52, 21CS53, 21CSL55",
                    "electives": '[{"group": "Elective-1", "options": ["21CS54A", "21CS54B"]}]'
                },
                {
                    "id": "ISE-5A",
                    "branch": "ISE",
                    "semester": 5,
                    "subjects": "21IS51, 21IS52, 21IS53, 21ISL55",
                    "electives": "[]"
                }
            ]
        }

        buffer = io.BytesIO()

        if entity_type == "workbook":
            # Multi-sheet Excel workbook
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                for sheet_key, data in templates_data.items():
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_key.capitalize(), index=False)
            buffer.seek(0)
            return buffer

        data = templates_data.get(entity_type, templates_data["teachers"])
        df = pd.DataFrame(data)

        if file_format == "excel" or file_format == "xlsx":
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=entity_type.capitalize(), index=False)
        else:
            df.to_csv(buffer, index=False)

        buffer.seek(0)
        return buffer
