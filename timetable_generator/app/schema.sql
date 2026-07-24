CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    max_periods_per_day INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL,
    periods_per_week INTEGER NOT NULL,
    required_room_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS student_groups (
    student_group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_group_name TEXT NOT NULL,
    year_group INTEGER NOT NULL,
    group_size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_name TEXT NOT NULL,
    room_capacity INTEGER NOT NULL,
    room_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teacher_availability (
    teacher_availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    day INTEGER NOT NULL,
    period INTEGER NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);

CREATE TABLE IF NOT EXISTS teacher_subjects (
    teacher_subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)    
);

CREATE TABLE IF NOT EXISTS group_subjects (
    group_subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_group_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    FOREIGN KEY (student_group_id) REFERENCES student_groups(student_group_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE IF NOT EXISTS room_unavailability (
    room_unavailability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE IF NOT EXISTS lesson_assignments(
    lesson_assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_group_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    day INTEGER NOT NULL,
    period INTEGER NOT NULL,
    FOREIGN KEY (student_group_id) REFERENCES student_groups(student_group_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    year_group INTEGER NOT NULL,
    student_group_id INTEGER NOT NULL,
    FOREIGN KEY (student_group_id) REFERENCES student_groups(student_group_id)
);

CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin','teacher','student','parent')),
    linked_id INTEGER
);

CREATE TABLE IF NOT EXISTS parent_child(
    parent_user_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    PRIMARY KEY (parent_user_id, student_id),
    FOREIGN KEY (parent_user_id) REFERENCES users(user_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS lesson_attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('present','absent','late')),
    notes TEXT,
    UNIQUE(lesson_assignment_id, student_id, date),
    FOREIGN KEY (lesson_assignment_id) REFERENCES lesson_assignments(lesson_assignment_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);