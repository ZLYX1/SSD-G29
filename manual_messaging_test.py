#!/usr/bin/env python3
"""
Manual messaging system test guide for Safe Companions.
This script provides step-by-step instructions for manually testing the messaging system.
"""

import requests
import webbrowser
import time

BASE_URL = "http://localhost:5000"

def test_application_accessibility():
    """Test if the application is accessible"""
    print("🔍 Testing application accessibility...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code in [200, 302]:
            print("✅ Application is accessible")
            return True
        else:
            print(f"❌ Application returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to application: {e}")
        return False

def check_static_resources():
    """Check if JavaScript files are available"""
    print("\n🔍 Checking static resources...")
    
    js_files = [
        "/static/js/messaging.js",
        "/static/js/encryption.js"
    ]
    
    for js_file in js_files:
        try:
            response = requests.get(f"{BASE_URL}{js_file}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {js_file} is accessible")
            else:
                print(f"❌ {js_file} returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Error accessing {js_file}: {e}")

def generate_test_instructions():
    """Generate comprehensive test instructions"""
    print("\n" + "="*60)
    print("🧪 MANUAL MESSAGING SYSTEM TEST GUIDE")
    print("="*60)
    
    print("\n📋 STEP 1: PREPARE TEST ENVIRONMENT")
    print("-" * 40)
    print("1. Ensure the Safe Companions application is running")
    print("2. Open two different browsers (or incognito windows)")
    print("3. Have the following ready:")
    print(f"   - Application URL: {BASE_URL}")
    print("   - Two different email addresses for test accounts")
    
    print("\n📋 STEP 2: CREATE TEST ACCOUNTS")
    print("-" * 40)
    print("Browser 1 (User A):")
    print(f"1. Navigate to {BASE_URL}")
    print("2. Click 'Register' or go to /auth/register")
    print("3. Create account with:")
    print("   - Email: testuser1@example.com")
    print("   - Password: TestPassword123!")
    print("   - Fill in all required fields")
    print("4. Complete registration and verify/login")
    
    print("\nBrowser 2 (User B):")
    print(f"1. Navigate to {BASE_URL}")
    print("2. Create account with:")
    print("   - Email: testuser2@example.com")
    print("   - Password: TestPassword123!")
    print("3. Complete registration and verify/login")
    
    print("\n📋 STEP 3: TEST MESSAGING SYSTEM")
    print("-" * 40)
    print("In Browser 1 (User A):")
    print("1. Navigate to the messaging section")
    print("2. Look for a way to start a new conversation")
    print("3. Search for or select User B (testuser2@example.com)")
    print("4. Open the chat with User B")
    
    print("\n📋 STEP 4: SEND AND RECEIVE MESSAGES")
    print("-" * 40)
    print("Test Message Sending:")
    print("1. In Browser 1, type: 'Hello from User A!'")
    print("2. Click Send button")
    print("3. Check for success/error messages")
    print("4. Open Browser 2, navigate to messaging")
    print("5. Check if message appears for User B")
    
    print("\nTest Reply:")
    print("1. In Browser 2, reply: 'Hello from User B!'")
    print("2. Click Send button")
    print("3. Switch to Browser 1")
    print("4. Check if reply appears")
    
    print("\n📋 STEP 5: TEST ENCRYPTION")
    print("-" * 40)
    print("Browser Developer Tools Check:")
    print("1. Open Developer Tools (F12) in both browsers")
    print("2. Go to Network tab")
    print("3. Send a message")
    print("4. Look for API calls to /messaging/send")
    print("5. Check the request payload:")
    print("   ✅ Should contain 'encrypted_data' field")
    print("   ❌ Should NOT contain plain text message")
    
    print("\nConsole Check:")
    print("1. Open Console tab in Developer Tools")
    print("2. Send a message")
    print("3. Look for debug output:")
    print("   - Encryption success messages")
    print("   - Key derivation messages")
    print("   - Any JavaScript errors")
    
    print("\n📋 STEP 6: DATABASE VERIFICATION")
    print("-" * 40)
    print("If you have database access:")
    print("1. Connect to the PostgreSQL database")
    print("2. Query the messages table:")
    print("   SELECT id, sender_id, recipient_id, content, encrypted_data")
    print("   FROM message ORDER BY created_at DESC LIMIT 5;")
    print("3. Verify:")
    print("   ✅ 'content' field should be NULL or encrypted")
    print("   ✅ 'encrypted_data' field should contain encrypted data")
    print("   ❌ No plain text messages in database")
    
    print("\n📋 STEP 7: ERROR HANDLING TESTS")
    print("-" * 40)
    print("1. Try sending empty message")
    print("2. Try sending very long message")
    print("3. Try sending message with special characters")
    print("4. Check network connectivity (disconnect/reconnect)")
    print("5. Verify appropriate error messages appear")
    
    print("\n📋 EXPECTED RESULTS")
    print("-" * 40)
    print("✅ Messages send successfully")
    print("✅ Messages appear in real-time or on refresh")
    print("✅ All messages are encrypted in transit and storage")
    print("✅ No JavaScript console errors")
    print("✅ Appropriate error handling for edge cases")
    print("✅ User-friendly interface and feedback")
    
    print("\n📋 TROUBLESHOOTING")
    print("-" * 40)
    print("If messages don't send:")
    print("1. Check browser console for JavaScript errors")
    print("2. Check network tab for failed API calls")
    print("3. Verify user authentication (try refreshing page)")
    print("4. Check server logs: docker logs safe-companions-web-dev")
    
    print("\nIf encryption fails:")
    print("1. Verify encryption.js is loaded")
    print("2. Check if Web Crypto API is supported")
    print("3. Look for 'MessageCrypto' object in console")
    print("4. Verify client-side key derivation is working")
    
    print("\n" + "="*60)
    print("🎯 After completing these tests, you will know if:")
    print("   • The messaging system works end-to-end")
    print("   • Messages are properly encrypted")
    print("   • The user interface is functional")
    print("   • Error handling is appropriate")
    print("="*60)

def main():
    """Run accessibility tests and generate manual test guide"""
    print("🧪 Safe Companions Messaging System Test Generator")
    print("=" * 50)
    
    # Test basic accessibility
    if test_application_accessibility():
        print("✅ Application is ready for testing")
    else:
        print("❌ Application is not accessible - fix this first")
        return
    
    # Check static resources
    check_static_resources()
    
    # Generate manual test instructions
    generate_test_instructions()
    
    # Ask user if they want to open the application
    print(f"\n🌐 Would you like to open {BASE_URL} in your browser? (y/n)")
    try:
        if input().lower().startswith('y'):
            webbrowser.open(BASE_URL)
            print("✅ Browser opened - you can now start manual testing")
    except:
        pass
    
    print("\n💡 Use the manual testing guide above to verify messaging functionality!")

if __name__ == "__main__":
    main()
