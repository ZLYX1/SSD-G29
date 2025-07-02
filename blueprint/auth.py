import os, requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import User, Profile
from extensions import db
from blueprint.decorators import login_required
from flask_wtf.csrf import generate_csrf  # Add this import
from utils.utils import send_verification_email, verify_email_token  # Import email verification functions

# from blueprint.models import User, Profile
# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def verify_recaptcha(token):
    # For development/testing, bypass reCAPTCHA if using test keys
    recaptcha_secret = os.environ.get('RECAPTCHA_SECRET_KEY', '')
    
    # Skip reCAPTCHA verification in development mode
    if recaptcha_secret == 'test_secret_key_for_development':
        print("🔧 Development Mode: Bypassing reCAPTCHA verification")
        return True
    
    # Production reCAPTCHA verification
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': recaptcha_secret,
        'response': token
    }
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        return result.get('success') and result.get('score', 0) >= 0.5  # threshold adjustable
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        # In development, allow registration to proceed if reCAPTCHA fails
        if os.environ.get('FLASK_ENV') == 'development':
            return True
        return False


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
                
                # Check if email is verified
                if not user.email_verified:
                    flash("Please verify your email address before logging in. Check your inbox for the verification link.", "warning")
                    return redirect(url_for('auth.auth', mode='login'))
                
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
            new_user.email_verified = False  # Start with unverified email
            db.session.add(new_user)

            new_profile = Profile(
                user=new_user,
                name=email.split('@')[0],
                age=age,
                preference=preference
            )
            db.session.add(new_profile)
            db.session.commit()

            # Send verification email
            if send_verification_email(new_user):
                flash("Registration successful! Please check your email to verify your account before logging in.", "success")
            else:
                flash("Registration successful, but there was an issue sending the verification email. Please contact support.", "warning")
            
            return redirect(url_for('auth.auth', mode='login'))

        elif form_type == 'reset':
            flash("Password reset link sent to your email.", "info")
            return redirect(url_for('auth.auth', mode='reset'))
	
    csrf_token = generate_csrf()  # Generate CSRF token for the form
    recaptcha_site_key = os.environ.get('RECAPTCHA_SITE_KEY', 'test_site_key_for_development')
    return render_template('auth.html', mode=mode, token=token, csrf_token=csrf_token, recaptcha_site_key=recaptcha_site_key)


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Handle email verification"""
    user, message = verify_email_token(token)
    
    if user:
        if "successfully" in message:
            flash("Email verified successfully! You can now log in.", "success")
        else:
            flash(message, "info")
    else:
        flash(message, "danger")
    
    return redirect(url_for('auth.auth', mode='login'))


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification for a user"""
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash("No account found with that email address.", "danger")
        return redirect(url_for('auth.auth', mode='login'))
    
    if user.email_verified:
        flash("Email is already verified.", "info")
        return redirect(url_for('auth.auth', mode='login'))
    
    if send_verification_email(user):
        flash("Verification email sent! Please check your inbox.", "success")
    else:
        flash("Failed to send verification email. Please try again later.", "danger")
    
    return redirect(url_for('auth.auth', mode='login'))


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
