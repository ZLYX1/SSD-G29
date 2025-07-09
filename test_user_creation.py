#!/usr/bin/env python3
"""
Simple test user creation script to ensure we have test data
"""

import requests
import json
import re

def create_test_user():
    """Try to create a test user via the registration form"""
    print("👤 Creating test user...")
    
    session = requests.Session()
    
    try:
        # Get registration page
        reg_response = session.get("http://localhost:5000/auth?mode=register")
        if reg_response.status_code != 200:
            print(f"❌ Failed to get registration page: {reg_response.status_code}")
            return None
        
        # Extract CSRF token
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', reg_response.text)
        if not csrf_match:
            print("❌ Could not find CSRF token on registration page")
            return None
        
        csrf_token = csrf_match.group(1)
        print(f"✅ Found CSRF token: {csrf_token[:20]}...")
        
        # Try to register a test user
        reg_data = {
            'csrf_token': csrf_token,
            'form_type': 'register',
            'username': 'testuser2025',
            'email': 'testuser2025@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!',
            'account_type': 'seeker',
            'g-recaptcha-response': 'test_response'  # This might fail
        }
        
        print("📝 Submitting registration...")
        reg_submit = session.post(
            "http://localhost:5000/auth",
            data=reg_data,
            allow_redirects=False
        )
        
        print(f"Registration response status: {reg_submit.status_code}")
        print(f"Registration response headers: {dict(reg_submit.headers)}")
        
        if reg_submit.status_code in [200, 302]:
            print("✅ Registration submitted successfully!")
            return {
                'email': 'testuser2025@example.com',
                'password': 'TestPassword123!'
            }
        else:
            print(f"❌ Registration failed: {reg_submit.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None

def test_login_with_user(credentials):
    """Test login with the given credentials"""
    if not credentials:
        return None
        
    print(f"🔐 Testing login with {credentials['email']}...")
    
    session = requests.Session()
    
    try:
        # Get login page
        login_response = session.get("http://localhost:5000/auth?mode=login")
        if login_response.status_code != 200:
            print(f"❌ Failed to get login page: {login_response.status_code}")
            return None
        
        # Extract CSRF token
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_response.text)
        if not csrf_match:
            print("❌ Could not find CSRF token on login page")
            return None
        
        csrf_token = csrf_match.group(1)
        
        # Submit login
        login_data = {
            'csrf_token': csrf_token,
            'form_type': 'login',
            'email': credentials['email'],
            'password': credentials['password']
        }
        
        login_submit = session.post(
            "http://localhost:5000/auth",
            data=login_data,
            allow_redirects=True
        )
        
        print(f"Login response status: {login_submit.status_code}")
        
        # Check if we're logged in
        if 'logout' in login_submit.text.lower() or 'dashboard' in login_submit.text.lower():
            print("✅ Login successful!")
            return session
        else:
            print("❌ Login failed - still showing login form")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_messaging_with_session(session):
    """Test messaging with an authenticated session"""
    if not session:
        print("❌ No authenticated session available")
        return
        
    print("📱 Testing messaging with authenticated session...")
    
    try:
        # Access messaging page
        msg_response = session.get("http://localhost:5000/messaging")
        print(f"Messaging page status: {msg_response.status_code}")
        
        if msg_response.status_code != 200:
            print("❌ Could not access messaging page")
            return
        
        # Extract CSRF token
        csrf_match = re.search(r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']', msg_response.text)
        if not csrf_match:
            csrf_match = re.search(r'name="csrf-token" content="([^"]+)"', msg_response.text)
        
        if not csrf_match:
            print("❌ Could not find CSRF token on messaging page")
            return
        
        csrf_token = csrf_match.group(1)
        print(f"✅ Found CSRF token: {csrf_token[:20]}...")
        
        # Test sending a message (this should trigger our debug output)
        test_message = {
            'recipient_id': 1,  # Try sending to user ID 1
            'encrypted_data': {
                'encrypted_content': 'dGVzdCBlbmNyeXB0ZWQgY29udGVudA==',
                'nonce': 'dGVzdG5vbmNl',
                'algorithm': 'AES-GCM-128'
            }
        }
        
        print("🚀 Sending test encrypted message...")
        print(f"Payload: {json.dumps(test_message, indent=2)}")
        
        msg_send_response = session.post(
            "http://localhost:5000/messaging/send",
            json=test_message,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest'
            }
        )
        
        print(f"Message send response status: {msg_send_response.status_code}")
        
        try:
            response_json = msg_send_response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            
            if response_json.get('success'):
                print("✅ Message sent successfully!")
            else:
                print(f"❌ Message failed: {response_json.get('error', 'Unknown error')}")
                
        except:
            print(f"❌ Could not parse response as JSON")
            print(f"Response text: {msg_send_response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Messaging test error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Starting user creation and messaging test...")
    
    # Try to create a test user
    credentials = create_test_user()
    
    # Test login
    session = test_login_with_user(credentials)
    
    # Test messaging
    test_messaging_with_session(session)
    
    print("🧪 Test complete!")
