from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.database import get_database
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        database = get_database()
        row = database.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        # Check if the user exists and the password is correct
        if row is None:
            return render_template("auth/login.html", error="Invalid username or password")

        user = User(row["user_id"], row["username"], row["password_hash"], row["role"], row["linked_id"])

    
        if not user.check_password(password):
            return render_template("auth/login.html", error="Invalid password")

        login_user(user)

        dashboard_routes = {
            "admin": "admin.dashboard",
            "teacher": "teacher.dashboard",
            "student": "student.dashboard",
            "parent": "parent.dashboard",
        }
    return redirect(url_for(dashboard_routes[user.role]))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
    # Redirects the user to the login page after logging out.

