from flask import Blueprint, render_template, request
from blueprint.models import AuditLog, db
from blueprint.decorators import role_required

audit_bp = Blueprint('audit', __name__, url_prefix='/admin/audit')

@audit_bp.route('/logs')
@role_required('admin')
def view_logs():
    filter_type = request.args.get('filter')
    query = AuditLog.query.order_by(AuditLog.created_at.desc())

    if filter_type == 'fail':
        query = query.filter(
            AuditLog.action.contains('fail') | 
            AuditLog.action.contains('lock')
        )
    elif filter_type == 'suspicious':
        query = query.filter(
            AuditLog.action.contains('ban') | 
            AuditLog.action.contains('delete')
        )

    logs = query.limit(200).all()
    return render_template('audit_log.html', logs=logs)

def log_event(user_id, action, details=None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )
    db.session.add(log)
    db.session.commit()
