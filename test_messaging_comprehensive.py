#!/usr/bin/env python3
"""
Comprehensive test script to debug the messaging encryption issue
This script will:
1. Login as a real user
2. Send an encrypted message
3. Check the server logs for our enhanced debug output
"""

import requests
import json
import re
from bs4 import BeautifulSoup

def extract_csrf_token(response_text):
    """Extract CSRF token from HTML response"""
    # Try multiple methods to find CSRF token
    patterns = [
        r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']',
        r'<meta name="csrf-token" content="([^"]+)"',
        r'name="csrf_token" value="([^"]+)"'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response_text)
        if match:
            return match.group(1)
    
    return None

def login_user(session, email, password):
    """Login as a user and return success status"""
    try:
        # Get login page first
        login_page = session.get("http://localhost:5000/auth?mode=login")
        if login_page.status_code != 200:
            print(f"❌ Failed to get login page: {login_page.status_code}")
            return False
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(login_page.text)
        if not csrf_token:
            print("❌ Could not find CSRF token on login page")
            return False
        
        print(f"✅ Found CSRF token: {csrf_token[:20]}...")
        
        # Submit login form
        login_data = {
            'csrf_token': csrf_token,
            'form_type': 'login',
            'email': email,
            'password': password
        }
        
        login_response = session.post(
            "http://localhost:5000/auth",
            data=login_data,
            allow_redirects=False
        )
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response headers: {dict(login_response.headers)}")
        
        # Check if login was successful (should redirect)
        if login_response.status_code in [302, 200]:
            # Follow redirect to check final destination
            final_response = session.get("http://localhost:5000/")
            print(f"Final redirect status: {final_response.status_code}")
            
            # Check if we're logged in by looking for user-specific content
            if 'logout' in final_response.text.lower() or 'dashboard' in final_response.text.lower():
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed - still showing login form")
                return False
        
        print(f"❌ Login failed with status: {login_response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def test_authenticated_messaging():
    """Test messaging with an authenticated session"""
    print("🧪 Testing authenticated messaging...")
    
    session = requests.Session()
    
    # Test credentials (you may need to update these)
    test_credentials = [
        ('seeker@example.com', 'password123'),
        ('admin@example.com', 'password123'),
        ('user@example.com', 'password123'),
    ]
    
    logged_in = False
    for email, password in test_credentials:
        print(f"🔐 Trying to login with {email}...")
        if login_user(session, email, password):
            logged_in = True
            print(f"✅ Successfully logged in as {email}")
            break
        else:
            print(f"❌ Failed to login as {email}")
    
    if not logged_in:
        print("❌ Could not login with any test credentials")
        print("💡 Try creating a user first or check the credentials")
        return
    
    # Now try to access messaging
    print("📱 Accessing messaging page...")
    messaging_response = session.get("http://localhost:5000/messaging")
    print(f"Messaging page status: {messaging_response.status_code}")
    
    if messaging_response.status_code != 200:
        print("❌ Could not access messaging page")
        return
    
    # Extract CSRF token from messaging page
    csrf_token = extract_csrf_token(messaging_response.text)
    if not csrf_token:
        print("❌ Could not find CSRF token on messaging page")
        return
    
    print(f"✅ Found CSRF token: {csrf_token[:20]}...")
    
    # Test both plain text and encrypted messages
    test_cases = [
        {
            'name': 'Plain text message',
            'data': {
                'recipient_id': 2,  # Assuming user ID 2 exists
                'content': 'Hello, this is a plain text test message!'
            }
        },
        {
            'name': 'Encrypted message',
            'data': {
                'recipient_id': 2,
                'encrypted_data': {
                    'encrypted_content': 'dGVzdCBlbmNyeXB0ZWQgY29udGVudA==',  # Base64 encoded test
                    'nonce': 'dGVzdG5vbmNl',  # Base64 encoded test nonce
                    'algorithm': 'AES-GCM-128'
                }
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\\n📤 Testing: {test_case['name']}")
        print(f"Payload: {json.dumps(test_case['data'], indent=2)}")
        
        # Send the message
        response = session.post(
            "http://localhost:5000/messaging/send",
            json=test_case['data'],
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest'
            }
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            
            if response_json.get('success'):
                print(f"✅ {test_case['name']} sent successfully!")
            else:
                print(f"❌ {test_case['name']} failed: {response_json.get('error', 'Unknown error')}")
                
        except:
            print(f"❌ Could not parse response as JSON")
            print(f"Response text: {response.text[:500]}...")

def check_container_logs():
    """Check the container logs for our debug output"""
    print("\\n📋 Checking container logs for debug output...")
    import subprocess
    
    try:
        result = subprocess.run(
            ['docker', 'logs', 'safe-companions-web-dev', '--tail', '50'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout
            print("📋 Recent container logs:")
            print("-" * 80)
            print(logs)
            print("-" * 80)
            
            # Look for our enhanced debug markers
            if "🚀🚀🚀 ENHANCED DEBUG" in logs:
                print("✅ Found our enhanced debug output in logs!")
            else:
                print("❌ Enhanced debug output not found in logs")
                
        else:
            print(f"❌ Failed to get container logs: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error checking logs: {str(e)}")

if __name__ == "__main__":
    print("🧪 Starting comprehensive messaging test...")
    test_authenticated_messaging()
    check_container_logs()
    print("🧪 Test complete!")
