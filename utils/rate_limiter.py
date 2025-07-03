"""
Rate Limiting and Account Lockout System for Safe Companions
Implements comprehensive rate limiting and security controls
"""

import datetime
import functools
import ipaddress
from flask import request, jsonify, session, redirect, url_for, flash
from extensions import db


class RateLimiter:
    """Comprehensive rate limiting system"""
    
    @staticmethod
    def get_client_ip():
        """Get the client's IP address, handling proxies"""
        if request.headers.get('X-Forwarded-For'):
            # Handle X-Forwarded-For header (comma-separated list)
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            # Handle X-Real-IP header
            ip = request.headers.get('X-Real-IP')
        else:
            # Direct connection
            ip = request.remote_addr
        
        # Validate IP address
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return '127.0.0.1'  # Fallback to localhost
    
    @staticmethod
    def is_whitelisted_ip(ip):
        """Check if IP is whitelisted (for development/admin IPs)"""
        whitelist = [
            '127.0.0.1',
            '::1',
            '0.0.0.0',
            '172.19.0.1',  # Docker network
            '172.18.0.1',  # Docker network
            '172.17.0.1',  # Docker network
        ]
        return ip in whitelist
    
    @staticmethod
    def log_security_event(event_type, details=None, severity='medium', user_id=None):
        """Log a security event"""
        try:
            # Import here to avoid circular imports
            from blueprint.models import SecurityEvent
            
            event = SecurityEvent(
                event_type=event_type,
                ip_address=RateLimiter.get_client_ip(),
                user_agent=request.headers.get('User-Agent', ''),
                user_id=user_id,
                endpoint=request.endpoint,
                details=details,
                severity=severity
            )
            db.session.add(event)
            db.session.commit()
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Error logging security event: {e}")
    
    @staticmethod
    def check_rate_limit(identifier, identifier_type, endpoint, max_requests, window_minutes, block_duration_minutes=60):
        """
        Check if a request should be rate limited
        
        Args:
            identifier: IP address or user ID
            identifier_type: 'ip' or 'user'
            endpoint: The endpoint being accessed
            max_requests: Maximum requests allowed in the window
            window_minutes: Time window in minutes
            block_duration_minutes: How long to block after exceeding limit
            
        Returns:
            tuple: (is_blocked, remaining_requests, reset_time)
        """
        # Import here to avoid circular imports
        from blueprint.models import RateLimitEntry
        
        now = datetime.datetime.utcnow()
        window_start = now - datetime.timedelta(minutes=window_minutes)
        
        # Find or create rate limit entry
        rate_entry = RateLimitEntry.query.filter_by(
            identifier=str(identifier),
            identifier_type=identifier_type,
            endpoint=endpoint
        ).first()
        
        if not rate_entry:
            # First request - create entry
            rate_entry = RateLimitEntry(
                identifier=str(identifier),
                identifier_type=identifier_type,
                endpoint=endpoint,
                request_count=1,
                window_start=now
            )
            db.session.add(rate_entry)
            db.session.commit()
            return False, max_requests - 1, now + datetime.timedelta(minutes=window_minutes)
        
        # Check if currently blocked
        if rate_entry.blocked_until and now < rate_entry.blocked_until:
            remaining_time = (rate_entry.blocked_until - now).total_seconds()
            return True, 0, rate_entry.blocked_until
        
        # Reset window if expired
        if rate_entry.window_start < window_start:
            rate_entry.window_start = now
            rate_entry.request_count = 1
            rate_entry.blocked_until = None
            db.session.commit()
            return False, max_requests - 1, now + datetime.timedelta(minutes=window_minutes)
        
        # Increment request count
        rate_entry.request_count += 1
        
        # Check if limit exceeded
        if rate_entry.request_count > max_requests:
            # Block the identifier
            rate_entry.blocked_until = now + datetime.timedelta(minutes=block_duration_minutes)
            db.session.commit()
            
            # Log security event
            RateLimiter.log_security_event(
                event_type='rate_limit_exceeded',
                details=f'Rate limit exceeded for {identifier_type} {identifier} on {endpoint}',
                severity='high',
                user_id=identifier if identifier_type == 'user' else None
            )
            
            return True, 0, rate_entry.blocked_until
        
        db.session.commit()
        remaining = max_requests - rate_entry.request_count
        reset_time = rate_entry.window_start + datetime.timedelta(minutes=window_minutes)
        
        return False, remaining, reset_time


def rate_limit(max_requests=10, window_minutes=1, block_duration_minutes=60, per_ip=True, per_user=False):
    """
    Decorator for rate limiting endpoints
    
    Args:
        max_requests: Maximum requests allowed in the window
        window_minutes: Time window in minutes
        block_duration_minutes: How long to block after exceeding limit
        per_ip: Apply rate limiting per IP address
        per_user: Apply rate limiting per authenticated user
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip rate limiting for whitelisted IPs in development
            client_ip = RateLimiter.get_client_ip()
            if RateLimiter.is_whitelisted_ip(client_ip):
                return f(*args, **kwargs)
            
            endpoint = request.endpoint or f.__name__
            
            # Check IP-based rate limiting
            if per_ip:
                is_blocked, remaining, reset_time = RateLimiter.check_rate_limit(
                    identifier=client_ip,
                    identifier_type='ip',
                    endpoint=endpoint,
                    max_requests=max_requests,
                    window_minutes=window_minutes,
                    block_duration_minutes=block_duration_minutes
                )
                
                if is_blocked:
                    if request.is_json:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Too many requests from your IP address. Try again after {reset_time.strftime("%Y-%m-%d %H:%M:%S")}',
                            'retry_after': reset_time.isoformat()
                        }), 429
                    else:
                        flash(f'Too many requests. Please try again later.', 'danger')
                        return redirect(url_for('auth.auth')), 429
            
            # Check user-based rate limiting
            if per_user and 'user_id' in session:
                user_id = session['user_id']
                is_blocked, remaining, reset_time = RateLimiter.check_rate_limit(
                    identifier=user_id,
                    identifier_type='user',
                    endpoint=endpoint,
                    max_requests=max_requests,
                    window_minutes=window_minutes,
                    block_duration_minutes=block_duration_minutes
                )
                
                if is_blocked:
                    if request.is_json:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Too many requests from your account. Try again after {reset_time.strftime("%Y-%m-%d %H:%M:%S")}',
                            'retry_after': reset_time.isoformat()
                        }), 429
                    else:
                        flash(f'Too many requests from your account. Please try again later.', 'danger')
                        return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def strict_rate_limit(max_requests=3, window_minutes=5, block_duration_minutes=30):
    """Strict rate limiting for sensitive endpoints like login"""
    return rate_limit(
        max_requests=max_requests,
        window_minutes=window_minutes,
        block_duration_minutes=block_duration_minutes,
        per_ip=True,
        per_user=False
    )


def api_rate_limit(max_requests=100, window_minutes=60, block_duration_minutes=60):
    """Rate limiting for API endpoints"""
    return rate_limit(
        max_requests=max_requests,
        window_minutes=window_minutes,
        block_duration_minutes=block_duration_minutes,
        per_ip=True,
        per_user=True
    )


def user_action_rate_limit(max_requests=20, window_minutes=15, block_duration_minutes=15):
    """Rate limiting for user actions like messaging, booking"""
    return rate_limit(
        max_requests=max_requests,
        window_minutes=window_minutes,
        block_duration_minutes=block_duration_minutes,
        per_ip=False,
        per_user=True
    )
