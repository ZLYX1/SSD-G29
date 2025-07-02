#!/usr/bin/env python3
"""
Test the login and dashboard fix
"""
import requests
import time

def test_login_and_dashboard():
    print("🔧 TESTING LOGIN AND DASHBOARD FIX")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Test 1: Access login page
        print("1. Testing login page access...")
        login_page = session.get("http://localhost:5000/auth")
        print(f"   Login page status: {login_page.status_code}")
        
        if login_page.status_code != 200:
            print("   ❌ Cannot access login page")
            return
        
        # Test 2: Attempt login with admin credentials
        print("2. Testing admin login...")
        login_data = {
            'email': 'admin@safecompanions.com',
            'password': 'admin123'
        }
        
        login_response = session.post("http://localhost:5000/login", data=login_data, allow_redirects=True)
        print(f"   Login response status: {login_response.status_code}")
        print(f"   Final URL: {login_response.url}")
        
        # Test 3: Try to access dashboard
        print("3. Testing dashboard access...")
        dashboard_response = session.get("http://localhost:5000/dashboard")
        print(f"   Dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("   ✅ Dashboard loads successfully!")
            
            # Check for the presence of key elements
            content = dashboard_response.text.lower()
            has_admin_welcome = "welcome, admin" in content
            has_system_stats = "system statistics" in content
            has_total_users = "total users" in content
            has_pending_reports = "pending reports" in content
            
            print(f"   Admin welcome message: {'✅ Found' if has_admin_welcome else '❌ Missing'}")
            print(f"   System statistics section: {'✅ Found' if has_system_stats else '❌ Missing'}")
            print(f"   Total users display: {'✅ Found' if has_total_users else '❌ Missing'}")
            print(f"   Pending reports display: {'✅ Found' if has_pending_reports else '❌ Missing'}")
            
            if all([has_admin_welcome, has_system_stats, has_total_users, has_pending_reports]):
                print("   🎉 All dashboard elements found - Fix successful!")
            else:
                print("   ⚠️ Some dashboard elements missing")
                
        else:
            print(f"   ❌ Dashboard access failed: {dashboard_response.status_code}")
            print(f"   Response URL: {dashboard_response.url}")
            
            # Save response for debugging
            with open("debug_dashboard_response.html", "w", encoding="utf-8") as f:
                f.write(dashboard_response.text)
            print("   Debug response saved to debug_dashboard_response.html")
    
    except Exception as e:
        print(f"   ❌ Error during testing: {e}")
    
    print("\n🔧 TEST COMPLETE")
    print("Now try logging in manually at: http://localhost:5000/auth")
    print("Admin credentials: admin@safecompanions.com / admin123")

if __name__ == '__main__':
    test_login_and_dashboard()
