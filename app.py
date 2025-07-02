from flask import Flask, g, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect  # Add this import at the top
from datetime import timedelta
from config.db_config import DBConfig
from db import PostgresConnector
import secrets
import os
import time
import requests
from functools import wraps
from faker import Faker
import random
import uuid
from datetime import datetime
from controllers.auth_controller import AuthController
from flask_migrate import Migrate
from flask.cli import with_appcontext

from blueprint.auth import auth_bp
from blueprint.profile import profile_bp
from blueprint.browse import browse_bp
from blueprint.booking import booking_bp
from blueprint.messaging import messaging_bp
from blueprint.payment import payment_bp

from dotenv import load_dotenv

load_dotenv()

from blueprint.models import db, User, Profile, Booking, Payment, Report

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure CSRF for local development - TEMPORARILY DISABLED FOR TESTING
app.config['WTF_CSRF_ENABLED'] = False
# Security configurations
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-development-secret-key')
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('CSRF_SECRET_KEY', 'your-csrf-secret-key')

# Disable these security measures for local development
app.config['WTF_CSRF_SSL_STRICT'] = False  # Disable HTTPS requirement
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # More lenient than 'Strict'

# Configure CSRF Protection
csrf = CSRFProtect(app)  # This initializes CSRF protection

csrf.init_app(app)

# Add CSRF token to template context
@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=generate_csrf)


# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# --- DUMMY DATA (Replaces a database for this example) ---
USERS = {
    1: {
        'username': 'seeker@example.com',
        'password': 'password123',
        'role': 'seeker',
        'active': True
    },
    2: {
        'username': 'escort@example.com',
        'password': 'password123',
        'role': 'escort',
        'active': True
    },
    3: {
        'username': 'admin@example.com',
        'password': 'password123',
        'role': 'admin',
        'active': True
    },
    # 4: {'username': 'locked@example.com', 'password': 'password123', 'role': 'seeker', 'active': False},
}


# # A simple way to get a user by username
def find_user_by_username(username):
    for user_id, user_data in USERS.items():
        if user_data['username'] == username:
            return user_id, user_data
    return None, None


# PROFILES = {
#     1: {'name': 'Alex the Seeker', 'bio': 'Looking for a good time.', 'photo': 'default.jpg'},
#     2: {'name': 'Bella the Escort', 'bio': 'Experienced and professional. Available on weekends.', 'photo': 'bella.jpg', 'availability': 'Available', 'rating': 4.8, 'age': 25},
#     3: {'name': 'Admin User', 'bio': 'System Administrator', 'photo': 'default.jpg'},
# }

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
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/test-session")
def test_session():
    return render_template("index.html")


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.auth', mode='timeout'))


app.register_blueprint(
    auth_bp)  # registers at /auth because of prefix in auth.py
app.register_blueprint(profile_bp)

