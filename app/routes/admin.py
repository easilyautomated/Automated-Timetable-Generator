from pyexpat import errors
from unicodedata import name
from webbrowser import get

from flask import Blueprint, render_template, request, redirect, url_for
from app.database import get_database
from app.auth import role_required
import database

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/teachers')
@role_required('admin')
def list_teachers():
    db = get_database()
    teachers = db.execute("SELECT * FROM teachers").fetchall()
    return render_template('admin/teachers/list.html', teachers=teachers)

# ADD TEACHER
@admin_bp.route('/teachers/add', methods=['GET', 'POST'])
@role_required('admin')
def add_teacher():
    if request.method == 'GET':
        return render_template('admin/teachers/add.html')
    else: # POST method
        full_name = request.form["full_name"]
        max_periods_per_day = request.form["max_periods_per_day"]
        confirm_duplicate = request.form.get("confirm_duplicate")

        errors = []
        if not full_name.strip():
            errors.append("Full name is required.")
        if not max_periods_per_day.isdigit() or int(max_periods_per_day) <= 0:
            errors.append("Max periods per day must be a positive number.")

        database = get_database()
        duplicate_warning = False
        # Only checks for duplicates if the basic validation passes and the user hasn't confirmed they want to add a duplicate.
        if not errors:
            existing_teacher = database.execute("SELECT * FROM teachers WHERE full_name = ?", (full_name,)).fetchone()[0]
            if existing_teacher > 0 and not confirm_duplicate:
                duplicate_warning = True
                
        if errors or duplicate_warning:
            return render_template('admin/teachers/add.html', errors=errors, duplicate_warning=duplicate_warning, full_name=full_name, max_periods_per_day=max_periods_per_day)

        database.execute("INSERT INTO teachers (full_name, max_periods_per_day) VALUES (?, ?)", (full_name, max_periods_per_day))
        database.commit()
        return redirect(url_for('admin.list_teachers'))

