#!/usr/bin/env python3
"""
Check the OTP for the newly registered user
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

# Initialize the database with the app
db.init_app(app)

def check_latest_user_otp():
    """Check OTP for the latest registered user"""
    print("🔍 Checking Latest User OTP")
    print("=" * 50)
    
    with app.app_context():
        # Check for user with specific phone number
        phone_user = User.query.filter_by(phone_number="+11234567890").first()
        
        if phone_user:
            print(f"Phone User (+11234567890): {phone_user.email}")
            print(f"Phone: {phone_user.phone_number}")
            print(f"Phone Verified: {phone_user.phone_verified}")
            print(f"OTP Code: {phone_user.otp_code}")
            print(f"OTP Expires: {phone_user.otp_expires}")
            print(f"OTP Attempts: {phone_user.otp_attempts}")
            
            if phone_user.otp_code:
                print(f"\n✅ OTP '{phone_user.otp_code}' is ready for verification!")
            else:
                print("\n❌ No OTP found for phone +11234567890")
        else:
            print("❌ No user found with phone +11234567890")
        
        print("\n" + "="*30)
        
        # Check for our test user
        test_user = User.query.filter_by(email="test_otp_debug2@example.com").first()
        
        if test_user:
            print(f"Test User: {test_user.email}")
            print(f"Phone: {test_user.phone_number}")
            print(f"Phone Verified: {test_user.phone_verified}")
            print(f"OTP Code: {test_user.otp_code}")
            print(f"OTP Expires: {test_user.otp_expires}")
            print(f"OTP Attempts: {test_user.otp_attempts}")
            
            if test_user.otp_code:
                print(f"\n✅ OTP '{test_user.otp_code}' is ready for verification!")
            else:
                print("\n❌ No OTP found for test user")
        else:
            print("❌ Test user not found")
            
        # Also check all users with phone numbers and OTPs
        print("\n📋 All users with phone numbers:")
        users_with_phones = User.query.filter(User.phone_number.isnot(None)).all()
        for user in users_with_phones:
            print(f"  - {user.email} | Phone: {user.phone_number} | OTP: {user.otp_code} | Verified: {user.phone_verified}")

if __name__ == '__main__':
    check_latest_user_otp()
