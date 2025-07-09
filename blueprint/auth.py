import os, requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import User, Profile
from extensions import db
from blueprint.decorators import login_required
from blueprint.audit_log import log_event
from utils.utils import send_verification_email, verify_email_token, generate_otp, validate_phone_number, send_otp_sms, verify_otp_code, resend_otp, validate_password_strength  # Import OTP and password functions
from flask_wtf.csrf import generate_csrf  # Add this import

import boto3
from botocore.exceptions import ClientError
from flask import current_app
# from app.email_utils import send_email_ses


# from blueprint.models import User, Profile
# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def verify_recaptcha(token):
    """Verify reCAPTCHA token. Returns True in development if no secret key is set."""
    recaptcha_secret = os.environ.get('RECAPTCHA_SECRET_KEY')
    
    # For development: if no secret key is set, skip verification
    if not recaptcha_secret:
        print("⚠️  WARNING: RECAPTCHA_SECRET_KEY not set - skipping reCAPTCHA verification (development mode)")
        return True
    
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
        print(f"❌ reCAPTCHA verification error: {e}")
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
           ''' recaptcha_token = request.form.get('g-recaptcha-response')
            if not recaptcha_token or not verify_recaptcha(recaptcha_token):
                flash("CAPTCHA verification failed.", "danger")
                return redirect(url_for('auth.auth', mode='register'))'''

        if form_type == 'login':
            user = User.query.filter_by(email=email).first()
            print("Submitted for login\n");
            if user:
                # Check if user has been soft deleted
                if user.deleted:
                    flash("This account is no longer available.", "danger")
                    return redirect(url_for('auth.auth', mode='login'))
                
                # Check if account is locked
                if user.is_account_locked():
                    flash("Account is temporarily locked due to too many failed login attempts. Please try again later.", "danger")
                    return redirect(url_for('auth.auth', mode='login'))
                
                if not user.activate:
                    flash("This account has been deactivated by the user.", "danger")
                    return redirect(url_for('auth.auth', mode='login'))
                
                # Check password
                if user.check_password(password):
                    # Reset failed login attempts on successful login
                    user.reset_failed_logins()
                    
                    if not user.active:
                        db.session.commit()  # Save reset of failed logins
                        return redirect(url_for('auth.auth', mode='locked'))
                    
                    # Check if password has expired
                    if user.is_password_expired() or user.password_change_required:
                        db.session.commit()  # Save reset of failed logins
                        flash("Your password has expired. Please change your password to continue.", "warning")
                        return redirect(url_for('auth.change_password', user_id=user.id, force=True))
                    
                    # Check if password expires soon (within 7 days)
                    days_left = user.days_until_password_expires()
                    if days_left is not None and days_left <= 7:
                        flash(f"Your password will expire in {days_left} days. Consider changing it soon.", "info")
                    
                    # Check if phone is verified (OTP System) - COMMENTED OUT FOR EMAIL-ONLY
                    '''
                    if not user.phone_verified:
                        db.session.commit()  # Save reset of failed logins
                        flash("Please verify your phone number first. Complete the phone verification process.", "warning")
                        return redirect(url_for('auth.verify_phone', user_id=user.id))
                    '''
                    
                    # Check if email is verified
                    if not user.email_verified:
                        db.session.commit()  # Save reset of failed logins
                        flash("Please verify your email address before logging in. Check your inbox for the verification link.", "warning")
                        return redirect(url_for('auth.auth', mode='login'))
                    
                    # Successful login
                    db.session.commit()  # Save reset of failed logins
                    session['user_id'] = user.id
                    session['role'] = user.role
                    session['username'] = user.email
                    log_event(user.id, 'login success', f"User {user.email} logged in successfully.")
                    
                    return redirect(url_for('dashboard'))
                else:
                    # Failed login - increment counter and potentially lock account
                    lockout_message = user.increment_failed_login()
                    db.session.commit()
                    flash(lockout_message, "danger")
                    log_event(user.id, 'login failed', f"User {user.email} failed to log in: {lockout_message}")
            else:
                flash("Invalid credentials.", "danger")

        elif form_type == 'register':
            print("🔧 DEBUG: Registration form submitted")

            # Get confirm password field
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validate password confirmation
            if password != confirm_password:
                flash("Passwords do not match. Please try again.", "danger")
                return redirect(url_for('auth.auth', mode='register'))

            recaptcha_token = request.form.get('g-recaptcha-response')
            print(f"🔧 DEBUG: reCAPTCHA token received: {bool(recaptcha_token)}")
            
            if not recaptcha_token:
                print("❌ DEBUG: No reCAPTCHA token provided")
                flash("CAPTCHA verification failed.", "danger")
                return redirect(url_for('auth.auth', mode='register'))
            
            # Verify the CAPTCHA token with Google
            recaptcha_result = verify_recaptcha(recaptcha_token)
            print(f"🔧 DEBUG: reCAPTCHA verification result: {recaptcha_result}")
            
            if not recaptcha_result:
                print("❌ DEBUG: reCAPTCHA verification failed")
                flash("CAPTCHA verification failed. Please try again.", "danger")
                return redirect(url_for('auth.auth', mode='register'))

            print("✅ DEBUG: reCAPTCHA verification passed")

            if User.query.filter_by(email=email).first():
                print(f"❌ DEBUG: Email {email} already registered")
                flash("Email already registered.", "danger")
                return redirect(url_for('auth.auth', mode='register'))

            print(f"✅ DEBUG: Email {email} is available for registration")

            age = int(request.form.get('age', 0))
            if age < 18:
                flash("You must be at least 18 years old.", "danger")
                return redirect(url_for('auth.auth', mode='register'))

            # UPDATED: Skip phone verification, use email verification only
            gender = request.form.get('gender')
            role = request.form.get('role')
            preference = request.form.get('preference')

            # Create user but don't activate yet (pending email verification)
            new_user = User(email=email, role=role, gender=gender)
            
            # Set password with history checking disabled for new users
            success, message = new_user.set_password(password, check_history=False, password_expiry_days=90)
            if not success:
                flash(f"Password error: {message}", "danger")
                return redirect(url_for('auth.auth', mode='register'))
            
            # Skip phone verification - set as verified by default
            new_user.phone_number = None  # No phone number required
            new_user.active = False  # Will be activated after email verification
            new_user.email_verified = False  # Requires email verification
            new_user.phone_verified = True  # Skip phone verification
            db.session.add(new_user)

            new_profile = Profile(
                user=new_user,
                name=email.split('@')[0],
                age=age,
                preference=preference
            )
            db.session.add(new_profile)
            db.session.commit()

            # Send email verification to user's email address using AWS SES
            print(f"🔧 DEBUG: Sending email verification to: {new_user.email}")
            
            email_sent = send_verification_email_ses(new_user)
            print(f"🔧 DEBUG: Email sending result: {email_sent}")
            
            if email_sent:
                print(f"✅ DEBUG: Email verification sent successfully to {new_user.email}")
                success_message = f"Registration successful! Please check your email ({new_user.email}) for a verification link."
                print(f"🔧 DEBUG: Flashing success message: {success_message}")
                flash(success_message, "success")
                return redirect(url_for('auth.auth', mode='login'))
            else:
                print(f"❌ DEBUG: Failed to send email verification to {new_user.email}")
                warning_message = "Registration successful, but there was an issue sending the verification email. Please contact support."
                print(f"🔧 DEBUG: Flashing warning message: {warning_message}")
                flash(warning_message, "warning")
                return redirect(url_for('auth.auth', mode='register'))

        elif form_type == 'reset':
            flash("Password reset link sent to your email.", "info")
            return redirect(url_for('auth.auth', mode='reset'))

    csrf_token = generate_csrf()  # Generate CSRF token for the form
    # Note: sitekey is now provided by global context processor in app.py
    return render_template('auth.html', mode=mode, token=token, csrf_token=csrf_token)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Handle email verification and activate user account"""
    user, message = verify_email_token(token)
    
    if user:
        if "successfully" in message:
            # Since we're skipping phone verification, activate the user account
            user.active = True
            db.session.commit()
            flash("Email verified successfully! Your account is now active. You can now log in.", "success")
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
    
    if send_verification_email_ses(user):
        flash("Verification email sent! Please check your inbox.", "success")
    else:
        flash("Failed to send verification email. Please try again later.", "danger")
    
    return redirect(url_for('auth.auth', mode='login'))


@auth_bp.route('/verify-phone/<int:user_id>', methods=['GET', 'POST'])
def verify_phone(user_id):
    """Handle phone verification with OTP"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        submitted_otp = request.form.get('otp_code', '').strip()
        
        if not submitted_otp:
            flash("Please enter the OTP code.", "danger")
            return render_template('phone_verification.html', user=user)
        
        # Verify OTP
        success, message = verify_otp_code(user, submitted_otp)
        
        if success:
            # Phone verified successfully - now activate account and send email verification
            user.active = True
            db.session.commit()
            
            # Send email verification
            if send_verification_email(user):
                flash("Phone verified successfully! Please check your email to complete account verification.", "success")
            else:
                flash("Phone verified successfully! However, there was an issue sending the email verification. Please contact support.", "warning")
            
            return redirect(url_for('auth.auth', mode='login'))
        else:
            flash(message, "danger")
    
    return render_template('phone_verification.html', user=user)


