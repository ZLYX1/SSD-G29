#!/usr/bin/env python3
"""
Login Test Script
Test the login functionality with the created test user.
"""

import os
import sys
import requests
from urllib.parse import urljoin

# Add the project root to the Python path
sys.path.append('/app')

def test_login():
    """Test login functionality with the test user."""
    print("🔐 Testing Login Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    login_url = urljoin(base_url, "/auth/")
    
    # Test credentials
    test_email = "seeker@example.com"
    test_password = "password123"
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        print("1. Accessing login page...")
        
        # Get the login page first to get any CSRF tokens
        response = session.get(login_url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login page accessible")
        else:
            print(f"   ❌ Login page not accessible: {response.status_code}")
            return False
        
        print("\n2. Attempting login...")
        
        # Prepare login data
        login_data = {
            'email': test_email,
            'password': test_password
        }
        
        # Attempt login
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code in [302, 301]:  # Redirect indicates successful login
            print("   ✅ Login successful (redirected)")
            redirect_url = login_response.headers.get('Location', 'Unknown')
            print(f"   Redirected to: {redirect_url}")
            
            # Follow the redirect to see if we're logged in
            if redirect_url:
                final_response = session.get(urljoin(base_url, redirect_url))
                print(f"   Final page status: {final_response.status_code}")
                
                if "dashboard" in redirect_url.lower() or "profile" in redirect_url.lower():
                    print("   ✅ Successfully logged in and redirected to user area")
                    return True
        
        elif login_response.status_code == 200:
            # Check if there are error messages in the response
            if "error" in login_response.text.lower() or "invalid" in login_response.text.lower():
                print("   ❌ Login failed - credentials rejected")
            else:
                print("   ⚠️  Login form returned 200 - may need investigation")
        
        else:
            print(f"   ❌ Unexpected response: {login_response.status_code}")
        
        return False
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to application - is it running?")
        return False
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
        return False

def test_user_exists():
    """Check if the test user exists in the database."""
    print("\n🗃️  Verifying Test User in Database")
    print("=" * 50)
    
    try:
        from blueprint.models import User
        from app import app
        
        with app.app_context():
            user = User.query.filter_by(email='seeker@example.com').first()
            if user:
                print(f"   ✅ User found: {user.email}")
                print(f"   Role: {user.role}")
                print(f"   Active: {user.active}")
                print(f"   Email Verified: {user.email_verified}")
                print(f"   Phone Verified: {user.phone_verified}")
                print(f"   Gender: {user.gender}")
                return True
            else:
                print("   ❌ Test user not found in database")
                return False
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Safe Companion Login Test")
    print("=" * 60)
    
    # Test 1: Check if user exists in database
    user_exists = test_user_exists()
    
    # Test 2: Test login functionality
    login_works = test_login()
    
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"User in Database: {'✅ PASS' if user_exists else '❌ FAIL'}")
    print(f"Login Functionality: {'✅ PASS' if login_works else '❌ FAIL'}")
    
    if user_exists and login_works:
        print("\n🎉 All tests passed! Login functionality is working.")
        print("\n🚀 You can now login with:")
        print("   Email: seeker@example.com")
        print("   Password: password123")
    else:
        print("\n🔧 Some tests failed. Check the errors above.")
    
    print("\n🌐 Access the application at: http://localhost:5000")
