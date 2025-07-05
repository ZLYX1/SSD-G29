# payment.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from extensions import db
from blueprint.models import Booking, Payment, TimeSlot, User
from blueprint.decorators import login_required
from flask_wtf.csrf import generate_csrf
from datetime import datetime, timedelta
from uuid import uuid4
import secrets
import logging

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')
logger = logging.getLogger(__name__)

# Simple in-memory token store (replace with DB in production)
payment_tokens = {}
TOKEN_EXPIRY_SECONDS = 300  # 5 minutes


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
    if not entry or entry['user_id'] != user_id:
        return False
    if entry['used'] or datetime.utcnow() > entry['expires_at']:
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
        abort(403)
    if booking.status != 'Confirmed':
        flash("This booking is not in a payable state.", "danger")
        return redirect(url_for('booking.booking'))

    token = generate_payment_token(user_id, booking_id)
    return redirect(url_for('payment.payment_page', token=token))


@payment_bp.route('/pay', methods=['GET', 'POST'])
@login_required
def payment_page():
    token = request.args.get('token')
    user_id = session['user_id']

    if not validate_payment_token(token, user_id):
        flash("Invalid or expired payment token.", "danger")
        return redirect(url_for('booking.booking'))

    booking_id = payment_tokens[token]['booking_id']
    booking = Booking.query.get_or_404(booking_id)
    escort = User.query.get_or_404(booking.escort_id)

    # Server-side price calculation (protects against manipulation)
    duration_minutes = int((booking.end_time - booking.start_time).total_seconds() / 60)
    rate_per_minute = 2.0  # Replace with actual dynamic rate if needed
    amount_due = duration_minutes * rate_per_minute

    if request.method == 'POST':
        card_number = request.form.get('card_number', '').strip()
        expiry = request.form.get('expiry', '').strip()
        cvv = request.form.get('cvv', '').strip()

        # Input validation and sanitization
        if not all([card_number.isdigit(), cvv.isdigit(), len(card_number) >= 12, len(cvv) in [3, 4]]):
            flash("Invalid payment details.", "danger")
            return redirect(url_for('payment.payment_page', token=token))

        # Simulate payment processing
        transaction_id = str(uuid4())
        new_payment = Payment(
            user_id=user_id,
            amount=amount_due,
            status='Completed',
            transaction_id=transaction_id
        )
        db.session.add(new_payment)

        # Mark token used and confirm booking
        booking.status = 'Confirmed'
        mark_token_used(token)
        db.session.commit()

        logger.info(f"Payment successful for booking {booking_id} by user {user_id}. TXN: {transaction_id}")

        flash("Payment successful. Booking confirmed.", "success")
        return redirect(url_for('booking.booking'))

    # Load payment history
    history = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()

    return render_template('payment.html',
                           booking=booking,
                           escort=escort,
                           amount_due=amount_due,
                           token=token,
                           csrf_token=generate_csrf(),
                           history=history)



'''
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Payment  # Uncomment this import
from flask_wtf.csrf import generate_csrf
from extensions import db
from blueprint.decorators import login_required
import uuid  # Add this import for transaction_id generation

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/payment', methods=['GET', 'POST'])  # Add POST method
@login_required
def payment():
    if request.method == 'POST':
        card_number = request.form.get('card_number', '').replace(' ', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        
        # Validate card number
        if not (card_number.isdigit() and len(card_number) == 16):
            flash("Invalid card number. Must be 16 digits.", "danger")
            return redirect(url_for('payment.payment'))

        # Validate amount
        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash("Invalid amount. Must be a positive number.", "danger")
            return redirect(url_for('payment.payment'))

            
            # Validate card number (basic validation)
        if card_number and len(card_number) == 16 and card_number.isdigit() and amount > 0:
            try:
                    new_payment = Payment(
                        user_id=session['user_id'],
                        amount=float(amount),
                        transaction_id=str(uuid.uuid4())
                    )
                    db.session.add(new_payment)
                    db.session.commit()
                    flash("Payment successful!", "success")
                    return redirect(url_for('payment.payment'))  # Use blueprint name
            except ValueError:
                    flash("Invalid amount entered", "danger")
        else:
            flash("Payment failed. Invalid card number or amount.", "danger")
            
            return redirect(url_for('payment.payment'))

    # # GET request - show payment history
    # history = Payment.query.filter_by(user_id=session['user_id']).order_by(Payment.created_at.desc()).all()
    # return render_template('payment.html', history=history)

 	# GET request - show payment form
    history = Payment.query.filter_by(user_id=session['user_id']).order_by(Payment.created_at.desc()).all()
    csrf_token = generate_csrf()  # Generate CSRF token for the form
    return render_template('payment.html', history=history, csrf_token=csrf_token)
    '''

