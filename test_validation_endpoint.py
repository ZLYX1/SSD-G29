#!/usr/bin/env python3
"""
Test the temporary validation endpoint to debug our logic
"""

import requests
import json

def test_validation_logic():
    """Test the validation logic using our temporary endpoint"""
    print("🧪 Testing validation logic with temporary endpoint...")
    
    test_cases = [
        {
            'name': 'Empty payload',
            'data': {}
        },
        {
            'name': 'Plain text message only',
            'data': {
                'recipient_id': 2,
                'content': 'Hello world'
            }
        },
        {
            'name': 'Empty encrypted_data',
            'data': {
                'recipient_id': 2,
                'encrypted_data': {}
            }
        },
        {
            'name': 'Encrypted data with missing encrypted_content',
            'data': {
                'recipient_id': 2,
                'encrypted_data': {
                    'nonce': 'dGVzdG5vbmNl',
                    'algorithm': 'AES-GCM-128'
                }
            }
        },
        {
            'name': 'Complete encrypted data',
            'data': {
                'recipient_id': 2,
                'encrypted_data': {
                    'encrypted_content': 'dGVzdCBlbmNyeXB0ZWQgY29udGVudA==',
                    'nonce': 'dGVzdG5vbmNl',
                    'algorithm': 'AES-GCM-128'
                }
            }
        },
        {
            'name': 'Both content and encrypted_data',
            'data': {
                'recipient_id': 2,
                'content': 'Hello world',
                'encrypted_data': {
                    'encrypted_content': 'dGVzdCBlbmNyeXB0ZWQgY29udGVudA==',
                    'nonce': 'dGVzdG5vbmNl',
                    'algorithm': 'AES-GCM-128'
                }
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\\n📤 Testing: {test_case['name']}")
        print(f"Payload: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(
                "http://localhost:5000/messaging/test-validation",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                    
                    if response_json.get('success'):
                        print("✅ Validation passed")
                    else:
                        print(f"❌ Validation failed: {response_json.get('error')}")
                        
                except:
                    print(f"❌ Could not parse response as JSON: {response.text}")
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")

def check_test_logs():
    """Check the logs for our test route output"""
    print("\\n📋 Checking logs for test route output...")
    import subprocess
    
    try:
        result = subprocess.run(
            ['docker', 'logs', 'safe-companions-web-dev', '--tail', '50'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout
            
            # Look for our test route markers
            test_markers = [
                "🧪 TEST ROUTE:",
                "✅ VALIDATION PASSED",
                "❌ VALIDATION FAILED"
            ]
            
            found_markers = []
            for marker in test_markers:
                if marker in logs:
                    found_markers.append(marker)
            
            if found_markers:
                print(f"✅ Found test markers: {found_markers}")
                print("\\n📋 Test route output:")
                print("-" * 80)
                
                lines = logs.split('\\n')
                test_lines = [line for line in lines if any(marker in line for marker in test_markers)]
                
                for line in test_lines[-20:]:
                    print(line)
                    
                print("-" * 80)
            else:
                print("❌ No test route output found in logs")
                
        else:
            print(f"❌ Failed to get container logs: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error checking logs: {str(e)}")

if __name__ == "__main__":
    print("🧪 Starting validation logic test...")
    test_validation_logic()
    check_test_logs()
    print("🧪 Test complete!")
