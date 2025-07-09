#!/usr/bin/env python3

import requests
import json
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64

# Base URL for API
BASE_URL = "http://localhost:5000"

def generate_key(password: str, salt: bytes) -> bytes:
    """Generate encryption key from password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

def encrypt_message(content: str, password: str) -> dict:
    """Encrypt message content using AES-GCM"""
    # Generate salt and derive key
    salt = os.urandom(16)
    key = generate_key(password, salt)
    
    # Generate nonce and encrypt
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, content.encode(), None)
    
    return {
        'encrypted_data': base64.b64encode(ciphertext).decode(),
        'salt': base64.b64encode(salt).decode(),
        'nonce': base64.b64encode(nonce).decode(),
        'algorithm': 'AES-GCM-128'
    }

def test_login_and_messaging():
    """Test login and send multiple encrypted messages"""
    
    # Create session
    session = requests.Session()
    
    print("=== Testing Login and Consecutive Encrypted Messages ===\n")
    
    # 1. Login
    print("1. Logging in...")
    login_data = {
        'email': 'seeker1@example.com',
        'password': 'password123'
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("Login failed!")
        print(f"Response: {login_response.text[:500]}")
        return
    
    print("Login successful!\n")
    
    # 2. Get messaging page to ensure proper session
    print("2. Getting messaging page...")
    messaging_response = session.get(f"{BASE_URL}/messaging")
    print(f"Messaging page status: {messaging_response.status_code}")
    
    if messaging_response.status_code != 200:
        print("Failed to access messaging page!")
        return
    
    print("Messaging page accessible!\n")
    
    # 3. Send multiple encrypted messages
    messages = [
        "First encrypted test message",
        "Second encrypted test message", 
        "Third encrypted test message",
        "Fourth encrypted test message"
    ]
    
    encryption_password = "test-encryption-password-123"
    
    for i, content in enumerate(messages, 1):
        print(f"3.{i} Sending encrypted message {i}...")
        
        # Encrypt the message
        encrypted_data = encrypt_message(content, encryption_password)
        
        # Prepare payload
        payload = {
            'recipient_id': 18,  # Match the frontend test
            'encrypted_data': encrypted_data
        }
        
        print(f"   Payload keys: {list(payload.keys())}")
        print(f"   Is encrypted: {payload['is_encrypted']}")
        print(f"   Algorithm: {payload['algorithm']}")
        print(f"   Has encrypted_data: {bool(payload['encrypted_data'])}")
        print(f"   Has salt: {bool(payload['salt'])}")
        print(f"   Has nonce: {bool(payload['nonce'])}")
        
        # Send message
        send_response = session.post(f"{BASE_URL}/messaging/send", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'})
        
        print(f"   Response status: {send_response.status_code}")
        
        if send_response.status_code == 200:
            try:
                response_json = send_response.json()
                print(f"   Response: {response_json}")
            except:
                print(f"   Response (text): {send_response.text[:200]}")
        else:
            print(f"   Error response: {send_response.text[:200]}")
        
        print(f"   Message {i} completed.\n")
        
        # Wait between messages
        time.sleep(1)
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_login_and_messaging()
