from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_wtf.csrf import generate_csrf
from blueprint.models import Message, User, Profile
from extensions import db
from blueprint.decorators import login_required
from controllers.message_controller import MessageController
import json

messaging_bp = Blueprint('messaging', __name__, url_prefix='/messaging')

# def serialize_conversation(conv):
#     return {
#         'other_user': {
#             'id': conv.other_user.id,
#             'profile': {
#                 'name': conv.other_user.profile.name if conv.other_user.profile else None,
#                 'photo': conv.other_user.profile.photo if conv.other_user.profile else None,
#             },
#             'email': conv.other_user.email,
#         },
#         'last_message': serialize_message(conv.last_message) if conv.last_message else None,
#         'unread_count': conv.unread_count,
#         # add more fields if needed
#     }

def serialize_conversation(conv):
    other_user = conv['other_user']
    profile = other_user.profile if hasattr(other_user, 'profile') else None

    return {
        'other_user': {
            'id': other_user.id,
            'profile': {
                'name': profile.name if profile else None,
                'photo': profile.photo if profile else None,
            },
            'email': other_user.email,
        },
        'last_message': serialize_message(conv['last_message']) if conv['last_message'] else None,
        'unread_count': conv['unread_count'],
    }
def serialize_message(msg):
    return {
        'id': msg.id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%m/%d %H:%M'),  # already formatted string
        'sender_id': msg.sender_id,
        'recipient_id': msg.recipient_id,
    }


@messaging_bp.route('/')
@messaging_bp.route('/messaging')
@login_required
def messaging():
    """Main messaging page - shows conversations list"""
    user_id = session['user_id']
    
    # Get all conversations for current user
    conversations = MessageController.get_user_conversations(user_id)
    
    # Get available users for new conversations
    available_users = MessageController.get_available_users(user_id)
    other_user = User.query.get_or_404(user_id)
    conversations_serialized = [serialize_conversation(c) for c in conversations]
    
    # return render_template('messaging.html', 
    #                      conversations=conversations,
    #                      available_users=available_users,
    #                      current_conversation=None,
    #                      messages=[])
    return render_template('messaging.html',
                           user_id=session['user_id'],
                           conversations=conversations_serialized,
                           available_users=available_users,
                           current_conversation=other_user,
                           messages=[],
                           csrf_token=generate_csrf())

# @messaging_bp.route('/conversation/<int:user_id>')
# @login_required
# def view_conversation(user_id):
#     """View specific conversation with another user"""
#     current_user_id = session['user_id']
    
#     # Get the other user
#     other_user = User.query.get_or_404(user_id)
    
#     # Get conversations list
#     conversations = MessageController.get_user_conversations(current_user_id)
    
#     # Get messages between users
#     messages = MessageController.get_conversation_messages(current_user_id, user_id)
    
#     # Get available users for new conversations
#     available_users = MessageController.get_available_users(current_user_id)
    
#     return render_template('messaging.html',
#                          conversations=conversations,
#                          available_users=available_users,
#                          current_conversation=other_user,
#                          messages=messages)

@messaging_bp.route('/conversation/<int:user_id>')
@login_required
def view_conversation(user_id):
    current_user_id = session['user_id']

    other_user = User.query.get_or_404(user_id)
    conversations = MessageController.get_user_conversations(current_user_id)
    messages = MessageController.get_conversation_messages(current_user_id, user_id)
    available_users = MessageController.get_available_users(current_user_id)

    # ✅ Fix: Serialize conversations
    conversations_serialized = [serialize_conversation(c) for c in conversations]
    current_conversation_serialized = other_user
    messages_serialized = [serialize_message(m) for m in messages]

    return render_template('messaging.html',
        user_id=session['user_id'],
        conversations=conversations_serialized,
        available_users=available_users,
        current_conversation=current_conversation_serialized,
        messages=messages_serialized,
        csrf_token=generate_csrf()
    )


    
        
