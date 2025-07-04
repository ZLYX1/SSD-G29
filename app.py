from flask import Flask, g, render_template, request, redirect, url_for, flash, session

from config.db_config import DBConfig
from db import PostgresConnector
import secrets
import os
from datetime import timedelta

from controllers.auth_controller import AuthController

from dotenv import load_dotenv

load_dotenv()
env = os.getenv("FLASK_ENV", "production")

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

def str2bool(val, default=False):
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "y", "on")

app.config['WTF_CSRF_SSL_STRICT'] = str2bool(os.getenv('WTF_CSRF_SSL_STRICT'), default=(env=="production"))
app.config['SESSION_COOKIE_SECURE'] = str2bool(os.getenv('SESSION_COOKIE_SECURE'), default=(env=="production"))
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Strict' if env=='production' else 'Lax')
app.config['SESSION_COOKIE_HTTPONLY'] = str2bool(os.getenv('SESSION_COOKIE_HTTPONLY'), default=True)


# Validate required environment variables
required_vars = [
    "DATABASE_HOST",
    "DATABASE_PORT",
    "DATABASE_NAME",
    "DATABASE_USERNAME",
    "DATABASE_PASSWORD",
]

for var in required_vars:
    if var not in os.environ:
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Log non-sensitive variables (for development only)
if os.environ.get("FLASK_ENV") == "development":
    print(f"[INFO] Connecting to DB host: {os.environ['DATABASE_HOST']}")
    print(f"[INFO] DB port: {os.environ['DATABASE_PORT']}")
    print(f"[INFO] DB name: {os.environ['DATABASE_NAME']}")

# Persistent database connection
config = DBConfig(
    # Matches the service name in docker-compose.yml
    host=os.environ["DATABASE_HOST"],
    # Internal port (not the mapped host port)
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME"],
    user=os.environ["DATABASE_USERNAME"],
    password=os.environ["DATABASE_PASSWORD"],
)
db = PostgresConnector(config)

def initialize_database():
    try:
        from data_sources.user_repository import UserRepository
        conn = db.get_connection()
        user_repo = UserRepository(conn)
        db.return_connection(conn)
    except Exception:
        # Fail silently - let the application handle DB errors during requests
        pass

# Initialize database when app starts
with app.app_context():
    initialize_database()

def get_db_conn():
    if "db_conn" not in g:
        g.db_conn = db.get_connection()
    return g.db_conn

def get_auth_controller():
    if "auth_controller" not in g:
        g.auth_controller = AuthController(get_db_conn())
    return g.auth_controller


@app.teardown_appcontext
def close_db_conn(exception):
    conn = g.pop("db_conn", None)
    if conn:
        db.return_connection(conn)


@app.route("/")
@app.route("/home")
def index():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        version = result[0] if result else "Unavailable"
        cursor.close()
    except Exception:
        version = "Unavailable"

    return render_template("index.html", version=version)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        auth_controller = get_auth_controller()
        if auth_controller.authenticate(email, password):
            # Successful login
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

# --- ROUTES ---
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    
    # User-Agent and IP protection
    current_ua = request.headers.get('User-Agent')
    current_ip = request.remote_addr

    if 'user_id' in session:
        # Enforce UA and IP match
        if session.get('bound_ua') != current_ua or session.get('bound_ip') != current_ip:
            session.clear()
            flash("Session ended for security reasons.", "danger")
            return redirect(url_for('auth.auth'))
    else:
        session['bound_ua'] = current_ua
        session['bound_ip'] = current_ip

# Regenerate session after login to ensure security
def regenerate_session():
    """Call this after successful login"""
    old_session = dict(session)
    session.clear()
    session.update(old_session)
    session.permanent = True

@app.route('/api/session-config')
def session_config():
    return {
        'session_lifetime_minutes': app.permanent_session_lifetime.total_seconds() // 60
    }


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")
        
        auth_controller = get_auth_controller()
        if auth_controller.register(email, password):
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Email already registered", "danger")

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development")
