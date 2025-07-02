#!/usr/bin/env python3
"""
Database migration script for Password History & Expiration system
Adds password security fields to existing users
"""
import os
import sys
from flask import Flask
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app for migration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-development-secret-key')

# Import after Flask app creation
from extensions import db
from blueprint.models import User, PasswordHistory

# Initialize the database with the app
db.init_app(app)

def migrate_password_security():
    """Add password security fields and create PasswordHistory table"""
    print("🔄 Starting Password Security Migration")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Create PasswordHistory table if it doesn't exist
            print("1. Creating PasswordHistory table...")
            db.create_all()
            print("   ✅ PasswordHistory table ready")
            
            # Get all users
            users = User.query.all()
            print(f"\n2. Updating {len(users)} users with password security fields...")
            
            updated_count = 0
            for user in users:
                # Set password creation date if not set
                if not user.password_created_at:
                    user.password_created_at = user.created_at or datetime.datetime.utcnow()
                
                # Set password expiration (90 days from creation)
                if not user.password_expires_at:
                    user.password_expires_at = user.password_created_at + datetime.timedelta(days=90)
                
                # Initialize security counters if not set
                if user.failed_login_attempts is None:
                    user.failed_login_attempts = 0
                
                if user.password_change_required is None:
                    user.password_change_required = False
                
                # Check if password has expired and mark for required change
                if user.password_expires_at < datetime.datetime.utcnow():
                    user.password_change_required = True
                    print(f"   ⚠️  User {user.email}: Password expired, change required")
                
                updated_count += 1
            
            # Commit all changes
            db.session.commit()
            print(f"   ✅ Updated {updated_count} users")
            
            # Display migration summary
            print(f"\n3. Migration Summary:")
            print(f"   • PasswordHistory table: Created")
            print(f"   • Users updated: {updated_count}")
            
            # Check for users with expired passwords
            expired_users = User.query.filter(User.password_expires_at < datetime.datetime.utcnow()).all()
            print(f"   • Users with expired passwords: {len(expired_users)}")
            
            if expired_users:
                print("\n   Users requiring password change:")
                for user in expired_users:
                    days_expired = (datetime.datetime.utcnow() - user.password_expires_at).days
                    print(f"     - {user.email} (expired {days_expired} days ago)")
            
            # Check for users with passwords expiring soon
            soon_expire = User.query.filter(
                User.password_expires_at > datetime.datetime.utcnow(),
                User.password_expires_at <= datetime.datetime.utcnow() + datetime.timedelta(days=7)
            ).all()
            
            if soon_expire:
                print(f"\n   Users with passwords expiring within 7 days: {len(soon_expire)}")
                for user in soon_expire:
                    days_left = (user.password_expires_at - datetime.datetime.utcnow()).days
                    print(f"     - {user.email} (expires in {days_left} days)")
            
            print(f"\n🎉 Password Security Migration Completed Successfully!")
            print(f"=" * 60)
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
            
    return True

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying Migration...")
    print("-" * 40)
    
    with app.app_context():
        try:
            # Check if PasswordHistory table exists and is accessible
            password_histories = PasswordHistory.query.count()
            print(f"✅ PasswordHistory table accessible (entries: {password_histories})")
            
            # Check user fields
            users = User.query.all()
            users_with_expiry = User.query.filter(User.password_expires_at.isnot(None)).count()
            users_with_creation_date = User.query.filter(User.password_created_at.isnot(None)).count()
            
            print(f"✅ Users with password expiration date: {users_with_expiry}/{len(users)}")
            print(f"✅ Users with password creation date: {users_with_creation_date}/{len(users)}")
            
            # Test password security methods
            if users:
                test_user = users[0]
                try:
                    expired = test_user.is_password_expired()
                    days_left = test_user.days_until_password_expires()
                    locked = test_user.is_account_locked()
                    print(f"✅ Password security methods working")
                except Exception as e:
                    print(f"❌ Password security methods error: {e}")
                    return False
            
            print("✅ Migration verification successful!")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

if __name__ == '__main__':
    print("🔒 Password History & Expiration System Migration")
    print("This will add password security features to your application.")
    print()
    
    # Run migration
    if migrate_password_security():
        # Verify migration
        if verify_migration():
            print("\n🎯 Next Steps:")
            print("1. Test password change functionality")
            print("2. Test login with expired passwords")
            print("3. Verify password history checking")
            print("4. Review password policy settings")
        else:
            print("\n⚠️  Migration completed but verification failed.")
            print("Please check the database manually.")
    else:
        print("\n❌ Migration failed. Please check errors and try again.")
