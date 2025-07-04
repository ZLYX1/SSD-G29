#!/usr/bin/env python3
"""
Quick test to verify the login flow is working correctly
"""
import requests
import sys

def test_login_flow():
    """Test the complete login flow"""
    base_url = "http://localhost:5000"
    
    print("🔧 Testing login flow...")
    
    # Create a session to preserve cookies
    session = requests.Session()
    
    # Test 1: Login with valid credentials
    print("📝 Testing login with seeker@example.com...")
    login_data = {
        "email": "seeker@example.com",
        "password": "password123",
        "form_type": "login"
    }
    
    response = session.post(f"{base_url}/auth/", data=login_data, allow_redirects=False)
    print(f"Status: {response.status_code}")
    print(f"Location: {response.headers.get('Location', 'None')}")
    
    if response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        if '/dashboard' in redirect_url:
            print("✅ Login redirects to dashboard correctly!")
        else:
            print(f"❌ Login redirects to {redirect_url}, expected /dashboard")
            return False
    else:
        print(f"❌ Login failed with status {response.status_code}")
        return False
    
    # Test 2: Access dashboard with session
    print("🏠 Testing dashboard access...")
    dashboard_response = session.get(f"{base_url}/dashboard", allow_redirects=False)
    print(f"Dashboard status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("✅ Dashboard access successful!")
        
        # Check if the response contains expected content
        if 'Dashboard (Seeker)' in dashboard_response.text:
            print("✅ Dashboard shows correct user role!")
        else:
            print("⚠️  Dashboard content may not be correct")
            
        return True
    elif dashboard_response.status_code == 302:
        redirect_url = dashboard_response.headers.get('Location', '')
        print(f"❌ Dashboard redirects to {redirect_url}, should be accessible")
        return False
    else:
        print(f"❌ Dashboard access failed with status {dashboard_response.status_code}")
        return False

if __name__ == "__main__":
    try:
        success = test_login_flow()
        if success:
            print("\n🎉 All tests passed! Login flow is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the output above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
