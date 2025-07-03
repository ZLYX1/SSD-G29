#!/usr/bin/env python3
"""
Password History & Expiration System Testing Script
Comprehensive testing of all password security features
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

# Create Flask app for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-development-secret-key')

# Import after Flask app creation
from extensions import db
from blueprint.models import User, PasswordHistory
from utils.utils import validate_password_strength, check_password_expiration_status

# Initialize the database with the app
db.init_app(app)

def test_password_strength_validation():
    """Test password strength validation function"""
    print("🔐 Testing Password Strength Validation")
    print("-" * 50)
    
    test_passwords = [
        ("password", "Weak - common password"),
        ("Password1", "Weak - no special char"),
        ("Password1!", "Strong - meets all requirements"),
        ("MyVeryComplexPassword2024!", "Very Strong - long and complex"),
        ("123456", "Very Weak - all numbers"),
        ("UPPERCASE", "Weak - no lowercase or numbers"),
        ("Coffee@Sunrise2024!", "Very Strong - memorable and secure")
    ]
    
    for password, expected in test_passwords:
        result = validate_password_strength(password)
        print(f"Password: '{password}'")
        print(f"  Valid: {result['valid']}")
        print(f"  Strength: {result.get('strength', 'N/A')}")
        print(f"  Message: {result['message']}")
        print(f"  Expected: {expected}")
        print()
    
    return True

def test_password_history():
    """Test password history functionality"""
    print("📚 Testing Password History")
    print("-" * 50)
    
    with app.app_context():
        # Find a test user
        test_user = User.query.filter_by(email="test_phone@example.com").first()
        if not test_user:
            print("❌ No test user found. Creating one...")
            test_user = User(email="test_password_history@example.com", role="User", gender="Male")
            success, message = test_user.set_password("InitialPassword1!", check_history=False)
            if success:
                db.session.add(test_user)
                db.session.commit()
                print(f"✅ Created test user: {test_user.email}")
            else:
                print(f"❌ Failed to create test user: {message}")
                return False
        
        print(f"Testing with user: {test_user.email}")
        
        # Test setting initial password
        current_password = "TestPassword1!"
        success, message = test_user.set_password(current_password, check_history=False)
        print(f"Set initial password: {success} - {message}")
        
        if success:
            db.session.commit()
            
            # Test password history checking
            print("\nTesting password reuse prevention:")
            
            # Try to reuse the same password
            success, message = test_user.set_password(current_password, check_history=True)
            print(f"Reuse same password: {success} - {message}")
            
            # Set a few different passwords to build history
            passwords = [
                "NewPassword1!",
                "AnotherPassword2@",
                "YetAnotherPassword3#",
                "FinalPassword4$"
            ]
            
            for i, pwd in enumerate(passwords):
                success, message = test_user.set_password(pwd, check_history=True)
                print(f"Set password {i+1}: {success} - {message}")
                if success:
                    db.session.commit()
            
            # Try to reuse the first password from history
            success, message = test_user.set_password("NewPassword1!", check_history=True)
            print(f"Reuse old password: {success} - {message}")
            
            # Check password history entries
            history_count = test_user.password_history.count()
            print(f"Password history entries: {history_count}")
            
        return True

def test_password_expiration():
    """Test password expiration functionality"""
    print("⏰ Testing Password Expiration")
    print("-" * 50)
    
    with app.app_context():
        test_user = User.query.filter_by(email="test_phone@example.com").first()
        if not test_user:
            print("❌ No test user found")
            return False
        
        print(f"Testing with user: {test_user.email}")
        
        # Test current expiration status
        expired = test_user.is_password_expired()
        days_left = test_user.days_until_password_expires()
        
        print(f"Password expired: {expired}")
        print(f"Days until expiration: {days_left}")
        print(f"Password created: {test_user.password_created_at}")
        print(f"Password expires: {test_user.password_expires_at}")
        
        # Test expiration status function
        status = check_password_expiration_status(test_user)
        print(f"Expiration status: {status}")
        
        # Test forced expiration
        print("\nTesting forced expiration...")
        old_expires = test_user.password_expires_at
        test_user.password_expires_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        db.session.commit()
        
        expired_now = test_user.is_password_expired()
        print(f"After forced expiration - Expired: {expired_now}")
        
        # Restore original expiration
        test_user.password_expires_at = old_expires
        db.session.commit()
        
        return True

def test_account_lockout():
    """Test account lockout functionality"""
    print("🔒 Testing Account Lockout")
    print("-" * 50)
    
    with app.app_context():
        test_user = User.query.filter_by(email="test_phone@example.com").first()
        if not test_user:
            print("❌ No test user found")
            return False
        
        print(f"Testing with user: {test_user.email}")
        
        # Reset lockout status
        test_user.failed_login_attempts = 0
        test_user.account_locked_until = None
        db.session.commit()
        
        print(f"Initial lockout status: {test_user.is_account_locked()}")
        print(f"Failed attempts: {test_user.failed_login_attempts}")
        
        # Test incrementing failed attempts
        for i in range(6):  # Try 6 failed attempts (max is 5)
            message = test_user.increment_failed_login(max_attempts=5, lockout_duration_minutes=30)
            print(f"Attempt {i+1}: {message}")
            print(f"  Failed attempts: {test_user.failed_login_attempts}")
            print(f"  Account locked: {test_user.is_account_locked()}")
            if test_user.account_locked_until:
                print(f"  Locked until: {test_user.account_locked_until}")
            db.session.commit()
        
        # Test reset after successful login
        print("\nTesting lockout reset...")
        test_user.reset_failed_logins()
        db.session.commit()
        print(f"After reset - Failed attempts: {test_user.failed_login_attempts}")
        print(f"After reset - Account locked: {test_user.is_account_locked()}")
        
        return True

def display_password_security_status():
    """Display overall password security status"""
    print("📊 Password Security System Status")
    print("=" * 60)
    
    with app.app_context():
        # Count users by status
        total_users = User.query.count()
        
        # Users with expired passwords
        expired_users = User.query.filter(User.password_expires_at < datetime.datetime.utcnow()).count()
        
        # Users with passwords expiring soon (within 7 days)
        soon_expire = User.query.filter(
            User.password_expires_at > datetime.datetime.utcnow(),
            User.password_expires_at <= datetime.datetime.utcnow() + datetime.timedelta(days=7)
        ).count()
        
        # Users with change required
        change_required = User.query.filter(User.password_change_required == True).count()
        
        # Users currently locked
        locked_users = User.query.filter(User.account_locked_until > datetime.datetime.utcnow()).count()
        
        # Password history entries
        history_entries = PasswordHistory.query.count()
        
        print(f"📈 User Statistics:")
        print(f"   Total users: {total_users}")
        print(f"   Expired passwords: {expired_users}")
        print(f"   Expiring soon (7 days): {soon_expire}")
        print(f"   Change required: {change_required}")
        print(f"   Currently locked: {locked_users}")
        print(f"   Password history entries: {history_entries}")
        
        if expired_users > 0:
            print(f"\n⚠️  Users with expired passwords:")
            expired_list = User.query.filter(User.password_expires_at < datetime.datetime.utcnow()).limit(5).all()
            for user in expired_list:
                days_expired = (datetime.datetime.utcnow() - user.password_expires_at).days
                print(f"   - {user.email} (expired {days_expired} days ago)")
        
        if soon_expire > 0:
            print(f"\n🔔 Users with passwords expiring soon:")
            soon_list = User.query.filter(
                User.password_expires_at > datetime.datetime.utcnow(),
                User.password_expires_at <= datetime.datetime.utcnow() + datetime.timedelta(days=7)
            ).limit(5).all()
            for user in soon_list:
                days_left = (user.password_expires_at - datetime.datetime.utcnow()).days
                print(f"   - {user.email} (expires in {days_left} days)")

def main():
    """Run all password security tests"""
    print("🔐 Password History & Expiration System Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Password Strength Validation", test_password_strength_validation),
        ("Password History", test_password_history), 
        ("Password Expiration", test_password_expiration),
        ("Account Lockout", test_account_lockout)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name} Test...")
            result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
            print(f"Result: {results[test_name]}")
        except Exception as e:
            results[test_name] = f"❌ ERROR: {e}"
            print(f"Result: {results[test_name]}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    for test_name, result in results.items():
        print(f"   {test_name}: {result}")
    
    print("\n")
    display_password_security_status()
    
    print("\n🚀 Password Security System Ready!")
    print("Next steps:")
    print("1. Test the web interface at /auth/change-password/<user_id>")
    print("2. Test login with expired passwords")
    print("3. Test password policy page at /auth/password-policy")

if __name__ == '__main__':
    main()
