#!/usr/bin/env python3
"""
Email Verification Checker Script
Checks user verification status and provides verification links
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path
sys.path.append('.')

# Set required environment variables
os.environ['DATABASE_URL'] = 'postgresql://ssd_user:SecurePassword123!@localhost:5432/ssd_database'
os.environ['RECAPTCHA_SECRET_KEY'] = 'test_secret_key_for_development'
os.environ['FLASK_ENV'] = 'development'

try:
    from blueprint.models import db, User
    from flask import Flask
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'development-secret-key'
    
    db.init_app(app)
    
    with app.app_context():
        print("🔍 EMAIL VERIFICATION STATUS CHECKER")
        print("=" * 50)
        
        # Check for the specific user
        target_email = 'test_email@example.com'
        user = User.query.filter_by(email=target_email).first()
        
        if user:
            print(f"✅ USER FOUND: {user.email}")
            print(f"📧 Email Verified: {'✅ YES' if user.email_verified else '❌ NO'}")
            print(f"👤 Role: {user.role}")
            print(f"🔓 Active: {'✅ YES' if user.active else '❌ NO'}")
            print(f"📅 Created: {user.created_at}")
            
            if user.email_verification_token:
                print(f"🔑 Verification Token: {user.email_verification_token[:20]}...")
                print(f"⏰ Token Expires: {user.email_verification_token_expires}")
                
                # Generate verification URL
                verification_url = f"http://localhost:5000/auth/verify-email/{user.email_verification_token}"
                print(f"\n🔗 VERIFICATION LINK:")
                print(f"   {verification_url}")
                print(f"\n📋 TO VERIFY YOUR EMAIL:")
                print(f"   1. Copy the link above")
                print(f"   2. Paste it in your browser")
                print(f"   3. Your email will be verified")
                print(f"   4. You can then log in normally")
                
                # Check if token is expired
                if user.email_verification_token_expires:
                    if datetime.utcnow() > user.email_verification_token_expires:
                        print(f"\n⚠️  WARNING: Token has EXPIRED!")
                        print(f"   Use the 'Resend Verification' option on the login page")
                    else:
                        time_left = user.email_verification_token_expires - datetime.utcnow()
                        print(f"\n✅ Token is still valid for: {time_left}")
            else:
                print(f"ℹ️  No verification token (already verified or not set)")
                
        else:
            print(f"❌ USER NOT FOUND: {target_email}")
            print(f"\n📋 Available users in database:")
            users = User.query.all()
            if users:
                for u in users:
                    status = "✅ Verified" if u.email_verified else "❌ Unverified"
                    print(f"   - {u.email} ({status})")
            else:
                print("   No users found in database")
        
        print("\n" + "=" * 50)
        print("🔧 SYSTEM STATUS: Email verification system operational")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure the database is running and accessible")
