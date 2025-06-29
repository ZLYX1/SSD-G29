
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Message
from extensions import db
from blueprint.decorators import login_required

messaging_bp = Blueprint('messaging', __name__, url_prefix='/messaging')


# MESSAGES = {
#     1: {'from_id': 1, 'to_id': 2, 'text': 'Hello, are you available next Friday?', 'timestamp': time.time()},
#     2: {'from_id': 2, 'to_id': 1, 'text': 'Hi! Let me check my calendar. Please use the booking system.', 'timestamp': time.time() + 60},
# }

# 6. MESSAGING NOT DONE!
@messaging_bp.route('/messaging')
@login_required
def messaging():
    # Simple simulation: show all messages involving the current user
    user_id = session['user_id']
    user_messages = Message.query.filter(
        (Message.sender_id == user_id) | 
        (Message.recipient_id == user_id)
    ).order_by(Message.timestamp.desc()).all()
    return render_template('messaging.html', messages=user_messages)

    # user_messages = [msg for msg in Message.values() if msg['from_id'] == user_id or msg['to_id'] == user_id]
    # return render_template('messaging.html', messages=user_messages)
