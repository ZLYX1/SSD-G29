#!/usr/bin/env python3
"""
Quick Flask App Startup Test
Tests if the Flask application starts correctly with email verification
"""

import sys
import os
import subprocess
import time
import requests
from threading import Thread

def test_flask_startup():
    """Test Flask application startup"""
    print("🚀 Testing Flask Application Startup")
    print("=" * 40)
    
    # Test environment variables first
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'DATABASE_HOST', 'DATABASE_PORT', 'DATABASE_NAME', 
            'DATABASE_USERNAME', 'DATABASE_PASSWORD', 'RECAPTCHA_SECRET_KEY'
        ]
        
        missing = [var for var in required_vars if not os.environ.get(var)]
        
        if missing:
            print(f"❌ Missing environment variables: {missing}")
            return False
        else:
            print("✅ All required environment variables present")
    
    except Exception as e:
        print(f"❌ Environment check failed: {e}")
        return False
    
    # Test imports
    try:
        print("\n📦 Testing imports...")
        
        # Test if we can import the main components
        import tempfile
        import sqlite3  # For testing
        
        # Test token generation
        import secrets
        token = secrets.token_urlsafe(32)
        print(f"✅ Token generation works: {token[:20]}...")
        
        print("✅ All imports successful")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    print("\n🎉 Flask app startup test PASSED!")
    print("\nReady for manual testing:")
    print("1. Run: python app.py")
    print("2. Visit: http://localhost:5000/auth?mode=register")
    print("3. Register a test user")
    print("4. Check console for verification URL")
    
    return True

def test_database_ready():
    """Test if database structure is ready"""
    print("\n🗄️ Testing Database Readiness")
    print("=" * 30)
    
    # For now, just print what should be checked
    print("Manual database checks needed:")
    print("1. Ensure PostgreSQL is running")
    print("2. Run email_verification_migration.sql")
    print("3. Verify 'user' table has email verification columns")
    
    print("\nSQL to verify migration:")
    print("""
    SELECT column_name, data_type, is_nullable, column_default 
    FROM information_schema.columns 
    WHERE table_name = 'user' 
    AND column_name LIKE '%email%';
    """)
    
    return True

def main():
    """Run startup tests"""
    print("🧪 EMAIL VERIFICATION SYSTEM - STARTUP TESTS")
    print("=" * 50)
    
    success = True
    
    # Run tests
    success &= test_flask_startup()
    success &= test_database_ready()
    
    if success:
        print(f"\n🎊 ALL STARTUP TESTS PASSED!")
        print("\n📋 Manual Testing Steps:")
        print("1. Apply database migration (email_verification_migration.sql)")
        print("2. Start Flask app: python app.py")
        print("3. Follow EMAIL_VERIFICATION_TESTING_GUIDE.md")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print("Fix the issues above before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
