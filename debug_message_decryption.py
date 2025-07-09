#!/usr/bin/env python3
"""
Debug script to test message decryption flow
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_message_loading():
    """Test the message loading API endpoint"""
    print("🔍 Testing message loading API endpoint...")
    
    session = requests.Session()
    
    # Test the messages API endpoint
    try:
        response = session.get(f"{BASE_URL}/messaging/api/messages/18")
        print(f"✓ API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response data: {json.dumps(data, indent=2)}")
            
            if 'messages' in data:
                messages = data['messages']
                print(f"✓ Found {len(messages)} messages")
                
                for i, msg in enumerate(messages):
                    print(f"\n📨 Message {i+1}:")
                    print(f"  - ID: {msg.get('id')}")
                    print(f"  - Sender: {msg.get('sender_id')}")
                    print(f"  - Recipient: {msg.get('recipient_id')}")
                    print(f"  - Is Encrypted: {msg.get('is_encrypted')}")
                    print(f"  - Content: {msg.get('content')}")
                    
                    if msg.get('is_encrypted'):
                        print(f"  - Encrypted Content: {msg.get('encrypted_content')}")
                        print(f"  - Nonce: {msg.get('nonce')}")
                        print(f"  - Algorithm: {msg.get('algorithm')}")
                        
            else:
                print("❌ No messages found in response")
        else:
            print(f"❌ API request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_conversations_api():
    """Test the conversations API endpoint"""
    print("\n🔍 Testing conversations API endpoint...")
    
    session = requests.Session()
    
    try:
        response = session.get(f"{BASE_URL}/messaging/api/conversations")
        print(f"✓ API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ API request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def main():
    print("🧪 DEBUGGING MESSAGE DECRYPTION FLOW")
    print("=" * 50)
    
    test_message_loading()
    test_conversations_api()
    
    print("\n" + "=" * 50)
    print("🎯 DEBUGGING COMPLETE")
    print("\nNext steps:")
    print("1. Check browser console for decryption errors")
    print("2. Verify conversation ID format in frontend")
    print("3. Test manual decryption in browser console")

if __name__ == "__main__":
    main()
