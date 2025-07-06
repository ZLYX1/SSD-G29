from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from extensions import db
from blueprint.models import Booking, Payment, User
from blueprint.decorators import login_required
from flask_wtf.csrf import generate_csrf
from datetime import datetime, timedelta
from uuid import uuid4
import secrets
import logging

from controllers.security_controller import SecurityController

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')
logger = logging.getLogger(__name__)

payment_tokens = {}
TOKEN_EXPIRY_SECONDS = 300


def generate_payment_token(user_id, booking_id):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY_SECONDS)
    payment_tokens[token] = {
        'user_id': user_id,
        'booking_id': booking_id,
        'expires_at': expires_at,
        'used': False
    }
    logger.info(f"Payment token issued for booking {booking_id} by user {user_id}.")
    return token


def validate_payment_token(token, user_id):
    entry = payment_tokens.get(token)
    if not entry:
        return False
    if entry['user_id'] != user_id or entry['used'] or datetime.utcnow() > entry['expires_at']:
        return False
    return True


def mark_token_used(token):
    if token in payment_tokens:
        payment_tokens[token]['used'] = True


@payment_bp.route('/initiate/<int:booking_id>', methods=['GET'])
@login_required
def initiate_payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    user_id = session['user_id']

    if booking.seeker_id != user_id:
        abort(403, description="You do not own this booking.")
    if booking.status != 'Confirmed':
        logger.warning(f"User {user_id} attempted to pay for non-confirmed booking {booking_id}")
        abort(403, description="Booking is not in a payable state.")

    token = generate_payment_token(user_id, booking_id)
    return redirect(url_for('payment.payment_page', token=token))


@payment_bp.route('/pay', methods=['GET', 'POST'])
@login_required
def payment_page():
    user_id = session['user_id']
    token = request.form.get('token') if request.method == 'POST' else request.args.get('token')

    if not validate_payment_token(token, user_id):
        logger.warning(f"User {user_id} attempted to use invalid/expired token: {token}")
        abort(403, description="Invalid or expired payment token")

    booking_id = payment_tokens[token]['booking_id']
    booking = Booking.query.get_or_404(booking_id)
    escort = User.query.get_or_404(booking.escort_id)

    duration_minutes = int((booking.end_time - booking.start_time).total_seconds() / 60)
    rate_per_minute = 2.0
    amount_due = duration_minutes * rate_per_minute

    if request.method == 'POST':
        SecurityController.check_csrf_token(request.form.get('csrf_token'))

        card_number = SecurityController.sanitize_input(request.form.get('card_number'))
        expiry = SecurityController.sanitize_input(request.form.get('expiry'))
        cvv = SecurityController.sanitize_input(request.form.get('cvv'))

        if not all([card_number.isdigit(), cvv.isdigit(), len(card_number) >= 12, len(cvv) in [3, 4]]):
            flash("Invalid payment details.", "danger")
            return redirect(url_for('payment.payment_page', token=token))

        transaction_id = str(uuid4())
        new_payment = Payment(
            user_id=user_id,
            amount=amount_due,
            status='Completed',
            transaction_id=transaction_id
        )
        db.session.add(new_payment)

        booking.status = 'Confirmed'
        mark_token_used(token)
        db.session.commit()

        logger.info(f"Payment successful for booking {booking_id} by user {user_id}. TXN: {transaction_id}")
        flash("Payment successful. Booking confirmed.", "success")
        return redirect(url_for('booking.booking'))

    history = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
    return render_template(
        'payment.html',
        booking=booking,
        escort=escort,
        amount_due=amount_due,
        token=token,
        csrf_token=generate_csrf(),
        history=history
    )




# '''
# from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
# from extensions import db
# from blueprint.models import Booking, Payment, User
# from blueprint.decorators import login_required
# from flask_wtf.csrf import generate_csrf
# from datetime import datetime, timedelta
# from uuid import uuid4
# import secrets
# import logging

# from controllers.security_controller import SecurityController

# payment_bp = Blueprint('payment', __name__, url_prefix='/payment')
# logger = logging.getLogger(__name__)

# payment_tokens = {}
# TOKEN_EXPIRY_SECONDS = 300


# def generate_payment_token(user_id, booking_id):
#     token = secrets.token_urlsafe(32)
#     expires_at = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY_SECONDS)
#     payment_tokens[token] = {
#         'user_id': user_id,
#         'booking_id': booking_id,
#         'expires_at': expires_at,
#         'used': False
#     }
#     logger.info(f"Payment token issued for booking {booking_id} by user {user_id}.")
#     return token


# def validate_payment_token(token, user_id):
#     entry = payment_tokens.get(token)
#     if not entry:
#         return False
#     if entry['user_id'] != user_id or entry['used'] or datetime.utcnow() > entry['expires_at']:
#         return False
#     return True


# def mark_token_used(token):
#     if token in payment_tokens:
#         payment_tokens[token]['used'] = True


# @payment_bp.route('/initiate/<int:booking_id>', methods=['GET'])
# @login_required
# def initiate_payment(booking_id):
#     booking = Booking.query.get_or_404(booking_id)
#     user_id = session['user_id']

#     if booking.seeker_id != user_id:
#         abort(403)
#     if booking.status != 'Confirmed':
#         flash("This booking is not in a payable state.", "danger")
#         return redirect(url_for('booking.booking'))

#     token = generate_payment_token(user_id, booking_id)
#     return redirect(url_for('payment.payment_page', token=token))


# @payment_bp.route('/pay', methods=['GET', 'POST'])
# @login_required
# def payment_page():
#     user_id = session['user_id']
#     token = request.form.get('token') if request.method == 'POST' else request.args.get('token')

#     if not validate_payment_token(token, user_id):
#         flash("Invalid or expired payment token.", "danger")
#         return redirect(url_for('booking.booking'))

#     booking_id = payment_tokens[token]['booking_id']
#     booking = Booking.query.get_or_404(booking_id)
#     escort = User.query.get_or_404(booking.escort_id)

#     duration_minutes = int((booking.end_time - booking.start_time).total_seconds() / 60)
#     rate_per_minute = 2.0
#     amount_due = duration_minutes * rate_per_minute

#     if request.method == 'POST':
#         SecurityController.check_csrf_token(request.form.get('csrf_token'))

#         card_number = SecurityController.sanitize_input(request.form.get('card_number'))
#         expiry = SecurityController.sanitize_input(request.form.get('expiry'))
#         cvv = SecurityController.sanitize_input(request.form.get('cvv'))

#         if not all([card_number.isdigit(), cvv.isdigit(), len(card_number) >= 12, len(cvv) in [3, 4]]):
#             flash("Invalid payment details.", "danger")
#             return redirect(url_for('payment.payment_page', token=token))

#         transaction_id = str(uuid4())
#         new_payment = Payment(
#             user_id=user_id,
#             amount=amount_due,
#             status='Completed',
#             transaction_id=transaction_id
#         )
#         db.session.add(new_payment)

#         booking.status = 'Confirmed'
#         mark_token_used(token)
#         db.session.commit()

#         logger.info(f"Payment successful for booking {booking_id} by user {user_id}. TXN: {transaction_id}")
#         flash("Payment successful. Booking confirmed.", "success")
#         return redirect(url_for('booking.booking'))

#     history = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
#     return render_template('payment.html', booking=booking, escort=escort, amount_due=amount_due, token=token, csrf_token=generate_csrf(), history=history)
# '''