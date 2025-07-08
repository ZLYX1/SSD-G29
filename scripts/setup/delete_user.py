#!/usr/bin/env python3
"""
Interactive script to delete users and all their associated data
Usage:
  python delete_user.py                    # Interactive mode
  python delete_user.py --all              # Delete all users (non-interactive)
  python delete_user.py --email user@test.com  # Delete specific user by email
  python delete_user.py --ids 1,2,3        # Delete users by IDs
"""
import sys
import os
import argparse
sys.path.append('/app')

# Check if running in a TTY (interactive terminal)
def is_interactive():
    return sys.stdin.isatty()

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

def non_interactive_delete(all_users=False, email=None, ids=None):
    """Non-interactive user deletion mode"""
    with app.app_context():
        if all_users:
            # Delete all users
            users = User.query.all()
            for user in users:
                delete_user_completely(user)
            db.session.commit()
            print(f"✅ Successfully deleted all users!")
            print(f"📊 Remaining users in database: {User.query.count()}")
        elif email:
            # Delete user by email
            user = User.query.filter_by(email=email).first()
            if user:
                delete_user_completely(user)
                db.session.commit()
                print(f"✅ Successfully deleted user {email}")
            else:
                print(f"❌ User with email {email} not found")
        elif ids:
            # Delete users by IDs
            user_ids = [int(id_str) for id_str in ids.split(',')]
            users = User.query.filter(User.id.in_(user_ids)).all()
            for user in users:
                delete_user_completely(user)
            db.session.commit()
            print(f"✅ Successfully deleted users with IDs: {ids}")
            print(f"📊 Remaining users in database: {User.query.count()}")
        else:
            print("❌ No valid options provided for deletion")

def delete_user_by_email(email):
    """Delete a user by email address"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ User with email '{email}' not found!")
            return False
        
        print(f"🔍 Found user: {user.email} (ID: {user.id})")
        delete_user_completely(user)
        db.session.commit()
        print(f"✅ Successfully deleted user: {email}")
        return True

def delete_users_by_ids(user_ids):
    """Delete users by their IDs"""
    with app.app_context():
        deleted_count = 0
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user:
                print(f"🔍 Found user: {user.email} (ID: {user.id})")
                delete_user_completely(user)
                deleted_count += 1
            else:
                print(f"❌ User with ID {user_id} not found!")
        
        if deleted_count > 0:
            db.session.commit()
            print(f"✅ Successfully deleted {deleted_count} users!")
        return deleted_count

def delete_all_users_non_interactive():
    """Delete all users without confirmation (for automated scripts)"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("❌ No users found in database")
            return 0
        
        print(f"🗑️ Deleting all {len(users)} users...")
        for user in users:
            delete_user_completely(user)
        
        db.session.commit()
        print(f"✅ Successfully deleted all {len(users)} users!")
        return len(users)

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Delete users and all their associated data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python delete_user.py                           # Interactive mode
  python delete_user.py --all                     # Delete all users
  python delete_user.py --email user@example.com  # Delete specific user
  python delete_user.py --ids 1,2,3               # Delete users by IDs
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Delete all users (non-interactive)')
    parser.add_argument('--email', type=str, 
                       help='Delete user by email address')
    parser.add_argument('--ids', type=str, 
                       help='Delete users by IDs (comma-separated)')
    parser.add_argument('--force', action='store_true', 
                       help='Skip confirmations (use with caution)')
    
    args = parser.parse_args()
    
    # If no arguments provided and running interactively, use interactive mode
    if not any(vars(args).values()) and is_interactive():
        print("🚀 Interactive User Deletion Tool")
        print("=" * 50)
        interactive_delete()
        return
    
    # Handle non-interactive modes
    if args.all:
        if not args.force and is_interactive():
            confirm = input("⚠️ Delete ALL users? Type 'DELETE_ALL' to confirm: ")
            if confirm != 'DELETE_ALL':
                print("❌ Deletion cancelled")
                return
        delete_all_users_non_interactive()
    
    elif args.email:
        if not args.force and is_interactive():
            confirm = input(f"⚠️ Delete user '{args.email}'? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Deletion cancelled")
                return
        delete_user_by_email(args.email)
    
    elif args.ids:
        try:
            user_ids = [int(id.strip()) for id in args.ids.split(',')]
            if not args.force and is_interactive():
                confirm = input(f"⚠️ Delete users with IDs {user_ids}? (yes/no): ").strip().lower()
                if confirm != 'yes':
                    print("❌ Deletion cancelled")
                    return
            delete_users_by_ids(user_ids)
        except ValueError:
            print("❌ Invalid user IDs. Please provide comma-separated numbers.")
    
    else:
        print("❌ No valid operation specified. Use --help for usage information.")
        if not is_interactive():
            print("🔍 Running in non-interactive mode. Use command line arguments.")

if __name__ == "__main__":
    main()