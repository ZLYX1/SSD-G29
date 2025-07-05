from flask import session, abort, request
from flask_wtf.csrf import validate_csrf
from markupsafe import escape
import logging
import datetime

from blueprint.models import PasswordHistory
from werkzeug.security import check_password_hash

logger = logging.getLogger(__name__)

class SecurityController:
    @staticmethod
    def enforce_rbac(required_role: str) -> bool:
        role = session.get('role')
        if role != required_role:
            abort(403, description="Access denied: insufficient privileges")
        return True

    @staticmethod
    def check_csrf_token(token: str) -> bool:
        try:
            validate_csrf(token)
            return True
        except Exception as e:
            logger.warning(f"CSRF validation failed: {e}")
            abort(403, description="Invalid CSRF token")

    @staticmethod
    def sanitize_input(input_data: str) -> str:
        return escape(input_data.strip()) if input_data else ''
    
    '''
    @staticmethod
    def check_brute_force(user) -> bool:
        if user.is_account_locked():
            abort(403, description="Account temporarily locked due to failed login attempts.")
        return True

    @staticmethod
    def enforce_session_timeout(last_activity: datetime.datetime, timeout_minutes: int = 15) -> bool:
        if datetime.datetime.utcnow() - last_activity > datetime.timedelta(minutes=timeout_minutes):
            session.clear()
            abort(403, description="Session expired. Please log in again.")
        return True

    @staticmethod
    def log_security_event(user_id: int, event: str, ip: str) -> None:
        logger.info(f"[SECURITY] User {user_id} - {event} - IP: {ip}")

    @staticmethod
    def validate_password_history(user, new_password: str, limit: int = 5) -> bool:
        if user.is_password_in_history(new_password, limit=limit):
            return False
        return True
'''