from flask import Flask, g, render_template, request, redirect, url_for, flash, session
# from flask_wtf.csrf import CSRFProtect  # Add this import at the top
from datetime import timedelta
from config.db_config import DBConfig
from db import PostgresConnector
import secrets
import os
import time
import requests
import click
from functools import wraps
from faker import Faker
import random
import uuid
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy import text

from flask.cli import with_appcontext

from extensions import csrf, limiter

from blueprint.auth import auth_bp
from blueprint.profile import profile_bp
from blueprint.browse import browse_bp
from blueprint.booking import booking_bp
from blueprint.messaging import messaging_bp
from blueprint.payment import payment_bp
from blueprint.rating import rating_bp
from blueprint.report import report_bp
from blueprint.audit_log import audit_bp, log_event
from dotenv import load_dotenv

load_dotenv()

# Check if running in CI/CD environment
CI_MODE = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

# Validate required environment variables (skip in CI/CD)
if not CI_MODE:
    required_env_vars = [
        'FLASK_SECRET_KEY',
        'CSRF_SECRET_KEY', 
        'SITEKEY',
        'RECAPTCHA_SECRET_KEY',
        'DATABASE_URL'
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"❌ Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please ensure these are set in your .env file."
        )
else:
    print("🔧 CI/CD Mode detected - Using test environment variables")
    # Set safe test values for CI/CD
    if not os.getenv('FLASK_SECRET_KEY'):
        os.environ['FLASK_SECRET_KEY'] = 'test-flask-secret-key-for-ci-cd-only'
    if not os.getenv('CSRF_SECRET_KEY'):
        os.environ['CSRF_SECRET_KEY'] = 'test-csrf-secret-key-for-ci-cd-only'
    if not os.getenv('SITEKEY'):
        os.environ['SITEKEY'] = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'  # Google test key
    if not os.getenv('RECAPTCHA_SECRET_KEY'):
        os.environ['RECAPTCHA_SECRET_KEY'] = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'  # Google test key

from blueprint.models import db, User, Profile, Booking, Payment, Report, Rating, TimeSlot, Message
from blueprint.models import Favourite, AuditLog, PasswordHistory

app = Flask(__name__)

