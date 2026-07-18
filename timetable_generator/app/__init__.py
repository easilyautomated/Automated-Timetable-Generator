import os, sqlite3
from flask import Flask, current_app, g

def create_app():
    app = Flask(__name__)
    # Set the secret key for session management and a fallback value if the external environment variable is not set for security purposes.
    secret_key = os.environ.get("SECRET_KEY", "default_secret_key")
    app.config["SECRET_KEY"] = secret_key

    # Ensure the instance folder exists as it holds the SQL database.
    os.makedirs(app.instance_path, exist_ok=True)
    # Connects path to the SQLite database file and makes it compatible with any web server or deployment environment.
    app.config["DATABASE"] = os.path.join(app.instance_path, "timetable.db")

    app.teardown_appcontext(close_db)

    return app

def get_db():
    # Connects to the SQLite database so multiple functions during the same request reuse one connection rather than opening several
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        # Enforces foreign key constraints.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    # Closes the database connection at the end of the request and returns None if no connection was made during the request to avoid errors.
    db = g.pop("db", None)
    if db is not None:
        db.close()