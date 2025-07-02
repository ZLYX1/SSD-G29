#!/usr/bin/env python3
"""
Automated test for the reporting system endpoints
"""
import requests
import json
from datetime import datetime

def test_reporting_endpoints():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Reporting System Endpoints")
    print("=" * 50)
    
    # Test 1: Check if app is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ App is running (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ App is not accessible: {e}")
        return
    
    # Test 2: Test admin dashboard (without auth - should redirect)
    try:
        response = requests.get(f"{base_url}/report/admin", allow_redirects=False)
        if response.status_code in [302, 401]:
            print(f"✅ Admin dashboard properly protected (Status: {response.status_code})")
        else:
            print(f"⚠️ Admin dashboard protection may be weak (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing admin dashboard: {e}")
    
    # Test 3: Test report submission form (should require auth)
    try:
        response = requests.get(f"{base_url}/report/submit", allow_redirects=False)
        if response.status_code in [302, 401]:
            print(f"✅ Report submission properly protected (Status: {response.status_code})")
        else:
            print(f"⚠️ Report submission protection may be weak (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing report submission: {e}")
    
    # Test 4: Test my reports page (should require auth)
    try:
        response = requests.get(f"{base_url}/report/my-reports", allow_redirects=False)
        if response.status_code in [302, 401]:
            print(f"✅ My reports page properly protected (Status: {response.status_code})")
        else:
            print(f"⚠️ My reports page protection may be weak (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing my reports page: {e}")
    
    # Test 5: Test auth endpoints are accessible
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print(f"✅ Login page accessible (Status: {response.status_code})")
        else:
            print(f"⚠️ Login page issue (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing login page: {e}")
    
    try:
        response = requests.get(f"{base_url}/register")
        if response.status_code == 200:
            print(f"✅ Register page accessible (Status: {response.status_code})")
        else:
            print(f"⚠️ Register page issue (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing register page: {e}")
    
    print("\n🎯 Endpoint Testing Complete!")
    print("\nNext Steps for Manual Testing:")
    print("1. Login as admin: admin@safecompanions.com / admin123")
    print("2. Visit: http://localhost:5000/report/admin")
    print("3. Test filtering, search, and report management")
    print("4. Login as regular user and test report submission")
    print("5. Test 'Report User' button on user profiles")

if __name__ == '__main__':
    test_reporting_endpoints()
