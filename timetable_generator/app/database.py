import sqlite3, click
from flask import current_app, g
from flask.cli import with_appcontext

def get_database():
    # Connects to the SQLite database so multiple functions during the same request reuse one connection rather than opening several
    if "database" not in g:
        g.database = sqlite3.connect(current_app.config["DATABASE"])
        g.database.row_factory = sqlite3.Row
        # Enforces foreign key constraints.
        g.database.execute("PRAGMA foreign_keys = ON")
    return g.database

def close_database(e=None):
    # Closes the database connection at the end of the request and returns None if no connection was made during the request to avoid errors.
    database = g.pop("database", None)
    if database is not None:
        database.close()

def init_database():
    database = get_database()
    with current_app.open_resource("schema.sql") as f:
        database.executescript(f.read().decode("utf8"))

# A command line to initialise the database, which can be run using Flask's CLI. "flask init-database" will set up the database schema.
@click.command("init-database")
@with_appcontext
def init_database_command():
    init_database()
    click.echo("Database has been initialised.")