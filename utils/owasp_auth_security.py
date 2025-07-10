#!/usr/bin/env python3
"""
OWASP-Compliant Authentication Security Module
Implements progressive delays, account lockout, and security monitoring
Based on OWASP Authentication Cheat Sheet recommendations
"""

import time
import datetime
import logging
from typing import Tuple, Optional
from functools import wraps
from flask import request, session, flash
from blueprint.models import db, User
from blueprint.audit_log import log_event

# Configure security logging
security_logger = logging.getLogger('owasp_security')
security_logger.setLevel(logging.INFO)

class OWASPAuthSecurity:
    """OWASP-compliant authentication security implementation"""
    
    # OWASP Recommended Settings
    MAX_FAILED_ATTEMPTS = 5  # Lock account after 5 failed attempts
    INITIAL_LOCKOUT_MINUTES = 15  # Initial lockout duration
    MAX_LOCKOUT_MINUTES = 60  # Maximum lockout duration
    PROGRESSIVE_DELAY_BASE = 1  # Base delay in seconds
    MAX_PROGRESSIVE_DELAY = 30  # Maximum progressive delay
    SUSPICIOUS_ACTIVITY_THRESHOLD = 3  # Flags before extended monitoring
    
    @staticmethod
    def calculate_progressive_delay(failed_attempts: int) -> int:
        """
        Calculate progressive delay based on failed attempts
        OWASP Pattern: 1s, 2s, 4s, 8s, 16s, 30s (max)
        """
        if failed_attempts <= 0:
            return 0
        
        # Exponential backoff: 2^(attempts-1) seconds
        delay = OWASPAuthSecurity.PROGRESSIVE_DELAY_BASE * (2 ** (failed_attempts - 1))
        return min(delay, OWASPAuthSecurity.MAX_PROGRESSIVE_DELAY)
    
    @staticmethod
    def calculate_lockout_duration(failed_attempts: int, previous_lockouts: int = 0) -> int:
        """
        Calculate lockout duration based on failed attempts and history
        OWASP Pattern: Progressive lockout with increasing duration
        """
        base_duration = OWASPAuthSecurity.INITIAL_LOCKOUT_MINUTES
        
        # Increase duration for repeat offenders
        multiplier = 1 + (previous_lockouts * 0.5)  # 1x, 1.5x, 2x, etc.
        duration = base_duration * multiplier
        
        return min(int(duration), OWASPAuthSecurity.MAX_LOCKOUT_MINUTES)
    
    @staticmethod
    def is_progressive_delay_active(user: User) -> Tuple[bool, int]:
        """
        Check if user is in progressive delay period
        Returns: (is_delayed, seconds_remaining)
        """
        if not user.progressive_delay_until:
            return False, 0
        
        now = datetime.datetime.utcnow()
        if now >= user.progressive_delay_until:
            # Delay expired, clear it
            user.progressive_delay_until = None
            db.session.commit()
            return False, 0
        
        # Calculate remaining delay
        remaining = (user.progressive_delay_until - now).total_seconds()
        return True, int(remaining)
    
    @staticmethod
    def apply_progressive_delay(user: User) -> None:
        """Apply progressive delay based on failed attempts"""
        delay_seconds = OWASPAuthSecurity.calculate_progressive_delay(user.failed_login_attempts)
        
        if delay_seconds > 0:
            user.progressive_delay_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay_seconds)
            user.last_failed_attempt = datetime.datetime.utcnow()
            
            # Log security event
            security_logger.warning(
                f"Progressive delay applied: {delay_seconds}s for user {user.email} "
                f"after {user.failed_login_attempts} failed attempts"
            )
    
    @staticmethod
    def handle_failed_login(user: User, ip_address: str = None, user_agent: str = None) -> Tuple[bool, str, int]:
        """
        Handle failed login attempt with OWASP-compliant security measures
        Returns: (is_locked, message, delay_seconds)
        """
        # Increment failed attempts
        user.failed_login_attempts += 1
        user.last_failed_attempt = datetime.datetime.utcnow()
        
        # Check for suspicious patterns
        user.suspicious_activity_flags += 1
        
        # Apply progressive delay
        OWASPAuthSecurity.apply_progressive_delay(user)
        
        # Check if account should be locked
        if user.failed_login_attempts >= OWASPAuthSecurity.MAX_FAILED_ATTEMPTS:
            # Calculate lockout duration
            lockout_minutes = OWASPAuthSecurity.calculate_lockout_duration(
                user.failed_login_attempts,
                user.suspicious_activity_flags
            )
            
            # Lock the account
            user.account_locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=lockout_minutes)
            user.lockout_reason = "Too many failed login attempts (OWASP Protection)"
            
            # Log security event
            security_logger.critical(
                f"Account locked: {user.email} for {lockout_minutes} minutes "
                f"after {user.failed_login_attempts} failed attempts from IP: {ip_address}"
            )
            
            # Audit log for admin monitoring
            log_event(
                user_id=user.id,
                action="account_locked_brute_force",
                details=f"Account locked for {lockout_minutes} minutes due to {user.failed_login_attempts} failed login attempts. IP: {ip_address}"
            )
            
            db.session.commit()
            return True, f"Account locked for {lockout_minutes} minutes due to too many failed attempts.", 0
        
        # Calculate progressive delay for next attempt
        delay_seconds = OWASPAuthSecurity.calculate_progressive_delay(user.failed_login_attempts + 1)
        attempts_remaining = OWASPAuthSecurity.MAX_FAILED_ATTEMPTS - user.failed_login_attempts
        
        # Log failed attempt
        security_logger.warning(
            f"Failed login attempt {user.failed_login_attempts}/{OWASPAuthSecurity.MAX_FAILED_ATTEMPTS} "
            f"for {user.email} from IP: {ip_address}"
        )
        
        db.session.commit()
        
        message = (
            f"Invalid credentials. {attempts_remaining} attempts remaining before account lockout. "
            f"Next attempt available in {delay_seconds} seconds."
        )
        
        return False, message, delay_seconds
    
    @staticmethod
    def handle_successful_login(user: User, ip_address: str = None) -> None:
        """Handle successful login - reset security counters"""
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.progressive_delay_until = None
        user.lockout_reason = None
        user.last_successful_login = datetime.datetime.utcnow()
        
        # Reduce suspicious activity flags on successful login
        if user.suspicious_activity_flags > 0:
            user.suspicious_activity_flags = max(0, user.suspicious_activity_flags - 1)
        
        # Log successful login
        security_logger.info(f"Successful login for {user.email} from IP: {ip_address}")
        
        db.session.commit()
    
    @staticmethod
    def check_account_status(user: User) -> Tuple[bool, str]:
        """
        Check if account can attempt login
        Returns: (can_login, status_message)
        """
        # Check if account is locked
        if user.is_account_locked():
            remaining_time = user.account_locked_until - datetime.datetime.utcnow()
            remaining_minutes = int(remaining_time.total_seconds() / 60)
            return False, f"Account is locked. Try again in {remaining_minutes} minutes."
        
        # Check progressive delay
        is_delayed, delay_seconds = OWASPAuthSecurity.is_progressive_delay_active(user)
        if is_delayed:
            return False, f"Too many rapid attempts. Please wait {delay_seconds} seconds before trying again."
        
        # Check if account is active
        if not user.active:
            return False, "Account is disabled. Please contact support."
        
        # Check if account is deleted
        if user.deleted:
            return False, "Account not found."
        
        return True, "Account is available for login."

