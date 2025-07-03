"""
Test script for Rate Limiting and Account Lockout functionality
Tests the comprehensive security features
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor
import threading

BASE_URL = "http://localhost:5000"
lock = threading.Lock()

def test_login_rate_limiting():
    """Test login rate limiting"""
    print("🔒 Testing Login Rate Limiting...")
    
    login_data = {
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword',
        'form_type': 'login'
    }
    
    responses = []
    
    # Make 6 failed login attempts (should trigger rate limiting after 5)
    for i in range(6):
        try:
            response = requests.post(f"{BASE_URL}/auth/", data=login_data, allow_redirects=False)
            responses.append({
                'attempt': i + 1,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content_length': len(response.content)
            })
            print(f"  Attempt {i + 1}: Status {response.status_code}")
        except Exception as e:
            print(f"  Attempt {i + 1}: Error - {e}")
        
        time.sleep(0.5)  # Small delay between attempts
    
    # Check if rate limiting kicked in
    rate_limited_attempts = [r for r in responses if r['status_code'] == 429]
    
    if rate_limited_attempts:
        print(f"✅ Rate limiting working! {len(rate_limited_attempts)} requests were rate limited")
    else:
        print("❌ Rate limiting may not be working properly")
    
    return responses


def test_messaging_rate_limiting():
    """Test messaging rate limiting (requires authentication)"""
    print("\n💬 Testing Messaging Rate Limiting...")
    
    # First login as a valid user
    login_data = {
        'email': 'seeker@example.com',
        'password': 'password123',
        'form_type': 'login'
    }
    
    session = requests.Session()
    
    try:
        # Login
        login_response = session.post(f"{BASE_URL}/auth/", data=login_data)
        print(f"  Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200 or 'dashboard' in login_response.url:
            print("  ✅ Successfully logged in")
            
            # Test messaging rate limit by sending many messages rapidly
            message_data = {
                'recipient_id': 5,  # Some escort user
                'content': 'Test message for rate limiting'
            }
            
            responses = []
            for i in range(35):  # Try to exceed the 30 messages per 15 minutes limit
                try:
                    response = session.post(f"{BASE_URL}/messaging/send", json=message_data)
                    responses.append({
                        'attempt': i + 1,
                        'status_code': response.status_code
                    })
                    if i % 10 == 0:
                        print(f"  Message {i + 1}: Status {response.status_code}")
                except Exception as e:
                    print(f"  Message {i + 1}: Error - {e}")
            
            # Check for rate limiting
            rate_limited = [r for r in responses if r['status_code'] == 429]
            if rate_limited:
                print(f"  ✅ Messaging rate limiting working! {len(rate_limited)} requests were rate limited")
            else:
                print("  ❌ Messaging rate limiting may not be working")
                
        else:
            print("  ❌ Failed to login for messaging test")
            
    except Exception as e:
        print(f"  ❌ Error in messaging test: {e}")


def test_security_dashboard():
    """Test security dashboard access"""
    print("\n🛡️ Testing Security Dashboard...")
    
    try:
        # Try to access without authentication
        response = requests.get(f"{BASE_URL}/security/dashboard")
        print(f"  Unauthenticated access: Status {response.status_code}")
        
        # Login as admin
        login_data = {
            'email': 'admin@example.com',
            'password': 'password123',
            'form_type': 'login'
        }
        
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/auth/", data=login_data)
        
        if login_response.status_code == 200 or 'dashboard' in login_response.url:
            # Try to access security dashboard as admin
            dashboard_response = session.get(f"{BASE_URL}/security/dashboard")
            print(f"  Admin access: Status {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("  ✅ Security dashboard accessible to admin")
            else:
                print("  ❌ Security dashboard not accessible to admin")
                
            # Test security API endpoints
            events_response = session.get(f"{BASE_URL}/security/events")
            print(f"  Security events API: Status {events_response.status_code}")
            
            stats_response = session.get(f"{BASE_URL}/security/stats")
            print(f"  Security stats API: Status {stats_response.status_code}")
            
        else:
            print("  ❌ Failed to login as admin")
            
    except Exception as e:
        print(f"  ❌ Error testing security dashboard: {e}")


def test_account_lockout():
    """Test account lockout functionality"""
    print("\n🔐 Testing Account Lockout...")
    
    # Use a test email that should exist
    test_email = "seeker@example.com"
    wrong_password = "definitelywrong"
    
    login_data = {
        'email': test_email,
        'password': wrong_password,
        'form_type': 'login'
    }
    
    responses = []
    
    # Make multiple failed login attempts to trigger account lockout
    for i in range(7):  # Should trigger lockout after 5 attempts
        try:
            response = requests.post(f"{BASE_URL}/auth/", data=login_data, allow_redirects=False)
            responses.append({
                'attempt': i + 1,
                'status_code': response.status_code,
                'content': response.text[:200] if response.text else ''
            })
            print(f"  Attempt {i + 1}: Status {response.status_code}")
            
            # Check if the response contains lockout message
            if 'locked' in response.text.lower():
                print(f"  🔒 Account lockout detected on attempt {i + 1}")
                break
                
        except Exception as e:
            print(f"  Attempt {i + 1}: Error - {e}")
        
        time.sleep(0.5)
    
    # Try with correct password to see if account is locked
    print("  Testing with correct password after lockout...")
    correct_login_data = {
        'email': test_email,
        'password': 'password123',
        'form_type': 'login'
    }
    
    try:
        correct_response = requests.post(f"{BASE_URL}/auth/", data=correct_login_data)
        if 'locked' in correct_response.text.lower():
            print("  ✅ Account lockout working - correct password also blocked")
        else:
            print("  ❌ Account lockout may not be working - correct password not blocked")
    except Exception as e:
        print(f"  Error testing correct password: {e}")


def concurrent_rate_limit_test():
    """Test rate limiting under concurrent load"""
    print("\n⚡ Testing Concurrent Rate Limiting...")
    
    def make_request(thread_id):
        with lock:
            print(f"  Thread {thread_id} starting...")
        
        login_data = {
            'email': f'test{thread_id}@example.com',
            'password': 'wrongpassword',
            'form_type': 'login'
        }
        
        results = []
        for i in range(3):
            try:
                response = requests.post(f"{BASE_URL}/auth/", data=login_data, timeout=10)
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Error: {e}")
        
        with lock:
            print(f"  Thread {thread_id} results: {results}")
        
        return results
    
    # Run concurrent requests
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        results = [future.result() for future in futures]
    
    print(f"  ✅ Concurrent test completed with {len(results)} threads")


def main():
    """Run all rate limiting and security tests"""
    print("🚀 Starting Rate Limiting and Account Lockout Tests")
    print("=" * 50)
    
    try:
        # Basic rate limiting tests
        test_login_rate_limiting()
        
        # Account lockout test
        test_account_lockout()
        
        # Messaging rate limiting (if user can login)
        test_messaging_rate_limiting()
        
        # Security dashboard test
        test_security_dashboard()
        
        # Concurrent load test
        concurrent_rate_limit_test()
        
        print("\n" + "=" * 50)
        print("🎉 All rate limiting tests completed!")
        print("\n📊 Check the security dashboard at:")
        print("   http://localhost:5000/security/dashboard")
        print("   (Login as admin@example.com / password123)")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")


if __name__ == "__main__":
    main()
