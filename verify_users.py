#!/usr/bin/env python3
"""
Quick verification script to check created test users
"""
import sys
sys.path.append('/app')

from blueprint.models import User
from app import app

def verify_test_users():
    """Verify that test users were created correctly"""
    print("🔍 Verifying test user accounts...")
    
    test_accounts = [
        'seeker1@example.com',
        'seeker2@example.com', 
        'escort1@example.com',
        'admin@safecompanions.com'
    ]
    
    with app.app_context():
        for email in test_accounts:
            user = User.query.filter_by(email=email).first()
            if user:
                # Test password
                success, result = user.check_password('password123')
                status = "✅ WORKING" if success else "❌ FAILED"
                print(f"   {status} {email} (role: {user.role})")
            else:
                print(f"   ❌ NOT FOUND {email}")
        
        # Show total user count
        total_users = User.query.count()
        print(f"\n📊 Total users in database: {total_users}")

if __name__ == '__main__':
    verify_test_users()
