#!/usr/bin/env python3
"""
Monitor OTP changes for the test user
"""
import os
import sys
from flask import Flask
from dotenv import load_dotenv
import time

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

def monitor_otp_changes():
    """Monitor OTP changes for the test user"""
    print("🔍 Monitoring OTP Changes")
    print("=" * 50)
    
    with app.app_context():
        test_user = User.query.filter_by(email="test_otp_debug2@example.com").first()
        
        if test_user:
            print(f"Monitoring user: {test_user.email}")
            print(f"Current OTP: {test_user.otp_code}")
            print(f"Current Expires: {test_user.otp_expires}")
            print("\n📱 Click 'Resend OTP' on the web page now...")
            print("Checking for changes every 2 seconds...")
            
            previous_otp = test_user.otp_code
            previous_expires = test_user.otp_expires
            
            for i in range(30):  # Check for 1 minute
                time.sleep(2)
                db.session.refresh(test_user)
                
                if test_user.otp_code != previous_otp or test_user.otp_expires != previous_expires:
                    print(f"\n🎉 OTP CHANGED!")
                    print(f"Previous OTP: {previous_otp}")
                    print(f"New OTP: {test_user.otp_code}")
                    print(f"Previous Expires: {previous_expires}")
                    print(f"New Expires: {test_user.otp_expires}")
                    print(f"Change detected at check #{i+1}")
                    break
                else:
                    print(f"Check #{i+1}: No change (OTP: {test_user.otp_code})")
                    
            print("\nMonitoring complete.")
        else:
            print("❌ Test user not found")

if __name__ == '__main__':
    monitor_otp_changes()
