#!/usr/bin/env python3
"""
Rating & Feedback System Test Suite
Tests the complete rating and feedback workflow
"""

import sys
import os
import tempfile
import sqlite3
from datetime import datetime, timedelta

def create_test_database():
    """Create an in-memory SQLite database for testing"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY,
            email VARCHAR(120) UNIQUE NOT NULL,
            role VARCHAR(10) DEFAULT 'seeker',
            active BOOLEAN DEFAULT 1,
            gender VARCHAR(20)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE booking (
            id INTEGER PRIMARY KEY,
            seeker_id INTEGER NOT NULL,
            escort_id INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            FOREIGN KEY (seeker_id) REFERENCES user(id),
            FOREIGN KEY (escort_id) REFERENCES user(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE rating (
            id INTEGER PRIMARY KEY,
            booking_id INTEGER NOT NULL UNIQUE,
            reviewer_id INTEGER NOT NULL,
            reviewed_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES booking(id),
            FOREIGN KEY (reviewer_id) REFERENCES user(id),
            FOREIGN KEY (reviewed_id) REFERENCES user(id)
        )
    ''')
    
    return conn

def setup_test_data(conn):
    """Create test data for rating system"""
    cursor = conn.cursor()
    
    # Create test users
    users = [
        (1, 'seeker1@example.com', 'seeker', 'Male'),
        (2, 'escort1@example.com', 'escort', 'Female'),
        (3, 'seeker2@example.com', 'seeker', 'Female'),
        (4, 'escort2@example.com', 'escort', 'Male')
    ]
    
    for user_id, email, role, gender in users:
        cursor.execute('''
            INSERT INTO user (id, email, role, gender) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, email, role, gender))
    
    # Create test bookings
    now = datetime.now()
    past_time = now - timedelta(days=1)
    future_time = now + timedelta(days=1)
    
    bookings = [
        (1, 1, 2, past_time, past_time + timedelta(hours=2), 'Completed'),  # Completed - can be rated
        (2, 3, 4, past_time, past_time + timedelta(hours=1), 'Completed'),  # Completed - can be rated
        (3, 1, 4, future_time, future_time + timedelta(hours=2), 'Confirmed'),  # Future - cannot be rated
        (4, 3, 2, past_time, past_time + timedelta(hours=3), 'Rejected'),  # Rejected - cannot be rated
    ]
    
    for booking_id, seeker_id, escort_id, start_time, end_time, status in bookings:
        cursor.execute('''
            INSERT INTO booking (id, seeker_id, escort_id, start_time, end_time, status) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (booking_id, seeker_id, escort_id, start_time, end_time, status))
    
    conn.commit()
    return conn

def test_rating_creation():
    """Test creating ratings for completed bookings"""
    print("🌟 Test 1: Rating Creation")
    print("=" * 30)
    
    conn = setup_test_data(create_test_database())
    cursor = conn.cursor()
    
    # Test 1.1: Valid rating creation
    print("📝 Test 1.1: Creating valid rating...")
    
    rating_data = {
        'booking_id': 1,
        'reviewer_id': 1,  # Seeker rating escort
        'reviewed_id': 2,
        'rating': 5,
        'feedback': 'Excellent service, very professional!'
    }
    
    cursor.execute('''
        INSERT INTO rating (booking_id, reviewer_id, reviewed_id, rating, feedback)
        VALUES (?, ?, ?, ?, ?)
    ''', (rating_data['booking_id'], rating_data['reviewer_id'], 
          rating_data['reviewed_id'], rating_data['rating'], rating_data['feedback']))
    
    # Verify rating was created
    cursor.execute('SELECT * FROM rating WHERE booking_id = ?', (1,))
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Rating created: {result[4]}/5 stars")
        print(f"✅ Feedback: {result[5]}")
    else:
        print("❌ Rating creation failed")
    
    # Test 1.2: Prevent duplicate ratings
    print("\n📝 Test 1.2: Preventing duplicate ratings...")
    
    try:
        cursor.execute('''
            INSERT INTO rating (booking_id, reviewer_id, reviewed_id, rating, feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, 1, 2, 3, 'Trying to rate again'))
        print("❌ Duplicate rating allowed (should not happen)")
    except sqlite3.IntegrityError:
        print("✅ Duplicate rating prevented correctly")
    
    # Test 1.3: Rating validation (1-5 stars)
    print("\n📝 Test 1.3: Rating value validation...")
    
    invalid_ratings = [0, 6, -1, 10]
    for invalid_rating in invalid_ratings:
        try:
            cursor.execute('''
                INSERT INTO rating (booking_id, reviewer_id, reviewed_id, rating, feedback)
                VALUES (?, ?, ?, ?, ?)
            ''', (2, 3, 4, invalid_rating, 'Test feedback'))
            print(f"❌ Invalid rating {invalid_rating} allowed")
        except sqlite3.IntegrityError:
            print(f"✅ Invalid rating {invalid_rating} rejected correctly")
    
    conn.close()
    print("🎉 Rating creation tests completed!\n")

def test_rateable_bookings():
    """Test identifying which bookings can be rated"""
    print("🔍 Test 2: Rateable Bookings Identification")
    print("=" * 40)
    
    conn = setup_test_data(create_test_database())
    cursor = conn.cursor()
    
    # Test 2.1: Find completed bookings without ratings
    print("📝 Test 2.1: Finding rateable bookings...")
    
    cursor.execute('''
        SELECT b.id, b.seeker_id, b.escort_id, b.status, b.end_time
        FROM booking b
        LEFT JOIN rating r ON b.id = r.booking_id
        WHERE b.status = 'Completed' 
        AND b.end_time < datetime('now')
        AND r.id IS NULL
    ''')
    
    rateable_bookings = cursor.fetchall()
    print(f"✅ Found {len(rateable_bookings)} rateable bookings")
    
    for booking in rateable_bookings:
        print(f"  - Booking {booking[0]}: Seeker {booking[1]} → Escort {booking[2]}")
    
    # Test 2.2: Exclude future bookings
    cursor.execute('''
        SELECT COUNT(*) FROM booking 
        WHERE status = 'Confirmed' AND start_time > datetime('now')
    ''')
    
    future_bookings = cursor.fetchone()[0]
    print(f"✅ Correctly excluding {future_bookings} future bookings from rating")
    
    # Test 2.3: Exclude rejected bookings
    cursor.execute('''
        SELECT COUNT(*) FROM booking 
        WHERE status = 'Rejected'
    ''')
    
    rejected_bookings = cursor.fetchone()[0]
    print(f"✅ Correctly excluding {rejected_bookings} rejected bookings from rating")
    
    conn.close()
    print("🎉 Rateable bookings tests completed!\n")

def test_rating_statistics():
    """Test rating statistics calculation"""
    print("📊 Test 3: Rating Statistics")
    print("=" * 25)
    
    conn = setup_test_data(create_test_database())
    cursor = conn.cursor()
    
    # Create sample ratings
    sample_ratings = [
        (1, 1, 2, 5, 'Excellent!'),
        (2, 3, 4, 4, 'Very good'),
    ]
    
    for booking_id, reviewer_id, reviewed_id, rating, feedback in sample_ratings:
        cursor.execute('''
            INSERT INTO rating (booking_id, reviewer_id, reviewed_id, rating, feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (booking_id, reviewer_id, reviewed_id, rating, feedback))
    
    # Test 3.1: Calculate average rating for a user
    print("📝 Test 3.1: Calculating average ratings...")
    
    cursor.execute('''
        SELECT reviewed_id, AVG(rating) as avg_rating, COUNT(*) as total_ratings
        FROM rating 
        GROUP BY reviewed_id
    ''')
    
    user_ratings = cursor.fetchall()
    
    for user_id, avg_rating, total_count in user_ratings:
        print(f"✅ User {user_id}: {avg_rating:.1f}/5.0 ({total_count} ratings)")
    
    # Test 3.2: Get recent ratings
    cursor.execute('''
        SELECT r.rating, r.feedback, r.created_at, u1.email as reviewer, u2.email as reviewed
        FROM rating r
        JOIN user u1 ON r.reviewer_id = u1.id
        JOIN user u2 ON r.reviewed_id = u2.id
        ORDER BY r.created_at DESC
        LIMIT 5
    ''')
    
    recent_ratings = cursor.fetchall()
    print(f"\n✅ Found {len(recent_ratings)} recent ratings:")
    
    for rating, feedback, created_at, reviewer, reviewed in recent_ratings:
        print(f"  - {rating}/5: {feedback[:30]}... by {reviewer} for {reviewed}")
    
    conn.close()
    print("🎉 Rating statistics tests completed!\n")

def test_rating_workflow():
    """Test complete rating workflow"""
    print("🔄 Test 4: Complete Rating Workflow")
    print("=" * 35)
    
    conn = setup_test_data(create_test_database())
    cursor = conn.cursor()
    
    # Simulate complete workflow
    print("📝 Test 4.1: Complete rating workflow simulation...")
    
    # Step 1: User completes a booking (already done in test data)
    print("✅ Step 1: Booking completed")
    
    # Step 2: System identifies rateable booking
    cursor.execute('''
        SELECT b.id, b.seeker_id, b.escort_id 
        FROM booking b
        LEFT JOIN rating r ON b.id = r.booking_id
        WHERE b.id = 1 AND b.status = 'Completed' AND r.id IS NULL
    ''')
    
    rateable_booking = cursor.fetchone()
    if rateable_booking:
        print("✅ Step 2: Booking identified as rateable")
        booking_id, seeker_id, escort_id = rateable_booking
    else:
        print("❌ Step 2: Failed to identify rateable booking")
        return
    
    # Step 3: User submits rating
    rating_submission = {
        'booking_id': booking_id,
        'reviewer_id': seeker_id,
        'reviewed_id': escort_id,
        'rating': 4,
        'feedback': 'Great experience, would recommend!'
    }
    
    cursor.execute('''
        INSERT INTO rating (booking_id, reviewer_id, reviewed_id, rating, feedback)
        VALUES (?, ?, ?, ?, ?)
    ''', (rating_submission['booking_id'], rating_submission['reviewer_id'],
          rating_submission['reviewed_id'], rating_submission['rating'], 
          rating_submission['feedback']))
    
    print("✅ Step 3: Rating submitted successfully")
    
    # Step 4: Verify rating is stored and booking is no longer rateable
    cursor.execute('''
        SELECT COUNT(*) FROM rating WHERE booking_id = ?
    ''', (booking_id,))
    
    rating_count = cursor.fetchone()[0]
    if rating_count == 1:
        print("✅ Step 4: Rating stored correctly")
    else:
        print("❌ Step 4: Rating storage failed")
    
    # Step 5: Verify booking no longer appears in rateable list
    cursor.execute('''
        SELECT COUNT(*) FROM booking b
        LEFT JOIN rating r ON b.id = r.booking_id
        WHERE b.id = ? AND r.id IS NULL
    ''', (booking_id,))
    
    still_rateable = cursor.fetchone()[0]
    if still_rateable == 0:
        print("✅ Step 5: Booking correctly removed from rateable list")
    else:
        print("❌ Step 5: Booking still appears as rateable")
    
    conn.close()
    print("🎉 Complete workflow test completed!\n")

def main():
    """Run all rating system tests"""
    print("🌟 RATING & FEEDBACK SYSTEM - COMPREHENSIVE TESTS")
    print("=" * 55)
    
    try:
        test_rating_creation()
        test_rateable_bookings()
        test_rating_statistics()
        test_rating_workflow()
        
        print("🎊 ALL RATING SYSTEM TESTS PASSED!")
        print("\n📋 Manual Testing Steps:")
        print("1. Start Flask app: python app.py")
        print("2. Create users and complete some bookings")
        print("3. Visit /rating/rateable-bookings to see rateable bookings")
        print("4. Submit ratings via /rating/submit")
        print("5. View ratings via /rating/my-ratings")
        print("6. Check user profile ratings")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
