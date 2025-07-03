#!/usr/bin/env python3
"""
Create test bookings for the test user so we can demonstrate rating
"""
import psycopg2
from datetime import datetime, timedelta

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='ssd_database',
        user='ssd_user',
        password='ssd_password'
    )
    cursor = conn.cursor()
    print("✅ Connected to database")
    
    # Get our test user ID
    cursor.execute("SELECT id FROM \"user\" WHERE email = 'testuser@example.com'")
    test_user_id = cursor.fetchone()[0]
    print(f"✅ Test user ID: {test_user_id}")
    
    # Get escort users we can book
    cursor.execute("SELECT id, email FROM \"user\" WHERE role = 'escort' AND id >= 101 LIMIT 3")
    escorts = cursor.fetchall()
    print(f"✅ Found {len(escorts)} escort users")
    
    # Create completed bookings
    bookings = []
    for i, (escort_id, escort_email) in enumerate(escorts):
        start_time = datetime.now() - timedelta(days=i+1)
        end_time = start_time + timedelta(hours=2)
        
        cursor.execute("""
            INSERT INTO booking (seeker_id, escort_id, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (test_user_id, escort_id, start_time, end_time, 'Completed'))
        
        booking_id = cursor.fetchone()[0]
        bookings.append((booking_id, escort_email, start_time))
        print(f"✅ Created booking {booking_id} with {escort_email}")
    
    # Create one future booking (should not be rateable)
    if escorts:
        future_start = datetime.now() + timedelta(days=1)
        future_end = future_start + timedelta(hours=2)
        cursor.execute("""
            INSERT INTO booking (seeker_id, escort_id, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (test_user_id, escorts[0][0], future_start, future_end, 'Accepted'))
        
        future_booking_id = cursor.fetchone()[0]
        print(f"✅ Created future booking {future_booking_id} (not rateable)")
    
    conn.commit()
    
    print(f"""
🎉 Test bookings created successfully!
📝 Login Details:
   Email: testuser@example.com
   Password: password123

📋 Test Plan:
1. Visit: http://localhost:5000/auth?mode=login
2. Login with the credentials above
3. Visit: http://localhost:5000/rating/rateable-bookings
4. You should see {len(bookings)} completed bookings ready to rate
5. Submit ratings and view the results

🌟 Rateable Bookings Created:
""")
    
    for booking_id, escort_email, start_time in bookings:
        print(f"   - Booking {booking_id} with {escort_email} on {start_time.strftime('%Y-%m-%d %H:%M')}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
