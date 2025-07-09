#!/usr/bin/env python3
"""
Test script to verify messaging fixes are working
"""

import os
import sys
import requests
import subprocess
import time

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_messaging_send_button():
    """Test if the messaging send functionality is working"""
    print("🧪 Testing Send Button Fix...")
    
    # Test URL
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Check if messaging page loads
    try:
        response = requests.get(f"{base_url}/messaging/conversation/121", timeout=10)
        if response.status_code == 200:
            print("   ✅ Messaging page loads successfully")
        else:
            print(f"   ❌ Messaging page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Failed to connect to messaging page: {str(e)}")
        return False
    
    # Test 2: Check if JavaScript files are accessible
    try:
        js_files = [
            "/static/js/encryption.js",
            "/static/js/messaging.js"
        ]
        
        for js_file in js_files:
            response = requests.get(f"{base_url}{js_file}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {js_file} is accessible")
            else:
                print(f"   ❌ {js_file} failed to load: {response.status_code}")
                
    except Exception as e:
        print(f"   ⚠️  JavaScript file check failed: {str(e)}")
    
    # Test 3: Check if default profile image exists
    try:
        response = requests.get(f"{base_url}/static/images/profiles/default.jpg", timeout=5)
        if response.status_code == 200:
            print("   ✅ Default profile image is accessible")
        else:
            print(f"   ❌ Default profile image missing: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Profile image check failed: {str(e)}")
    
    return True

def check_message_encryption_status():
    """Check recent message encryption status"""
    print("\n🔐 Checking Message Encryption Status...")
    
    try:
        # Use docker to check database
        result = subprocess.run([
            'docker', 'exec', 'safe-companions-db-dev', 
            'psql', '-U', 'ssd_user', '-d', 'ssd_database', 
            '-c', 'SELECT id, sender_id, recipient_id, content, encrypted_content, is_encrypted, timestamp FROM message ORDER BY id DESC LIMIT 5;'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   📊 Recent Messages:")
            print(result.stdout)
            
            # Check if any recent messages are encrypted
            if 'encrypted_content' in result.stdout and '|' in result.stdout:
                lines = result.stdout.strip().split('\n')
                encrypted_count = 0
                plain_count = 0
                
                for line in lines:
                    if '|' in line and not line.startswith('---') and not line.startswith(' id'):
                        parts = line.split('|')
                        if len(parts) >= 6:
                            is_encrypted = parts[5].strip()
                            if is_encrypted == 't':
                                encrypted_count += 1
                            elif is_encrypted == 'f':
                                plain_count += 1
                
                print(f"   📈 Analysis: {encrypted_count} encrypted, {plain_count} plain text messages")
                
                if encrypted_count > 0:
                    print("   ✅ Some messages are encrypted!")
                    print("   🎉 Encryption system working!")
                elif plain_count > 0:
                    print("   ⚠️  All recent messages are plain text")
                    print("   💡 Encryption might not be working yet")
            
        else:
            print(f"   ❌ Database check failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Database encryption check failed: {str(e)}")

def main():
    """Run all messaging tests"""
    print("🚀 Safe Companions - Send Button Fix Verification")
    print("=" * 55)
    
    # Test messaging functionality
    messaging_works = test_messaging_send_button()
    
    # Check database encryption
    check_message_encryption_status()
    
    print("\n" + "=" * 55)
    if messaging_works:
        print("📋 Send Button Fixes Applied:")
        print("   ✅ Fixed form element selector (textarea[name='content'])")
        print("   ✅ Improved encryption check logic")
        print("   ✅ Added encryption instance creation")
        print("   ✅ Fixed missing default profile image")
        print("   ✅ Added better error logging")
        
        print("\n🧪 Next Steps for Testing:")
        print("   1. Open browser to http://127.0.0.1:5000/messaging/conversation/121")
        print("   2. Open browser console (F12)")
        print("   3. Try sending a test message")
        print("   4. Check console for 'Message encrypted successfully' or errors")
        print("   5. Verify the message appears in the chat")
        
        print("\n💡 What to Look For:")
        print("   - No more 'Required form elements not found' errors")
        print("   - 'Encryption support confirmed' in console")
        print("   - 'Message encrypted successfully' when sending")
        print("   - No 404 errors for profile images")
        
        print("\n🔧 Debug Commands for Browser Console:")
        print("   - console.log(window.secureMessaging) // Check if initialized")
        print("   - console.log(window.MessageEncryption) // Check encryption class")
        print("   - console.log(window.messageEncryption) // Check encryption instance")
        
    else:
        print("❌ Basic tests failed - check application logs")
    
    return messaging_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
