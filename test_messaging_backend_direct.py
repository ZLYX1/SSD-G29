#!/usr/bin/env python3
"""
Direct backend test for messaging endpoint
"""

import requests
import json

def test_messaging_backend():
    """Test the messaging backend directly"""
    
    base_url = "http://localhost:5000"
    
    # Test data that mimics what the frontend sends
    test_payload = {
        "recipient_id": 18,
        "encrypted_data": {
            "encrypted_content": "testEncryptedContent123",
            "nonce": "testNonce123",
            "algorithm": "AES-GCM-128"
        }
    }
    
    # Create a session
    session = requests.Session()
    
    print("🚀 Testing backend messaging endpoint...")
    print(f"📡 Sending to: {base_url}/messaging/send")
    print(f"📦 Payload: {json.dumps(test_payload, indent=2)}")
    
    # First, get the login page to establish session
    print("\n🔐 Getting session...")
    login_page = session.get(f"{base_url}/auth/")
    print(f"   Login page status: {login_page.status_code}")
    
    # Extract CSRF token from login page
    csrf_token = None
    if 'csrf_token' in login_page.text:
        import re
        match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', login_page.text)
        if match:
            csrf_token = match.group(1)
    
    if not csrf_token:
        print("❌ Could not extract CSRF token")
        return
    
    print(f"   CSRF token: {csrf_token[:20]}...")
    
    # Login with test user
    login_data = {
        'email': 'seeker1@example.com',
        'password': 'password123',
        'csrf_token': csrf_token
    }
    
    print("\n👤 Logging in...")
    login_response = session.post(f"{base_url}/auth/", data=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text[:200]}")
        return
    
    # Get a fresh CSRF token for the API request
    messaging_page = session.get(f"{base_url}/messaging")
    if messaging_page.status_code == 200:
        match = re.search(r'csrf_token["\'\s]*[:=]["\'\s]*([^"\']+)', messaging_page.text)
        if match:
            csrf_token = match.group(1)
            print(f"   Updated CSRF token: {csrf_token[:20]}...")
    
    # Test the messaging endpoint
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    print("\n📨 Sending test message...")
    response = session.post(
        f"{base_url}/messaging/send",
        headers=headers,
        json=test_payload
    )
    
    print(f"   Response status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"   Response data: {json.dumps(response_data, indent=2)}")
        
        if response_data.get('success'):
            print("✅ SUCCESS: Message sent successfully!")
        else:
            print(f"❌ ERROR: {response_data.get('error', 'Unknown error')}")
            
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {response.text}")

if __name__ == "__main__":
    test_messaging_backend()
