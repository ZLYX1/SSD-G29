#!/usr/bin/env python3
"""
Quick test to verify the new messaging code is working
"""
import requests
import json
import time

def test_messaging_endpoint():
    """Test the messaging endpoint with both types of payloads"""
    
    print("🔧 QUICK MESSAGING TEST")
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
    
    print("🧪 Test 1: Encrypted data payload")
    print(f"📤 Payload: {json.dumps(encrypted_payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/messaging/send',
            json=encrypted_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📥 Response: {response.json()}")
        elif response.status_code == 302:
            print("📥 Response: Redirected (authentication required)")
        elif response.status_code == 400:
            print(f"📥 Response: {response.text}")
        else:
            print(f"📥 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 2: Plain text payload
    plain_payload = {
        "recipient_id": 18,
        "content": "Test plain text message"
    }
    
    print("\n🧪 Test 2: Plain text payload")
    print(f"📤 Payload: {json.dumps(plain_payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/messaging/send',
            json=plain_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📥 Response: {response.json()}")
        elif response.status_code == 302:
            print("📥 Response: Redirected (authentication required)")
        elif response.status_code == 400:
            print(f"📥 Response: {response.text}")
        else:
            print(f"📥 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Check logs
    print("\n📋 Checking container logs...")
    try:
        import subprocess
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.dev.yml', 'logs', 'web', '--tail=30'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logs = result.stdout
        if "NEW CODE v3.0" in logs:
            print("✅ NEW CODE IS RUNNING!")
        else:
            print("❌ Old code still running")
            
        print("Recent logs:")
        print(logs[-1000:])  # Last 1000 characters
        
    except Exception as e:
        print(f"❌ Could not get logs: {e}")

if __name__ == '__main__':
    test_messaging_endpoint()
