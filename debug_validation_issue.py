#!/usr/bin/env python3
"""
Quick test to send a message and see the exact validation issue
"""

import requests
import json

# Test data that matches what the frontend sends
test_data = {
    "recipient_id": 18,
    "encrypted_data": {
        "encrypted_content": "ChbI745DoqKLqZR/zrMXA7gaFoeXYg==",
        "nonce": "Ajkqv6G4Ss+ORw+B",
        "algorithm": "AES-GCM-128"
    }
}

print("=== Testing message sending with encrypted data ===")
print(f"Sending data: {json.dumps(test_data, indent=2)}")

# Send the request to the messaging endpoint
try:
    response = requests.post(
        'http://localhost:8080/messaging/send',
        json=test_data,
        headers={
            'Content-Type': 'application/json',
            'Cookie': 'session=.eJwlzj0OQjEMQOG7eO4SP_-EdxOl6dAoHYo4PQVWb973JZ94xgse8YInvOFnx0_u8Q9Hs36lq63z2uZtj9m9aTVX2mItISLBcGKEhBADbr0hChA0ykGxoL1DEwMEEmJGJBAx5AhVZGTXfaXJVne_V3PtLdtQ-u1btqH027dsQ-m3b8-5b9Qhd--J6PcCi5w29w.Z6IUjg.KH5OiR_eHuNwUwLbcOhE8lUJzI4'  # From the working session
        }
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        if not result.get('success'):
            print(f"Error: {result.get('error')}")
    
except Exception as e:
    print(f"Error making request: {e}")

print("\n=== Checking if encrypted_data evaluates correctly ===")
encrypted_data = {
    "encrypted_content": "ChbI745DoqKLqZR/zrMXA7gaFoeXYg==",
    "nonce": "Ajkqv6G4Ss+ORw+B",
    "algorithm": "AES-GCM-128"
}

print(f"encrypted_data: {encrypted_data}")
print(f"bool(encrypted_data): {bool(encrypted_data)}")
print(f"not encrypted_data: {not encrypted_data}")
print(f"type(encrypted_data): {type(encrypted_data)}")

# Test various edge cases
empty_dict = {}
print(f"bool(empty_dict): {bool(empty_dict)}")
print(f"not empty_dict: {not empty_dict}")

none_value = None
print(f"bool(none_value): {bool(none_value)}")
print(f"not none_value: {not none_value}")
