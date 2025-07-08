# utils.py
import smtplib
import secrets
import datetime
import random
import re
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for, current_app
from blueprint.models import User, db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def send_verification_email(user):
    """Send email verification link to user"""
    try:
        # Generate verification token
        token = generate_verification_token()
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        
        # Update user with verification token
        user.email_verification_token = token
        user.email_verification_token_expires = expires_at
        db.session.commit()
        
        # Create verification URL
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        
        # Email content
        subject = "Verify Your Email Address"
        body = f"""
        Hello,
        
        Please click the link below to verify your email address:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        Safe Companion Team
        """
        
        # For development, print the verification URL to console
        if current_app.config.get('FLASK_ENV') == 'development':
            print(f"\n{'='*50}")
            print(f"EMAIL VERIFICATION FOR: {user.email}")
            print(f"Verification URL: {verification_url}")
            print(f"Token expires: {expires_at}")
            print(f"{'='*50}\n")
        else:
            # Production: Send actual email
            email_sent = send_email(user.email, subject, body)
            if not email_sent:
                print(f"Failed to send verification email to {user.email}")
                return False
            print(f"Verification email sent to {user.email}")
        
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def verify_email_token(token):
    """Verify email verification token and activate user account"""
    try:
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            return None, "Invalid verification token"
        
        if user.email_verification_token_expires < datetime.datetime.utcnow():
            return None, "Verification token has expired"
        
        if user.email_verified:
            return user, "Email already verified"
        
        # Mark email as verified
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_token_expires = None
        db.session.commit()
        
        return user, "Email verified successfully"
    
    except Exception as e:
        print(f"Error verifying email token: {e}")
        return None, "Verification failed"


def send_reset_email(user):
    """Send password reset email (placeholder)"""
    # Implementation for password reset
    pass


def verify_reset_token(token):
    """Verify password reset token (placeholder)"""
    # Implementation for password reset verification
    pass


def verify_captcha(response):
    """Verify CAPTCHA response (placeholder)"""
    # Implementation for CAPTCHA verification
    pass


def send_email(to_email, subject, body):
    """
    Send email using SMTP (for production use)
    This is a placeholder implementation
    """
    try:
        # Configure your SMTP settings - USE ENVIRONMENT VARIABLES IN PRODUCTION
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', 'your-email@gmail.com')
        smtp_password = os.getenv('SMTP_PASSWORD', 'your-app-password')
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def generate_otp():
    """Generate a 6-digit OTP code"""
    return f"{random.randint(100000, 999999)}"


