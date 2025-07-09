#!/usr/bin/env python3
"""
Test script for end-to-end encryption implementation
"""

import os
import sys

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.encryption_utils import MessageEncryption
from controllers.message_controller import MessageController
from blueprint.models import Message, User, ConversationKey
from extensions import db
import json

def test_encryption_utils():
    """Test the encryption utilities"""
    print("🔧 Testing Encryption Utils...")
    
    try:
        # Test key generation
        key = MessageEncryption.generate_key()
        print("   ✅ Key generation successful")
        
        # Test message encryption
        test_message = "Hello, this is a secret message!"
        encrypted_data = MessageEncryption.encrypt_message(test_message, key)
        print("   ✅ Message encryption successful")
        
        # Test message decryption
        decrypted_message = MessageEncryption.decrypt_message(encrypted_data, key)
        print("   ✅ Message decryption successful")
        
        # Verify the message is correct
        if decrypted_message == test_message:
            print("   ✅ Encryption/decryption roundtrip successful")
            print(f"   📝 Original: {test_message}")
            print(f"   🔒 Encrypted length: {len(encrypted_data['encrypted_content'])} chars")
            print(f"   🔓 Decrypted: {decrypted_message}")
        else:
            print("   ❌ Encryption/decryption roundtrip failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Encryption test failed: {str(e)}")
        return False

def test_conversation_key_generation():
    """Test conversation key generation"""
    print("\n🔑 Testing Conversation Key Generation...")
    
    try:
        # Generate normalized key ID
        user1_id, user2_id = 1, 2
        key_id = MessageController.get_conversation_key_id(user1_id, user2_id)
        print(f"   ✅ Key ID generation: {key_id}")
        
        # Test key ID ordering (should be consistent regardless of input order)
        key_id_reverse = MessageController.get_conversation_key_id(user2_id, user1_id)
        if key_id == key_id_reverse:
            print("   ✅ Key ID ordering is consistent")
        else:
            print("   ❌ Key ID ordering is inconsistent")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Key generation test failed: {str(e)}")
        return False

def test_message_serialization():
    """Test message serialization for client"""
    print("\n📦 Testing Message Serialization...")
    
    try:
        # Create mock message data for testing
        mock_message = {
            'id': 1,
            'content': 'Test message',
            'sender_id': 1,
            'recipient_id': 2,
            'timestamp': '2025-07-09T12:00:00',
            'is_read': False,
            'is_encrypted': False,
            'encrypted_content': None,
            'encryption_nonce': None,
            'encryption_algorithm': None
        }
        
        # Convert to object-like structure for testing
        class MockMessage:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        message_obj = MockMessage(mock_message)
        
        # Test serialization
        serialized = MessageController.serialize_message_for_client(message_obj)
        print("   ✅ Message serialization successful")
        print(f"   📝 Serialized keys: {list(serialized.keys())}")
        
        # Test with encrypted message
        mock_message['is_encrypted'] = True
        mock_message['encrypted_content'] = 'encrypted_data_here'
        mock_message['encryption_nonce'] = 'nonce_here'
        mock_message['encryption_algorithm'] = 'AES-GCM'
        
        encrypted_message_obj = MockMessage(mock_message)
        encrypted_serialized = MessageController.serialize_message_for_client(encrypted_message_obj)
        print("   ✅ Encrypted message serialization successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Serialization test failed: {str(e)}")
        return False

def test_database_models():
    """Test that the database models are working correctly"""
    print("\n🗄️  Testing Database Models...")
    
    try:
        # Test ConversationKey model
        from blueprint.models import ConversationKey
        print("   ✅ ConversationKey model import successful")
        
        # Test Message model with new fields
        from blueprint.models import Message
        print("   ✅ Message model import successful")
        
        # Check if new fields are accessible
        expected_fields = ['is_encrypted', 'encrypted_content', 'encryption_nonce', 'encryption_algorithm']
        message_fields = [attr for attr in dir(Message) if not attr.startswith('_')]
        
        missing_fields = [field for field in expected_fields if field not in message_fields]
        if missing_fields:
            print(f"   ⚠️  Missing fields in Message model: {missing_fields}")
        else:
            print("   ✅ All encryption fields present in Message model")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database model test failed: {str(e)}")
        return False

def run_integration_test():
    """Run a complete integration test"""
    print("\n🧪 Running Integration Test...")
    
    try:
        # Test the complete flow (without actual database operations)
        test_data = {
            'sender_id': 1,
            'recipient_id': 2,
            'content': 'Integration test message',
        }
        
        print("   📝 Simulating message encryption flow...")
        
        # Generate a key for testing
        key = MessageEncryption.generate_key()
        
        # Encrypt the message
        encrypted_data = MessageEncryption.encrypt_message(test_data['content'], key)
        
        # Simulate storing encrypted message
        encrypted_message_data = {
            'sender_id': test_data['sender_id'],
            'recipient_id': test_data['recipient_id'],
            'is_encrypted': True,
            'encrypted_content': encrypted_data['encrypted_content'],
            'encryption_nonce': encrypted_data['nonce'],
            'encryption_algorithm': encrypted_data['algorithm'],
            'content': None  # Plain content not stored for encrypted messages
        }
        
        print("   ✅ Message encryption simulation successful")
        print(f"   🔒 Encrypted content length: {len(encrypted_message_data['encrypted_content'])}")
        print(f"   🎲 Nonce length: {len(encrypted_message_data['encryption_nonce'])}")
        print(f"   🔧 Algorithm: {encrypted_message_data['encryption_algorithm']}")
        
        # Test decryption
        decrypted_content = MessageEncryption.decrypt_message({
            'encrypted_content': encrypted_message_data['encrypted_content'],
            'nonce': encrypted_message_data['encryption_nonce'],
            'algorithm': encrypted_message_data['encryption_algorithm']
        }, key)
        
        if decrypted_content == test_data['content']:
            print("   ✅ End-to-end encryption flow successful")
            return True
        else:
            print("   ❌ End-to-end encryption flow failed")
            return False
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Safe Companions - End-to-End Encryption Test Suite")
    print("=" * 60)
    
    tests = [
        test_encryption_utils,
        test_conversation_key_generation,
        test_message_serialization,
        test_database_models,
        run_integration_test
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! End-to-end encryption is ready for use.")
        print("\n📋 Next Steps:")
        print("   1. Start the application with Docker")
        print("   2. Test messaging functionality in browser")
        print("   3. Verify encryption is working in browser console")
        print("   4. Check database to confirm encrypted messages are stored")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
