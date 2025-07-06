#!/usr/bin/env python3
"""
Create test user with proper password hash for manual testing
"""
import os
import sys
from werkzeug.security import generate_password_hash
import psycopg2
import datetime

# Database connection
try:
    conn = psycopg2.connect(
        host='db',
        port=5432,
        database='ssd_database',
        user='ssd_user',
        password='ssd_password'
    )
    cursor = conn.cursor()
    print("✅ Connected to database")
    
    # Create test user with proper password hash
    password_hash = generate_password_hash('password123')
    print(f"✅ Generated password hash: {password_hash[:50]}...")
    
    # Insert test user
    cursor.execute("""
        INSERT INTO "user" (
            email, 
            password_hash, 
            role, 
            active,
            activate,
            deleted,
            gender, 
            email_verified, 
            phone_verified,
            otp_attempts,
            password_created_at,
            password_change_required,
            failed_login_attempts
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE SET
            password_hash = EXCLUDED.password_hash,
            email_verified = EXCLUDED.email_verified,
            phone_verified = EXCLUDED.phone_verified,
            otp_attempts = EXCLUDED.otp_attempts,
            password_created_at = EXCLUDED.password_created_at,
            password_change_required = EXCLUDED.password_change_required,
            failed_login_attempts = EXCLUDED.failed_login_attempts
        RETURNING id, email
    """, (
        'testuser2@example.com',
        password_hash,
        'escort',
        True,
        True,
        False,
        'Male',
        True,          # email_verified
        True,         # phone_verified
        0,             # otp_attempts
        datetime.datetime.now(), # password_created_at
        False,         # password_change_required
        0              # failed_login_attempts
    ))
    
    user_id, email = cursor.fetchone()
    print(f"✅ Created/updated user: ID={user_id}, Email={email}")
    
    # Create profile for the user
    cursor.execute("""
        INSERT INTO profile (user_id, name, age, bio, preference)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
        name = EXCLUDED.name,
        age = EXCLUDED.age,
        bio = EXCLUDED.bio,
        preference = EXCLUDED.preference
    """, (user_id, 'Test User', 25, 'Test user for rating system demo', 'Professional'))
    
    print(f"✅ Created/updated profile for user {user_id}")
    
    # Commit changes
    conn.commit()
    
    print(f"""
🎉 Test user created successfully!
📧 Email: testuser@example.com
🔑 Password: password123
👤 Role: seeker
🆔 User ID: {user_id}
""")
    
    # Check for rateable bookings for this user
    cursor.execute("""
        SELECT b.id, u_escort.email as escort_email, b.start_time, b.end_time, b.status
        FROM booking b
        JOIN "user" u_escort ON b.escort_id = u_escort.id
        WHERE b.seeker_id = %s AND b.status = 'Completed'
        AND b.id NOT IN (SELECT booking_id FROM rating)
        ORDER BY b.start_time DESC
    """, (user_id,))
    
    rateable_bookings = cursor.fetchall()
    if rateable_bookings:
        print(f"📝 Found {len(rateable_bookings)} rateable bookings for this user:")
        for booking in rateable_bookings:
            print(f"  - Booking {booking[0]} with {booking[1]} on {booking[2]}")
    else:
        print("📝 No rateable bookings found for this user")
        
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