app.register_blueprint(browse_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(messaging_bp)
app.register_blueprint(payment_bp)


@app.route('/profile', methods=['GET', 'POST'])
# @app.route('/auth', methods=['GET', 'POST'])

# 3. BROWSE & SEARCH
# @app.route('/browse')
# def browse():
#     # Filter profiles to only show escorts
#     escort_profiles = {uid: prof for uid, prof in PROFILES.items() if USERS[uid]['role'] == 'escort'}
#     return render_template('browse.html', profiles=escort_profiles)

# @app.route('/browse')
# @login_required
# def browse():
#     escort_profiles = Profile.query.join(User).filter(User.role == 'escort').all()
#     return render_template('browse.html', profiles=escort_profiles)

# 4. BOOKING SYSTEM
# @app.route('/booking', methods=['GET', 'POST'])
# @login_required
# def booking():
#     user_id = session['user_id']
#     role = session['role']
#     user_bookings = {}

#     if role == 'seeker':
#         user_bookings = {bid: b for bid, b in BOOKINGS.items() if b['seeker_id'] == user_id}
#     elif role == 'escort':
#         user_bookings = {bid: b for bid, b in BOOKINGS.items() if b['escort_id'] == user_id}

#     if request.method == 'POST':
#         # Simulate creating a new booking
#         if request.form.get('action') == 'create_booking':
#             flash("Booking request sent!", "success")
#         # Simulate managing a booking
#         elif request.form.get('action') == 'accept_booking':
#             booking_id = int(request.form.get('booking_id'))
#             if booking_id in BOOKINGS and BOOKINGS[booking_id]['escort_id'] == user_id:
#                 BOOKINGS[booking_id]['status'] = 'Confirmed'
#                 flash(f"Booking #{booking_id} confirmed!", "success")
#         return redirect(url_for('booking'))
#     return render_template('booking.html', bookings=user_bookings, role=role)
# @app.route('/booking', methods=['GET', 'POST'])
# @login_required
# def booking():
#     user_id = session['user_id']
#     role = session['role']
#     bookings_data = []

#     if role == 'seeker':
#         bookings_data = Booking.query.filter_by(seeker_id=user_id).order_by(Booking.booking_date.desc()).all()
#     elif role == 'escort':
#         bookings_data = Booking.query.filter_by(escort_id=user_id).order_by(Booking.booking_date.desc()).all()

#     return render_template('booking.html', bookings=bookings_data, role=role)

# 5. PAYMENT SIMULATION
# @app.route('/payment', methods=['GET', 'POST'])
# @login_required
# def payment():
#     if request.method == 'POST':
#         # Simulate payment validation
#         card_number = request.form.get('card_number')
#         if card_number and len(card_number) == 16:
#              flash("Payment successful! Transaction recorded.", "success")
#         else:
#              flash("Payment failed. Invalid card number.", "danger")
#         return redirect(url_for('1'))

#     user_payments = {pid: p for pid, p in PAYMENTS.items() if p['user_id'] == session['user_id']}
#     return render_template('payment.html', history=user_payments)


# 7. DASHBOARD (Role-Based)
# @app.route('/dashboard')
# @login_required
# def dashboard():
#     role = session.get('role')
#     user_id = session.get('user_id')

#     # Fetch data specific to the user's role
#     if role == 'seeker':
#         data = {'upcoming_bookings': {bid: b for bid, b in BOOKINGS.items() if b['seeker_id'] == user_id}}
#     elif role == 'escort':
#         data = {'booking_requests': {bid: b for bid, b in BOOKINGS.items() if b['escort_id'] == user_id and b['status'] == 'Pending'}}
#     elif role == 'admin':
#         data = {'system_stats': {'total_users': len(USERS), 'total_reports': len(REPORTS)}}
#     else:
#         # Should not happen if logic is correct
#         return "Error: Unknown role.", 403

#     return render_template('dashboard.html', role=role, data=data)
@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    user_id = session.get('user_id')
    data = {}

    if role == 'seeker':
        data['upcoming_bookings_count'] = Booking.query.filter_by(
            seeker_id=user_id, status='Confirmed').count()
    elif role == 'escort':
        data['booking_requests_count'] = Booking.query.filter_by(
            escort_id=user_id, status='Pending').count()
    elif role == 'admin':
        data['total_users'] = User.query.count()
        data['total_reports'] = Report.query.filter_by(
            status='Pending Review').count()

    return render_template('dashboard.html', role=role, data=data)


# # 8. ADMIN PANEL
# @app.route('/admin', methods=['GET', 'POST'])
# @role_required('admin')
# def admin():
#     if request.method == 'POST':
#         action = request.form.get('action')
#         user_id_to_modify = int(request.form.get('user_id'))
#         if action == 'delete_user':
#             if user_id_to_modify in USERS:
#                 del USERS[user_id_to_modify]
#                 if user_id_to_modify in PROFILES:
#                     del PROFILES[user_id_to_modify]
#                 flash(f"User #{user_id_to_modify} has been deleted.", "success")
#         return redirect(url_for('admin'))

#     return render_template('admin.html', users=USERS, reports=REPORTS)


@app.route('/admin', methods=['GET', 'POST'])
@role_required('admin')
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        user_id_to_modify = int(request.form.get('user_id'))
        user_to_modify = User.query.get(user_id_to_modify)
        if user_to_modify:
            if action == 'delete_user':
                db.session.delete(user_to_modify)
                db.session.commit()
                flash(f"User {user_to_modify.email} has been deleted.",
                      "success")
            elif action == 'toggle_ban':
                user_to_modify.active = not user_to_modify.active
                db.session.commit()
                status = "unbanned" if user_to_modify.active else "banned"
                flash(f"User {user_to_modify.email} has been {status}.",
                      "success")
        return redirect(url_for('admin'))

    users = User.query.all()
    reports = Report.query.all()
    return render_template('admin.html', users=users, reports=reports)


# --- Add a command to seed the database ---
@app.cli.command("seed")
@with_appcontext
def seed_database():
    """Seeds the database with realistic mock data."""
    print("Seeding database...")
    faker = Faker()

    # 1. Clean up existing data
    print("-> Deleting existing data...")
    db.session.query(Report).delete()
    db.session.query(Payment).delete()
    db.session.query(Booking).delete()
    db.session.query(Profile).delete()
    db.session.query(User).delete()
    db.session.commit()

    # 2. Create Users and Profiles
    print("-> Creating users and profiles...")
    seekers = []
    escorts = []

    for _ in range(20):
        user = User(email=faker.unique.email(), role='seeker', active=True,
                    gender=random.choice(['Male', 'Female', 'Non-binary']))
        user.set_password('password123')
        profile = Profile(user=user, name=faker.name(), bio=faker.paragraph(nb_sentences=3))
        db.session.add(user)
        seekers.append(user)

    for _ in range(10):
        user = User(email=faker.unique.email(), role='escort', active=True,
                    gender=random.choice(['Male', 'Female', 'Non-binary']))
        user.set_password('password123')
        profile = Profile(user=user,
                          name=faker.name(),
                          bio=faker.paragraph(nb_sentences=5),
                          rating=round(random.uniform(3.5, 5.0), 1),
                          age=random.randint(19, 35))
        db.session.add(user)
        escorts.append(user)

    admin_user = User(email='admin@example.com', role='admin', active=True, gender="male")
    admin_user.set_password('password123')
    admin_profile = Profile(user=admin_user, name='Admin User')

    seeker_user = User(email='seeker@example.com', role='seeker', active=True, gender="male")
    seeker_user.set_password('password123')
    seeker_profile = Profile(user=seeker_user, name='Alex the Seeker')

    escort_user = User(email='escort@example.com', role='escort', active=True, gender="male")
    escort_user.set_password('password123')
    escort_profile = Profile(user=escort_user,
                             name='Bella the Escort',
                             bio='Experienced and professional.',
                             rating=4.8,
                             age=25)

    db.session.add_all([admin_user, seeker_user, escort_user])
    db.session.commit()

    print(f"   - Created {len(seekers)} seekers, {len(escorts)} escorts, and 3 test users.")

    # 3. Create Bookings with start_time and end_time
    print("-> Creating bookings...")
    booking_statuses = ['Pending', 'Confirmed', 'Rejected', 'Completed']
    for _ in range(30):
        seeker = random.choice(seekers)
        escort = random.choice(escorts)
        start_dt = datetime.utcnow() + timedelta(days=random.randint(1, 10), hours=random.randint(0, 23))
        duration = random.choice([30, 60, 90])
        end_dt = start_dt + timedelta(minutes=duration)

        booking = Booking(
            seeker_id=seeker.id,
            escort_id=escort.id,
            start_time=start_dt,
            end_time=end_dt,
            status=random.choice(booking_statuses)
        )
        db.session.add(booking)
    print("   - Created 30 bookings.")

    # 4. Create Payments
    print("-> Creating payments...")
    for _ in range(50):
        payment = Payment(
            user_id=random.choice(seekers).id,
            amount=round(random.uniform(50.0, 500.0), 2),
            transaction_id=str(uuid.uuid4()),
            created_at=faker.date_time_between(start_date='-1y', end_date='now')
        )
        db.session.add(payment)
    print("   - Created 50 payments.")

    # 5. Create Reports
    print("-> Creating reports...")
    all_users = seekers + escorts
    for _ in range(5):
        reporter = random.choice(all_users)
        reported = random.choice(all_users)
        while reporter.id == reported.id:
            reported = random.choice(all_users)

        report = Report(
            reporter_id=reporter.id,
            reported_id=reported.id,
            reason=faker.sentence(),
            status=random.choice(['Pending Review', 'Resolved'])
        )
        db.session.add(report)
    print("   - Created 5 reports.")

    db.session.commit()

    print("\n✅ Database seeding complete!")
    print("Test login accounts (password: 'password123'):")
    print("  - Admin:   admin@example.com")
    print("  - Seeker:  seeker@example.com")
    print("  - Escort:  escort@example.com")

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

# Authentication controller
auth_controller = AuthController()


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if auth_controller.authenticate(email, password):
            # Successful login
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        if auth_controller.register(email, password):
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Email already registered", "danger")

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
