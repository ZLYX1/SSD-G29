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
        
        # For development, just print the verification URL
        print(f"\n{'='*50}")
        print(f"EMAIL VERIFICATION FOR: {user.email}")
        print(f"Verification URL: {verification_url}")
        print(f"Token expires: {expires_at}")
        print(f"{'='*50}\n")
        
        # In production, you would send actual email here:
        # send_email(user.email, subject, body)
        
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
    """Send password reset email with secure token"""
    try:
        # Generate secure reset token
        reset_token = generate_verification_token()  # Reuse secure token generation
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1 hour expiry for security
        
        # Update user with reset token
        user.password_reset_token = reset_token
        user.password_reset_token_expires = expires_at
        db.session.commit()
        
        # Create reset URL
        reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
        
        # Email content
        subject = "Password Reset Request - Safe Companion"
        body_text = f"""
Hello,

We received a request to reset the password for your Safe Companion account. If you made this request, please click the link below to reset your password:

{reset_url}

IMPORTANT SECURITY INFORMATION:
- This link will expire in 1 hour for security reasons
- If you didn't request this password reset, please ignore this email
- Never share this link with anyone
- Contact support if you suspect unauthorized access

For security purposes, this password reset link can only be used once and will expire automatically.

Best regards,
Safe Companion Team
        """
        
        # Load HTML template
        try:
            with open('templates/emails/password_reset_email.html', 'r') as f:
                html_template = f.read()
            body_html = html_template.replace('{{reset_url}}', reset_url)
        except:
            body_html = None
        
        # For development, print the reset URL
        print(f"\n{'='*60}")
        print(f"PASSWORD RESET REQUEST FOR: {user.email}")
        print(f"Reset URL: {reset_url}")
        print(f"Token expires: {expires_at}")
        print(f"{'='*60}\n")
        
        # In production, send actual email here
        # For now, we'll use the same email function as verification
        from flask import current_app
        try:
            # Try to use SES if available
            from blueprint.auth import send_email_ses
            success = send_email_ses(user.email, subject, body_text, body_html)
            if success:
                return True
        except:
            pass
        
        # Fallback to console output for development
        print("📧 Password reset email would be sent via email system")
        return True
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def verify_reset_token(token):
    """Verify password reset token and return user if valid"""
    try:
        if not token:
            return None, "Invalid reset token"
        
        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            return None, "Invalid or expired reset token"
        
        if user.password_reset_token_expires < datetime.datetime.utcnow():
            # Clean up expired token
            user.password_reset_token = None
            user.password_reset_token_expires = None
            db.session.commit()
            return None, "Reset token has expired"
        
        return user, "Token is valid"
    
    except Exception as e:
        print(f"Error verifying reset token: {e}")
        return None, "Token verification failed"


def consume_reset_token(user):
    """Consume/invalidate a reset token after successful password change"""
    try:
        user.password_reset_token = None
        user.password_reset_token_expires = None
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error consuming reset token: {e}")
        return False


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
        # Configure your SMTP settings - ALL VALUES MUST BE IN ENVIRONMENT VARIABLES
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        # Validate SMTP configuration
        if not all([smtp_server, smtp_username, smtp_password]):
            print("❌ WARNING: SMTP not configured. Email functionality disabled.")
            print("Set SMTP_SERVER, SMTP_USERNAME, and SMTP_PASSWORD environment variables.")
            return False
        
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
        
        # Send new OTP
        if send_otp_sms(user, new_otp):
            return True, "New OTP code sent to your phone."
        else:
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
    Validate password strength based on NIST guidelines (SP 800-63B)
    NIST recommendations focus on length and avoiding compromised passwords
    rather than complex character requirements.
    
    Key NIST principles:
    - Length is more important than complexity
    - 8-64 character range
    - Avoid common/compromised passwords
    - No forced composition rules (upper, lower, special chars)
    
    Returns:
        dict: {'valid': bool, 'message': str, 'score': int, 'strength': str}
    """
    import string
    
    errors = []
    score = 0
    
    # NIST Requirement 1: Length between 8-64 characters
    if len(password) < 8:
        errors.append("at least 8 characters")
    elif len(password) > 64:
        errors.append("no more than 64 characters")
    else:
        # Score based on length (NIST emphasizes length over complexity)
        if len(password) >= 20:
            score += 5  # Excellent length
        elif len(password) >= 15:
            score += 4  # Very good length
        elif len(password) >= 12:
            score += 3  # Good length
        elif len(password) >= 10:
            score += 2  # Acceptable length
        else:
            score += 1  # Minimum acceptable
    
    # NIST Requirement 2: Check against common/compromised passwords
    # Extended list of common passwords and patterns
    common_passwords = [
        'password', 'password123', '123456', '123456789', 'qwerty',
        'abc123', 'password1', 'admin', 'letmein', 'welcome',
        'monkey', '1234567890', 'dragon', '123123', 'football',
        'baseball', 'master', 'shadow', 'michael', 'jordan',
        'superman', 'batman', 'trustno1', 'hello', 'freedom',
        'whatever', 'ninja', 'mustang', 'access', 'maggie',
        'starwars', 'tiger', 'internet', 'service', 'banana',
        'orange', 'cheese', 'secret', 'passw0rd', 'password!',
        'Password1', 'Password123', 'Password!', 'Passw0rd',
        'qwertyuiop', 'asdfghjkl', 'zxcvbnm', '1q2w3e4r',
        'iloveyou', '000000', '111111', '222222', '333333'
    ]
    
    # Check exact matches and close variants of common passwords
    password_lower = password.lower()
    for common in common_passwords:
        # Only flag if it's an exact match or starts with common password
        # But avoid false positives for longer unique passwords
        if (password_lower == common.lower() or 
            (password_lower.startswith(common.lower()) and len(password) <= len(common) + 3)):
            errors.append("cannot be a commonly used password")
            score = 0
            break
    
    # Check for simple sequential patterns (NIST discourages predictable patterns)
    sequential_patterns = [
        '123456', '654321', 'abcdef', 'fedcba', 'qwerty', 'asdfgh',
        'zxcvbn', '098765', '987654', 'mnbvcx', 'poiuyt', 'lkjhgf'
    ]
    for pattern in sequential_patterns:
        if len(pattern) >= 6 and pattern in password.lower():
            errors.append("cannot contain common sequential patterns")
            score = max(0, score - 2)
            break
    
    # Check for excessive character repetition (adjusted for real-world use)
    if len(password) > 0:
        char_counts = {}
        for char in password.lower():
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # If any character appears more than 70% of the time, it's too repetitive
        # This allows for reasonable repetition while blocking obvious patterns
        max_char_ratio = max(char_counts.values()) / len(password)
        if max_char_ratio > 0.7:
            errors.append("cannot have excessive character repetition")
            score = max(0, score - 1)
    
    # Bonus points for character diversity (optional enhancement, not required)
    character_types = 0
    if any(c.islower() for c in password):
        character_types += 1
    if any(c.isupper() for c in password):
        character_types += 1
    if any(c.isdigit() for c in password):
        character_types += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in password):
        character_types += 1
    
    # Add bonus for character diversity (but don't require it per NIST)
    if character_types >= 3:
        score += 1
    if character_types >= 4:
        score += 1
    
    valid = len(errors) == 0
    
    if valid:
        if score >= 6:
            strength = "Excellent"
        elif score >= 4:
            strength = "Strong"
        elif score >= 2:
            strength = "Good"
        else:
            strength = "Acceptable"
        message = f"Password strength: {strength}"
    else:
        message = "Password must have " + ", ".join(errors)
    
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
