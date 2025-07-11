# controllers/payment_controller.py

from blueprint.models import Booking, Payment, User
from extensions import db
from flask import session, abort
from datetime import datetime, timedelta
from uuid import uuid4
import secrets
import logging

logger = logging.getLogger(__name__)

class PaymentController:
    payment_tokens = {}
    TOKEN_EXPIRY_SECONDS = 300

    @staticmethod
    def generate_payment_token(user_id, booking_id):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=PaymentController.TOKEN_EXPIRY_SECONDS)
        PaymentController.payment_tokens[token] = {
            'user_id': user_id,
            'booking_id': booking_id,
            'expires_at': expires_at,
            'used': False
        }
        logger.info(f"Payment token issued for booking {booking_id} by user {user_id}.")
        return token

    @staticmethod
    def validate_payment_token(token, user_id):
        entry = PaymentController.payment_tokens.get(token)
        if not entry:
            return False
        if entry['user_id'] != user_id or entry['used'] or datetime.utcnow() > entry['expires_at']:
            return False
        return True

    @staticmethod
    def mark_token_used(token):
        if token in PaymentController.payment_tokens:
            PaymentController.payment_tokens[token]['used'] = True
##
    # @staticmethod
    # def get_amount_due(booking):
    #     duration_minutes = int((booking.end_time - booking.start_time).total_seconds() / 60)
    #     rate_per_minute = 2.0
    #     return duration_minutes * rate_per_minute

    @staticmethod
    def authorize_booking_payment(user_id, booking_id):
        booking = Booking.query.get_or_404(booking_id)

        if booking.seeker_id != user_id:
            logger.warning(f"User {user_id} attempted to pay for booking {booking_id} they don't own")
            abort(403, description="You do not own this booking.")

        if booking.status != 'Confirmed':
            logger.warning(f"User {user_id} attempted to pay for non-confirmed booking {booking_id}")
            abort(403, description="Booking is not in a payable state.")

        existing_payment = Payment.query.filter_by(booking_id=booking_id, status='Completed').first()
        if existing_payment:
            logger.warning(f"User {user_id} attempted to pay for already paid booking {booking_id}")
            abort(403, description="This booking has already been paid for.")

        grace_period = timedelta(hours=1)
        if booking.start_time < datetime.now() - grace_period:
            logger.warning(f"User {user_id} attempted to pay for expired booking {booking_id}")
            abort(403, description="Cannot pay for expired bookings.")

        user = User.query.get_or_404(user_id)
        if not user.active or user.deleted:
            logger.warning(f"Inactive/deleted user {user_id} attempted payment for booking {booking_id}")
            abort(403, description="Account not authorized for payments.")


















    @staticmethod
    def create_payment(user_id, booking,booking_id, amount_due,token):
        transaction_id = str(uuid4())
        new_payment = Payment(
            user_id=user_id,
            amount=amount_due,
            status='Completed',
            transaction_id=transaction_id,
            booking_id=booking_id
        )
        try:
            db.session.add(new_payment)
            booking.status = 'Confirmed'
            PaymentController.mark_token_used(token)
            db.session.commit()
            logger.info(f"Payment successful for booking {booking_id} by user {user_id}. TXN: {transaction_id}")
            return transaction_id
        except Exception as e:
            logger.error(f"Payment creation failed:{e}")
            return None

    @staticmethod
    def get_payment_history(user_id):
        return Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()