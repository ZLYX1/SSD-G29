"""
Security monitoring and admin utilities
"""

from flask import Blueprint, render_template, request, jsonify
from blueprint.models import SecurityEvent, RateLimitEntry, User
from blueprint.decorators import login_required, admin_required
from extensions import db
from utils.rate_limiter import api_rate_limit
import datetime
from sqlalchemy import func

security_bp = Blueprint('security', __name__, url_prefix='/security')


@security_bp.route('/dashboard')
@admin_required
def security_dashboard():
    """Security monitoring dashboard for admins"""
    
    # Get recent security events
    recent_events = SecurityEvent.query.order_by(SecurityEvent.created_at.desc()).limit(50).all()
    
    # Get current rate limit blocks
    now = datetime.datetime.utcnow()
    active_blocks = RateLimitEntry.query.filter(
        RateLimitEntry.blocked_until > now
    ).all()
    
    # Get security event statistics
    event_stats = db.session.query(
        SecurityEvent.event_type,
        func.count(SecurityEvent.id).label('count'),
        func.max(SecurityEvent.created_at).label('last_occurrence')
    ).filter(
        SecurityEvent.created_at >= datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    ).group_by(SecurityEvent.event_type).all()
    
    # Get top blocked IPs
    blocked_ips = db.session.query(
        RateLimitEntry.identifier,
        func.count(RateLimitEntry.id).label('block_count'),
        func.max(RateLimitEntry.blocked_until).label('last_blocked')
    ).filter(
        RateLimitEntry.identifier_type == 'ip',
        RateLimitEntry.blocked_until.isnot(None)
    ).group_by(RateLimitEntry.identifier).order_by(
        func.count(RateLimitEntry.id).desc()
    ).limit(10).all()
    
    return render_template('security/dashboard.html', 
                         recent_events=recent_events,
                         active_blocks=active_blocks,
                         event_stats=event_stats,
                         blocked_ips=blocked_ips)


@security_bp.route('/events')
@api_rate_limit(max_requests=50, window_minutes=60)
@admin_required
def get_security_events():
    """API endpoint to get security events with filtering"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    event_type = request.args.get('event_type', '')
    severity = request.args.get('severity', '')
    hours = request.args.get('hours', 24, type=int)
    
    # Build query
    query = SecurityEvent.query
    
    # Apply filters
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    
    if hours > 0:
        since = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        query = query.filter(SecurityEvent.created_at >= since)
    
    # Pagination
    events = query.order_by(SecurityEvent.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'events': [{
            'id': event.id,
            'event_type': event.event_type,
            'ip_address': event.ip_address,
            'user_id': event.user_id,
            'endpoint': event.endpoint,
            'details': event.details,
            'severity': event.severity,
            'created_at': event.created_at.isoformat(),
            'user_email': event.user.email if event.user else None
        } for event in events.items],
        'pagination': {
            'page': events.page,
            'pages': events.pages,
            'per_page': events.per_page,
            'total': events.total,
            'has_next': events.has_next,
            'has_prev': events.has_prev
        }
    })


@security_bp.route('/rate-limits')
@api_rate_limit(max_requests=30, window_minutes=60)
@admin_required
def get_rate_limits():
    """API endpoint to get rate limiting status"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    identifier_type = request.args.get('type', '')  # 'ip' or 'user'
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    # Build query
    query = RateLimitEntry.query
    
    # Apply filters
    if identifier_type:
        query = query.filter(RateLimitEntry.identifier_type == identifier_type)
    
    if active_only:
        now = datetime.datetime.utcnow()
        query = query.filter(RateLimitEntry.blocked_until > now)
    
    # Pagination
    rate_limits = query.order_by(RateLimitEntry.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'rate_limits': [{
            'id': rl.id,
            'identifier': rl.identifier,
            'identifier_type': rl.identifier_type,
            'endpoint': rl.endpoint,
            'request_count': rl.request_count,
            'window_start': rl.window_start.isoformat(),
            'blocked_until': rl.blocked_until.isoformat() if rl.blocked_until else None,
            'is_blocked': rl.blocked_until and rl.blocked_until > datetime.datetime.utcnow(),
            'created_at': rl.created_at.isoformat()
        } for rl in rate_limits.items],
        'pagination': {
            'page': rate_limits.page,
            'pages': rate_limits.pages,
            'per_page': rate_limits.per_page,
            'total': rate_limits.total,
            'has_next': rate_limits.has_next,
            'has_prev': rate_limits.has_prev
        }
    })


@security_bp.route('/unblock', methods=['POST'])
@api_rate_limit(max_requests=10, window_minutes=60)
@admin_required
def unblock_identifier():
    """Admin endpoint to manually unblock rate limited identifiers"""
    
    identifier = request.json.get('identifier')
    identifier_type = request.json.get('identifier_type')
    
    if not identifier or not identifier_type:
        return jsonify({'error': 'Missing identifier or identifier_type'}), 400
    
    # Find and unblock the rate limit entries
    entries = RateLimitEntry.query.filter_by(
        identifier=identifier,
        identifier_type=identifier_type
    ).filter(
        RateLimitEntry.blocked_until.isnot(None)
    ).all()
    
    count = 0
    for entry in entries:
        entry.blocked_until = None
        count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Unblocked {count} rate limit entries for {identifier_type} {identifier}',
        'count': count
    })


@security_bp.route('/stats')
@api_rate_limit(max_requests=20, window_minutes=60)
@admin_required
def security_stats():
    """Get security statistics"""
    
    now = datetime.datetime.utcnow()
    
    # Time ranges for statistics
    ranges = {
        'last_hour': now - datetime.timedelta(hours=1),
        'last_24h': now - datetime.timedelta(hours=24),
        'last_7d': now - datetime.timedelta(days=7),
        'last_30d': now - datetime.timedelta(days=30)
    }
    
    stats = {}
    
    for range_name, since in ranges.items():
        # Security events
        events_count = SecurityEvent.query.filter(
            SecurityEvent.created_at >= since
        ).count()
        
        # Failed logins
        failed_logins = SecurityEvent.query.filter(
            SecurityEvent.event_type == 'failed_login',
            SecurityEvent.created_at >= since
        ).count()
        
        # Account lockouts
        lockouts = SecurityEvent.query.filter(
            SecurityEvent.event_type == 'account_lockout',
            SecurityEvent.created_at >= since
        ).count()
        
        # Rate limit violations
        rate_violations = SecurityEvent.query.filter(
            SecurityEvent.event_type == 'rate_limit_exceeded',
            SecurityEvent.created_at >= since
        ).count()
        
        # Unique IPs
        unique_ips = db.session.query(
            func.count(func.distinct(SecurityEvent.ip_address))
        ).filter(
            SecurityEvent.created_at >= since
        ).scalar()
        
        stats[range_name] = {
            'total_events': events_count,
            'failed_logins': failed_logins,
            'account_lockouts': lockouts,
            'rate_violations': rate_violations,
            'unique_ips': unique_ips
        }
    
    # Current blocks
    current_blocks = RateLimitEntry.query.filter(
        RateLimitEntry.blocked_until > now
    ).count()
    
    stats['current_blocks'] = current_blocks
    
    return jsonify(stats)
