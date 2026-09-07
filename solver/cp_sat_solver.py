import time
from typing import List, Dict, Any, Optional, Tuple
from ortools.sat.python import cp_model
from models.teacher import Teacher
from models.subject import Subject
from models.room import Room
from models.section import Section, ElectiveGroup
from models.timetable_entry import TimetableEntry

class TimetableSolver:
    def __init__(
        self,
        teachers: List[Teacher],
        subjects: List[Subject],
        rooms: List[Room],
        sections: List[Section],
        days: List[str],
        periods_per_day: int = 7,
        lunch_break_period: Optional[int] = 4,
        locked_entries: Optional[List[Dict[str, Any]]] = None
    ):
        self.teachers = {t.id: t for t in teachers}
        self.subjects = {s.id: s for s in subjects}
        self.rooms = {r.id: r for r in rooms}
        self.sections = {sec.id: sec for sec in sections}
        self.days = days
        self.periods = list(range(1, periods_per_day + 1))
        self.lunch_break_period = lunch_break_period
        self.locked_entries = locked_entries or []
        
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = 30.0
        self.solver.parameters.num_workers = 4
        self.solver.parameters.log_search_progress = False

    def solve(self) -> Tuple[bool, List[TimetableEntry], Dict[str, Any]]:
        start_time = time.time()
        
        # 1. Gather all tasks per section
        # Regular subjects and Elective options
        # Task format: (section_id, subject_id, is_elective, elective_group)
        tasks = []
        for sec in self.sections.values():
            for subj_id in sec.subjects:
                if subj_id in self.subjects:
                    tasks.append({
                        "section_id": sec.id,
                        "subject_id": subj_id,
                        "is_elective": False,
                        "elective_group": None,
                        "weekly_hours": self.subjects[subj_id].weekly_hours,
                        "needs_lab": self.subjects[subj_id].needs_lab,
                        "consecutive_hours": self.subjects[subj_id].consecutive_hours
                    })
            for eg in sec.electives:
                for opt_subj_id in eg.options:
                    if opt_subj_id in self.subjects:
                        tasks.append({
                            "section_id": sec.id,
                            "subject_id": opt_subj_id,
                            "is_elective": True,
                            "elective_group": eg.group,
                            "weekly_hours": self.subjects[opt_subj_id].weekly_hours,
                            "needs_lab": self.subjects[opt_subj_id].needs_lab,
                            "consecutive_hours": self.subjects[opt_subj_id].consecutive_hours
                        })

        # 2. Identify candidate teachers and candidate rooms for each task
        task_candidates = {}
        for idx, task in enumerate(tasks):
            subj = self.subjects[task["subject_id"]]
            cand_teachers = [t.id for t in self.teachers.values() if t.can_teach(subj.id)]
            
            if subj.needs_lab:
                cand_rooms = [r.id for r in self.rooms.values() if r.is_lab]
            else:
                cand_rooms = [r.id for r in self.rooms.values() if not r.is_lab]
                
            if not cand_teachers:
                return False, [], {
                    "error": f"No qualified teacher found for subject '{subj.name}' ({subj.id}) in branch '{subj.branch}'."
                }
            if not cand_rooms:
                room_type_str = "lab" if subj.needs_lab else "regular lecture"
                return False, [], {
                    "error": f"No {room_type_str} room available for subject '{subj.name}' ({subj.id})."
                }
            task_candidates[idx] = {
                "teachers": cand_teachers,
                "rooms": cand_rooms
            }

        # 3. Create Decision Variables
        # X[task_idx, t, r, d, p] \in {0, 1}
        X = {}
        for idx, task in enumerate(tasks):
            for t in task_candidates[idx]["teachers"]:
                for r in task_candidates[idx]["rooms"]:
                    for d in self.days:
                        for p in self.periods:
                            var_name = f"x_t{idx}_{t}_{r}_{d}_{p}"
                            X[(idx, t, r, d, p)] = self.model.NewBoolVar(var_name)

        # 4. Teacher consistency: A subject in a section should be taught by 1 designated teacher
        # Y[task_idx, t] \in {0, 1}
        Y = {}
        for idx, task in enumerate(tasks):
            c_teachers = task_candidates[idx]["teachers"]
            for t in c_teachers:
                Y[(idx, t)] = self.model.NewBoolVar(f"y_t{idx}_{t}")
            self.model.Add(sum(Y[(idx, t)] for t in c_teachers) == 1)
            
            # Link X and Y
            for t in c_teachers:
                for r in task_candidates[idx]["rooms"]:
                    for d in self.days:
                        for p in self.periods:
                            self.model.Add(X[(idx, t, r, d, p)] <= Y[(idx, t)])

        # 5. Weekly Hours Satisfaction
        # For each task, sum of all assigned slots must equal weekly_hours
        for idx, task in enumerate(tasks):
            cand = task_candidates[idx]
            task_vars = [
                X[(idx, t, r, d, p)]
                for t in cand["teachers"]
                for r in cand["rooms"]
                for d in self.days
                for p in self.periods
            ]
            self.model.Add(sum(task_vars) == task["weekly_hours"])

        # 6. Elective Synchronization
        # All options in the same elective group for a section MUST occur at the EXACT same (day, period)
        for sec in self.sections.values():
            for eg in sec.electives:
                eg_task_indices = [
                    idx for idx, task in enumerate(tasks)
                    if task["section_id"] == sec.id and task["is_elective"] and task["elective_group"] == eg.group
                ]
                if len(eg_task_indices) > 1:
                    first_idx = eg_task_indices[0]
                    first_cand = task_candidates[first_idx]
                    for other_idx in eg_task_indices[1:]:
                        other_cand = task_candidates[other_idx]
                        for d in self.days:
                            for p in self.periods:
                                first_slot_vars = [
                                    X[(first_idx, t, r, d, p)]
                                    for t in first_cand["teachers"]
                                    for r in first_cand["rooms"]
                                ]
                                other_slot_vars = [
                                    X[(other_idx, t, r, d, p)]
                                    for t in other_cand["teachers"]
                                    for r in other_cand["rooms"]
                                ]
                                self.model.Add(sum(first_slot_vars) == sum(other_slot_vars))

        # 7. Section No-Clash
        # For each section and (d, p), sum of regular tasks + 1 per active elective group <= 1
        for sec_id, sec in self.sections.items():
            regular_indices = [
                idx for idx, task in enumerate(tasks)
                if task["section_id"] == sec_id and not task["is_elective"]
            ]
            elective_groups = {
                task["elective_group"]: idx
                for idx, task in enumerate(tasks)
                if task["section_id"] == sec_id and task["is_elective"]
            }
            for d in self.days:
                for p in self.periods:
                    slot_vars = []
                    # Regular subjects
                    for idx in regular_indices:
                        cand = task_candidates[idx]
                        for t in cand["teachers"]:
                            for r in cand["rooms"]:
                                slot_vars.append(X[(idx, t, r, d, p)])
                    # Electives (take first option representing the group)
                    for grp, first_idx in elective_groups.items():
                        cand = task_candidates[first_idx]
                        for t in cand["teachers"]:
                            for r in cand["rooms"]:
                                slot_vars.append(X[(first_idx, t, r, d, p)])
                    self.model.Add(sum(slot_vars) <= 1)

        # 8. Teacher No-Clash
        # A teacher can teach at most 1 session at any (d, p) across all sections/subjects/rooms
        for t_id in self.teachers.keys():
            for d in self.days:
                for p in self.periods:
                    t_slot_vars = []
                    for idx, task in enumerate(tasks):
                        if t_id in task_candidates[idx]["teachers"]:
                            for r in task_candidates[idx]["rooms"]:
                                t_slot_vars.append(X[(idx, t_id, r, d, p)])
                    if t_slot_vars:
                        self.model.Add(sum(t_slot_vars) <= 1)

        # 9. Room No-Clash
        # A room can host at most 1 session at any (d, p) across all sections/subjects/teachers
        for r_id in self.rooms.keys():
            for d in self.days:
                for p in self.periods:
                    r_slot_vars = []
                    for idx, task in enumerate(tasks):
                        if r_id in task_candidates[idx]["rooms"]:
                            for t in task_candidates[idx]["teachers"]:
                                r_slot_vars.append(X[(idx, t, r_id, d, p)])
                    if r_slot_vars:
                        self.model.Add(sum(r_slot_vars) <= 1)

        # 10. Teacher Daily Hours Limit
        for t_id, teacher in self.teachers.items():
            for d in self.days:
                day_vars = []
                for p in self.periods:
                    for idx, task in enumerate(tasks):
                        if t_id in task_candidates[idx]["teachers"]:
                            for r in task_candidates[idx]["rooms"]:
                                day_vars.append(X[(idx, t_id, r, d, p)])
                if day_vars:
                    self.model.Add(sum(day_vars) <= teacher.max_hours_per_day)

        # 11. Consecutive Lab Blocks (e.g. 2-hour labs)
        # If consecutive_hours == 2, lab must be scheduled in 2 consecutive periods on the same day
        for idx, task in enumerate(tasks):
            if task["needs_lab"] and task["consecutive_hours"] == 2:
                cand = task_candidates[idx]
                for d in self.days:
                    for p in self.periods:
                        slot_vars = [X[(idx, t, r, d, p)] for t in cand["teachers"] for r in cand["rooms"]]
                        # If scheduled at (d, p), then either (d, p-1) or (d, p+1) must also be scheduled
                        adj_vars = []
                        if p > 1:
                            adj_vars.extend([X[(idx, t, r, d, p - 1)] for t in cand["teachers"] for r in cand["rooms"]])
                        if p < len(self.periods):
                            adj_vars.extend([X[(idx, t, r, d, p + 1)] for t in cand["teachers"] for r in cand["rooms"]])
                        
                        if adj_vars:
                            self.model.Add(sum(slot_vars) <= sum(adj_vars))

        # 12. Theory Daily Spread (Max 1 period of the same theory subject per day for a section)
        for idx, task in enumerate(tasks):
            if not task["needs_lab"] and task["weekly_hours"] <= len(self.days):
                cand = task_candidates[idx]
                for d in self.days:
                    day_sub_vars = [
                        X[(idx, t, r, d, p)]
                        for t in cand["teachers"]
                        for r in cand["rooms"]
                        for p in self.periods
                    ]
                    self.model.Add(sum(day_sub_vars) <= 1)

        # 13. Locked / Pinned entries from Manual Overrides
        for entry in self.locked_entries:
            # Find matching task
            for idx, task in enumerate(tasks):
                if (
                    task["section_id"] == entry["section_id"]
                    and task["subject_id"] == entry["subject_id"]
                    and entry["teacher_id"] in task_candidates[idx]["teachers"]
                    and entry["room_id"] in task_candidates[idx]["rooms"]
                    and entry["day"] in self.days
                    and entry["period"] in self.periods
                ):
                    self.model.Add(
                        X[(idx, entry["teacher_id"], entry["room_id"], entry["day"], entry["period"])] == 1
                    )

        # 14. Objective Function: Soft Optimization
        # - Encourage compact schedules for sections (penalize middle gaps)
        # - Encourage scheduling core theory earlier in the day
        objective_terms = []
        
        # Morning preference (periods 1-3 have smaller cost, later periods have slight penalty)
        for idx, task in enumerate(tasks):
            cand = task_candidates[idx]
            for t in cand["teachers"]:
                for r in cand["rooms"]:
                    for d in self.days:
                        for p in self.periods:
                            # Higher period = small penalty (1 point per period)
                            objective_terms.append(X[(idx, t, r, d, p)] * p)

        if objective_terms:
            self.model.Minimize(sum(objective_terms))

        # 15. Solve
        status = self.solver.Solve(self.model)
        elapsed_time = time.time() - start_time
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            result_entries = []
            for idx, task in enumerate(tasks):
                cand = task_candidates[idx]
                for t in cand["teachers"]:
                    for r in cand["rooms"]:
                        for d in self.days:
                            for p in self.periods:
                                if self.solver.Value(X[(idx, t, r, d, p)]) == 1:
                                    # Check if this was originally locked
                                    is_locked = any(
                                        le["section_id"] == task["section_id"]
                                        and le["subject_id"] == task["subject_id"]
                                        and le["day"] == d
                                        and le["period"] == p
                                        for le in self.locked_entries
                                    )
                                    result_entries.append(TimetableEntry(
                                        day=d,
                                        period=p,
                                        subject_id=task["subject_id"],
                                        teacher_id=t,
                                        room_id=r,
                                        section_id=task["section_id"],
                                        is_elective=task["is_elective"],
                                        elective_group=task["elective_group"],
                                        is_locked=is_locked
                                    ))
            
            stats = {
                "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
                "time_taken_seconds": round(elapsed_time, 3),
                "num_entries": len(result_entries),
                "objective_value": self.solver.ObjectiveValue() if self.model.HasObjective() else 0
            }
            return True, result_entries, stats
        else:
            status_name = self.solver.StatusName(status)
            return False, [], {
                "status": status_name,
                "time_taken_seconds": round(elapsed_time, 3),
                "error": f"CP-SAT solver could not find a feasible timetable ({status_name}). This usually means constraints (such as teacher hours, room counts, or locked slots) conflict."
            }