# EDIT TEACHER
@admin_bp.route('/teachers/<int:teacher_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit_teacher(teacher_id):
    database = get_database()

    if request.method == 'GET':
        teacher = database.execute("SELECT * FROM teachers WHERE teacher_id = ?", (teacher_id,)).fetchone()
        return render_template('admin/teachers/edit.html', teacher=teacher)

    else:  # POST method
        full_name = request.form["full_name"]
        max_periods_per_day = request.form["max_periods_per_day"]

        errors = []
        if not full_name.strip():
            errors.append("Full name is required.")
        if not max_periods_per_day.isdigit() or int(max_periods_per_day) <= 0:
            errors.append("Max periods per day must be a positive number.")

        if errors:
            return render_template('admin/teachers/edit.html', errors=errors, teacher={"teacher_id": teacher_id, "full_name": full_name, "max_periods_per_day": max_periods_per_day})
        database.execute("UPDATE teachers SET full_name = ?, max_periods_per_day = ? WHERE teacher_id = ?", (full_name, max_periods_per_day, teacher_id))
        database.commit()
        return redirect(url_for('admin.list_teachers'))

# DELETE TEACHER 
@admin_bp.route('/teachers/<int:teacher_id>/delete', methods=['POST'])
@role_required('admin')
def delete_teacher(teacher_id):
    database = get_database()

    in_use = database.execute(
        "SELECT COUNT(*) FROM lesson_assignments WHERE teacher_id = ?", (teacher_id,)
    ).fetchone()[0]

    if in_use > 0:
        return "Cannot delete: this teacher has lesson assignments.", 400

    database.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
    database.commit()
    return redirect(url_for('admin.list_teachers'))


# ROOMS
@admin_bp.route('/rooms')
@role_required('admin')
def list_rooms():
    database = get_database()
    rooms = database.execute("SELECT * FROM rooms").fetchall()
    return render_template('admin/rooms/list.html', rooms=rooms)

# ADD ROOM
@admin_bp.route('/rooms/add', methods=['GET', 'POST'])
@role_required('admin')
def add_room():
    if request.method == 'GET':
        return render_template('admin/rooms/add.html')

    else:  # POST method
        room_name = request.form["room_name"]
        capacity = request.form["capacity"]
        room_type = request.form["room_type"]

        errors = []
        if not room_name.strip():
            errors.append("Room name is required.")
        if not capacity.isdigit() or int(capacity) <= 0:
            errors.append("Capacity must be a positive number.")
        if not room_type.strip():
            errors.append("Room type is required.")

        database = get_database()

        if not errors:
            existing = database.execute(
                "SELECT COUNT(*) FROM rooms WHERE name = ?", (room_name,)
            ).fetchone()[0]
            if existing > 0:
                errors.append(f"A room named '{room_name}' already exists. Room names must be unique.")

        # Blocks any duplicate room names unconditionally, since room names must be unique.
        if errors:
            return render_template('admin/rooms/add.html', errors=errors, room_name=room_name, capacity=capacity, room_type=room_type)

        database.execute(
            "INSERT INTO rooms (name, capacity, room_type) VALUES (?, ?, ?)",
            (room_name, capacity, room_type)
        )
        database.commit()
        return redirect(url_for('admin.list_rooms'))

# EDIT ROOM
@admin_bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit_room(room_id):
    database = get_database()

    if request.method == 'GET':
        room = database.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
        return render_template('admin/rooms/edit.html', room=room)

    else:  # POST method
        room_name = request.form["room_name"]
        capacity = request.form["capacity"]
        room_type = request.form["room_type"]
        existing = database.execute("SELECT COUNT(*) FROM rooms WHERE name = ? AND room_id != ?", (room_name, room_id)).fetchone()[0]

        errors = []
        if not room_name.strip():
            errors.append("Room name is required.")
        if not capacity.isdigit() or int(capacity) <= 0:
            errors.append("Capacity must be a positive number.")
        if not room_type.strip():
            errors.append("Room type is required.")
        if existing > 0:
            errors.append(f"A room named '{room_name}' already exists. Room names must be unique.")
        if errors:
            return render_template('admin/rooms/edit.html', errors=errors, room={"room_id": room_id, "name": room_name, "capacity": capacity, "room_type": room_type})
        database.execute("UPDATE rooms SET name = ?, capacity = ?, room_type = ? WHERE room_id = ?", (room_name, capacity, room_type, room_id))
        database.commit()
        return redirect(url_for('admin.list_rooms'))

# DELETE ROOM
@admin_bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@role_required('admin')
def delete_room(room_id):
    database = get_database()

    in_use = database.execute("SELECT COUNT(*) FROM lesson_assignments WHERE room_id = ?", (room_id,)).fetchone()[0]

    if in_use > 0:
        return "Cannot delete: this room has lesson assignments.", 400

    database.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
    database.commit()
    return redirect(url_for('admin.list_rooms'))

# SUBJECTS
@admin_bp.route('/subjects')
@role_required('admin')
def list_subjects():
    database = get_database()
    subjects = database.execute("SELECT * FROM subjects").fetchall()
    return render_template('admin/subjects/list.html', subjects=subjects)

# ADD SUBJECT
@admin_bp.route('/subjects/add', methods=['GET', 'POST'])
@role_required('admin')
def add_subject():
    if request.method == 'GET':
        return render_template('admin/subjects/add.html')

    else:  # POST method
        subject_name = request.form["subject_name"]
        periods_per_week = request.form["periods_per_week"]
        required_room_type = request.form["required_room_type"]

        errors = []
        if not subject_name.strip():
            errors.append("Subject name is required.")
        if not periods_per_week.isdigit() or int(periods_per_week) <= 0:
            errors.append("Periods per week must be a positive number.")
        if not required_room_type.strip():
            errors.append("A required room type is required.")

        database = get_database()

        if not errors:
            existing = database.execute(
                "SELECT COUNT(*) FROM subjects WHERE name = ?", (subject_name,)
            ).fetchone()[0]
            if existing > 0:
                errors.append(f"A subject named '{subject_name}' already exists. Subject names must be unique.")

        if errors:
            return render_template('admin/subjects/add.html', errors=errors, subject_name=subject_name)

        database.execute("INSERT INTO subjects (name) VALUES (?)", (subject_name,))
        database.commit()
        return redirect(url_for('admin.list_subjects'))

# EDIT SUBJECT
@admin_bp.route('/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit_subject(subject_id):
    database = get_database()

    if request.method == 'GET':
        subject = database.execute("SELECT * FROM subjects WHERE subject_id = ?", (subject_id,)).fetchone()
        return render_template('admin/subjects/edit.html', subject=subject)

    else:  # POST method
        subject_name = request.form["subject_name"]
        periods_per_week = request.form["periods_per_week"]
        required_room_type = request.form["required_room_type"]

        errors = []
        if not subject_name.strip():
            errors.append("Subject name is required.")
        if not periods_per_week.isdigit() or int(periods_per_week) <= 0:
            errors.append("Periods per week must be a positive number.")
        if not required_room_type.strip():
            errors.append("A required room type is required.")

        existing = database.execute(
            "SELECT COUNT(*) FROM subjects WHERE name = ? AND subject_id != ?", (subject_name, subject_id)).fetchone()[0]
        if existing > 0:
            errors.append(f"A subject named '{subject_name}' already exists. Subject names must be unique.")

        if errors:
            return render_template('admin/subjects/edit.html', errors=errors, subject={"subject_id": subject_id, "name": subject_name, "periods_per_week": periods_per_week, "required_room_type": required_room_type})

        database.execute(
            "UPDATE subjects SET name = ?, periods_per_week = ?, required_room_type = ? WHERE subject_id = ?",
            (subject_name, periods_per_week, required_room_type, subject_id)
        )
        database.commit()
        return redirect(url_for('admin.list_subjects'))

# DELETE SUBJECT
@admin_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@role_required('admin')
def delete_subject(subject_id):
    database = get_database()

    # Checks if the subject is associated with any lesson assignments, group subjects, or teacher subjects before allowing deletion.
    in_lesson_assignments = database.execute("SELECT COUNT(*) FROM lesson_assignments WHERE subject_id = ?", (subject_id,)).fetchone()[0]
    in_group_subjects = database.execute("SELECT COUNT(*) FROM group_subjects WHERE subject_id = ?", (subject_id,)).fetchone()[0]
    in_teacher_subjects = database.execute("SELECT COUNT(*) FROM teacher_subjects WHERE subject_id = ?", (subject_id,)).fetchone()[0]

    if in_lesson_assignments > 0 or in_group_subjects > 0 or in_teacher_subjects > 0:
        return "The subject is associated with existing records so it cannot be deleted.", 400

    database.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id,))
    database.commit()
    return redirect(url_for('admin.list_subjects'))

