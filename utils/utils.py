# utils.py
import smtplib
import secrets
import datetime
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
