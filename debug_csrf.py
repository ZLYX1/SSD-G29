#!/usr/bin/env python3
"""CSRF Debug Script - Check login form CSRF token handling"""

import os
import sys
import re
import requests
from bs4 import BeautifulSoup

print("🔍 CSRF Debug Script - Testing Login Form")
print("=" * 50)

# Test with the running Docker app
BASE_URL = "http://localhost:5000"

def test_csrf_tokens():
    session = requests.Session()
    
    # Test 1: Get login page and check for CSRF token
    print("\n1. Testing GET /auth/?mode=login")
    try:
        response = session.get(f"{BASE_URL}/auth/?mode=login")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for CSRF token in meta tag
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                print(f"   ✓ CSRF meta tag found: {csrf_meta.get('content', '')[:20]}...")
            else:
                print("   ❌ No CSRF meta tag found")
            
            # Look for CSRF token in forms
            csrf_inputs = soup.find_all('input', {'name': 'csrf_token'})
            print(f"   Found {len(csrf_inputs)} CSRF token inputs")
            
            for i, csrf_input in enumerate(csrf_inputs):
                token_value = csrf_input.get('value', '')
                if token_value:
                    print(f"   ✓ CSRF input {i+1}: {token_value[:20]}...")
                else:
                    print(f"   ❌ CSRF input {i+1}: empty value")
                    
            # Check for login form
            login_form = soup.find('form')
            if login_form:
                print("   ✓ Login form found")
                form_csrf = login_form.find('input', {'name': 'csrf_token'})
                if form_csrf and form_csrf.get('value'):
                    csrf_token = form_csrf.get('value')
                    print(f"   ✓ Form CSRF token: {csrf_token[:20]}...")
                    
                    # Test 2: Try to login with CSRF token
                    print("\n2. Testing POST /auth/ with CSRF token")
                    login_data = {
                        'form_type': 'login',
                        'email': 'seeker@example.com',
                        'password': 'password123',
                        'csrf_token': csrf_token
                    }
                    
                    # Set headers that might be required
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': f"{BASE_URL}/auth/?mode=login"
                    }
                    
                    login_response = session.post(f"{BASE_URL}/auth/", data=login_data, headers=headers, allow_redirects=False)
                    print(f"   Status: {login_response.status_code}")
                    
                    if login_response.status_code == 400:
                        print("   ❌ Login failed with 400 Bad Request")
                        print(f"   Response: {login_response.text[:200]}...")
                    elif login_response.status_code in [302, 303]:
                        print("   ✓ Login successful (redirect)")
                        print(f"   Redirect to: {login_response.headers.get('Location', 'Unknown')}")
                    else:
                        print(f"   Response: {login_response.text[:200]}...")
                        
                    # Test 3: Try to login without CSRF token
                    print("\n3. Testing POST /auth/ without CSRF token")
                    login_data_no_csrf = {
                        'form_type': 'login',
                        'email': 'seeker@example.com',
                        'password': 'password123'
                    }
                    
                    no_csrf_response = session.post(f"{BASE_URL}/auth/", data=login_data_no_csrf, headers=headers, allow_redirects=False)
                    print(f"   Status: {no_csrf_response.status_code}")
                    
                    if no_csrf_response.status_code == 400:
                        print("   ✓ Correctly rejected request without CSRF token")
                    else:
                        print("   ❌ Request without CSRF token was accepted")
                        
                else:
                    print("   ❌ No CSRF token found in login form")
            else:
                print("   ❌ No login form found")
                
        else:
            print(f"   ❌ Failed to get login page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_csrf_configuration():
    print("\n4. Testing CSRF Configuration")
    try:
        # Try to access a protected endpoint to see CSRF behavior
        session = requests.Session()
        
        # First get a CSRF token
        response = session.get(f"{BASE_URL}/auth/?mode=login")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            
            if csrf_input and csrf_input.get('value'):
                valid_token = csrf_input.get('value')
                print(f"   Got valid token: {valid_token[:20]}...")
                
                # Test with invalid token
                print("\n5. Testing with invalid CSRF token")
                invalid_data = {
                    'form_type': 'login',
                    'email': 'test@example.com',
                    'password': 'test123',
                    'csrf_token': 'invalid_token_12345'
                }
                
                invalid_response = session.post(f"{BASE_URL}/auth/", data=invalid_data, allow_redirects=False)
                print(f"   Status with invalid token: {invalid_response.status_code}")
                
                if invalid_response.status_code == 400:
                    print("   ✓ CSRF protection working - invalid token rejected")
                else:
                    print("   ❌ CSRF protection not working - invalid token accepted")
                    
            else:
                print("   ❌ Could not get CSRF token for testing")
        else:
            print(f"   ❌ Could not access login page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing CSRF configuration: {e}")

if __name__ == "__main__":
    test_csrf_tokens()
    test_csrf_configuration()
    print("\n🎯 CSRF Debug Complete!")
