#!/usr/bin/env python3
"""
Test the new test endpoint to verify the fix
"""
import requests
import json
import time

def test_new_endpoint():
    """Test the new test endpoint"""
    
    print("🧪 TESTING NEW TEST ENDPOINT")
    print("=" * 50)
    
    # Wait for container to be ready
    print("⏳ Waiting for container to be ready...")
    time.sleep(10)
    
    # Test 1: Encrypted data payload
    encrypted_payload = {
        "recipient_id": 18,
        "encrypted_data": {
            "encrypted_content": "grgu5cs+dfAw+8kPpm8VZ9tjg44ESQ==",
            "nonce": "LPCDIq34zp9QLPT5",
            "algorithm": "AES-GCM-128"
        }
    }
    
    print("🧪 Test 1: Encrypted data payload to /messaging/test-send")
    print(f"📤 Payload: {json.dumps(encrypted_payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/messaging/test-send',
            json=encrypted_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📥 Response: {response.json()}")
        else:
            print(f"📥 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 2: Plain text payload
    plain_payload = {
        "recipient_id": 18,
        "content": "Test plain text message"
    }
    
    print("\n🧪 Test 2: Plain text payload to /messaging/test-send")
    print(f"📤 Payload: {json.dumps(plain_payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/messaging/test-send',
            json=plain_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📥 Response: {response.json()}")
        else:
            print(f"📥 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 3: Missing fields payload
    missing_payload = {
        "recipient_id": 18
        # No content or encrypted_data
    }
    
    print("\n🧪 Test 3: Missing fields payload to /messaging/test-send")
    print(f"📤 Payload: {json.dumps(missing_payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/messaging/test-send',
            json=missing_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📥 Response: {response.json()}")
        else:
            print(f"📥 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Check logs
    print("\n📋 Checking container logs...")
    try:
        import subprocess
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.dev.yml', 'logs', 'web', '--tail=50'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logs = result.stdout
        if "NEW CODE v3.0 TEST" in logs:
            print("✅ NEW TEST ENDPOINT IS WORKING!")
        else:
            print("❌ Test endpoint not found in logs")
            
        print("Recent logs:")
        print(logs[-2000:])  # Last 2000 characters
        
    except Exception as e:
        print(f"❌ Could not get logs: {e}")

if __name__ == '__main__':
    test_new_endpoint()
