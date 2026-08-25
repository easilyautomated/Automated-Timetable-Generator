from flask_login import login_required, current_user
from flask import redirect, url_for
from functools import wraps


def role_required(role):
    # Maps each role to the name of that role's own dashboard route,
    # used to redirect a logged-in user with the WRONG role back to
    # somewhere appropriate for them (not the login page since they ARE logged in).
    dashboard_routes = {
        "admin": "admin.dashboard",
        "teacher": "teacher.dashboard",
        "student": "student.dashboard",
        "parent": "parent.dashboard",
    }
    # role_required(role) takes an argument, so it needs an extra layer
    # compared to a normal decorator: this function returns the ACTUAL
    # decorator (decorator), which then wraps the route function (func).
    def decorator(func):
        @wraps(func)          # keeps Flask able to tell routes apart correctly
        @login_required       # Ensures if not logged in at all, they're redirected to login page
        def wrapper(*args, **kwargs):
            # *args, **kwargs let this work on ANY route, regardless of
            # what arguments that route function normally takes
            if current_user.role == role:
                # if correct then let the real route run as normal
                return func(*args, **kwargs)
            else:
                # Ensures if logged in but WRONG role then they're redirected to THEIR OWN dashboard
                return redirect(url_for(dashboard_routes[current_user.role]))
        return wrapper
    return decorator