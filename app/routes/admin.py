from flask import Blueprint, render_template, request, redirect, url_for
from app.database import get_database
from app.auth import role_required

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