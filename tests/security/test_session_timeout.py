#!/usr/bin/env python3
"""
Test Session Timeout with Warnings
Tests the session timeout functionality including warnings and automatic logout
"""

import requests
import time
import json
import sys
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "email": "admin@example.com",
    "password": "password123"
}

def test_session_timeout():
    """Test session timeout functionality"""
    print("🔍 Testing Session Timeout with Warnings...")
    
    # Create session
    session = requests.Session()
    
    # Step 1: Login to get a session
    print("\n1. Login to establish session...")
    login_response = session.post(f"{BASE_URL}/auth/", data={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "form_type": "login"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Check if redirected to dashboard (successful login)
    if "dashboard" in login_response.url or login_response.history:
        print("✅ Login successful - session established")
    else:
        print("❌ Login may have failed - no redirect to dashboard")
        return False
    
    # Step 2: Test session check endpoint
    print("\n2. Testing session check endpoint...")
    session_check_response = session.get(f"{BASE_URL}/auth/session-check")
    
    if session_check_response.status_code == 200:
        session_data = session_check_response.json()
        print(f"✅ Session check successful: {session_data}")
        
        if session_data.get('valid') == True:
            print("✅ Session is valid")
        else:
            print("❌ Session is not valid")
            return False
    else:
        print(f"❌ Session check failed: {session_check_response.status_code}")
        return False
    
    # Step 3: Test session extend endpoint
    print("\n3. Testing session extend endpoint...")
    # Get CSRF token first
    csrf_response = session.get(f"{BASE_URL}/dashboard")
    csrf_token = None
    
    if csrf_response.status_code == 200:
        # Try to extract CSRF token from response
        csrf_content = csrf_response.text
        if 'csrf-token' in csrf_content:
            import re
            csrf_match = re.search(r'csrf-token["\']?\s*content=["\']([^"\']+)["\']', csrf_content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token extracted: {csrf_token[:20]}...")
    
    # Test session extend
    extend_headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    extend_response = session.post(f"{BASE_URL}/auth/extend-session", 
                                  headers=extend_headers,
                                  json={})
    
    if extend_response.status_code == 200:
        extend_data = extend_response.json()
        print(f"✅ Session extend successful: {extend_data}")
        
        if extend_data.get('success') == True:
            print("✅ Session successfully extended")
        else:
            print("❌ Session extension failed")
            return False
    else:
        print(f"❌ Session extend failed: {extend_response.status_code}")
        return False
    
    # Step 4: Test session timeout (this would require waiting or manipulating session)
    print("\n4. Testing session timeout behavior...")
    print("⏳ In a real scenario, this would test:")
    print("   - Session expires after 30 minutes")
    print("   - Warning shown 5 minutes before expiry")
    print("   - User can extend session when warned")
    print("   - Automatic logout after session expires")
    
    # Step 5: Test invalid session
    print("\n5. Testing invalid session behavior...")
    # Clear session cookies to simulate expired session
    session.cookies.clear()
    
    invalid_session_response = session.get(f"{BASE_URL}/auth/session-check")
    if invalid_session_response.status_code == 200:
        invalid_data = invalid_session_response.json()
        print(f"✅ Invalid session check: {invalid_data}")
        
        if invalid_data.get('valid') == False:
            print("✅ Invalid session correctly detected")
        else:
            print("❌ Invalid session not detected")
            return False
    else:
        print(f"❌ Invalid session check failed: {invalid_session_response.status_code}")
        return False
    
    return True

def test_session_timeout_client_side():
    """Test client-side session timeout functionality"""
    print("\n🔍 Testing Client-Side Session Timeout...")
    
    # Create session
    session = requests.Session()
    
    # Login first
    login_response = session.post(f"{BASE_URL}/auth/", data={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "form_type": "login"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Test accessing a protected page that should include session timeout JS
    dashboard_response = session.get(f"{BASE_URL}/dashboard")
    
    if dashboard_response.status_code == 200:
        dashboard_content = dashboard_response.text
        
        # Check if session timeout JS is included
        if 'session-timeout.js' in dashboard_content:
            print("✅ Session timeout JavaScript included in page")
        else:
            print("❌ Session timeout JavaScript not found in page")
            return False
        
        # Check if user ID is set in body data attribute
        if 'data-user-id' in dashboard_content:
            print("✅ User ID data attribute found in page")
        else:
            print("❌ User ID data attribute not found in page")
            return False
        
        print("✅ Client-side session timeout setup verified")
        return True
    else:
        print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
        return False

def run_all_tests():
    """Run all session timeout tests"""
    print("🚀 Starting Session Timeout Tests...")
    print("=" * 60)
    
    try:
        # Test server-side functionality
        server_test = test_session_timeout()
        
        # Test client-side functionality
        client_test = test_session_timeout_client_side()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Server-side tests: {'✅ PASSED' if server_test else '❌ FAILED'}")
        print(f"Client-side tests: {'✅ PASSED' if client_test else '❌ FAILED'}")
        
        if server_test and client_test:
            print("\n🎉 All session timeout tests PASSED!")
            print("\n📋 Session Timeout Features Verified:")
            print("   ✅ Session check endpoint working")
            print("   ✅ Session extend endpoint working")
            print("   ✅ Invalid session detection working")
            print("   ✅ Client-side JavaScript included")
            print("   ✅ User ID data attribute present")
            print("   ✅ Session timeout infrastructure ready")
            
            print("\n⚠️  Note: Full session timeout testing requires:")
            print("   - 30-minute wait for actual timeout")
            print("   - Manual testing of warning modal")
            print("   - Browser-based JavaScript testing")
            
            return True
        else:
            print("\n❌ Some session timeout tests FAILED!")
            return False
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