# STUDENT GROUPS
@admin_bp.route('/student_groups')
@role_required('admin')
def list_student_groups():
    database = get_database()
    student_groups = database.execute("SELECT * FROM student_groups").fetchall()
    return render_template('admin/student_groups/list.html', student_groups=student_groups)

# ADD STUDENT GROUP
@admin_bp.route('/student_groups/add', methods=['GET', 'POST'])
@role_required('admin')
def add_student_group():
    if request.method == 'GET':
        # need the full subject list so the form can show a checkbox for each subject
        subjects = get_database().execute("SELECT * FROM subjects").fetchall()
        return render_template('admin/student_groups/add.html', subjects=subjects)

    else:  # POST method
        student_group_name = request.form["student_group_name"]
        year_group = request.form["year_group"]
        group_size = request.form["group_size"]

        errors = []
        if not student_group_name.strip():
            errors.append("Student group name is required.")
        if not year_group.isdigit() or int(year_group) <= 0:
            errors.append("Year group must be a positive integer.")
        if not group_size.isdigit() or int(group_size) <= 0:
            errors.append("Group size must be a positive integer.")

        database = get_database()

        if not errors:
            existing = database.execute("SELECT COUNT(*) FROM student_groups WHERE name = ?", (student_group_name,)).fetchone()[0]
            if existing > 0:
                errors.append(f"A student group named '{student_group_name}' already exists. Student group names must be unique.")

        if errors:
            # re-fetch subjects so the checkbox list still shows on the re-rendered form
            subjects = database.execute("SELECT * FROM subjects").fetchall()
            return render_template('admin/student_groups/add.html',
                errors=errors,
                student_group_name=student_group_name,
                year_group=year_group,
                group_size=group_size,
                subjects=subjects
            )

        # insert the group first - lastrowid gives us the new auto-generated group_id, which we need before we can link any subjects to it
        cursor = database.execute(
            "INSERT INTO student_groups (name, year_group, group_size) VALUES (?, ?, ?)",
            (student_group_name, int(year_group), int(group_size))
        )
        new_group_id = cursor.lastrowid

        # getlist (NOT get!) because checkboxes can submit multiple values under one name
        selected_subject_ids = request.form.getlist("subjects")
        for subject_id in selected_subject_ids:
            database.execute("INSERT INTO group_subjects (group_id, subject_id) VALUES (?, ?)", (new_group_id, subject_id))

        database.commit()
        return redirect(url_for('admin.list_student_groups'))


