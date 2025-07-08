#!/usr/bin/env python3
"""
Interactive script to delete users and all their associated data
"""
import sys
import os
sys.path.append('/app')

from app import app
from blueprint.models import User, Profile, Booking, Payment, Report, Rating, Message, db

def delete_user_completely(user):
    """Delete a user and all their associated data"""
    user_id = user.id
    email = user.email
    print(f"🔍 Deleting user: {email} (ID: {user_id})")
    
    # Delete associated data in proper order (to handle foreign key constraints)
    
    # 1. Delete ratings given by this user
    ratings_given = Rating.query.filter_by(reviewer_id=user_id).all()
    for rating in ratings_given:
        db.session.delete(rating)
    print(f"   - Deleted {len(ratings_given)} ratings given by user")
    
    # 2. Delete ratings received by this user
    ratings_received = Rating.query.filter_by(reviewed_id=user_id).all()
    for rating in ratings_received:
        db.session.delete(rating)
    print(f"   - Deleted {len(ratings_received)} ratings received by user")
    
    # 3. Delete messages sent by this user
    messages_sent = Message.query.filter_by(sender_id=user_id).all()
    for message in messages_sent:
        db.session.delete(message)
    print(f"   - Deleted {len(messages_sent)} messages sent by user")
    
    # 4. Delete messages received by this user
    messages_received = Message.query.filter_by(recipient_id=user_id).all()
    for message in messages_received:
        db.session.delete(message)
    print(f"   - Deleted {len(messages_received)} messages received by user")
    
    # 5. Delete reports made by this user
    reports_made = Report.query.filter_by(reporter_id=user_id).all()
    for report in reports_made:
        db.session.delete(report)
    print(f"   - Deleted {len(reports_made)} reports made by user")
    
    # 6. Delete reports made against this user
    reports_against = Report.query.filter_by(reported_id=user_id).all()
    for report in reports_against:
        db.session.delete(report)
    print(f"   - Deleted {len(reports_against)} reports against user")
    
    # 7. Delete payments made by this user
    payments = Payment.query.filter_by(user_id=user_id).all()
    for payment in payments:
        db.session.delete(payment)
    print(f"   - Deleted {len(payments)} payments by user")
    
    # 8. Delete bookings where user is seeker
    bookings_as_seeker = Booking.query.filter_by(seeker_id=user_id).all()
    for booking in bookings_as_seeker:
        db.session.delete(booking)
    print(f"   - Deleted {len(bookings_as_seeker)} bookings as seeker")
    
    # 9. Delete bookings where user is escort
    bookings_as_escort = Booking.query.filter_by(escort_id=user_id).all()
    for booking in bookings_as_escort:
        db.session.delete(booking)
    print(f"   - Deleted {len(bookings_as_escort)} bookings as escort")
    
    # 10. Delete TimeSlots if user is escort
    from blueprint.models import TimeSlot
    time_slots = TimeSlot.query.filter_by(user_id=user_id).all()
    for slot in time_slots:
        db.session.delete(slot)
    print(f"   - Deleted {len(time_slots)} time slots")
    
    # 11. Delete user profile
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        db.session.delete(profile)
        print(f"   - Deleted user profile")
    
    # 12. Finally, delete the user
    db.session.delete(user)
    
    print(f"✅ Successfully deleted user {email}")

def list_all_users():
    """List all users in the database"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("❌ No users found in database")
            return []
        
        print(f"\n📋 Found {len(users)} users in database:")
        print("=" * 80)
        print(f"{'No.':<4} {'ID':<4} {'Email':<30} {'Role':<10} {'Active':<8} {'Verified':<8}")
        print("-" * 80)
        
        for i, user in enumerate(users, 1):
            print(f"{i:<4} {user.id:<4} {user.email:<30} {user.role:<10} {user.active:<8} {user.email_verified:<8}")
        
        print("=" * 80)
        return users

def interactive_delete():
    """Interactive user deletion interface"""
    with app.app_context():
        while True:
            users = list_all_users()
            
            if not users:
                break
            
            print("\n🔧 Options:")
            print("• Enter user numbers (1, 2, 3) to delete specific users")
            print("• Enter 'all' to delete all users")
            print("• Enter 'q' or 'quit' to exit")
            
            choice = input("\n👉 Your choice: ").strip().lower()
            
            if choice in ['q', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif choice == 'all':
                confirm = input(f"⚠️  Are you sure you want to delete ALL {len(users)} users? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    print("\n🗑️  Deleting all users...")
                    for user in users:
                        delete_user_completely(user)
                    db.session.commit()
                    print(f"\n✅ Successfully deleted all users!")
                    print(f"📊 Remaining users in database: {User.query.count()}")
                else:
                    print("❌ Deletion cancelled")
            else:
                # Parse user numbers
                try:
                    user_numbers = []
                    for num_str in choice.replace(',', ' ').split():
                        num = int(num_str.strip())
                        if 1 <= num <= len(users):
                            user_numbers.append(num)
                        else:
                            print(f"❌ Invalid user number: {num}")
                            raise ValueError
                    
                    if not user_numbers:
                        print("❌ No valid user numbers provided")
                        continue
                    
                    # Show selected users
                    selected_users = [users[num - 1] for num in user_numbers]
                    print(f"\n📋 Selected users for deletion:")
                    for i, user in enumerate(selected_users, 1):
                        print(f"  {i}. {user.email} (ID: {user.id})")
                    
                    confirm = input(f"\n⚠️  Are you sure you want to delete these {len(selected_users)} users? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        print("\n🗑️  Deleting selected users...")
                        for user in selected_users:
                            delete_user_completely(user)
                        db.session.commit()
                        print(f"\n✅ Successfully deleted {len(selected_users)} users!")
                        print(f"📊 Remaining users in database: {User.query.count()}")
                    else:
                        print("❌ Deletion cancelled")
                        
                except ValueError:
                    print("❌ Invalid input. Please enter valid user numbers (e.g., 1, 2, 3) or 'all'")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            print("\n" + "=" * 50)

if __name__ == "__main__":
    print("🚀 Interactive User Deletion Tool")
    print("=" * 50)
    interactive_delete()
