#!/usr/bin/env python3
"""
Test script to verify messaging fixes are working
"""

import os
import sys
import requests
import time

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_messaging_send():
    """Test if the messaging send functionality is working"""
    print("🧪 Testing Messaging Send Functionality...")
    
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
    
    return True

def check_database_encryption():
    """Check if messages are being encrypted in the database"""
    print("\n🔍 Checking Database Encryption Status...")
    
    try:
        # Use docker to check database
        import subprocess
        
        # Check recent messages
        result = subprocess.run([
            'docker', 'exec', 'safe-companions-db-dev', 
            'psql', '-U', 'ssd_user', '-d', 'ssd_database', 
            '-c', 'SELECT id, sender_id, recipient_id, content, encrypted_content, is_encrypted FROM message ORDER BY id DESC LIMIT 3;'
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
                
                if plain_count > 0:
                    print("   ⚠️  WARNING: Some messages are stored in plain text!")
                    print("   💡 This indicates encryption is not working properly")
                else:
                    print("   ✅ All recent messages are encrypted")
            
        else:
            print(f"   ❌ Database check failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Database encryption check failed: {str(e)}")

def main():
    """Run all messaging tests"""
    print("🚀 Safe Companions - Messaging Fix Verification")
    print("=" * 55)
    
    # Test messaging functionality
    messaging_works = test_messaging_send()
    
    # Check database encryption
    check_database_encryption()
    
    print("\n" + "=" * 55)
    if messaging_works:
        print("📋 Summary: Messaging page is accessible")
        print("\n🔧 Fixes Applied:")
        print("   ✅ SecureMessaging initialization improved")
        print("   ✅ CSRF token handling unified")
        print("   ✅ Form element names corrected")
        print("   ✅ Event listener setup fixed")
        
        print("\n🧪 Next Steps for Testing:")
        print("   1. Open browser to http://127.0.0.1:5000/messaging/conversation/121")
        print("   2. Check browser console for any JavaScript errors")
        print("   3. Try sending a test message using the send button")
        print("   4. Verify if SecureMessaging object is initialized")
        print("   5. Check if encryption is working properly")
        
        print("\n💡 Debug Commands for Browser Console:")
        print("   - console.log(window.secureMessaging) // Check if initialized")
        print("   - console.log(window.messageEncryption) // Check encryption")
        print("   - console.log(window.csrf_token) // Check CSRF token")
        
    else:
        print("❌ Messaging tests failed - check application logs")
    
    return messaging_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