# EDIT STUDENT GROUP
@admin_bp.route('/student_groups/<int:group_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit_student_group(group_id):
    database = get_database()
    if request.method == 'GET':
        student_group = database.execute("SELECT * FROM student_groups WHERE group_id = ?", (group_id,)).fetchone()
        subjects = database.execute("SELECT * FROM subjects").fetchall()
        selected_subject_ids = [row['subject_id'] for row in database.execute("SELECT subject_id FROM group_subjects WHERE group_id = ?", (group_id,)).fetchall()]
        return render_template('admin/student_groups/edit.html', student_group=student_group, subjects=subjects, selected_subject_ids=selected_subject_ids)
    else:  # POST method
        student_group_name = request.form["student_group_name"]
        year_group = request.form["year_group"]
        group_size = request.form["group_size"]

        errors = []

        if not errors:
            existing = database.execute("SELECT COUNT(*) FROM student_groups WHERE name = ? AND group_id != ?",(student_group_name, group_id)).fetchone()[0]
            if existing > 0:
                errors.append(f"A student group named '{student_group_name}' already exists. Student group names must be unique.")

        if errors:
            subjects = database.execute("SELECT * FROM subjects").fetchall()
            selected_subject_ids = request.form.getlist("selected_subject_ids")
            return render_template('admin/student_groups/edit.html',
                errors=errors,
                student_group={"group_id": group_id, "name": student_group_name, "year_group": year_group, "group_size": group_size},
                subjects=subjects,
                selected_subject_ids=selected_subject_ids
            )

        database.execute("UPDATE student_groups SET name = ?, year_group = ?, group_size = ? WHERE group_id = ?",(student_group_name, int(year_group), int(group_size), group_id))

        # wipe and rebuild the group's subject links
        database.execute("DELETE FROM group_subjects WHERE group_id = ?", (group_id,))
        selected_subject_ids = request.form.getlist("selected_subject_ids")
        for subject_id in selected_subject_ids:
            database.execute("INSERT INTO group_subjects (group_id, subject_id) VALUES (?, ?)", (group_id, subject_id))

        database.commit()
        return redirect(url_for('admin.list_student_groups'))

# DELETE STUDENT GROUP
@admin_bp.route('/student_groups/<int:group_id>/delete', methods=['POST'])
@role_required('admin')
def delete_student_group(group_id):
    database = get_database()
    in_lesson_assignments = database.execute("SELECT COUNT(*) FROM lesson_assignments WHERE group_id = ?", (group_id,)).fetchone()[0]
    in_students = database.execute("SELECT COUNT(*) FROM students WHERE group_id = ?", (group_id,)).fetchone()[0]

    if in_lesson_assignments > 0 or in_students > 0:
        return "Cannot delete: this student group still has students or lesson assignments linked to it.", 400

    # safe to remove the group's subject links automatically, since they belong to the group itself
    database.execute("DELETE FROM group_subjects WHERE group_id = ?", (group_id,))
    database.execute("DELETE FROM student_groups WHERE group_id = ?", (group_id,))
    database.commit()
    return redirect(url_for('admin.list_student_groups'))

# OPTION BLOCKS
@admin_bp.route('/option_blocks')
@role_required('admin')
def list_option_blocks():
    database = get_database()
    rows = database.execute(
        "SELECT ob.block_name, s.name AS subject_name, s.subject_id "
        "FROM option_blocks ob JOIN subjects s ON ob.subject_id = s.subject_id "
        "ORDER BY ob.block_name"
    ).fetchall()

    blocks = {}
    for row in rows:
        blocks.setdefault(row["block_name"], []).append(row["subject_name"])

    return render_template('admin/option_blocks/list.html', blocks=blocks)

# ADD OPTION BLOCK
@admin_bp.route('/option_blocks/add', methods=['GET', 'POST'])
@role_required('admin')
def add_option_block():
    database = get_database()

    if request.method == 'GET':
        subjects = database.execute("SELECT * FROM subjects").fetchall()
        return render_template('admin/option_blocks/add.html', subjects=subjects)

    else:  # POST method
        block_name = request.form["block_name"]
        selected_subject_ids = request.form.getlist("subjects")

        errors = []
        if not block_name.strip():
            errors.append("Block name is required.")
        if not selected_subject_ids:
            errors.append("Select at least one subject for this block.")

        if errors:
            subjects = database.execute("SELECT * FROM subjects").fetchall()
            return render_template('admin/option_blocks/add.html', errors=errors, block_name=block_name, subjects=subjects)

        for subject_id in selected_subject_ids:
            database.execute("INSERT INTO option_blocks (block_name, subject_id) VALUES (?, ?)", (block_name, subject_id))

        database.commit()
        return redirect(url_for('admin.list_option_blocks'))

# DELETE OPTION BLOCK
@admin_bp.route('/option_blocks/<block_name>/delete', methods=['POST'])
@role_required('admin')
def delete_option_block(block_name):
    database = get_database()
    database.execute("DELETE FROM option_blocks WHERE block_name = ?", (block_name,))
    database.commit()
    return redirect(url_for('admin.list_option_blocks'))