from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Payment  # Uncomment this import
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