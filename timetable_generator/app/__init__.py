import os
from flask import Flask
from .database import close_database, init_database_command


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

    return app

