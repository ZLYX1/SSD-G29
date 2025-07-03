#!/usr/bin/env python3
"""Simple CSRF Test - Testing login form CSRF token handling"""

import sys
import os
sys.path.append('/app')

# Import Flask app and test client
from app import app

def test_csrf_in_flask():
    print("🔍 Testing CSRF in Flask App")
    print("=" * 40)
    
    with app.test_client() as client:
        # Test 1: Get login page
        print("\n1. Getting login page...")
        response = client.get('/auth/?mode=login')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.get_data(as_text=True)
            
            # Check for CSRF token in the HTML
            if 'csrf_token' in html_content:
                print("   ✓ CSRF token found in HTML")
                
                # Look for the token value in a hidden input
                import re
                csrf_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', html_content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   ✓ CSRF token extracted: {csrf_token[:20]}...")
                    
                    # Test 2: Try login with CSRF token
                    print("\n2. Testing login with CSRF token...")
                    
                    # We need to get the session to maintain CSRF state
                    with client.session_transaction() as sess:
                        # The CSRF token should be in the session
                        pass
                    
                    login_data = {
                        'form_type': 'login',
                        'email': 'seeker@example.com',
                        'password': 'password123',
                        'csrf_token': csrf_token
                    }
                    
                    login_response = client.post('/auth/', data=login_data, follow_redirects=False)
                    print(f"   Status: {login_response.status_code}")
                    
                    if login_response.status_code == 400:
                        error_text = login_response.get_data(as_text=True)
                        if "CSRF" in error_text:
                            print("   ❌ CSRF error occurred")
                            print(f"   Error: {error_text[:200]}...")
                        else:
                            print("   ❌ 400 error but not CSRF related")
                    elif login_response.status_code in [302, 303]:
                        print("   ✓ Login successful (redirect)")
                    else:
                        print(f"   Other response: {login_response.status_code}")
                    
                    # Test 3: Try login without CSRF token
                    print("\n3. Testing login without CSRF token...")
                    login_data_no_csrf = {
                        'form_type': 'login',
                        'email': 'seeker@example.com',
                        'password': 'password123'
                    }
                    
                    no_csrf_response = client.post('/auth/', data=login_data_no_csrf, follow_redirects=False)
                    print(f"   Status: {no_csrf_response.status_code}")
                    
                    if no_csrf_response.status_code == 400:
                        print("   ✓ Request without CSRF token correctly rejected")
                    else:
                        print("   ❌ Request without CSRF token was accepted")
                        
                else:
                    print("   ❌ Could not extract CSRF token value from HTML")
            else:
                print("   ❌ No CSRF token found in HTML")
                
        else:
            print(f"   ❌ Failed to get login page: {response.status_code}")

def check_csrf_config():
    print("\n4. Checking CSRF configuration...")
    
    # Check app config
    csrf_enabled = app.config.get('WTF_CSRF_ENABLED', False)
    print(f"   WTF_CSRF_ENABLED: {csrf_enabled}")
    
    csrf_secret = app.config.get('WTF_CSRF_SECRET_KEY', None)
    if csrf_secret:
        print(f"   WTF_CSRF_SECRET_KEY: {'*' * 10} (configured)")
    else:
        print("   WTF_CSRF_SECRET_KEY: Not configured")
        
    csrf_ssl_strict = app.config.get('WTF_CSRF_SSL_STRICT', None)
    print(f"   WTF_CSRF_SSL_STRICT: {csrf_ssl_strict}")

if __name__ == "__main__":
    check_csrf_config()
    test_csrf_in_flask()
    print("\n🎯 CSRF Test Complete!")