@auth_bp.route('/resend-otp/<int:user_id>', methods=['POST'])
def resend_otp_code(user_id):
    """Resend OTP code to user's phone"""
    print(f"🔧 DEBUG: Resend OTP request for user_id: {user_id}")
    user = User.query.get_or_404(user_id)
    print(f"🔧 DEBUG: Found user: {user.email}, phone: {user.phone_number}")
    
    # Check if user is still eligible for OTP
    if user.phone_verified:
        print(f"🔧 DEBUG: User {user.email} phone already verified")
        flash("Phone number is already verified.", "info")
        return redirect(url_for('auth.auth', mode='login'))
    
    print(f"🔧 DEBUG: Calling resend_otp for user: {user.email}")
    success, message = resend_otp(user)
    print(f"🔧 DEBUG: Resend result - Success: {success}, Message: {message}")
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for('auth.verify_phone', user_id=user_id))


@auth_bp.route('/change-password/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    """Allow user to change their password"""
    user = User.query.get_or_404(user_id)
    force_change = request.args.get('force', 'false').lower() == 'true'
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate inputs
        if not all([current_password, new_password, confirm_password]):
            flash("All fields are required.", "danger")
            return render_template('change_password.html', user=user, force_change=force_change)
        
        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return render_template('change_password.html', user=user, force_change=force_change)
        
        # Verify current password (skip if forced change due to expiration)
        if not force_change and not user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return render_template('change_password.html', user=user, force_change=force_change)
        
        # Validate new password strength
        validation_result = validate_password_strength(new_password)
        if not validation_result['valid']:
            flash(f"Password requirements not met: {validation_result['message']}", "danger")
            return render_template('change_password.html', user=user, force_change=force_change)
        
        # Set new password with history checking
        success, message = user.set_password(new_password, check_history=True, password_expiry_days=90)
        
        if success:
            db.session.commit()
            flash("Password changed successfully.", "success")
            log_event(user.id, 'password_change', f"User {user.email} changed their password successfully.")
            
            # If this was a forced change, redirect to login
            if force_change:
                session.pop('user_id', None)
                flash("Please log in with your new password.", "info")
                return redirect(url_for('auth.auth', mode='login'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash(message, "danger")
            log_event(user.id, 'password_change_failed', f"User {user.email} failed to change their password: {message}")
            return render_template('change_password.html', user=user, force_change=force_change)
    
    return render_template('change_password.html', user=user, force_change=force_change)


@auth_bp.route('/password-policy')
def password_policy():
    """Display password policy information"""
    return render_template('password_policy.html') 

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




# AWS SES

def send_email_ses(to_email, subject, body_text, body_html=None):
    SENDER = "Your Name <13eddie07@gmail.com>"
    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name="us-east-1")  # Replace with your SES region

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [to_email],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html or body_text,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        current_app.logger.error(f"SES Error: {e.response['Error']['Message']}")
        return False
    else:
        return True
   

def send_verification_email_ses(user):
    """Send email verification using AWS SES"""
    try:
        # Use the existing utility function for consistency
        from utils.utils import send_verification_email
        
        # Call the utility function which handles token generation and saving
        success = send_verification_email(user)
        if not success:
            return False
        
        # Get the token that was just generated and saved
        token = user.email_verification_token
        
        # Create verification URL
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        
        # Email content
        subject = "Verify Your Email Address - Safe Companion"
        body_text = f"""
Hello,

Welcome to Safe Companion! Please click the link below to verify your email address:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Safe Companion Team
        """
        
        body_html = f"""
<html>
<head></head>
<body>
    <h2>Welcome to Safe Companion!</h2>
    <p>Hello,</p>
    <p>Please click the link below to verify your email address:</p>
    <p><a href="{verification_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email Address</a></p>
    <p>Or copy and paste this link into your browser:</p>
    <p>{verification_url}</p>
    <p>This link will expire in 24 hours.</p>
    <p>If you didn't create an account, please ignore this email.</p>
    <p>Best regards,<br>Safe Companion Team</p>
</body>
</html>
        """
        
        # Send email using AWS SES to the user's email address
        success = send_email_ses(user.email, subject, body_text, body_html)
        
        if success:
            print(f"✅ Email verification sent successfully to {user.email}")
            print(f"📧 Verification URL: {verification_url}")
            return True
        else:
            print(f"❌ Failed to send email verification to {user.email}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending verification email: {e}")
        return False