@messaging_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    print("send message in .py")
    """Send a message via AJAX"""
    try:
        # Add debug logging
        print(f"Request content type: {request.content_type}")
        print(f"Request data: {request.data}")
        print(f"Request JSON: {request.get_json()}")
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'})
            
        sender_id = session['user_id']
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        
        print(f"Sender ID: {sender_id}, Recipient ID: {recipient_id}, Content: {content}")
        
        if not recipient_id or not content:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        success, result = MessageController.send_message(sender_id, recipient_id, content)
        
        if success:
            message_data = {
                'id': result.id,
                'content': result.content,
                'timestamp': result.timestamp.isoformat(),
                'sender_id': result.sender_id,
                'recipient_id': result.recipient_id
            }
            return jsonify({'success': True, 'message': message_data})
        else:
            return jsonify({'success': False, 'error': result})
    
    except Excecurrent_conversation_serializedption as e:
        print(f"Error in send_message: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@messaging_bp.route('/report', methods=['POST'])
@login_required
def report_user():
    """Report a user for inappropriate behavior"""
    try:
        data = request.get_json()
        reporter_id = session['user_id']
        reported_id = data.get('reported_id')
        reason = data.get('reason')
        details = data.get('details', '')
        
        if not reported_id or not reason:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        success, message = MessageController.report_user(reporter_id, reported_id, reason, details)
        
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@messaging_bp.route('/block', methods=['POST'])
@login_required
def block_user():
    """Block a user (placeholder for now)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'})
        
        # For now, just return success - blocking logic can be implemented later
        # This would typically involve adding a BlockedUser model and checking
        # blocked status before showing messages
        return jsonify({'success': True, 'message': 'User blocked successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@messaging_bp.route('/delete_conversation/<int:user_id>', methods=['POST'])
@login_required
def delete_conversation(user_id):
    """Delete/hide a conversation"""
    current_user_id = session['user_id']
    
    success, message = MessageController.delete_conversation(current_user_id, user_id)
    
    if success:
        flash("Conversation deleted successfully", "success")
    else:
        flash(f"Error deleting conversation: {message}", "error")
    
    return redirect(url_for('messaging.messaging'))


@messaging_bp.route('/api/conversations')
@login_required
def api_conversations():
    """API endpoint to get conversations (for AJAX refresh)"""
    user_id = session['user_id']
    conversations = MessageController.get_user_conversations(user_id)
    
    conversations_data = []
    for conv in conversations:
        conversations_data.append({
            'other_user_id': conv['other_user'].id,
            'other_user_name': conv['other_user'].profile.name if conv['other_user'].profile and conv['other_user'].profile.name else conv['other_user'].email,
            'other_user_photo': conv['other_user'].profile.photo if conv['other_user'].profile and conv['other_user'].profile.photo else 'default.jpg',
            'last_message': {
                'content': conv['last_message'].content[:50] + '...' if conv['last_message'] and len(conv['last_message'].content) > 50 else conv['last_message'].content if conv['last_message'] else '',
                'timestamp': conv['last_message'].timestamp.isoformat() if conv['last_message'] else '',
                'sender_id': conv['last_message'].sender_id if conv['last_message'] else None
            } if conv['last_message'] else None,
            'unread_count': conv['unread_count']
        })
    
    return jsonify({'conversations': conversations_data})


@messaging_bp.route('/api/messages/<int:user_id>')
@login_required
def api_messages(user_id):
    """API endpoint to get messages with a specific user"""
    current_user_id = session['user_id']
    messages = MessageController.get_conversation_messages(current_user_id, user_id)
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id,
            'is_read': message.is_read
        })
    
    return jsonify({'messages': messages_data})


@messaging_bp.route('/stats')
@login_required
def messaging_stats():
    """Get messaging statistics for current user"""
    user_id = session['user_id']
    stats = MessageController.get_message_statistics(user_id)
    return jsonify(stats)
