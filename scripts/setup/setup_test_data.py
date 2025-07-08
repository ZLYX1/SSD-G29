#!/usr/bin/env python3
"""
Comprehensive Test Data Setup Script
This script creates test users with different roles and comprehensive test data
for all functionality in the Safe Companions application.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add the project root to the Python path
sys.path.append('/app')

from blueprint.models import (
    db, User, Profile, Booking, Payment, Report, Rating, 
    PasswordHistory, Message, Favourite, AuditLog, TimeSlot
)
from app import app

# Test data configurations
TEST_PASSWORD = "password123"
ADMIN_EMAIL = "admin@safecompanions.com"
ADMIN_PASSWORD = "password123"

# Test users data
TEST_USERS = [
    # Admin Users
    {
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD,
        'role': 'admin',
        'name': 'Super Admin',
        'gender': 'Non-binary',
        'age': 30,
        'bio': 'System administrator with full access to all features.',
        'phone': '+1234567890',
        'verified': True
    },
    {
        'email': 'admin2@safecompanions.com',
        'password': TEST_PASSWORD,
        'role': 'admin',
        'name': 'Admin Two',
        'gender': 'Female',
        'age': 35,
        'bio': 'Secondary admin for testing multi-admin scenarios.',
        'phone': '+1234567891',
        'verified': True
    },
    
    # Seeker Users
    {
        'email': 'seeker1@example.com',
        'password': TEST_PASSWORD,
        'role': 'seeker',
        'name': 'John Seeker',
        'gender': 'Male',
        'age': 28,
        'bio': 'Looking for companionship and meaningful connections.',
        'phone': '+1234567892',
        'verified': True,
        'preference': 'Women'
    },
    {
        'email': 'seeker2@example.com',
        'password': TEST_PASSWORD,
        'role': 'seeker',
        'name': 'Jane Seeker',
        'gender': 'Female',
        'age': 32,
        'bio': 'Seeking quality time with interesting people.',
        'phone': '+1234567893',
        'verified': True,
        'preference': 'Men'
    },
    {
        'email': 'seeker3@example.com',
        'password': TEST_PASSWORD,
        'role': 'seeker',
        'name': 'Alex Seeker',
        'gender': 'Non-binary',
        'age': 25,
        'bio': 'Open-minded seeker looking for diverse experiences.',
        'phone': '+1234567894',
        'verified': True,
        'preference': 'Both'
    },
    
    # Escort Users
    {
        'email': 'escort1@example.com',
        'password': TEST_PASSWORD,
        'role': 'escort',
        'name': 'Emma Companion',
        'gender': 'Female',
        'age': 26,
        'bio': 'Professional companion offering quality experiences.',
        'phone': '+1234567895',
        'verified': True,
        'preference': 'Men'
    },
    {
        'email': 'escort2@example.com',
        'password': TEST_PASSWORD,
        'role': 'escort',
        'name': 'David Companion',
        'gender': 'Male',
        'age': 29,
        'bio': 'Experienced companion specializing in elegant evenings.',
        'phone': '+1234567896',
        'verified': True,
        'preference': 'Women'
    },
    {
        'email': 'escort3@example.com',
        'password': TEST_PASSWORD,
        'role': 'escort',
        'name': 'Taylor Companion',
        'gender': 'Non-binary',
        'age': 31,
        'bio': 'Versatile companion with diverse interests.',
        'phone': '+1234567897',
        'verified': True,
        'preference': 'Both'
    },
    {
        'email': 'escort4@example.com',
        'password': TEST_PASSWORD,
        'role': 'escort',
        'name': 'Sophie Elite',
        'gender': 'Female',
        'age': 27,
        'bio': 'High-end companion for sophisticated clients.',
        'phone': '+1234567898',
        'verified': True,
        'preference': 'Men'
    },
    
    # Test users for specific scenarios
    {
        'email': 'unverified@example.com',
        'password': TEST_PASSWORD,
        'role': 'seeker',
        'name': 'Unverified User',
        'gender': 'Male',
        'age': 24,
        'bio': 'Test user for email verification flows.',
        'phone': '+1234567899',
        'verified': False
    },
    {
        'email': 'locked@example.com',
        'password': TEST_PASSWORD,
        'role': 'seeker',
        'name': 'Locked User',
        'gender': 'Female',
        'age': 26,
        'bio': 'Test user for account lockout scenarios.',
        'phone': '+1234567800',
        'verified': True,
        'locked': True
    },
    {
        'email': 'pending@example.com',
        'password': TEST_PASSWORD,
        'role': 'seeker',
        'name': 'Pending Role User',
        'gender': 'Male',
        'age': 30,
        'bio': 'Test user with pending role change.',
        'phone': '+1234567801',
        'verified': True,
        'pending_role': 'escort'
    }
]

def clear_existing_data():
    """Clear all existing test data from the database"""
    print("🗑️  Clearing existing test data...")
    
    try:
        # Delete in reverse order of dependencies
        AuditLog.query.delete()
        Favourite.query.delete()
        Rating.query.delete()
        Message.query.delete()
        Report.query.delete()
        Payment.query.delete()
        Booking.query.delete()
        TimeSlot.query.delete()
        PasswordHistory.query.delete()
        Profile.query.delete()
        User.query.delete()
        
        db.session.commit()
        print("   ✅ All existing test data cleared")
        
    except Exception as e:
        print(f"   ⚠️  Error clearing data: {e}")
        db.session.rollback()
        raise

def create_test_users():
    """Create test users with different roles and states"""
    print("1. Creating test users...")
    created_users = {}
    
    for user_data in TEST_USERS:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            print(f"   ✓ User {user_data['email']} already exists")
            created_users[user_data['email']] = existing_user
            continue
        
        # Create user
        user = User(
            email=user_data['email'],
            role=user_data['role'],
            gender=user_data['gender'],
            phone_number=user_data['phone'],
            email_verified=user_data['verified'],
            phone_verified=user_data['verified'],
            active=True,
            activate=True,
            deleted=False,
            created_at=datetime.utcnow(),
            password_created_at=datetime.utcnow(),
            failed_login_attempts=0,
            password_change_required=False
        )
        
        # Set password
        success, message = user.set_password(user_data['password'], check_history=False)
        if not success:
            print(f"   ⚠️  Failed to set password for {user_data['email']}: {message}")
            continue
        
        # Handle special cases
        if user_data.get('locked'):
            user.failed_login_attempts = 5
            user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        if user_data.get('pending_role'):
            user.pending_role = user_data['pending_role']
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create profile
        profile = Profile(
            user_id=user.id,
            name=user_data['name'],
            bio=user_data['bio'],
            age=user_data['age'],
            preference=user_data.get('preference'),
            availability='Available',
            photo='default.jpg',
            rating=0.0
        )
        db.session.add(profile)
        
        created_users[user_data['email']] = user
        print(f"   ✓ Created {user_data['role']} user: {user_data['email']}")
    
    db.session.commit()
    print(f"   ✅ Created {len(created_users)} test users")
    return created_users

def create_time_slots(users):
    """Create time slots for escort users"""
    print("2. Creating time slots for escorts...")
    
    escorts = [user for user in users.values() if user.role == 'escort']
    
    for escort in escorts:
        # Create time slots for the next 2 weeks
        start_date = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        
        for day in range(14):  # 2 weeks
            current_date = start_date + timedelta(days=day)
            
            # Create 3 time slots per day (morning, afternoon, evening)
            time_slots = [
                (current_date.replace(hour=10), current_date.replace(hour=12)),  # Morning
                (current_date.replace(hour=14), current_date.replace(hour=16)),  # Afternoon
                (current_date.replace(hour=19), current_date.replace(hour=21))   # Evening
            ]
            
            for start_time, end_time in time_slots:
                # Skip weekends for some variety
                if day % 7 in [5, 6] and random.random() < 0.5:
                    continue
                
                time_slot = TimeSlot(
                    user_id=escort.id,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(time_slot)
    
    db.session.commit()
    slot_count = TimeSlot.query.count()
    print(f"   ✅ Created {slot_count} time slots")

def create_bookings(users):
    """Create test bookings between seekers and escorts"""
    print("3. Creating test bookings...")
    
    seekers = [user for user in users.values() if user.role == 'seeker']
    escorts = [user for user in users.values() if user.role == 'escort']
    
    booking_statuses = ['Pending', 'Confirmed', 'Rejected']
    
    for i in range(20):  # Create 20 bookings
        seeker = random.choice(seekers)
        escort = random.choice(escorts)
        
        # Get available time slots for the escort
        available_slots = TimeSlot.query.filter_by(user_id=escort.id).all()
        if not available_slots:
            continue
        
        slot = random.choice(available_slots)
        
        # Check if booking already exists for this time slot
        existing_booking = Booking.query.filter_by(
            escort_id=escort.id,
            start_time=slot.start_time,
            end_time=slot.end_time
        ).first()
        
        if existing_booking:
            continue
        
        booking = Booking(
            seeker_id=seeker.id,
            escort_id=escort.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status=random.choice(booking_statuses)
        )
        db.session.add(booking)
    
    db.session.commit()
    booking_count = Booking.query.count()
    print(f"   ✅ Created {booking_count} bookings")

def create_payments(users):
    """Create test payment records"""
    print("4. Creating test payments...")
    
    users_list = list(users.values())
    
    for i in range(30):  # Create 30 payments
        user = random.choice(users_list)
        
        # Generate unique transaction ID
        transaction_id = f"TXN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{i:04d}_{random.randint(1000, 9999)}"
        
        payment = Payment(
            user_id=user.id,
            amount=round(random.uniform(50.0, 500.0), 2),
            status=random.choice(['Completed', 'Pending', 'Failed']),
            transaction_id=transaction_id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.session.add(payment)
    
    db.session.commit()
    payment_count = Payment.query.count()
    print(f"   ✅ Created {payment_count} payments")

def create_messages(users):
    """Create test messages between users"""
    print("5. Creating test messages...")
    
    users_list = list(users.values())
    
    for i in range(50):  # Create 50 messages
        sender = random.choice(users_list)
        recipient = random.choice(users_list)
        
        if sender.id == recipient.id:
            continue
        
        message = Message(
            sender_id=sender.id,
            recipient_id=recipient.id,
            content=f"This is test message #{i+1}. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            is_read=random.choice([True, False])
        )
        db.session.add(message)
    
    db.session.commit()
    message_count = Message.query.count()
    print(f"   ✅ Created {message_count} messages")

def create_ratings(users):
    """Create test ratings based on confirmed bookings"""
    print("6. Creating test ratings...")
    
    confirmed_bookings = Booking.query.filter_by(status='Confirmed').all()
    
    for booking in confirmed_bookings:
        # Skip if rating already exists
        existing_rating = Rating.query.filter_by(booking_id=booking.id).first()
        if existing_rating:
            continue
        
        # Create rating (50% chance)
        if random.random() < 0.5:
            rating = Rating(
                booking_id=booking.id,
                reviewer_id=booking.seeker_id,
                reviewed_id=booking.escort_id,
                rating=random.randint(3, 5),  # Mostly positive ratings
                feedback=random.choice([
                    "Great experience, highly recommended!",
                    "Professional and courteous service.",
                    "Excellent companion, will book again.",
                    "Very pleasant evening, thank you!",
                    "Good service, met expectations."
                ]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(rating)
    
    db.session.commit()
    rating_count = Rating.query.count()
    print(f"   ✅ Created {rating_count} ratings")

def create_reports(users):
    """Create test reports"""
    print("7. Creating test reports...")
    
    users_list = list(users.values())
    admin_users = [user for user in users.values() if user.role == 'admin']
    
    report_types = [
        'inappropriate_behavior',
        'harassment',
        'fraud',
        'fake_profile',
        'violence_threats',
        'spam',
        'underage',
        'identity_theft',
        'privacy_violation',
        'other'
    ]
    
    for i in range(10):  # Create 10 reports
        reporter = random.choice(users_list)
        reported = random.choice(users_list)
        
        if reporter.id == reported.id:
            continue
        
        report = Report(
            reporter_id=reporter.id,
            reported_id=reported.id,
            report_type=random.choice(report_types),
            title=f"Test Report #{i+1}",
            description=f"This is a test report for testing purposes. Report details would go here.",
            severity=random.choice(['Low', 'Medium', 'High']),
            status=random.choice(['Pending Review', 'Under Investigation', 'Resolved', 'Dismissed']),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        
        # Assign admin for some reports
        if admin_users and random.random() < 0.7:
            report.assigned_admin_id = random.choice(admin_users).id
        
        db.session.add(report)
    
    db.session.commit()
    report_count = Report.query.count()
    print(f"   ✅ Created {report_count} reports")

def create_favourites(users):
    """Create test favourites"""
    print("8. Creating test favourites...")
    
    seekers = [user for user in users.values() if user.role == 'seeker']
    escorts = [user for user in users.values() if user.role == 'escort']
    
    for seeker in seekers:
        # Each seeker favorites 1-3 escorts
        num_favorites = random.randint(1, 3)
        chosen_escorts = random.sample(escorts, min(num_favorites, len(escorts)))
        
        for escort in chosen_escorts:
            # Check if favourite already exists
            existing_fav = Favourite.query.filter_by(
                user_id=seeker.id,
                favourite_user_id=escort.id
            ).first()
            
            if not existing_fav:
                favourite = Favourite(
                    user_id=seeker.id,
                    favourite_user_id=escort.id,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                db.session.add(favourite)
    
    db.session.commit()
    favourite_count = Favourite.query.count()
    print(f"   ✅ Created {favourite_count} favourites")

def create_audit_logs(users):
    """Create test audit logs"""
    print("9. Creating test audit logs...")
    
    users_list = list(users.values())
    
    actions = [
        'login',
        'logout',
        'password_change',
        'profile_update',
        'booking_created',
        'booking_cancelled',
        'payment_made',
        'message_sent',
        'report_filed'
    ]
    
    for i in range(100):  # Create 100 audit logs
        user = random.choice(users_list)
        action = random.choice(actions)
        
        audit_log = AuditLog(
            user_id=user.id,
            action=action,
            details=f"Test audit log entry for {action}",
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.session.add(audit_log)
    
    db.session.commit()
    audit_count = AuditLog.query.count()
    print(f"   ✅ Created {audit_count} audit logs")

def update_profile_ratings(users):
    """Update profile ratings based on rating data"""
    print("10. Updating profile ratings...")
    
    escorts = [user for user in users.values() if user.role == 'escort']
    
    for escort in escorts:
        ratings = Rating.query.filter_by(reviewed_id=escort.id).all()
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
            escort.profile.rating = round(avg_rating, 1)
    
    db.session.commit()
    print("   ✅ Updated profile ratings")

def setup_test_data():
    """Main function to set up all test data"""
    print("🎯 Setting up comprehensive test data for Safe Companions")
    print("=" * 60)
    
    try:
        with app.app_context():
            # Clear existing data
            clear_existing_data()
            
            # Create users first
            users = create_test_users()
            
            # Create related data
            create_time_slots(users)
            create_bookings(users)
            create_payments(users)
            create_messages(users)
            create_ratings(users)
            create_reports(users)
            create_favourites(users)
            create_audit_logs(users)
            update_profile_ratings(users)
            
            print("\n✅ Test data setup completed successfully!")
            print("\n🔐 Test Login Credentials:")
            print("=" * 40)
            print(f"🔑 ADMIN: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
            print(f"👤 SEEKER: seeker1@example.com / {TEST_PASSWORD}")
            print(f"💼 ESCORT: escort1@example.com / {TEST_PASSWORD}")
            print(f"🔒 LOCKED: locked@example.com / {TEST_PASSWORD}")
            print(f"❌ UNVERIFIED: unverified@example.com / {TEST_PASSWORD}")
            
            print("\n📊 Database Summary:")
            print("=" * 40)
            print(f"👥 Users: {User.query.count()}")
            print(f"👤 Profiles: {Profile.query.count()}")
            print(f"⏰ Time Slots: {TimeSlot.query.count()}")
            print(f"📅 Bookings: {Booking.query.count()}")
            print(f"💳 Payments: {Payment.query.count()}")
            print(f"💬 Messages: {Message.query.count()}")
            print(f"⭐ Ratings: {Rating.query.count()}")
            print(f"🚨 Reports: {Report.query.count()}")
            print(f"❤️ Favourites: {Favourite.query.count()}")
            print(f"📝 Audit Logs: {AuditLog.query.count()}")
            
    except Exception as e:
        print(f"❌ Test data setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = setup_test_data()
    if success:
        print("\n🚀 Test data is ready! You can now test all features.")
    else:
        print("\n💥 Test data setup failed. Please check the errors above.")
        sys.exit(1)
