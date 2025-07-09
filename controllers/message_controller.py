from flask import session, jsonify
from blueprint.models import db, User, Message, Profile, Report
from sqlalchemy import or_, and_, desc
from datetime import datetime
from utils.encryption_utils import MessageEncryption, ConversationKeyManager


class MessageController:
    @staticmethod
    def get_user_conversations(user_id):
        """Get all conversations for a user with the last message and unread count"""
        conversations = []
        
        # Get all unique conversations (users we've messaged with)
        conversation_users = db.session.query(
            User.id.label('other_user_id')
        ).join(
            Message, 
            or_(
                and_(Message.sender_id == User.id, Message.recipient_id == user_id),
                and_(Message.recipient_id == User.id, Message.sender_id == user_id)
            )
        ).filter(
            User.id != user_id
        ).distinct().all()
        
        for conv_user in conversation_users:
            other_user = User.query.get(conv_user.other_user_id)
            if not other_user:
                continue
                
            # Get last message in conversation
            last_message = Message.query.filter(
                or_(
                    and_(Message.sender_id == user_id, Message.recipient_id == other_user.id),
                    and_(Message.sender_id == other_user.id, Message.recipient_id == user_id)
                )
            ).order_by(desc(Message.timestamp)).first()
            
            # Count unread messages from this user
            unread_count = Message.query.filter(
                and_(
                    Message.sender_id == other_user.id,
                    Message.recipient_id == user_id,
                    Message.is_read == False
                )
            ).count()
            
            conversations.append({
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': unread_count
            })
        
        # Sort by last message timestamp
        conversations.sort(
            key=lambda x: x['last_message'].timestamp if x['last_message'] else datetime.min,
            reverse=True
        )
        
        return conversations
    
    @staticmethod
    def get_conversation_messages(user_id, other_user_id, limit=50):
        """Get messages between two users"""
        messages = Message.query.filter(
            or_(
                and_(Message.sender_id == user_id, Message.recipient_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.recipient_id == user_id)
            )
        ).order_by(Message.timestamp.asc()).limit(limit).all()
        
        # Mark messages as read
        Message.query.filter(
            and_(
                Message.sender_id == other_user_id,
                Message.recipient_id == user_id,
                Message.is_read == False
            )
        ).update({'is_read': True})
        db.session.commit()
        
        return messages
    
    @staticmethod
    def send_message(sender_id, recipient_id, content=None, encrypted_data=None):
        """
        Send a message between users - supports both plain text and encrypted content
        
        Args:
            sender_id: ID of sender
            recipient_id: ID of recipient  
            content: Plain text message (for backwards compatibility)
            encrypted_data: Encrypted message data (dict with encrypted_content, nonce, algorithm)
        """
        try:
            # Validate recipient exists
            recipient = User.query.get(recipient_id)
            if not recipient:
                return False, "Recipient not found"
            
            # Check if sender is trying to message themselves
            if sender_id == recipient_id:
                return False, "Cannot send message to yourself"
            
            # Validate input - must have either content or encrypted_data
            has_content = content and content.strip()
            has_encrypted_data = (encrypted_data and 
                                isinstance(encrypted_data, dict) and 
                                bool(encrypted_data.get('encrypted_content')))
            
            print(f"🔧 MessageController: Input validation:")
            print(f"  - content: {repr(content)} -> has_content: {has_content}")
            print(f"  - encrypted_data: {repr(encrypted_data)} -> has_encrypted_data: {has_encrypted_data}")
            
            if not has_content and not has_encrypted_data:
                return False, "No message content provided"
            
            if has_content and has_encrypted_data:
                return False, "Cannot send both plain text and encrypted content"
            
            # Create message
            message = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                timestamp=datetime.utcnow()
            )
            
            # Handle encrypted content
            if encrypted_data:
                print(f"🔧 MessageController: Processing encrypted data: {encrypted_data}")
                # Extract encrypted fields from the dictionary
                encrypted_content = encrypted_data.get('encrypted_content')
                nonce = encrypted_data.get('nonce')
                algorithm = encrypted_data.get('algorithm')
                
                print(f"🔧 MessageController: Extracted fields - content: {bool(encrypted_content)}, nonce: {bool(nonce)}, algorithm: {algorithm}")
                
                # Validate we have all required fields
                if not all([encrypted_content, nonce, algorithm]):
                    print(f"❌ MessageController: Missing encrypted fields - content: {encrypted_content}, nonce: {nonce}, algorithm: {algorithm}")
                    return False, "Missing required encrypted data fields"
                
                # Create validation structure
                encrypted_msg = {
                    'encrypted_content': encrypted_content,
                    'nonce': nonce,
                    'algorithm': algorithm
                }
                
                print(f"🔧 MessageController: Validation structure: {encrypted_msg}")
                
                # Validate encrypted data format
                is_valid, validation_msg = MessageEncryption.validate_encrypted_message(encrypted_msg)
                print(f"🔧 MessageController: Validation result - valid: {is_valid}, message: {validation_msg}")
                if not is_valid:
                    return False, f"Invalid encrypted data: {validation_msg}"
                
                # Set encrypted content
                message.set_encrypted_content(encrypted_msg)
            else:
                # Handle plain text content (backwards compatibility)
                message.content = content.strip()
                message.is_encrypted = False
            
            db.session.add(message)
            db.session.commit()
            
            return True, message
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_available_users(current_user_id):
        """Get users that can be messaged (excluding current user)"""
        return User.query.filter(
            and_(
                User.id != current_user_id,
                User.active == True
            )
        ).all()
    
    @staticmethod
    def report_user(reporter_id, reported_id, reason, details=None):
        """Report a user for inappropriate behavior"""
        try:
            # Check if user exists
            reported_user = User.query.get(reported_id)
            if not reported_user:
                return False, "User not found"
            
            # Check if already reported recently
            existing_report = Report.query.filter(
                and_(
                    Report.reporter_id == reporter_id,
                    Report.reported_id == reported_id,
                    Report.status == 'Pending Review'
                )
            ).first()
            
            if existing_report:
                return False, "You have already reported this user"
            
            # Create report
            report = Report(
                reporter_id=reporter_id,
                reported_id=reported_id,
                reason=f"{reason}: {details}" if details else reason,
                status='Pending Review'
            )
            
            db.session.add(report)
            db.session.commit()
            
            return True, "Report submitted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def delete_conversation(user_id, other_user_id):
        """Soft delete a conversation for a user"""
        try:
            # Mark messages as deleted for this user
            messages_as_sender = Message.query.filter(
                and_(
                    Message.sender_id == user_id,
                    Message.recipient_id == other_user_id
                )
            )
            
            messages_as_recipient = Message.query.filter(
                and_(
                    Message.sender_id == other_user_id,
                    Message.recipient_id == user_id
                )
            )
            
            # Update deletion flags
            for message in messages_as_sender:
                message.deleted_by_sender = True
            
            for message in messages_as_recipient:
                message.deleted_by_recipient = True
            
            db.session.commit()
            return True, "Conversation deleted"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_message_statistics(user_id):
        """Get messaging statistics for a user"""
        try:
            total_sent = Message.query.filter(Message.sender_id == user_id).count()
            total_received = Message.query.filter(Message.recipient_id == user_id).count()
            unread_count = Message.query.filter(
                and_(
                    Message.recipient_id == user_id,
                    Message.is_read == False
                )
            ).count()
            
            return {
                'total_sent': total_sent,
                'total_received': total_received,
                'unread_count': unread_count,
                'total_conversations': len(MessageController.get_user_conversations(user_id))
            }
        except Exception as e:
            return {
                'total_sent': 0,
                'total_received': 0,
                'unread_count': 0,
                'total_conversations': 0
            }
    
    @staticmethod
    def serialize_message_for_client(message):
        """
        Serialize message for client-side display
        Returns encrypted data for encrypted messages, plain text for non-encrypted
        """
        base_data = {
            'id': message.id,
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id,
            'timestamp': message.timestamp.strftime('%m/%d %H:%M'),
            'is_read': message.is_read,
            'is_encrypted': message.is_encrypted
        }
        
        # Add content based on encryption status
        if message.is_encrypted:
            base_data.update({
                'encrypted_content': message.encrypted_content,
                'nonce': message.encryption_nonce,
                'algorithm': message.encryption_algorithm,
                'content': '[Encrypted Message]'  # Placeholder for server logs
            })
        else:
            base_data['content'] = message.content
        
        return base_data
    
    @staticmethod
    def get_conversation_key_info(user1_id, user2_id):
        """
        Get key information for a conversation between two users
        This doesn't return the actual key (for security) but provides metadata
        """
        return ConversationKeyManager.create_key_exchange_data(user1_id, user2_id)
    
    @staticmethod
    def ensure_conversation_key(user1_id, user2_id):
        """
        Ensure a conversation key exists between two users
        """
        return ConversationKeyManager.ensure_conversation_key(user1_id, user2_id)
    
    @staticmethod
    def get_last_message_preview(message):
        """
        Get a preview of the last message for conversation list
        Handles both encrypted and plain text messages
        """
        if not message:
            return ''
        
        if message.is_encrypted:
            return '[Encrypted Message]'
        
        if message.content:
            return message.content[:50] + '...' if len(message.content) > 50 else message.content
        
        return ''
