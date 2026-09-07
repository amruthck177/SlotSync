CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    days TEXT NOT NULL DEFAULT '["Mon", "Tue", "Wed", "Thu", "Fri"]',
    periods_per_day INTEGER NOT NULL DEFAULT 7,
    start_time TEXT NOT NULL DEFAULT '09:00',
    period_duration INTEGER NOT NULL DEFAULT 55,
    short_break_after INTEGER NOT NULL DEFAULT 2,
    short_break_duration INTEGER NOT NULL DEFAULT 15,
    lunch_break_after INTEGER NOT NULL DEFAULT 4,
    lunch_break_duration INTEGER NOT NULL DEFAULT 50,
    time_slots_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS teachers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    branch TEXT NOT NULL,
    subjects_json TEXT NOT NULL DEFAULT '[]',
    cross_branch_json TEXT NOT NULL DEFAULT '[]',
    max_hours_per_day INTEGER NOT NULL DEFAULT 4,
    max_hours_per_week INTEGER NOT NULL DEFAULT 20
);

CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    branch TEXT NOT NULL,
    weekly_hours INTEGER NOT NULL DEFAULT 4,
    needs_lab INTEGER NOT NULL DEFAULT 0,
    consecutive_hours INTEGER NOT NULL DEFAULT 1,
    semester INTEGER NOT NULL DEFAULT 5
);

CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL DEFAULT 'regular',
    capacity INTEGER NOT NULL DEFAULT 60,
    branch TEXT NOT NULL DEFAULT 'GENERAL'
);

CREATE TABLE IF NOT EXISTS sections (
    id TEXT PRIMARY KEY,
    branch TEXT NOT NULL,
    semester INTEGER NOT NULL DEFAULT 5,
    subjects_json TEXT NOT NULL DEFAULT '[]',
    electives_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS timetable_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,
    period INTEGER NOT NULL,
    subject_id TEXT NOT NULL,
    teacher_id TEXT NOT NULL,
    room_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    is_elective INTEGER NOT NULL DEFAULT 0,
    elective_group TEXT,
    is_locked INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lectures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id TEXT NOT NULL,
    teacher_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    credits INTEGER NOT NULL DEFAULT 4,
    preferred_room_type TEXT NOT NULL DEFAULT 'regular',
    is_tutorial INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
    FOREIGN KEY (section_id) REFERENCES sections(id)
);
