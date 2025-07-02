# utils.py
import smtplib
import secrets
import datetime
import random
import re
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
        SSD-G29 Team
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
        # Configure your SMTP settings
        smtp_server = "smtp.gmail.com"  # or your SMTP server
        smtp_port = 587
        smtp_username = "your-email@gmail.com"
        smtp_password = "your-app-password"
        
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