def progressive_delay_required(f):
    """
    Decorator to enforce progressive delays on authentication endpoints
    OWASP-compliant rate limiting at the user level
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get email from form data
        email = request.form.get('email', '').strip().lower()
        
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                # Check if user has active progressive delay
                is_delayed, delay_seconds = OWASPAuthSecurity.is_progressive_delay_active(user)
                
                if is_delayed:
                    flash(
                        f"Too many rapid login attempts. Please wait {delay_seconds} seconds before trying again.",
                        "warning"
                    )
                    
                    # Log the attempt during delay period
                    security_logger.warning(
                        f"Login attempt during progressive delay period: {email} "
                        f"({delay_seconds}s remaining) from IP: {request.remote_addr}"
                    )
                    
                    return f(*args, **kwargs)  # Return to form with error message
        
        return f(*args, **kwargs)
    
    return decorated_function

# Security monitoring functions
def detect_suspicious_patterns(user: User, ip_address: str, user_agent: str) -> bool:
    """Detect suspicious login patterns (for future enhancement)"""
    # This could be expanded to detect:
    # - Multiple IPs for same user
    # - Unusual geographic locations
    # - Automated tools/bots
    # - Time-based patterns
    return False

def log_security_metrics():
    """Log security metrics for monitoring (for future enhancement)"""
    # Count locked accounts, failed attempts, etc.
    # This could feed into security dashboards
    pass
