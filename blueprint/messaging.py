from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_wtf.csrf import generate_csrf
from blueprint.models import Message, User, Profile
from extensions import db
from blueprint.decorators import login_required
from controllers.message_controller import MessageController
import json
import os

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
    """Serialize message for template display - handles both encrypted and plain text"""
    base_data = {
        'id': msg.id,
        'sender_id': msg.sender_id,
        'recipient_id': msg.recipient_id,
        'timestamp': msg.timestamp.strftime('%m/%d %H:%M'),
        'is_encrypted': msg.is_encrypted
    }
    
    if msg.is_encrypted:
        # For encrypted messages, include encrypted data for client-side decryption
        base_data.update({
            'encrypted_content': msg.encrypted_content,
            'nonce': msg.encryption_nonce,
            'algorithm': msg.encryption_algorithm,
            'content': '[Encrypted Message - Decrypting...]'  # Placeholder while decrypting
        })
    else:
        base_data['content'] = msg.content
    
    return base_data


@messaging_bp.route('/')
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
    """Send a message via AJAX - supports both plain text and encrypted content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'})
        
        sender_id = session['user_id']
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        encrypted_data = data.get('encrypted_data')
        
        if not recipient_id:
            return jsonify({'success': False, 'error': 'Recipient ID required'})
        
        # NEW LOGIC: Accept EITHER content OR encrypted_data
        has_content = content and content.strip()
        has_encrypted_data = encrypted_data and isinstance(encrypted_data, dict) and bool(encrypted_data.get('encrypted_content'))
        
        if not has_content and not has_encrypted_data:
            return jsonify({'success': False, 'error': 'Missing required fields: need either content or encrypted_data'})
        
        # Security check: In production, require encryption unless explicitly disabled
        if not encrypted_data and os.environ.get('FLASK_ENV') == 'production':
            if not os.environ.get('ALLOW_PLAINTEXT_MESSAGES') == 'true':
                return jsonify({'success': False, 'error': 'Encrypted messages are required in production'})
        
        # Send message with appropriate content type
        if encrypted_data:
            success, result = MessageController.send_message(
                sender_id, recipient_id, encrypted_data=encrypted_data
            )
        else:
            success, result = MessageController.send_message(
                sender_id, recipient_id, content=content
            )
        
        if success:
            # Use new serialization method that handles encryption
            message_data = MessageController.serialize_message_for_client(result)
            response_data = {'success': True, 'message': message_data}
            return jsonify(response_data)
        else:
            return jsonify({'success': False, 'error': result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@messaging_bp.route('/test-send', methods=['POST'])
def test_send_message():
    """Test endpoint to verify encrypted_data handling without authentication"""
    try:
        print(f"🧪 TEST ENDPOINT HIT - NEW CODE v3.0 TEST")
        data = request.get_json()
        print(f"Test received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'})
        
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        encrypted_data = data.get('encrypted_data')
        
        print(f"Test: recipient_id={recipient_id}")
        print(f"Test: content='{content}', encrypted_data={encrypted_data}")
        
        if not recipient_id:
            return jsonify({'success': False, 'error': 'Recipient ID required'})
        
        # NEW LOGIC: Accept EITHER content OR encrypted_data
        has_content = content and content.strip()
        has_encrypted_data = encrypted_data and isinstance(encrypted_data, dict) and bool(encrypted_data.get('encrypted_content'))
        
        print(f"Test: has_content: {has_content}, has_encrypted_data: {has_encrypted_data}")
        
        if not has_content and not has_encrypted_data:
            print("Test: ❌ VALIDATION FAILED - Missing required fields")
            return jsonify({'success': False, 'error': 'Missing required fields: need either content or encrypted_data'})
        else:
            print("Test: ✅ VALIDATION PASSED - Found required fields")
            return jsonify({'success': True, 'message': 'Test validation passed - would send message'})
    
    except Exception as e:
        print(f"Error in test_send_message: {str(e)}")
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
        other = conv['other_user']
        last = conv['last_message']

        # Build a safe preview
        if last:
            if last.is_encrypted:
                preview = '[Encrypted Message - Decrypting...]'
            else:
                raw = last.content or ''
                preview = (raw[:50] + '...') if len(raw) > 50 else raw
            ts = last.timestamp.isoformat()
            sender = last.sender_id
        else:
            preview, ts, sender = '', '', None

        conversations_data.append({
            'other_user_id': other.id,
            'other_user_name': other.profile.name
                if other.profile and other.profile.name
                else other.email,
            'other_user_photo': other.profile.photo
                if other.profile and other.profile.photo
                else 'default.jpg',
            'last_message': {
                'content': preview,
                'timestamp': ts,
                'sender_id': sender
            },
            'unread_count': conv['unread_count']
        })

    return jsonify({'conversations': conversations_data})


@messaging_bp.route('/api/messages/<int:user_id>')
@login_required
def api_messages(user_id):
    """API endpoint to get messages with a specific user - handles encrypted content"""
    current_user_id = session['user_id']
    messages = MessageController.get_conversation_messages(current_user_id, user_id)
    
    messages_data = []
    for message in messages:
        message_data = MessageController.serialize_message_for_client(message)
        messages_data.append(message_data)
    
    return jsonify({'messages': messages_data})


@messaging_bp.route('/stats')
@login_required
def messaging_stats():
    """Get messaging statistics for current user"""
    user_id = session['user_id']
    stats = MessageController.get_message_statistics(user_id)
    return jsonify(stats)


@messaging_bp.route('/debug-test')
def debug_test():
    """Simple test route to verify blueprint is working"""
    return jsonify({'status': 'OK', 'message': 'Messaging blueprint is working'})


@messaging_bp.route('/conversation-key-info/<int:user_id>')
@login_required
def get_conversation_key_info(user_id):
    """Get key exchange information for a conversation"""
    try:
        current_user_id = session['user_id']
        
        # Verify the other user exists
        other_user = User.query.get(user_id)
        if not other_user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Get key information (metadata only, not the actual key)
        key_info = MessageController.get_conversation_key_info(current_user_id, user_id)
        
        return jsonify({
            'success': True,
            'key_info': key_info,
            'current_user_id': current_user_id,
            'other_user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@messaging_bp.route('/generate-conversation-key/<int:user_id>', methods=['POST'])
@login_required
def generate_conversation_key(user_id):
    """Generate or get existing conversation encryption key"""
    try:
        current_user_id = session['user_id']
        
        # Verify the other user exists
        other_user = User.query.get(user_id)
        if not other_user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Generate or get existing key
        success, result = MessageController.ensure_conversation_key(current_user_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'key_id': result['key_id'],
                'algorithm': result['algorithm'],
                'created_at': result['created_at'].isoformat() if result['created_at'] else None
            })
        else:
            return jsonify({'success': False, 'error': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
