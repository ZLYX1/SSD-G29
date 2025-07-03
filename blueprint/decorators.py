from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to access this page.", "warning")
            return redirect(url_for('auth.auth'))  # redirect to /auth route
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash("You don't have permission to access this page.", "danger")
                return redirect(url_for('auth.auth'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to access this page.", "warning")
            return redirect(url_for('auth.auth'))
        if 'role' not in session or session['role'] != 'admin':
            flash("Administrator access required.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function