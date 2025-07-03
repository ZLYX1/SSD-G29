#!/usr/bin/env python3
"""Quick CSRF test to debug the login issue"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from flask import session
from flask_wtf.csrf import generate_csrf

print("🔍 Testing CSRF Configuration...")

# Test 1: Check if CSRF is enabled
print(f"✓ CSRF Enabled: {app.config.get('WTF_CSRF_ENABLED', 'Not set')}")
print(f"✓ CSRF Secret Key: {app.config.get('WTF_CSRF_SECRET_KEY', 'Not set')}")
print(f"✓ CSRF SSL Strict: {app.config.get('WTF_CSRF_SSL_STRICT', 'Not set')}")

# Test 2: Test CSRF token generation
with app.app_context():
    try:
        token = generate_csrf()
        print(f"✓ CSRF Token Generated: {token[:20]}...")
    except Exception as e:
        print(f"❌ CSRF Token Generation Failed: {e}")

# Test 3: Test with request context
with app.test_request_context():
    try:
        token = generate_csrf()
        print(f"✓ CSRF Token in Request Context: {token[:20]}...")
    except Exception as e:
        print(f"❌ CSRF Token in Request Context Failed: {e}")

print("\n🔍 Testing Login Form...")

# Test 4: Simulate login form submission
with app.test_client() as client:
    # Get the login page first
    response = client.get('/auth/?mode=login')
    print(f"✓ Login page response: {response.status_code}")
    
    # Check if CSRF token is in the response
    if 'csrf_token' in response.get_data(as_text=True):
        print("✓ CSRF token found in login page")
    else:
        print("❌ CSRF token NOT found in login page")
    
    # Try to login with CSRF token
    with client.session_transaction() as sess:
        # Get CSRF token from session
        csrf_token = generate_csrf()
        
    login_data = {
        'form_type': 'login',
        'email': 'seeker@example.com',
        'password': 'password123',
        'csrf_token': csrf_token
    }
    
    response = client.post('/auth/', data=login_data)
    print(f"✓ Login attempt response: {response.status_code}")
    
    if response.status_code == 400:
        print("❌ Login failed with 400 Bad Request (CSRF issue)")
        print(f"Response data: {response.get_data(as_text=True)[:200]}...")
    else:
        print("✓ Login attempt successful (no CSRF error)")

print("\n🎯 CSRF Test Complete!")
