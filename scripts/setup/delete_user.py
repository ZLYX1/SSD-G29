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

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Check if running in a TTY (interactive terminal)
def is_interactive():
    return sys.stdin.isatty()

from app import app

def delete_user_completely(user_id, email):
    """Delete a user and all their associated data using raw SQL"""
    print(f"🔍 Deleting user: {email} (ID: {user_id})")
    
    with app.app_context():
        from extensions import db
        from sqlalchemy import text
        
        # Start a new transaction
        db.session.rollback()  # Clear any existing transaction
        
        # Delete associated data in the correct order to handle foreign key constraints
        delete_queries = [
            ("password_history", "user_id"),
            ("time_slot", "user_id"),
            ("payment", "user_id"),
            ("report", "reporter_id"),
            ("report", "reported_id"),
            ("report", "assigned_admin_id"),
            ("message", "sender_id"),
            ("message", "recipient_id"),
            ("favourite", "user_id"),
            ("favourite", "favourite_user_id"),
            ("audit_log", "user_id"),
            ("favourites", "user_id"),
            ("favourites", "favourite_user_id"),
            ("conversation_key", "user1_id"),
            ("conversation_key", "user2_id"),
            ("rating", "reviewer_id"),
            ("rating", "reviewed_id"),
            ("booking", "seeker_id"),
            ("booking", "escort_id"),
            ("profile", "user_id"),
            ("user", "id")
        ]
        
        try:
            total_deleted = 0
            for table, column in delete_queries:
                try:
                    result = db.session.execute(
                        text(f"DELETE FROM public.{table} WHERE {column} = :user_id"),
                        {"user_id": user_id}
                    )
                    if result.rowcount > 0:
                        print(f"   - Deleted {result.rowcount} records from {table} (column: {column})")
                        total_deleted += result.rowcount
                except Exception as e:
                    # Table or column might not exist, continue
                    print(f"   - Warning: Could not delete from {table}.{column}: {e}")
                    continue
            
            # Commit the transaction immediately after deletion
            db.session.commit()
            print(f"✅ Successfully deleted user {email} (Total records deleted: {total_deleted})")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting user: {e}")
            return False

def list_all_users():
    """List all users in the database using raw SQL"""
    with app.app_context():
        from extensions import db
        from sqlalchemy import text
        
        users = db.session.execute(text("SELECT id, email, role, active, email_verified FROM public.user ORDER BY id")).fetchall()
        
        if not users:
            print("❌ No users found in database")
            return []
        
        print(f"\n📋 Found {len(users)} users in database:")
        print("=" * 80)
        print(f"{'No.':<4} {'ID':<4} {'Email':<30} {'Role':<10} {'Active':<8} {'Verified':<8}")
        print("-" * 80)
        
        for i, user in enumerate(users, 1):
            print(f"{i:<4} {user[0]:<4} {user[1]:<30} {user[2]:<10} {user[3]:<8} {user[4]:<8}")
        
        print("=" * 80)
        return users

def interactive_delete():
    """Interactive user deletion interface"""
    with app.app_context():
        from extensions import db
        from sqlalchemy import text
        
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
                        user_id, email = user[0], user[1]
                        delete_user_completely(user_id, email)
                    print(f"\n✅ Successfully deleted all users!")
                    # Get remaining user count
                    remaining = db.session.execute(text("SELECT COUNT(*) FROM public.user")).fetchone()[0]
                    print(f"📊 Remaining users in database: {remaining}")
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
                        print(f"  {i}. {user[1]} (ID: {user[0]})")
                    
                    confirm = input(f"\n⚠️  Are you sure you want to delete these {len(selected_users)} users? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        print("\n🗑️  Deleting selected users...")
                        for user in selected_users:
                            user_id, email = user[0], user[1]
                            delete_user_completely(user_id, email)
                        print(f"\n✅ Successfully deleted {len(selected_users)} users!")
                        # Get remaining user count
                        remaining = db.session.execute(text("SELECT COUNT(*) FROM public.user")).fetchone()[0]
                        print(f"📊 Remaining users in database: {remaining}")
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
        from extensions import db
        from sqlalchemy import text
        
        if all_users:
            # Delete all users
            users = db.session.execute(text("SELECT id, email FROM public.user")).fetchall()
            for user in users:
                user_id, user_email = user[0], user[1]
                delete_user_completely(user_id, user_email)
            print(f"✅ Successfully deleted all users!")
            remaining = db.session.execute(text("SELECT COUNT(*) FROM public.user")).fetchone()[0]
            print(f"📊 Remaining users in database: {remaining}")
        elif email:
            # Delete user by email
            user = db.session.execute(text("SELECT id, email FROM public.user WHERE email = :email"), {"email": email}).fetchone()
            if user:
                user_id, user_email = user[0], user[1]
                delete_user_completely(user_id, user_email)
                print(f"✅ Successfully deleted user {email}")
            else:
                print(f"❌ User with email {email} not found")
        elif ids:
            # Delete users by IDs
            user_ids = [int(id_str) for id_str in ids.split(',')]
            users = db.session.execute(text("SELECT id, email FROM public.user WHERE id = ANY(:ids)"), {"ids": user_ids}).fetchall()
            for user in users:
                user_id, user_email = user[0], user[1]
                delete_user_completely(user_id, user_email)
            print(f"✅ Successfully deleted users with IDs: {ids}")
            remaining = db.session.execute(text("SELECT COUNT(*) FROM public.user")).fetchone()[0]
            print(f"📊 Remaining users in database: {remaining}")
        else:
            print("❌ No valid options provided for deletion")

def delete_user_by_email(email):
    """Delete a user by email address"""
    with app.app_context():
        from extensions import db
        from sqlalchemy import text
        
        user = db.session.execute(text("SELECT id, email FROM public.user WHERE email = :email"), {"email": email}).fetchone()
        if not user:
            print(f"❌ User with email '{email}' not found!")
            return False
        
        user_id, user_email = user[0], user[1]
        print(f"🔍 Found user: {user_email} (ID: {user_id})")
        if delete_user_completely(user_id, user_email):
            print(f"✅ Successfully deleted user: {email}")
            return True
        else:
            return False

def delete_users_by_ids(user_ids):
    """Delete users by their IDs"""
    with app.app_context():
        from extensions import db
        from sqlalchemy import text
        
        deleted_count = 0
        for user_id in user_ids:
            user = db.session.execute(text("SELECT id, email FROM public.user WHERE id = :user_id"), {"user_id": user_id}).fetchone()
            if user:
                user_id, user_email = user[0], user[1]
                print(f"🔍 Found user: {user_email} (ID: {user_id})")
                if delete_user_completely(user_id, user_email):
                    deleted_count += 1
            else:
                print(f"❌ User with ID {user_id} not found!")
        
        if deleted_count > 0:
            print(f"✅ Successfully deleted {deleted_count} users!")
        return deleted_count

def delete_all_users_non_interactive():
    """Delete all users without confirmation (for automated scripts)"""
    with app.app_context():
        from extensions import db
        from sqlalchemy import text
        
        users = db.session.execute(text("SELECT id, email FROM public.user")).fetchall()
        if not users:
            print("❌ No users found in database")
            return 0
        
        print(f"🗑️ Deleting all {len(users)} users...")
        deleted_count = 0
        for user in users:
            user_id, user_email = user[0], user[1]
            if delete_user_completely(user_id, user_email):
                deleted_count += 1
        
        print(f"✅ Successfully deleted all {deleted_count} users!")
        return deleted_count

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