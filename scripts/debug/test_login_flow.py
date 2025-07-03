#!/usr/bin/env python3
"""
Test script to debug the login flow
"""
import requests
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_login_flow():
    """Test the complete login flow"""
    base_url = "http://localhost:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🔍 Testing Login Flow...")
    print(f"Base URL: {base_url}")
    
    # Step 1: Get the login page
    print("\n1. Getting login page...")
    login_page_url = f"{base_url}/auth/"
    response = session.get(login_page_url)
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    
    if response.status_code != 200:
        print("❌ Failed to get login page")
        return False
    
    # Step 2: Post login credentials
    print("\n2. Posting login credentials...")
    login_data = {
        'email': 'seeker@example.com',
        'password': 'password123',
        'form_type': 'login'
    }
    
    response = session.post(login_page_url, data=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if 'Location' in response.headers:
        print(f"   Redirect Location: {response.headers['Location']}")
    
    # Step 3: Check what happens with redirects
    print("\n3. Following redirects...")
    response = session.post(login_page_url, data=login_data, allow_redirects=True)
    print(f"   Final Status: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    # Step 4: Check if we can access the dashboard
    print("\n4. Checking dashboard access...")
    dashboard_url = f"{base_url}/dashboard"
    response = session.get(dashboard_url)
    print(f"   Dashboard Status: {response.status_code}")
    print(f"   Dashboard URL: {response.url}")
    
    if response.status_code == 200 and 'dashboard' in response.url:
        print("✅ Login flow working correctly!")
        return True
    else:
        print("❌ Login flow has issues")
        print(f"   Response content (first 500 chars): {response.text[:500]}")
        return False

if __name__ == "__main__":
    test_login_flow()
