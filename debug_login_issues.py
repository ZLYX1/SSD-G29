#!/usr/bin/env python3
"""
Debug login issues - Check user accounts and authentication
"""

import sys
import os
sys.path.append('/app')

from config.db_config import DBConfig
from blueprint.models import User, Profile
from extensions import db
from werkzeug.security import check_password_hash
import traceback

def check_user_accounts():
    """Check what user accounts exist and their status"""
    print("🔍 Checking user accounts in database...")
    
    try:
        # Get all users
        users = User.query.all()
        print(f"\n📊 Found {len(users)} total users in database")
        
        # Check common test accounts
        test_accounts = [
            'seeker@example.com',
            'seeker1@example.com', 
            'escort@example.com',
            'admin@example.com',
            'testuser1@example.com',
            'testuser2@example.com'
        ]
        
        print("\n🔍 Checking test accounts:")
        for email in test_accounts:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"✅ {email}")
                print(f"   - ID: {user.id}")
                print(f"   - Active: {getattr(user, 'active', 'N/A')}")
                print(f"   - Verified: {getattr(user, 'is_verified', 'N/A')}")
                print(f"   - Locked: {getattr(user, 'account_locked', 'N/A')}")
                print(f"   - Password Hash: {user.password_hash[:20]}..." if user.password_hash else "   - No password hash!")
                
                # Test password verification
                try:
                    test_password = "password123"
                    if check_password_hash(user.password_hash, test_password):
                        print(f"   - Password 'password123': ✅ VALID")
                    else:
                        print(f"   - Password 'password123': ❌ INVALID")
                        
                    # Try other common passwords
                    for pwd in ["TestPassword123!", "password", "123456"]:
                        if check_password_hash(user.password_hash, pwd):
                            print(f"   - Password '{pwd}': ✅ VALID")
                            break
                    else:
                        print(f"   - No common passwords work")
                        
                except Exception as e:
                    print(f"   - Password check error: {e}")
                
            else:
                print(f"❌ {email} - NOT FOUND")
        
        # Show first few users for reference
        print(f"\n📋 First 5 users in database:")
        for user in users[:5]:
            print(f"   - {user.email} (ID: {user.id})")
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        traceback.print_exc()

def check_authentication_system():
    """Check if authentication system is working"""
    print("\n🔍 Checking authentication system...")
    
    try:
        # Import auth controller
        from controllers.auth_controller import AuthController
        print("✅ AuthController imported successfully")
        
        # Check if we can create a test user
        test_email = "debug_test@example.com"
        
        # Clean up any existing test user
        existing = User.query.filter_by(email=test_email).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print(f"🧹 Cleaned up existing test user")
        
        # Try to create a new user
        print(f"🧪 Testing user creation...")
        user_data = {
            'first_name': 'Debug',
            'last_name': 'Test',
            'email': test_email,
            'password': 'TestPass123!',
            'phone': '1234567890',
            'date_of_birth': '1990-01-01',
            'gender': 'Other',
            'bio': 'Test user'
        }
        
        success, result = AuthController.register_user(user_data)
        if success:
            print(f"✅ User creation successful: {result}")
            
            # Test authentication
            print(f"🧪 Testing authentication...")
            auth_success, auth_result = AuthController.authenticate_user(test_email, 'TestPass123!')
            if auth_success:
                print(f"✅ Authentication successful: User ID {auth_result}")
            else:
                print(f"❌ Authentication failed: {auth_result}")
                
            # Clean up
            test_user = User.query.filter_by(email=test_email).first()
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
                print(f"🧹 Test user cleaned up")
                
        else:
            print(f"❌ User creation failed: {result}")
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        traceback.print_exc()

def main():
    """Main debug function"""
    print("🚨 DEBUG: Login Issues Investigation")
    print("=" * 50)
    
    # Initialize Flask app context
    try:
        # Import and create Flask app
        from app import app
        print("🔗 Creating Flask app context...")
        
        with app.app_context():
            print("✅ Flask app context established")
            check_user_accounts()
            check_authentication_system()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        traceback.print_exc()
        return
    
    print("\n" + "=" * 50)
    print("🎯 DEBUG COMPLETE")
    print("\n💡 Suggested next steps:")
    print("1. Check if any accounts have valid passwords")
    print("2. Verify user account status (active, verified, not locked)")
    print("3. Test authentication system functionality")
    print("4. Create fresh test accounts if needed")

if __name__ == "__main__":
    main()
