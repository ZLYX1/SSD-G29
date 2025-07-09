#!/usr/bin/env python3
"""
Direct backend test script to test message validation logic
This bypasses frontend authentication and tests the backend directly
"""

import requests
import json

def test_messaging_validation():
    """Test the messaging validation logic directly"""
    print("🧪 Testing messaging validation logic...")
    
    # Create a session with fake authentication
    session = requests.Session()
    
    # Test cases to verify our validation fix
    test_cases = [
        {
            'name': 'Empty payload',
            'data': {},
            'expected_error': True
        },
        {
            'name': 'Missing recipient_id',
            'data': {
                'content': 'Hello world'
            },
            'expected_error': True
        },
        {
            'name': 'Plain text message (no authentication)',
            'data': {
                'recipient_id': 2,
                'content': 'Hello, this is a plain text test message!'
            },
            'expected_error': True  # Should fail due to no auth
        },
        {
            'name': 'Empty encrypted_data',
            'data': {
                'recipient_id': 2,
                'encrypted_data': {}
            },
            'expected_error': True
        },
        {
            'name': 'Encrypted data with missing fields',
            'data': {
                'recipient_id': 2,
                'encrypted_data': {
                    'encrypted_content': 'dGVzdA=='
                    # Missing nonce and algorithm
                }
            },
            'expected_error': True
        },
        {
            'name': 'Complete encrypted data (no authentication)',
            'data': {
                'recipient_id': 2,
                'encrypted_data': {
                    'encrypted_content': 'dGVzdCBlbmNyeXB0ZWQgY29udGVudA==',
                    'nonce': 'dGVzdG5vbmNl',
                    'algorithm': 'AES-GCM-128'
                }
            },
            'expected_error': True  # Should fail due to no auth, not validation
        }
    ]
    
    for test_case in test_cases:
        print(f"\\n📤 Testing: {test_case['name']}")
        print(f"Payload: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            # Send the message
            response = session.post(
                "http://localhost:5000/messaging/send",
                json=test_case['data'],
                headers={
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")
            
            # Try to parse as JSON
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                
                error_msg = response_json.get('error', '')
                
                # Check if we're getting the validation error we expect
                if 'Missing required fields' in error_msg:
                    print("✅ Got 'Missing required fields' error as expected")
                elif 'CSRF token' in response.text:
                    print("⚠️ CSRF token error (expected without auth)")
                elif 'login' in response.text.lower():
                    print("⚠️ Authentication required (expected without auth)")
                elif response_json.get('success'):
                    print("✅ Request succeeded")
                else:
                    print(f"❓ Other error: {error_msg}")
                    
            except:
                if response.status_code == 400 and 'CSRF token' in response.text:
                    print("⚠️ CSRF token error (expected without auth)")
                elif response.status_code == 302 or 'login' in response.text.lower():
                    print("⚠️ Authentication redirect (expected without auth)")
                else:
                    print(f"❌ Could not parse response as JSON")
                    print(f"Response text (first 200 chars): {response.text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Request error: {str(e)}")

def check_enhanced_debug_logs():
    """Check the logs for our enhanced debug output"""
    print("\\n📋 Checking container logs for enhanced debug output...")
    import subprocess
    
    try:
        result = subprocess.run(
            ['docker', 'logs', 'safe-companions-web-dev', '--tail', '100'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout
            
            # Look for our specific debug markers
            debug_markers = [
                "🚀🚀🚀 ENHANCED DEBUG",
                "DEBUG: Validation check details:",
                "DEBUG: ✅ VALIDATION PASSED",
                "DEBUG: ❌ VALIDATION FAILED",
                "🔧 MessageController:"
            ]
            
            found_markers = []
            for marker in debug_markers:
                if marker in logs:
                    found_markers.append(marker)
            
            if found_markers:
                print(f"✅ Found debug markers: {found_markers}")
                print("\\n📋 Recent debug output:")
                print("-" * 80)
                
                # Extract lines containing our debug output
                lines = logs.split('\\n')
                debug_lines = [line for line in lines if any(marker in line for marker in debug_markers)]
                
                for line in debug_lines[-20:]:  # Show last 20 debug lines
                    print(line)
                    
                print("-" * 80)
            else:
                print("❌ No enhanced debug output found in logs")
                print("💡 This suggests the enhanced debug code is not running")
                
        else:
            print(f"❌ Failed to get container logs: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error checking logs: {str(e)}")

if __name__ == "__main__":
    print("🧪 Starting direct backend validation test...")
    test_messaging_validation()
    check_enhanced_debug_logs()
    print("🧪 Test complete!")
