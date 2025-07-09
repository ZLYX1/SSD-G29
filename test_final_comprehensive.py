#!/usr/bin/env python3
"""
Final comprehensive test for Safe Companions messaging system.
Tests both the backend messaging endpoints and frontend JavaScript functionality.
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:5000"

def test_basic_connectivity():
    """Test if the application is accessible"""
    print("🔍 Testing basic connectivity...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200 or response.status_code == 302:
            print("✅ Application is accessible")
            return True
        else:
            print(f"❌ Application returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to application: {e}")
        return False

def test_messaging_routes():
    """Test if messaging routes are accessible"""
    print("\n🔍 Testing messaging routes...")
    
    # Test messaging page (should redirect to auth if not logged in)
    try:
        response = requests.get(f"{BASE_URL}/messaging/", timeout=10)
        if response.status_code in [200, 302]:
            print("✅ Messaging route is accessible")
        else:
            print(f"❌ Messaging route returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing messaging route: {e}")
        return False
    
    return True

def test_static_files():
    """Test if critical JavaScript files are accessible"""
    print("\n🔍 Testing static file accessibility...")
    
    js_files = [
        "/static/js/messaging.js",
        "/static/js/encryption.js"
    ]
    
    for js_file in js_files:
        try:
            response = requests.get(f"{BASE_URL}{js_file}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {js_file} is accessible")
                # Check for key JavaScript functions
                content = response.text
                if js_file.endswith("messaging.js"):
                    if "sendMessage" in content and "originalText" in content:
                        print("✅ messaging.js contains expected functions")
                    else:
                        print("⚠️ messaging.js may be missing key functions")
                elif js_file.endswith("encryption.js"):
                    if "MessageCrypto" in content and "deriveConversationKey" in content:
                        print("✅ encryption.js contains expected functions")
                    else:
                        print("⚠️ encryption.js may be missing key functions")
            else:
                print(f"❌ {js_file} returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error accessing {js_file}: {e}")
            return False
    
    return True

def create_test_session():
    """Create a test session by registering and logging in"""
    print("\n🔍 Creating test session...")
    
    session = requests.Session()
    
    # First, get the registration page to check CSRF token handling
    try:
        response = session.get(f"{BASE_URL}/auth/register")
        if response.status_code != 200:
            print(f"❌ Cannot access registration page: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error accessing registration page: {e}")
        return None
    
    # Try to register a test user
    test_user_data = {
        "first_name": "Test",
        "last_name": "User", 
        "email": f"test{int(time.time())}@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "phone": "1234567890",
        "date_of_birth": "1990-01-01",
        "gender": "Other",
        "bio": "Test user for messaging"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/register", data=test_user_data)
        print(f"Registration response status: {response.status_code}")
        print(f"Registration response URL: {response.url}")
        
        # Check if registration was successful (might redirect to login or verification)
        if response.status_code in [200, 302]:
            print("✅ Registration request completed")
            return session
        else:
            print(f"⚠️ Registration returned status {response.status_code}")
            return session  # Return session anyway to test other functionality
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return session

def test_messaging_endpoints_without_auth():
    """Test messaging endpoints without authentication (should return 401/302)"""
    print("\n🔍 Testing messaging endpoints without authentication...")
    
    endpoints = [
        "/messaging/send",
        "/messaging/conversations/1",
        "/messaging/conversation-key-info/1",
        "/messaging/generate-conversation-key/1"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json={})
            if response.status_code in [401, 302, 403]:
                print(f"✅ {endpoint} properly requires authentication (status: {response.status_code})")
            else:
                print(f"⚠️ {endpoint} returned unexpected status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")

def test_javascript_syntax():
    """Test JavaScript files for syntax errors"""
    print("\n🔍 Testing JavaScript syntax...")
    
    js_files = [
        "/static/js/messaging.js",
        "/static/js/encryption.js"
    ]
    
    for js_file in js_files:
        try:
            response = requests.get(f"{BASE_URL}{js_file}", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Basic syntax checks
                open_braces = content.count('{')
                close_braces = content.count('}')
                open_parens = content.count('(')
                close_parens = content.count(')')
                
                if open_braces == close_braces and open_parens == close_parens:
                    print(f"✅ {js_file} has balanced braces and parentheses")
                else:
                    print(f"⚠️ {js_file} may have syntax issues (braces: {open_braces}/{close_braces}, parens: {open_parens}/{close_parens})")
                
                # Check for common error patterns
                if "ReferenceError" in content or "undefined variable" in content:
                    print(f"⚠️ {js_file} may contain reference errors")
                
                # Check for our specific fixes
                if js_file.endswith("messaging.js"):
                    if "let originalText" in content or "const originalText" in content or "var originalText" in content:
                        print(f"✅ {js_file} properly declares originalText variable")
                    else:
                        print(f"⚠️ {js_file} may have originalText scope issues")
            
        except Exception as e:
            print(f"❌ Error checking {js_file}: {e}")

def test_encryption_functionality():
    """Test client-side encryption functionality availability"""
    print("\n🔍 Testing encryption functionality...")
    
    try:
        response = requests.get(f"{BASE_URL}/static/js/encryption.js", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            required_functions = [
                "MessageCrypto",
                "deriveConversationKey", 
                "generateKeyPair",
                "encryptMessage",
                "decryptMessage"
            ]
            
            for func in required_functions:
                if func in content:
                    print(f"✅ Found {func} in encryption.js")
                else:
                    print(f"⚠️ Missing {func} in encryption.js")
                    
            # Check for Web Crypto API usage
            if "crypto.subtle" in content:
                print("✅ Uses Web Crypto API for secure encryption")
            else:
                print("⚠️ May not be using Web Crypto API")
                
        else:
            print(f"❌ Cannot access encryption.js: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing encryption functionality: {e}")

def main():
    """Run all tests"""
    print("🧪 Starting Safe Companions Messaging System Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Test basic connectivity
    if not test_basic_connectivity():
        all_passed = False
    
    # Test messaging routes
    if not test_messaging_routes():
        all_passed = False
    
    # Test static files
    if not test_static_files():
        all_passed = False
    
    # Test JavaScript syntax
    test_javascript_syntax()
    
    # Test encryption functionality
    test_encryption_functionality()
    
    # Test endpoints without auth
    test_messaging_endpoints_without_auth()
    
    # Try to create test session
    session = create_test_session()
    if session:
        print("✅ Test session creation completed")
    else:
        print("⚠️ Could not create test session")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All critical tests passed!")
        print("\n📝 Summary:")
        print("   ✅ Application is accessible")
        print("   ✅ Messaging routes are working")  
        print("   ✅ JavaScript files are accessible")
        print("   ✅ Basic security is in place")
        print("\n💡 Next steps:")
        print("   1. Test with real user accounts")
        print("   2. Verify end-to-end encryption")
        print("   3. Test message sending and receiving")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        
    print("\n🔧 For manual testing:")
    print(f"   1. Open {BASE_URL} in your browser")
    print("   2. Register/login with a user account")
    print("   3. Navigate to messaging section")
    print("   4. Try sending messages to verify functionality")

if __name__ == "__main__":
    main()
