#!/usr/bin/env python3
"""Test script to simulate frontend message sending and debug the backend directly"""

import requests
import json
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def encrypt_message(message, password="test_password"):
    """Encrypt a message using AES-GCM-128"""
    # Derive key from password
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=16,  # 128 bits for AES-128
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(password.encode())
    
    # Generate nonce
    nonce = os.urandom(12)  # 96 bits for GCM
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
    
    return {
        'encrypted_content': base64.b64encode(ciphertext + encryptor.tag).decode(),
        'nonce': base64.b64encode(nonce).decode(),
        'algorithm': 'AES-GCM-128'
    }

def test_message_sending():
    """Test sending an encrypted message to the backend"""
    
    # First, let's try to login
    login_url = "http://localhost:5000/auth/login"
    messaging_url = "http://localhost:5000/messaging/send"
    
    session = requests.Session()
    
    # Try to get a session first by visiting the main page
    try:
        response = session.get("http://localhost:5000/")
        print(f"Main page status: {response.status_code}")
        
        # Try to access messaging directly to get cookies and CSRF token
        response = session.get("http://localhost:5000/messaging")
        print(f"Messaging page status: {response.status_code}")
        
        # Extract CSRF token from the page
        csrf_token = None
        if response.status_code == 200:
            # Look for CSRF token in response
            response_text = response.text
            import re
            csrf_match = re.search(r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']', response_text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"Found CSRF token: {csrf_token[:20]}...")
            else:
                # Try to find it in meta tag
                meta_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response_text)
                if meta_match:
                    csrf_token = meta_match.group(1)
                    print(f"Found CSRF token in meta: {csrf_token[:20]}...")
        
        # Get cookies from response
        print(f"Session cookies: {session.cookies}")
        
        # Now try to send a message
        message_text = "Hello, this is a test encrypted message!"
        encrypted_data = encrypt_message(message_text)
        
        payload = {
            'recipient_id': 18,  # Using known user ID
            'encrypted_data': encrypted_data
        }
        
        print(f"Sending payload: {json.dumps(payload, indent=2)}")
        
        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Add CSRF token if found
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token
            print(f"Added CSRF token to headers")
        
        # Send the message
        response = session.post(
            messaging_url,
            json=payload,
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                print("Could not parse response as JSON")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_message_sending()
