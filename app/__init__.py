import os
from flask import Flask, app
from .database import close_database, init_database_command
from flask_login import LoginManager
from app.models.user import User
from app.database import get_database, close_database, init_database_command

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # Set the secret key for session management and a fallback value if the external environment variable is not set for security purposes.
    secret_key = os.environ.get("SECRET_KEY", "default_secret_key")
    app.config["SECRET_KEY"] = secret_key

    # Ensure the instance folder exists as it holds the SQL database.
    os.makedirs(app.instance_path, exist_ok=True)
    # Connects path to the SQLite database file and makes it compatible with any web server or deployment environment.
    app.config["DATABASE"] = os.path.join(app.instance_path, "timetable.database")

    app.teardown_appcontext(close_database)
    app.cli.add_command(init_database_command)

    login_manager = LoginManager() # Creates the manager instance for handling user sessions and authentication
    login_manager.login_view = "auth.login"  # Set the login view for the login manager
    login_manager.init_app(app) # Initialize the login manager with the Flask app

    @login_manager.user_loader
    def load_user(user_id):
        database = get_database()  # Get the database connection
        row = database.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()  # Fetches the user from the database
        if row is None:
            return None
        return User(row["user_id"], row["username"], row["password_hash"], row["role"], row["linked_id"])  # Return the User object

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    return app
