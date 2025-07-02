#!/usr/bin/env python3
"""
Debug script to test OTP functionality
"""
import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-development-secret-key')

# Import after Flask app creation
from extensions import db
from blueprint.models import User
from utils.utils import generate_otp, send_otp_sms, validate_phone_number

# Initialize the database with the app
db.init_app(app)

def test_otp_functions():
    """Test OTP generation and sending functions"""
    print("🔧 Testing OTP Functions")
    print("=" * 50)
    
    with app.app_context():
        # Test OTP generation
        print("1. Testing OTP generation...")
        otp = generate_otp()
        print(f"   Generated OTP: {otp}")
        print(f"   OTP Length: {len(otp)}")
        print(f"   OTP Type: {type(otp)}")
        
        # Test phone validation
        print("\n2. Testing phone validation...")
        test_phones = [
            "+1234567890",
            "1234567890", 
            "12345678901",
            "+12345678901"
        ]
        
        for phone in test_phones:
            is_valid, result = validate_phone_number(phone)
            print(f"   Phone: {phone} -> Valid: {is_valid}, Result: {result}")
        
        # Test with existing user
        print("\n3. Testing with existing user...")
        user = User.query.filter_by(email="test_phone@example.com").first()
        if user:
            print(f"   Found user: {user.email}")
            print(f"   Phone: {user.phone_number}")
            print(f"   Phone verified: {user.phone_verified}")
            
            # Test OTP sending
            print("\n4. Testing OTP sending...")
            test_otp = generate_otp()
            print(f"   About to send OTP: {test_otp}")
            
            result = send_otp_sms(user, test_otp)
            print(f"   Send result: {result}")
            
            # Check user OTP fields after sending
            db.session.refresh(user)
            print(f"   User OTP code in DB: {user.otp_code}")
            print(f"   User OTP expires: {user.otp_expires}")
            print(f"   User OTP attempts: {user.otp_attempts}")
        else:
            print("   User 'test_phone@example.com' not found!")
            
            # List all users
            print("\n   Available users:")
            users = User.query.all()
            for u in users:
                print(f"   - {u.email} (phone: {u.phone_number})")

if __name__ == '__main__':
    test_otp_functions()
