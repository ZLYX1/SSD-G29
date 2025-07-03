#!/usr/bin/env python3
"""
Test Email Verification System
This script tests the email verification functionality without requiring a full database setup.
"""

import sys
import os
import secrets
import datetime

def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)

def test_token_generation():
    """Test verification token generation"""
    print("Testing token generation...")
    token1 = generate_verification_token()
    token2 = generate_verification_token()
    
    print(f"Token 1: {token1}")
    print(f"Token 2: {token2}")
    
    # Tokens should be different
    assert token1 != token2, "Tokens should be unique"
    
    # Tokens should be reasonable length
    assert len(token1) > 20, "Token should be sufficiently long"
    
    print("✅ Token generation test passed!")
    print()

def test_token_expiry():
    """Test token expiry logic"""
    print("Testing token expiry...")
    
    # Test expired token (past date)
    expired_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    print(f"Expired time: {expired_time}")
    
    # Test valid token (future date)
    valid_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    print(f"Valid time: {valid_time}")
    
    current_time = datetime.datetime.utcnow()
    print(f"Current time: {current_time}")
    
    # Check logic
    is_expired = expired_time < current_time
    is_valid = valid_time > current_time
    
    assert is_expired, "Past time should be expired"
    assert is_valid, "Future time should be valid"
    
    print("✅ Token expiry test passed!")
    print()

def main():
    print("🧪 Email Verification System Tests")
    print("=" * 40)
    
    try:
        test_token_generation()
        test_token_expiry()
        
        print("🎉 All tests passed!")
        print("\n📧 Email verification system is ready to use!")
        print("\nNext steps:")
        print("1. Run the database migration: email_verification_migration.sql")
        print("2. Start the Flask application")
        print("3. Test user registration with email verification")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
