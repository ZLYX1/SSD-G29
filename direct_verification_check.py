#!/usr/bin/env python3
"""
Direct Email Verification Helper
This script connects directly to the database and helps with email verification
"""

import psycopg2
from datetime import datetime, timedelta
import secrets

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ssd_database',
    'user': 'ssd_user',
    'password': 'ssd_password'
}

def check_user_verification(email):
    """Check user verification status and provide verification link"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query for the user
        cursor.execute("""
            SELECT id, email, email_verified, email_verification_token, 
                   email_verification_token_expires, created_at
            FROM "user" 
            WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        
        if user:
            user_id, email, email_verified, token, token_expires, created_at = user
            
            print(f"✅ USER FOUND: {email}")
            print(f"📧 Email Verified: {'✅ YES' if email_verified else '❌ NO'}")
            print(f"🆔 User ID: {user_id}")
            print(f"📅 Created: {created_at}")
            
            if not email_verified:
                if token:
                    print(f"🔑 Current Token: {token[:20]}...")
                    if token_expires:
                        print(f"⏰ Token Expires: {token_expires}")
                        
                        # Check if token is still valid
                        if datetime.now() < token_expires.replace(tzinfo=None):
                            verification_url = f"http://localhost:5000/auth/verify-email/{token}"
                            print(f"\n🔗 VERIFICATION LINK (COPY & PASTE IN BROWSER):")
                            print(f"   {verification_url}")
                            print(f"\n📋 INSTRUCTIONS:")
                            print(f"   1. Copy the link above")
                            print(f"   2. Paste it in your browser")
                            print(f"   3. Your email will be verified!")
                        else:
                            print(f"\n⚠️  TOKEN EXPIRED - Generating new one...")
                            # Generate new token
                            new_token = secrets.token_urlsafe(32)
                            new_expires = datetime.now() + timedelta(hours=24)
                            
                            cursor.execute("""
                                UPDATE "user" 
                                SET email_verification_token = %s,
                                    email_verification_token_expires = %s
                                WHERE id = %s
                            """, (new_token, new_expires, user_id))
                            conn.commit()
                            
                            verification_url = f"http://localhost:5000/auth/verify-email/{new_token}"
                            print(f"🔗 NEW VERIFICATION LINK:")
                            print(f"   {verification_url}")
                    else:
                        print(f"⚠️  Token has no expiration set")
                else:
                    print(f"⚠️  No verification token found - Generating new one...")
                    # Generate new token
                    new_token = secrets.token_urlsafe(32)
                    new_expires = datetime.now() + timedelta(hours=24)
                    
                    cursor.execute("""
                        UPDATE "user" 
                        SET email_verification_token = %s,
                            email_verification_token_expires = %s
                        WHERE id = %s
                    """, (new_token, new_expires, user_id))
                    conn.commit()
                    
                    verification_url = f"http://localhost:5000/auth/verify-email/{new_token}"
                    print(f"🔗 VERIFICATION LINK:")
                    print(f"   {verification_url}")
            else:
                print(f"✅ Email is already verified! You can log in normally.")
                
        else:
            print(f"❌ USER NOT FOUND: {email}")
            print(f"\n🔍 Searching for similar emails...")
            
            # Search for similar emails
            cursor.execute("""
                SELECT email, email_verified 
                FROM "user" 
                WHERE email ILIKE %s
                ORDER BY email
            """, (f'%{email.split("@")[0]}%',))
            
            similar_users = cursor.fetchall()
            if similar_users:
                print(f"📋 Found similar emails:")
                for user_email, verified in similar_users:
                    status = "✅ Verified" if verified else "❌ Unverified"
                    print(f"   - {user_email} ({status})")
            else:
                print(f"📋 No similar emails found")
                
                # Show all users
                cursor.execute("SELECT email, email_verified FROM \"user\" ORDER BY email")
                all_users = cursor.fetchall()
                if all_users:
                    print(f"\n📋 All users in database:")
                    for user_email, verified in all_users:
                        status = "✅ Verified" if verified else "❌ Unverified"
                        print(f"   - {user_email} ({status})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        print(f"Make sure PostgreSQL is running and accessible")

if __name__ == "__main__":
    print("🔍 EMAIL VERIFICATION CHECKER")
    print("=" * 50)
    
    target_email = "test_email@example.com"
    check_user_verification(target_email)
    
    print("\n" + "=" * 50)
    print("🔧 Direct database check completed")
