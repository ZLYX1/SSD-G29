#!/usr/bin/env python3
"""
Debug script to test consecutive message sending
"""

import requests
import json
import sys

def test_consecutive_messages():
    """Test sending multiple messages consecutively"""
    
    # Configuration
    base_url = "http://localhost:5000"
    
    # Login first to get session
    login_data = {
        "email": "alice@example.com",
        "password": "Alice123!"
    }
    
    session = requests.Session()
    
    print("🔐 Logging in...")
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Get CSRF token
    csrf_response = session.get(f"{base_url}/messaging")
    csrf_token = None
    
    if 'csrf_token' in csrf_response.text:
        # Extract CSRF token from page
        import re
        match = re.search(r'csrf_token["\'\s]*[:=]["\'\s]*([^"\']+)', csrf_response.text)
        if match:
            csrf_token = match.group(1)
    
    if not csrf_token:
        print("❌ Could not get CSRF token")
        return
    
    print(f"✅ Got CSRF token: {csrf_token[:10]}...")
    
    # Test messages
    test_messages = [
        {"content": "First test message", "recipient_id": 2},
        {"content": "Second test message", "recipient_id": 2},
        {"content": "Third test message", "recipient_id": 2}
    ]
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    for i, message_data in enumerate(test_messages, 1):
        print(f"\n📨 Sending message {i}: '{message_data['content']}'")
        
        response = session.post(
            f"{base_url}/messaging/send",
            headers=headers,
            json=message_data
        )
        
        print(f"   Status: {response.status_code}")
        try:
            result = response.json()
            print(f"   Response: {result}")
            
            if not result.get('success'):
                print(f"   ❌ Error: {result.get('error')}")
                break
            else:
                print(f"   ✅ Success")
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text[:200]}")
            break

if __name__ == "__main__":
    test_consecutive_messages()