def validate_phone_number(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    if len(phone_digits) < 10 or len(phone_digits) > 15:
        return False, "Phone number must be between 10-15 digits"
    
    # Basic format validation - must start with country code or local format
    if len(phone_digits) == 10:  # US format without country code
        return True, f"+1{phone_digits}"
    elif len(phone_digits) == 11 and phone_digits.startswith('1'):  # US format with country code
        return True, f"+{phone_digits}"
    elif len(phone_digits) >= 10:  # International format
        return True, f"+{phone_digits}"
    
    return False, "Invalid phone number format"


def send_otp_sms(user, otp_code):
    """Send OTP code via SMS (development version)"""
    try:
        # Generate OTP and set expiration (5 minutes)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        
        # Update user with OTP details
        user.otp_code = otp_code
        user.otp_expires = expires_at
        user.otp_attempts = 0
        db.session.commit()
        
        # For development, print the OTP to console
        import sys
        print(f"\n{'='*50}")
        print(f"📱 SMS OTP VERIFICATION")
        print(f"Phone: {user.phone_number}")
        print(f"OTP Code: {otp_code}")
        print(f"Expires: {expires_at}")
        print(f"{'='*50}\n")
        sys.stdout.flush()  # Force flush output buffer
        
        # In production, you would integrate with SMS service like Twilio:
        # send_sms_via_twilio(user.phone_number, f"Your verification code is: {otp_code}")
        
        return True
    except Exception as e:
        print(f"Error sending OTP SMS: {e}")
        import sys
        sys.stdout.flush()
        return False


def verify_otp_code(user, submitted_otp):
    """Verify submitted OTP code"""
    try:
        # Check if OTP exists
        if not user.otp_code:
            return False, "No OTP code found. Please request a new code."
        
        # Check if OTP has expired
        if user.otp_expires < datetime.datetime.utcnow():
            return False, "OTP code has expired. Please request a new code."
        
        # Check attempt limit (max 3 attempts)
        if user.otp_attempts >= 3:
            return False, "Too many failed attempts. Please request a new code."
        
        # Verify the OTP code
        if user.otp_code == submitted_otp:
            # Mark phone as verified
            user.phone_verified = True
            user.otp_code = None
            user.otp_expires = None
            user.otp_attempts = 0
            db.session.commit()
            return True, "Phone number verified successfully!"
        else:
            # Increment failed attempts
            user.otp_attempts += 1
            db.session.commit()
            attempts_left = 3 - user.otp_attempts
            return False, f"Invalid OTP code. {attempts_left} attempts remaining."
    
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return False, "OTP verification failed. Please try again."


def resend_otp(user):
    """Resend OTP code to user"""
    try:
        # Generate new OTP
        new_otp = generate_otp()
        print(f"🔧 DEBUG: Resending OTP - Generated new OTP: {new_otp} for user: {user.email}")
        
        # Send new OTP
        if send_otp_sms(user, new_otp):
            print(f"🔧 DEBUG: Resend OTP successful for {user.email}")
            return True, "New OTP code sent to your phone."
        else:
            print(f"🔧 DEBUG: Resend OTP failed for {user.email}")
            return False, "Failed to send OTP. Please try again later."
    except Exception as e:
        print(f"Error resending OTP: {e}")
        import sys
        sys.stdout.flush()
        return False, "Failed to resend OTP."


def send_sms_via_twilio(phone_number, message):
    """
    Send SMS using Twilio (for production use)
    This is a placeholder implementation
    """
    try:
        # Configure Twilio settings
        # account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        # from_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_=from_number,
        #     to=phone_number
        # )
        
        print(f"📱 SMS would be sent to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False


# Password Security Functions

def validate_password_strength(password):
    """
    Validate password strength according to security requirements
    
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter  
    - Contains at least one digit
    - Contains at least one special character
    - Not a common password
    
    Returns:
        dict: {'valid': bool, 'message': str, 'score': int}
    """
    import string
    
    errors = []
    score = 0
    
    # Check length
    if len(password) < 8:
        errors.append("at least 8 characters")
    elif len(password) >= 12:
        score += 2
    else:
        score += 1
    
    # Check for uppercase
    if not any(c.isupper() for c in password):
        errors.append("at least one uppercase letter")
    else:
        score += 1
    
    # Check for lowercase
    if not any(c.islower() for c in password):
        errors.append("at least one lowercase letter")
    else:
        score += 1
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        errors.append("at least one number")
    else:
        score += 1
    
    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
    else:
        score += 1
    
    # Check for common passwords
    common_passwords = [
        'password', 'password123', '123456', '123456789', 'qwerty',
        'abc123', 'password1', 'admin', 'letmein', 'welcome',
        'monkey', '1234567890', 'dragon', '123123', 'football'
    ]
    
    if password.lower() in common_passwords:
        errors.append("cannot be a common password")
        score = 0
    
    # Check for sequential characters
    sequential_patterns = ['123', 'abc', 'qwe', 'asd', 'zxc']
    if any(pattern in password.lower() for pattern in sequential_patterns):
        score -= 1
    
    # Check for repeated characters
    if len(set(password)) < len(password) * 0.6:  # More than 40% repeated chars
        score -= 1
    
    valid = len(errors) == 0
    
    if valid:
        if score >= 6:
            strength = "Very Strong"
        elif score >= 4:
            strength = "Strong"
        elif score >= 3:
            strength = "Moderate"
        else:
            strength = "Weak"
        message = f"Password strength: {strength}"
    else:
        message = "Password must contain " + ", ".join(errors)
    
    return {
        'valid': valid,
        'message': message,
        'score': max(0, score),
        'strength': strength if valid else "Invalid"
    }


def check_password_expiration_status(user):
    """
    Check password expiration status and return appropriate messages
    
    Returns:
        dict: {
            'expired': bool,
            'expires_soon': bool, 
            'days_left': int or None,
            'message': str,
            'action_required': bool
        }
    """
    if not user.password_expires_at:
        return {
            'expired': False,
            'expires_soon': False,
            'days_left': None,
            'message': "Password does not expire",
            'action_required': False
        }
    
    days_left = user.days_until_password_expires()
    expired = user.is_password_expired()
    expires_soon = days_left is not None and days_left <= 7
    
    if expired:
        message = "Password has expired and must be changed"
        action_required = True
    elif expires_soon:
        message = f"Password expires in {days_left} days"
        action_required = days_left <= 3
    else:
        message = f"Password expires in {days_left} days"
        action_required = False
    
    return {
        'expired': expired,
        'expires_soon': expires_soon,
        'days_left': days_left,
        'message': message,
        'action_required': action_required
    }
