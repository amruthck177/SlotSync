import itertools
from typing import List, Dict, Any, Optional, Tuple
from models.teacher import Teacher
from models.subject import Subject
from models.room import Room
from models.section import Section
from models.timetable_entry import TimetableEntry

class ManualAssistEngine:
    """
    Permutation & Combination engine for fine-tuning individual teacher or section schedules.
    Finds valid clash-free slot allocations and ranks them for human selection.
    """
    def __init__(
        self,
        teachers: List[Teacher],
        subjects: List[Subject],
        rooms: List[Room],
        sections: List[Section],
        days: List[str],
        periods_per_day: int = 7,
        current_timetable: Optional[List[Dict[str, Any]]] = None
    ):
        self.teachers = {t.id: t for t in teachers}
        self.subjects = {s.id: s for s in subjects}
        self.rooms = {r.id: r for r in rooms}
        self.sections = {sec.id: sec for sec in sections}
        self.days = days
        self.periods = list(range(1, periods_per_day + 1))
        self.current_timetable = current_timetable or []

    def get_valid_placements_for_teacher(
        self,
        teacher_id: str,
        section_id: str,
        subject_id: str,
        max_options: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Calculates all valid permutations of slots for a teacher's subject in a specific section,
        ensuring no clashes with other existing entries.
        """
        if teacher_id not in self.teachers or subject_id not in self.subjects:
            return []

        teacher = self.teachers[teacher_id]
        subject = self.subjects[subject_id]
        hours_needed = subject.weekly_hours
        
        # Check teacher qualification
        if not teacher.can_teach(subject_id):
            return []

        # Compatible rooms
        if subject.needs_lab:
            avail_rooms = [r.id for r in self.rooms.values() if r.is_lab]
        else:
            avail_rooms = [r.id for r in self.rooms.values() if not r.is_lab]

        if not avail_rooms:
            return []

        # Collect occupied slots from existing timetable (excluding current target's subject in this section)
        teacher_busy = set()
        section_busy = set()
        room_busy = set() # (room_id, day, period)

        for e in self.current_timetable:
            if e.get("teacher_id") == teacher_id and not (e.get("section_id") == section_id and e.get("subject_id") == subject_id):
                teacher_busy.add((e["day"], e["period"]))
            if e.get("section_id") == section_id and e.get("subject_id") != subject_id:
                section_busy.add((e["day"], e["period"]))
            room_busy.add((e["room_id"], e["day"], e["period"]))

        # Identify all candidate single slots (day, period, room) where teacher, section, and room are all free
        candidate_slots = []
        for d in self.days:
            for p in self.periods:
                if (d, p) not in teacher_busy and (d, p) not in section_busy:
                    # Find any free room
                    free_rooms = [r for r in avail_rooms if (r, d, p) not in room_busy]
                    if free_rooms:
                        candidate_slots.append({
                            "day": d,
                            "period": p,
                            "room_id": free_rooms[0], # choose primary free room
                            "all_free_rooms": free_rooms
                        })

        if len(candidate_slots) < hours_needed:
            return []

        # Generate combinations of slots of size `hours_needed`
        valid_options = []
        
        # Rule: max 1 slot per day for theory subject, or consecutive for lab
        # To make search efficient, group candidate slots by day
        slots_by_day = {}
        for slot in candidate_slots:
            slots_by_day.setdefault(slot["day"], []).append(slot)

        if subject.needs_lab and subject.consecutive_hours == 2:
            # Lab needs 2 consecutive periods on the same day
            lab_pairs = []
            for d, d_slots in slots_by_day.items():
                slot_map = {s["period"]: s for s in d_slots}
                for p in self.periods[:-1]:
                    if p in slot_map and (p + 1) in slot_map:
                        lab_pairs.append([slot_map[p], slot_map[p + 1]])
            
            for pair in lab_pairs[:max_options]:
                valid_options.append({
                    "score": 100 - pair[0]["period"],
                    "description": f"{pair[0]['day']} Periods {pair[0]['period']}-{pair[1]['period']} in {pair[0]['room_id']}",
                    "slots": [
                        {
                            "day": s["day"],
                            "period": s["period"],
                            "room_id": s["room_id"],
                            "teacher_id": teacher_id,
                            "section_id": section_id,
                            "subject_id": subject_id
                        }
                        for s in pair
                    ]
                })
        else:
            # Regular theory subject: pick 1 slot per day across different days where possible
            all_combos = []
            
            # If hours_needed <= len(days), pick 1 slot per day from distinct days
            available_days = [d for d in self.days if d in slots_by_day]
            if len(available_days) >= hours_needed:
                for day_combo in itertools.combinations(available_days, hours_needed):
                    # For each day in combo, pick 1 slot
                    day_choices = [slots_by_day[d] for d in day_combo]
                    for chosen_slots in itertools.product(*day_choices):
                        # Score: compact periods (lower period numbers preferred), avoid isolated gaps
                        score = 100 - sum(s["period"] for s in chosen_slots)
                        all_combos.append((score, list(chosen_slots)))
                        if len(all_combos) > 200:
                            break
                    if len(all_combos) > 200:
                        break

            # Sort by score descending
            all_combos.sort(key=lambda x: x[0], reverse=True)

            for score, combo in all_combos[:max_options]:
                desc = ", ".join(f"{s['day']} P{s['period']} ({s['room_id']})" for s in combo)
                valid_options.append({
                    "score": score,
                    "description": desc,
                    "slots": [
                        {
                            "day": s["day"],
                            "period": s["period"],
                            "room_id": s["room_id"],
                            "teacher_id": teacher_id,
                            "section_id": section_id,
                            "subject_id": subject_id
                        }
                        for s in combo
                    ]
                })

        return valid_options

    def get_clash_diagnostics_for_slot(
        self,
        day: str,
        period: int,
        teacher_id: str,
        room_id: str,
        section_id: str
    ) -> List[str]:
        """
        Explains why a specific slot might clash with existing schedule.
        """
        clashes = []
        for e in self.current_timetable:
            if e["day"] == day and e["period"] == period:
                if e["teacher_id"] == teacher_id:
                    clashes.append(f"Teacher {teacher_id} is already teaching {e['subject_id']} for section {e['section_id']}.")
                if e["room_id"] == room_id:
                    clashes.append(f"Room {room_id} is occupied by {e['section_id']} ({e['subject_id']}).")
                if e["section_id"] == section_id and not e.get("is_elective"):
                    clashes.append(f"Section {section_id} already has {e['subject_id']} scheduled at this period.")
        return clashes
