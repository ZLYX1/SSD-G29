#!/usr/bin/env python3
"""
Test registration flow to check OTP terminal output
"""
import requests
import time

def test_registration():
    """Test the registration endpoint"""
    print("🧪 Testing Registration Flow")
    print("=" * 50)
    
    # Registration data
    registration_data = {
        'form_type': 'register',
        'email': 'test_otp_debug2@example.com',  # New email
        'password': 'TestPassword123!',
        'age': '25',
        'phone_number': '5551234568',  # Different phone
        'gender': 'Male',
        'role': 'User',
        'preference': 'Female',
        'g-recaptcha-response': 'test_token'  # Development bypass
    }
    
    try:
        print("Sending registration request...")
        response = requests.post('http://127.0.0.1:5000/auth', data=registration_data)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ Registration request successful")
            if "verify" in response.url:
                print("✅ Redirected to phone verification page")
            else:
                print("❓ Unexpected redirect")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing registration: {e}")

if __name__ == '__main__':
    test_registration()
