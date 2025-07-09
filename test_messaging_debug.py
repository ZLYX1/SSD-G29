#!/usr/bin/env python3
"""
Test messaging debug to trace the missing fields error
"""

import requests
import json

# Test sending a message to see what's happening
def test_send_message():
    print("🧪 Testing message sending to debug 'Missing required fields' error...")
    
    # First login to get session cookies
    login_url = "http://127.0.0.1:5000/auth"
    login_data = {
        'mode': 'login',
        'email': 'seeker@example.com',
        'password': 'password123'
    }
    
    session = requests.Session()
    
    # Get the login page first to get CSRF token
    print("1. Getting login page...")
    login_page = session.get(login_url)
    print(f"   Login page status: {login_page.status_code}")
    
    # Extract CSRF token
    csrf_token = None
    if 'csrf_token' in login_page.text:
        import re
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
    
    if not csrf_token:
        print("❌ Could not extract CSRF token")
        return
    
    print(f"   CSRF token: {csrf_token[:20]}...")
    
    # Login
    print("2. Logging in...")
    login_data['csrf_token'] = csrf_token
    login_response = session.post(login_url, data=login_data)
    print(f"   Login status: {login_response.status_code}")
    print(f"   Login URL after redirect: {login_response.url}")
    
    # Test sending a message
    print("3. Testing message send...")
    send_url = "http://127.0.0.1:5000/messaging/send"
    
    # Test data exactly as JavaScript would send it
    message_data = {
        'recipient_id': 121,  # User ID we're messaging
        'content': 'Test message from debug script'
    }
    
    print(f"   Sending data: {json.dumps(message_data, indent=2)}")
    
    # Send the message
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    send_response = session.post(send_url, 
                                json=message_data, 
                                headers=headers)
    
    print(f"   Send status: {send_response.status_code}")
    print(f"   Response headers: {send_response.headers}")
    print(f"   Response text: {send_response.text}")
    
    try:
        response_json = send_response.json()
        print(f"   Response JSON: {json.dumps(response_json, indent=2)}")
    except:
        print("   Could not parse response as JSON")

if __name__ == "__main__":
    test_send_message()
