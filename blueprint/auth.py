import os, requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import User, Profile
from extensions import db
from blueprint.decorators import login_required
from flask_wtf.csrf import generate_csrf  # Add this import

# from blueprint.models import User, Profile
# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def verify_recaptcha(token):
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': os.environ['RECAPTCHA_SECRET_KEY'],
        'response': token
    }
    response = requests.post(url, data=payload)
    result = response.json()
    return result.get('success') and result.get('score', 0) >= 0.5  # threshold adjustable


# @auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/', methods=['GET', 'POST']) 
def auth():
    mode = request.args.get('mode', 'login')
    token = request.args.get('token')
    print("auth auth\n");

    if request.method == 'POST':
        email = request.form.get('email')
        form_type = request.form.get('form_type')
        password = request.form.get('password', '').strip()

        # reCAPTCHA only for register (based on your JS)
        if form_type == 'register':
            recaptcha_token = request.form.get('g-recaptcha-response')
            if not recaptcha_token or not verify_recaptcha(recaptcha_token):
                flash("CAPTCHA verification failed.", "danger")
                return redirect(url_for('auth.auth', mode='register'))

        if form_type == 'login':
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                if not user.active:
                    return redirect(url_for('auth.auth', mode='locked'))
                session['user_id'] = user.id
                session['role'] = user.role
                session['username'] = user.email
                
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials.", "danger")

        elif form_type == 'register':
            if User.query.filter_by(email=email).first():
                flash("Email already registered.", "danger")
                return redirect(url_for('auth.auth', mode='register'))

            age = int(request.form.get('age', 0))
            if age < 18:
                flash("You must be at least 18 years old.", "danger")
                return redirect(url_for('auth.auth', mode='register'))

            gender = request.form.get('gender')
            role = request.form.get('role')
            preference = request.form.get('preference')

            new_user = User(email=email, role=role, gender=gender)
            new_user.set_password(password)
            new_user.active = True
            db.session.add(new_user)

            new_profile = Profile(
                user=new_user,
                name=email.split('@')[0],
                age=age,
                preference=preference
            )
            db.session.add(new_profile)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth.auth', mode='login'))

        elif form_type == 'reset':
            flash("Password reset link sent to your email.", "info")
            return redirect(url_for('auth.auth', mode='reset'))
	
    csrf_token = generate_csrf()  # Generate CSRF token for the form
    return render_template('auth.html', mode=mode, token=token, csrf_token=csrf_token)


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")

#         if auth_controller.authenticate(email, password):
#             # Successful login
#             return redirect(url_for("index"))
#         else:
#             flash("Invalid email or password", "danger")

#     return render_template("login.html")


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         confirm_password = request.form.get("confirm_password")

#         if password != confirm_password:
#             flash("Passwords do not match", "danger")
#             return render_template("register.html")

#         if auth_controller.register(email, password):
#             flash("Account created successfully. Please log in.", "success")
#             return redirect(url_for("login"))
#         else:
#             flash("Email already registered", "danger")

#     return render_template("register.html")