# Cache control function to prevent browser caching of sensitive pages
def add_no_cache_headers(response):
    """Add headers to prevent browser caching of sensitive pages"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Add cache control to all responses
@app.after_request
def apply_cache_control(response):
    """Apply cache control headers to sensitive routes"""
    if request.endpoint and request.endpoint in [
        'payment.payment_page',
        'auth.login', 
        'auth.register',
        'profile.profile',
        'booking.booking'
    ]:
        response = add_no_cache_headers(response)
    return response

# Add security headers to all responses
@app.after_request
def apply_security_headers(response):
    """Apply security headers to all responses"""
    # Only add security headers if not already present (nginx might add them)
    if 'X-Content-Type-Options' not in response.headers:
        response.headers['X-Content-Type-Options'] = 'nosniff'
    
    if 'X-Frame-Options' not in response.headers:
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    if 'X-XSS-Protection' not in response.headers:
        response.headers['X-XSS-Protection'] = '1; mode=block'
    
    if 'Referrer-Policy' not in response.headers:
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

# Session management and security
@app.before_request
def check_session_timeout():
    """Check for session timeout and security"""
    # Clear stale flash messages to prevent cached error displays
    # This ensures flash messages are fresh and not cached
    
    # Check if user is logged in and session is still valid
    if 'user_id' in session:
        # Check if session has expired (based on last activity)
        if session.get('last_activity'):
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(hours=2):
                # Session has expired
                session.clear()
                flash("Your session has expired. Please log in again.", "warning")
                return redirect(url_for('auth.auth', mode='login'))
        
        # Update last activity time
        session['last_activity'] = datetime.now().isoformat()
        session.permanent = True

# Add timestamp filter for consistent formatting
@app.template_filter('timestamp')
def format_timestamp(timestamp):
    """Format timestamp consistently across all templates"""
    if timestamp is None:
        return ''
    
    # Convert to datetime if it's a string
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    now = datetime.now()
    diff = now - timestamp
    diff_days = diff.days
    
    # Same day - show time only
    if diff_days == 0:
        return timestamp.strftime('%H:%M')
    # Yesterday
    elif diff_days == 1:
        return f'Yesterday {timestamp.strftime("%H:%M")}'
    # Less than 7 days - show day and time
    elif diff_days < 7:
        return timestamp.strftime('%a %H:%M')
    # Older messages - show month/day and time
    else:
        return timestamp.strftime('%m/%d %H:%M')

def str2bool(val, default=False):
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "y", "on")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CSRF Configuration
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('CSRF_SECRET_KEY')

# Secure Session Configuration
# Check if we're in production (HTTPS) or development (HTTP)
is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('ENVIRONMENT') == 'production'

if is_production:
    # Production security settings (HTTPS required)
    app.config['WTF_CSRF_SSL_STRICT'] = True  # Require HTTPS for CSRF
    app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only cookies
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # Strict CSRF protection
else:
    # Development security settings (HTTP allowed but still secure)
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow HTTP for development
    app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP cookies in development
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Less strict for development

# Common security settings for both environments
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Session timeout
app.config['SESSION_COOKIE_NAME'] = 'safe_companions_session'  # Custom session name

csrf.init_app(app)

# Initialize rate limiter
limiter.init_app(app)

# Rate limit error handler
@app.errorhandler(429)
def handle_rate_limit_exceeded(e):
    """Handle rate limit exceeded errors with user-friendly messages"""
    flash("Too many requests. Please wait a moment before trying again.", "warning")
    
    # Check if the request was for authentication
    if request.endpoint and 'auth' in request.endpoint:
        return redirect(url_for('auth.auth', mode='login')), 429
    
    # Default fallback
    return redirect(url_for('index')), 429

# Add CSRF token and environment variables to template context
@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(
        csrf_token=generate_csrf(),
        sitekey=os.environ.get('SITEKEY')  # No default - validated at startup
    )

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

BOOKINGS = {
    1: {
        'seeker_id': 1,
        'escort_id': 2,
        'date': '2023-10-28',
        'status': 'Confirmed'
    },
    2: {
        'seeker_id': 1,
        'escort_id': 2,
        'date': '2023-11-05',
        'status': 'Pending'
    },
}

PAYMENTS = {
    1: {
        'user_id': 1,
        'amount': 250.00,
        'date': '2023-10-20',
        'status': 'Completed',
        'transaction_id': 'TXN12345'
    },
}

REPORTS = {
    1: {
        'reporter_id': 1,
        'reported_id': 2,
        'reason': 'Spam message',
        'status': 'Pending Review'
    },
}


# --- DECORATORS for Role-Based Access Control (RBAC) ---
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "warning")
            return redirect(url_for('auth.auth'))
        return f(*args, **kwargs)

    return decorated_function


def role_required(role):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("You must be logged in to view this page.", "warning")
                return redirect(url_for('auth.auth'))
            if session.get('role') != role:
                flash(f"You must be an {role} to access this page.", "danger")
                return redirect(
                    url_for('dashboard'))  # Redirect to a safe page
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# --- ROUTES ---
@app.route("/test-session")
def test_session():
    return render_template("index.html")


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.auth', mode='login'))


app.register_blueprint(
    auth_bp)  # registers at /auth because of prefix in auth.py
app.register_blueprint(profile_bp)
app.register_blueprint(browse_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(messaging_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(rating_bp)
app.register_blueprint(report_bp)
app.register_blueprint(audit_bp)

def get_user_spending_summary(user_id):
    """Returns total spending and payment details for the given user."""
    if not user_id:
        return None

    # Total amount spent
    total_spent = db.session.query(func.sum(Payment.amount)).filter_by(user_id=user_id).scalar() or 0

    # Total number of payments
    total_transactions = db.session.query(func.count(Payment.id)).filter_by(user_id=user_id).scalar()

    # Optional: Monthly breakdown (last 6 months)
    monthly_breakdown = db.session.query(
        func.date_trunc('month', Payment.created_at).label('month'),
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.user_id == user_id
    ).group_by(
        func.date_trunc('month', Payment.created_at)
    ).order_by(text('month desc')).limit(6).all()

    # Format breakdown
    breakdown = [
        {"month": month.strftime("%Y-%m"), "total": float(total)}
        for month, total in monthly_breakdown
    ]

    return {
        "total_spent": round(float(total_spent), 2),
        "transaction_count": total_transactions,
        "monthly_breakdown": breakdown
    }
    
def get_user_earning_summary(user_id):
    """Returns total earnings for a given escort user."""
    if not user_id:
        return None

    # Join Payment → Booking → escort
    # from models import Payment, Booking

    # Total earnings
    total_earned = db.session.query(func.sum(Payment.amount))\
        .join(Booking, Payment.booking_id == Booking.id)\
        .filter(Booking.escort_id == user_id).scalar() or 0

    # Count of bookings that resulted in payment
    total_paid_bookings = db.session.query(func.count(Payment.id))\
        .join(Booking, Payment.booking_id == Booking.id)\
        .filter(Booking.escort_id == user_id).scalar()

    # Optional: Earnings by month
    monthly_earnings = db.session.query(
        func.date_trunc('month', Payment.created_at).label('month'),
        func.sum(Payment.amount).label('total')
    ).join(Booking, Payment.booking_id == Booking.id)\
     .filter(Booking.escort_id == user_id)\
     .group_by(func.date_trunc('month', Payment.created_at))\
     .order_by(text('month desc')).limit(6).all()

    breakdown = [
        {"month": month.strftime("%Y-%m"), "total": float(total)}
        for month, total in monthly_earnings
    ]

    return {
        "total_earned": round(float(total_earned), 2),
        "paid_bookings": total_paid_bookings,
        "monthly_breakdown": breakdown
    }
    
@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    user_id = session.get('user_id')
    data = {}
    
    # Initialize default values for all variables
    summary = None
    favourite_profiles = []

    if role == 'seeker':
        data['upcoming_bookings_count'] = db.session.query(Booking).join(
            User, Booking.escort_id == User.id
        ).filter(
            Booking.seeker_id == user_id,
            Booking.status == 'Confirmed',
            User.deleted == False,
            User.active == True,
            User.activate == True
        ).count()
        # Fetch favourite escorts for this seeker
        favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
        if favourite_ids:
            favourite_profiles = Profile.query.filter(Profile.user_id.in_(favourite_ids)).all()
        else:
            favourite_profiles = []
        summary = get_user_spending_summary(user_id)
        

        
    elif role == 'escort':
        data['booking_requests_count'] = db.session.query(Booking).join(
            User, Booking.seeker_id == User.id
        ).filter(
            Booking.escort_id == user_id,
            Booking.status == 'Pending',
            User.deleted == False,
            User.active == True,
            User.activate == True
        ).count()
        
        # Fetch favourite seeker
        favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
        if favourite_ids:
            favourite_profiles = Profile.query.filter(Profile.user_id.in_(favourite_ids)).all()
        else:
            favourite_profiles = []
        summary = get_user_earning_summary(user_id)
        
    elif role == 'admin':
        data['total_users'] = User.query.count()
        data['total_reports'] = Report.query.filter_by(
            status='Pending Review').count()
        data['seeker_to_escort_requests'] = User.query.filter(
            User.role == 'seeker',
            User.pending_role == 'escort'
        ).count()

        data['escort_to_seeker_requests'] = User.query.filter(
            User.role == 'escort',
            User.pending_role == 'seeker'
        ).count()
        
        # Admin doesn't need summary or favourite_profiles, but initialize them to avoid errors
        summary = None
        favourite_profiles = []

    return render_template('dashboard.html', role=role, data=data, summary=summary, favourite_profiles=favourite_profiles)


@app.route('/admin', methods=['GET', 'POST'])
@role_required('admin')
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        user_id_to_modify = int(request.form.get('user_id'))
        user_to_modify = User.query.get(user_id_to_modify)
        if user_to_modify:
            if action == 'delete_user':
                user_to_modify.deleted = True  # Soft delete
                db.session.commit()
                flash(f"User {user_to_modify.email} has been deleted.", "success")
                log_event(session.get('user_id'),  # the admin who performed the action
                        'admin delete user',
                        f"Deleted user {user_to_modify.email} (id={user_to_modify.id})")
            elif action == 'toggle_ban':
                user_to_modify.active = not user_to_modify.active
                db.session.commit()
                if user_to_modify.active:
                    flash(f"User {user_to_modify.email} has been unbanned.", "success")
                    log_event(session.get('user_id'),  # the admin who performed the action
                        'admin unban user',
                        f"Unbanned user {user_to_modify.email} (id={user_to_modify.id})")
                else:
                    flash(f"User {user_to_modify.email} has been banned.", "warning")
                    log_event(session.get('user_id'),  # the admin who performed the action
                        'admin ban user',
                        f"Banned user {user_to_modify.email} (id={user_to_modify.id})")
            elif action == 'approve_role_change':
                user_to_modify.role = user_to_modify.pending_role
                user_to_modify.pending_role = None
                db.session.commit()
                flash(f"Role change approved for {user_to_modify.email}.", "success")
                log_event(session.get('user_id'),  # the admin who performed the action
                        'admin approved role change',
                        f"Deleted user {user_to_modify.email} (id={user_to_modify.id})")
            elif action == 'reject_role_change':
                user_to_modify.pending_role = None
                db.session.commit()
                flash(f"Role change rejected for {user_to_modify.email}.", "warning")
                log_event(session.get('user_id'),  # the admin who performed the action
                        'admin rejected role change',
                        f"Rejected user {user_to_modify.email} (id={user_to_modify.id}) request.")

        return redirect(url_for('admin'))

    users = User.query.all()
    reports = Report.query.all()
    role_requests = User.query.filter(User.pending_role.isnot(None)).all()

    return render_template('admin.html', users=users, reports=reports, role_requests=role_requests)


@click.command("reset-db")
@with_appcontext
def reset_database():
    """Drops and recreates all database tables."""
    confirm = input("⚠️ This will DROP ALL TABLES. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        print("📛 Dropping all tables...")
        db.drop_all()
        print("✅ Tables dropped.")

        print("📦 Recreating all tables...")
        db.create_all()
        print("✅ Tables recreated.")
    else:
        print("❌ Cancelled.")

app.cli.add_command(reset_database)

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
        print(var)
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
    # port=int(os.environ["DATABASE_PORT"]),
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME"],
    user=os.environ["DATABASE_USERNAME"],
    password=os.environ["DATABASE_PASSWORD"],
)
print(config.database)
pg_connector = PostgresConnector(config)

def get_db_conn():
    if "db_conn" not in g:
        g.db_conn = pg_connector.get_connection()
    return g.db_conn

@app.teardown_appcontext
def close_db_conn(exception):
    conn = g.pop("db_conn", None)
    if conn:
        # db.return_connection(conn)
        pg_connector.return_connection(conn)


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

    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.auth'))
    # return render_template("index.html", version=version)


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
            log_event(session.get('user_id'), 'security', f"Session ended due to User-Agent or IP mismatch. UA: {current_ua}, IP: {current_ip}")
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

if __name__ == "__main__":
    app.run(debug=True)
