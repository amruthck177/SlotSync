<div align="center">

# 🗓️ SlotSync

### AI-Powered College Timetable Generator

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-CP--SAT-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **Stop wrestling with spreadsheets.** SlotSync automatically builds a clash-free college timetable in seconds — assigning teachers, subjects, and rooms across the week with zero double-bookings. Fine-tune any slot manually, and the solver re-adjusts the rest for you.

[Features](#-features) · [How It Works](#-how-it-works) · [Tech Stack](#-tech-stack) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Project Structure](#-project-structure)

---

</div>

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Solver** | Google OR-Tools CP-SAT engine evaluates millions of combinations to produce a zero-clash schedule |
| 🔒 **Hard Constraints** | Teacher, room & section conflicts are mathematically impossible in the output |
| 🎯 **Soft Optimisations** | Minimises teacher idle gaps, avoids back-to-back labs, spreads load evenly |
| 🖐️ **Manual Assist** | Hand-place any teacher or section's slots; solver re-routes the rest automatically |
| 🏛️ **Elective Support** | Elective groups run in parallel — section splits, each option gets its own room & teacher |
| 📊 **Visual Heatmap** | Colour-coded teacher load heatmap — spot overloaded staff at a glance |
| 📥 **Import / Export** | Bulk-import data via JSON/CSV; export the finished timetable to Excel or print layout |
| 🔬 **Diagnostics** | Built-in conflict detector reports exactly which constraints are at risk before generation |
| 🖨️ **Print View** | Clean, printer-ready CSS layout with one timetable per page |
| 🌙 **Dark Mode UI** | Responsive single-page app with full dark/light theme toggle |

---

## 🧠 How It Works

Making a college timetable by hand is like solving a giant puzzle: every teacher, every room, and every subject must fit into a weekly grid without clashing with anything else. SlotSync automates that puzzle.

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   Enter Data     │────▶│    CP-SAT Solver      │────▶│  Clash-Free Output  │
│                  │     │                      │     │                     │
│ • Teachers       │     │ Evaluates millions   │     │ • Day × Period grid │
│ • Subjects       │     │ of combinations &    │     │ • Per-section view  │
│ • Rooms          │     │ eliminates invalid   │     │ • Per-teacher view  │
│ • Sections       │     │ ones using           │     │ • Export ready      │
│ • Lectures       │     │ constraint prop.     │     │                     │
└─────────────────┘     └──────────────────────┘     └─────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Manual Assist       │
                        │                      │
                        │ Permutation engine   │
                        │ lists every valid    │
                        │ option for one       │
                        │ teacher/section →    │
                        │ you pick, solver     │
                        │ fills the rest       │
                        └──────────────────────┘
```

### Why Two Methods?

| Scenario | Method | Why |
|---|---|---|
| Build the whole college timetable at once | **OR-Tools CP-SAT** | Too many combinations to enumerate — constraint propagation skips impossible branches |
| Fine-tune a single teacher or section | **Permutation & Combination** | Small enough to list every valid option; human makes the final call |

---

## 📐 Constraint System

### 🔴 Hard Constraints *(never broken)*

- A teacher **cannot** teach two classes at the same time  
- A room **cannot** host two classes at the same time  
- A section **cannot** attend two subjects simultaneously *(exception: parallel elective groups)*  
- Every subject receives **exactly** its required weekly hours — no more, no less  
- Elective groups occupy a **single normal working-hours slot** — never extra periods  

### 🟡 Soft Constraints *(optimised, not enforced)*

- Minimise idle gaps in a section's day  
- Avoid consecutive lab sessions  
- Spread teacher hours evenly across the week  
- Schedule heavier subjects earlier in the day  

### 🔵 Branch Rules

- By default, a teacher teaches subjects from their **own branch/department only**  
- **Cross-branch teaching** must be explicitly tagged — it is never assumed  

---

## 🏗️ Data Model

<details>
<summary><strong>Teacher</strong></summary>

```json
{
  "id": "T5",
  "name": "Dr. Suresh",
  "branch": "CSE",
  "subjects": ["CS301", "CS302"],
  "cross_branch_subjects": [
    { "code": "IS402", "branch": "ISE" }
  ],
  "max_hours_per_day": 4
}
```
- `subjects` — subjects from the teacher's own branch (no extra tagging needed)  
- `cross_branch_subjects` — exception cases, each tagged with its actual branch  

</details>

<details>
<summary><strong>Subject</strong></summary>

```json
{
  "id": "CS301",
  "name": "DBMS",
  "branch": "CSE",
  "weekly_hours": 4,
  "needs_lab": false
}
```

</details>

<details>
<summary><strong>Room</strong></summary>

```json
{
  "id": "LAB1",
  "type": "lab",
  "capacity": 30
}
```

</details>

<details>
<summary><strong>Section</strong></summary>

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
`electives` holds parallel subject groups — the section splits, each option lands in one normal working-hours slot.

</details>

<details>
<summary><strong>Timetable Entry (solver output)</strong></summary>

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

</details>

---

## 🛠️ Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **Backend** | Python 3.10+ · Flask 3.0 | Lightweight, fast to iterate, excellent library ecosystem |
| **Scheduling Engine** | Google OR-Tools (CP-SAT) | Purpose-built constraint programming; handles millions of variables |
| **Manual Assist** | Python `itertools.permutations` | Perfect for small human-sized choices (one teacher/section at a time) |
| **Database** | SQLite → PostgreSQL | SQLite for zero-setup development; swap to Postgres for production |
| **Frontend** | Vanilla HTML · CSS · JavaScript | Single-page app with no build toolchain; fast and dependency-free |
| **Import/Export** | pandas · openpyxl | Colleges keep data in Excel; output must be printable |
| **Data Loading** | python-dotenv | Clean environment configuration |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/amruthck177/SlotSync.git
cd SlotSync

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Open your browser at **http://127.0.0.1:5000** 🎉

### Dependency Overview

```
flask>=3.0.0        # Web framework
ortools>=9.8.3296   # CP-SAT constraint solver
pandas>=2.0.0       # Data manipulation for import/export
openpyxl>=3.1.0     # Excel read/write
python-dotenv>=1.0.0 # Environment variable management
```

---

## 📂 Project Structure

```
SlotSync/
│
├── app.py                          # Flask application factory & entry point
│
├── api/
│   ├── routes.py                   # All REST endpoints (/generate, /timetable, /manual-assist …)
│   ├── export_service.py           # Excel / CSV / print export logic
│   └── import_service.py           # Bulk data import from JSON / CSV
│
├── solver/
│   ├── cp_sat_solver.py            # Full-timetable solver (OR-Tools CP-SAT)
│   └── manual_assist.py            # Permutation engine for single teacher/section assist
│
├── models/
│   ├── __init__.py
│   ├── teacher.py                  # Teacher data class
│   ├── subject.py                  # Subject data class
│   ├── room.py                     # Room data class
│   ├── section.py                  # Section (class) data class
│   └── timetable_entry.py          # Output entry model
│
├── database/
│   ├── db.py                       # Database connection & CRUD helpers
│   ├── schema.sql                  # SQLite schema definition
│   └── vtu_syllabus.py             # VTU syllabus seed data helper
│
├── templates/
│   └── index.html                  # Single-page app shell
│
├── static/
│   ├── css/
│   │   ├── style.css               # Main application styles (dark/light mode)
│   │   └── print.css               # Print-optimised stylesheet
│   └── js/
│       ├── app.js                  # Core app logic & navigation
│       ├── data_manager.js         # CRUD forms for teachers, subjects, rooms, sections
│       ├── timetable.js            # Timetable grid rendering
│       ├── lectures.js             # Lecture management
│       ├── manual_assist.js        # Manual slot assignment UI
│       ├── heatmap.js              # Teacher load heatmap
│       └── diagnostics.js          # Constraint diagnostics dashboard
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the single-page application |
| `GET` | `/api/teachers` | List all teachers |
| `POST` | `/api/teachers` | Add a new teacher |
| `PUT` | `/api/teachers/<id>` | Update teacher |
| `DELETE` | `/api/teachers/<id>` | Remove teacher |
| `GET` | `/api/subjects` | List all subjects |
| `POST` | `/api/subjects` | Add a new subject |
| `GET` | `/api/rooms` | List all rooms |
| `POST` | `/api/rooms` | Add a new room |
| `GET` | `/api/sections` | List all sections |
| `POST` | `/api/sections` | Add a new section |
| `GET` | `/api/lectures` | List all lecture assignments |
| `POST` | `/api/lectures` | Assign lecture to section |
| `POST` | `/api/generate` | **Run the CP-SAT solver** and generate a clash-free timetable |
| `GET` | `/api/timetable` | Retrieve the current timetable (all entries) |
| `GET` | `/api/timetable/<section_id>` | Timetable for a specific section |
| `GET` | `/api/timetable/teacher/<id>` | Timetable for a specific teacher |
| `GET` | `/api/manual-assist/<section_id>` | List valid slot permutations for manual patching |
| `POST` | `/api/manual-assist/apply` | Apply a selected manual slot arrangement |
| `GET` | `/api/diagnostics` | Run conflict detection before generation |
| `GET` | `/api/export` | Export timetable (JSON / CSV / Excel) |
| `POST` | `/api/import` | Bulk-import data from file |

---

## 📋 Usage Workflow

```
1. ➕ Add Data
   Add teachers, subjects, rooms, sections (via UI forms or bulk import)

2. 🔬 Run Diagnostics
   Check for potential conflicts before generation

3. ⚡ Generate Timetable
   Click "Generate Timetable" — solver runs and produces a clash-free schedule

4. 📊 Review
   View the grid per section, per teacher, or as a full college heatmap

5. 🖐️ Manual Patch (optional)
   Use "Manual Assist" to hand-place specific slots, solver re-adjusts the rest

6. 📤 Export
   Download as Excel or use the print layout for physical distribution
```

---

## 🗺️ Roadmap

- [x] CP-SAT automatic timetable generation  
- [x] Manual assist with permutation engine  
- [x] Teacher / section grid views  
- [x] Teacher load heatmap  
- [x] Import / Export (JSON, CSV, Excel)  
- [x] Diagnostics & conflict detection  
- [x] Print-ready CSS layout  
- [x] Dark mode UI  
- [ ] User authentication (HOD / admin login)  
- [ ] PostgreSQL production database  
- [ ] Multi-department / multi-college support  
- [ ] Timetable regeneration with different priority profiles  
- [ ] Email / notification when timetable is published  
- [ ] Mobile-responsive grid view  

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the repository  
2. Create a feature branch: `git checkout -b feature/my-feature`  
3. Commit your changes: `git commit -m "feat: add my feature"`  
4. Push the branch: `git push origin feature/my-feature`  
5. Open a Pull Request  

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by [amruthck177](https://github.com/amruthck177)

⭐ Star this repo if SlotSync saved your sanity!

</div>
