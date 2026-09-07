# AI-Based Timetable Generator

A tool that automatically creates a clash-free class timetable for a college — assigning subjects, teachers, and rooms to time slots without double-bookings — with a manual "patch" mode for fine-tuning individual teachers or sections by hand.

---

## 1. What this project does (in simple words)

Making a college timetable by hand is like solving a giant puzzle: every teacher, every room, and every subject has to fit into a weekly grid without clashing with anything else. This project automates that puzzle.

You feed it:
- Which teachers exist, which branch they belong to, and which subjects they teach
- Which subjects exist, how many hours a week each needs, and whether it needs a lab
- Which rooms exist and their type (lab / regular)
- Which sections (classes) exist and which subjects they need

It gives you back:
- A full weekly timetable, with no teacher, room, or section double-booked
- The option to manually tweak one teacher or section's slots by hand, and have the rest of the timetable re-adjust around your choice

---

## 2. How it works (the simple flow)

1. **Enter data** — teachers, subjects, rooms, sections (through a form, or imported from Excel/CSV)
2. **Solver runs** — an algorithm (Google OR-Tools) checks millions of possible arrangements internally and finds one that breaks no rules
3. **Timetable is produced** — a clash-free schedule, shown as a grid (days x periods)
4. **Optional manual patch** — if you want to hand-place one teacher's or section's slots yourself, the system shows you every valid way to do it (using permutations and combinations) so you can pick one, then re-solves everything else around your pick

---

## 3. Why two different methods (solver + manual)?

There are two very different situations this project needs to handle:

| Situation | Method used | Why |
|---|---|---|
| Building the whole college's timetable at once | **OR-Tools solver (CP-SAT)** | Too many combinations to check one by one — the solver is smart enough to skip impossible options instead of trying every one |
| Fine-tuning just one teacher's or one section's slots | **Permutation & combination (manual mode)** | Small enough (a handful of subjects into a handful of free slots) to simply list every valid option and let a human choose |

In short: the computer handles the big, impossible-to-do-by-hand puzzle. You get manual control only where a human actually can compare a few options and make a judgment call.

---

## 4. Core rules (constraints)

**Hard rules — must never be broken:**
- A teacher cannot teach two classes at the same time
- A room cannot host two classes at the same time
- A section cannot attend two subjects at the same time — **except** subjects within the same elective group, which are expected to overlap (the section splits into groups, each attending a different elective option, in a different room with a different teacher)
- Electives are placed inside the normal working-hours grid like everything else — never as an extra period tacked on outside the regular day
- Every subject gets exactly its required number of hours per week — no more, no less

**Soft rules — the system tries to satisfy these, but can bend if needed:**
- Minimize free/idle gaps in a section's day
- Avoid two lab sessions back-to-back
- Spread each teacher's hours evenly across the week instead of bunching them
- Keep heavier subjects earlier in the day where possible

**Branch rule:**
- By default, a teacher only teaches subjects from their own branch/department
- Cross-branch teaching (a teacher covering a subject from a different branch) is the exception, and must be explicitly marked — it isn't assumed

---

## 5. Data model

This is the shape of the information the system works with.

**Teacher**
```json
{
  "id": "T5",
  "name": "Dr. Suresh",
  "branch": "CSE",
  "subjects": ["CS301", "CS302"],
  "cross_branch_subjects": [
    {"code": "IS402", "branch": "ISE"}
  ],
  "num_subjects": 3,
  "max_hours_per_day": 4
}
```
- `subjects` — subjects from the teacher's own branch (the common case, no extra tagging needed)
- `cross_branch_subjects` — only used for the exception cases, each tagged with its actual branch
- `num_subjects` — automatically counted, not typed in by hand

**Subject**
```json
{
  "id": "CS301",
  "name": "DBMS",
  "branch": "CSE",
  "weekly_hours": 4,
  "needs_lab": false
}
```

**Room**
```json
{
  "id": "LAB1",
  "type": "lab",
  "capacity": 30
}
```

**Section (a class, e.g. "5th sem CSE - A")**
```json
{
  "id": "5A",
  "branch": "CSE",
  "subjects": ["CS301", "CS302"],
  "electives": [
    {
      "group": "Elective-1",
      "options": ["CS401", "CS402", "CS403"]
    }
  ]
}
```
`electives` holds groups of subjects meant to happen at the same time — the section splits up, each option gets its own room and teacher, but the whole group still lands in a single normal working-hours slot, same as any other period.

**Time slots**
```json
{
  "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
  "periods_per_day": 7
}
```

**Output timetable entry (what the solver produces)**
```json
{
  "day": "Mon",
  "period": 3,
  "subject": "CS301",
  "teacher": "T5",
  "room": "R1",
  "section": "5A"
}
```

---

## 6. Tech stack

| Part | Choice | Why |
|---|---|---|
| Backend | Python + Flask | Simple, and Python has the best scheduling libraries |
| Scheduling engine | Google OR-Tools (CP-SAT solver) | Purpose-built for exactly this kind of "assign things without clashes" problem |
| Manual assist | Python `itertools.permutations` | Perfect for small, human-sized choices (one teacher/section at a time) |
| Database | SQLite (while building) → PostgreSQL (for real use) | SQLite needs no setup; PostgreSQL handles real, multi-user load |
| Frontend | HTML/CSS/JS (or React later) | A simple grid table is enough to start |
| Import/Export | pandas / openpyxl (Excel), a PDF library | Colleges already keep data in Excel and need printable timetables |

---

## 7. Project structure

```
timetable-generator/
├── app.py                  # Flask entry point
├── models/                 # Data classes for Teacher, Subject, Room, Section
│   ├── teacher.py
│   ├── subject.py
│   ├── room.py
│   └── section.py
├── solver/
│   ├── cp_sat_solver.py    # Automatic full-timetable solver (OR-Tools)
│   └── manual_assist.py    # Permutation/combination tool for single teacher/section
├── api/
│   └── routes.py           # /generate, /timetable/<section>, /manual-assist endpoints
├── database/
│   └── schema.sql
├── frontend/
│   └── (grid UI, data-entry forms)
└── README.md
```

---

## 8. Setup (once code exists)

```bash
git clone <your-repo-url>
cd timetable-generator
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install flask ortools pandas openpyxl
python app.py
```

---

## 9. Usage

1. Add teachers, subjects, rooms, and sections through the admin form (or import from Excel)
2. Click **Generate Timetable** — the solver runs and produces a clash-free schedule
3. View the result as a grid, per section or per teacher
4. If you want to hand-adjust one teacher or section, use **Manual Assist** to see every valid arrangement for just that part, pick one, and the system re-solves the rest around it
5. Export the final timetable to PDF or Excel for printing

---

## 10. What's needed to make this real (not just a demo)

- [ ] Persistent database instead of in-memory data
- [ ] Proper data-entry forms for teachers, subjects, rooms, sections
- [ ] Manual override + re-solve (the permutation/combination assist)
- [ ] Import from Excel/CSV, export to PDF/Excel
- [ ] Login for admins only (HOD / timetable committee)
- [ ] Hosting + backups so it's actually reachable and safe to rely on

---

## 11. Possible future additions

- Multi-college / multi-department support
- Notifications when a timetable is regenerated
- A "regenerate with different priorities" option (e.g. prioritize even teacher load vs. minimizing gaps)

---

## License

Personal/learning project — license to be decided.
