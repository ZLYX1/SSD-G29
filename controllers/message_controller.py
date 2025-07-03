from flask import session, jsonify
from blueprint.models import db, User, Message, Profile, Report
from sqlalchemy import or_, and_, desc
from datetime import datetime


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
    def send_message(sender_id, recipient_id, content):
        """Send a message between users"""
        try:
            # Validate recipient exists
            recipient = User.query.get(recipient_id)
            if not recipient:
                return False, "Recipient not found"
            
            # Check if sender is trying to message themselves
            if sender_id == recipient_id:
                return False, "Cannot send message to yourself"
            
            # Create message
            message = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content.strip(),
                timestamp=datetime.utcnow()
            )
            
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
