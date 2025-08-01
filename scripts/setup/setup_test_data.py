#!/usr/bin/env python3
"""
Comprehensive Test Data Setup Script
This script creates test users with different roles and comprehensive test data
for all functionality in the Safe Companions application.

Usage:
  python setup_test_data.py                    # Interactive mode
  python setup_test_data.py --clear-all        # Clear all data and recreate
  python setup_test_data.py --production       # Production-safe mode
  python setup_test_data.py --help             # Show help
"""

import os
import sys
import random
import argparse
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
            photo='https://sitssd.s3.ap-southeast-1.amazonaws.com/profile_photos/default.jpg',
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
    
    # STRATEGY: Weight booking statuses to get more confirmed bookings for testing
    booking_statuses = ['Pending', 'Confirmed', 'Rejected']
    booking_weights = [25, 60, 15]  # 25% pending, 60% confirmed, 15% rejected
    
    for i in range(25):  # Create 25 bookings (increased from 20)
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
        
        # Use weighted random choice to get more confirmed bookings
        booking_status = random.choices(booking_statuses, weights=booking_weights)[0]
        
        booking = Booking(
            seeker_id=seeker.id,
            escort_id=escort.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status=booking_status
        )
        db.session.add(booking)
    
    db.session.commit()
    booking_count = Booking.query.count()
    
    # Print summary for testing guidance
    confirmed_count = Booking.query.filter_by(status='Confirmed').count()
    pending_count = Booking.query.filter_by(status='Pending').count()
    rejected_count = Booking.query.filter_by(status='Rejected').count()
    
    print(f"   ✅ Created {booking_count} bookings")
    print(f"   📊 Confirmed: {confirmed_count}, Pending: {pending_count}, Rejected: {rejected_count}")

def create_payments(users):
    """Create test payment records - strategically distributed to showcase Pay Now and Rate User features"""
    print("4. Creating test payments...")
    
    # Get all bookings that could have payments
    confirmed_bookings = Booking.query.filter_by(status='Confirmed').all()
    pending_bookings = Booking.query.filter_by(status='Pending').all()
    
    if not confirmed_bookings and not pending_bookings:
        print("   ⚠️  No bookings available for payment creation")
        return
    
    payment_count = 0
    
    # STRATEGY 1: Leave 30% of confirmed bookings WITHOUT payments (for "Pay Now" button testing)
    print("   📋 Processing confirmed bookings for strategic payment distribution...")
    for booking in confirmed_bookings:
        # Check if payment already exists for this booking
        existing_payment = Payment.query.filter_by(booking_id=booking.id).first()
        if existing_payment:
            continue
        
        # Only create payment for 70% of confirmed bookings (30% will show "Pay Now")
        if random.random() < 0.7:
            # Generate unique transaction ID
            transaction_id = f"TXN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{booking.id:04d}_{random.randint(1000, 9999)}"
            
            # For confirmed bookings, bias towards completed payments (so "Rate User" shows)
            payment_status = random.choices(
                ['Completed', 'Pending', 'Failed'],
                weights=[70, 20, 10]  # 70% completed, 20% pending, 10% failed
            )[0]
            
            payment = Payment(
                user_id=booking.seeker_id,  # Payment made by seeker
                booking_id=booking.id,      # Associate with booking
                amount=round(random.uniform(50.0, 500.0), 2),
                status=payment_status,
                transaction_id=transaction_id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(payment)
            payment_count += 1
    
    # STRATEGY 2: Create some payments for pending bookings (50% chance)
    print("   📋 Processing pending bookings for payment distribution...")
    for booking in pending_bookings:
        # Check if payment already exists for this booking
        existing_payment = Payment.query.filter_by(booking_id=booking.id).first()
        if existing_payment:
            continue
        
        # 50% chance for pending bookings (realistic scenario)
        if random.random() < 0.5:
            # Generate unique transaction ID
            transaction_id = f"TXN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{booking.id:04d}_{random.randint(1000, 9999)}"
            
            # For pending bookings, bias towards pending/failed payments
            payment_status = random.choices(
                ['Completed', 'Pending', 'Failed'],
                weights=[40, 40, 20]  # 40% completed, 40% pending, 20% failed
            )[0]
            
            payment = Payment(
                user_id=booking.seeker_id,  # Payment made by seeker
                booking_id=booking.id,      # Associate with booking
                amount=round(random.uniform(50.0, 500.0), 2),
                status=payment_status,
                transaction_id=transaction_id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(payment)
            payment_count += 1
    
    db.session.commit()
    
    # Print summary for testing guidance
    confirmed_no_payment = len([b for b in confirmed_bookings if not Payment.query.filter_by(booking_id=b.id).first()])
    confirmed_with_payment = len([b for b in confirmed_bookings if Payment.query.filter_by(booking_id=b.id).first()])
    
    print(f"   ✅ Created {payment_count} payments")
    print(f"   📊 Confirmed bookings WITHOUT payments: {confirmed_no_payment} (will show 'Pay Now')")
    print(f"   📊 Confirmed bookings WITH payments: {confirmed_with_payment} (potential 'Rate User')")

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
    """Create test ratings strategically - leave some completed payments without ratings for 'Rate User' button testing"""
    print("6. Creating test ratings...")
    
    # Get confirmed bookings that have completed payments
    confirmed_bookings = Booking.query.filter_by(status='Confirmed').all()
    rateable_bookings = []
    
    for booking in confirmed_bookings:
        # Only consider bookings with completed payments
        completed_payment = Payment.query.filter_by(booking_id=booking.id, status='Completed').first()
        if completed_payment:
            rateable_bookings.append(booking)
    
    print(f"   📋 Found {len(rateable_bookings)} bookings with completed payments")
    
    rating_count = 0
    for booking in rateable_bookings:
        # Skip if rating already exists
        existing_rating = Rating.query.filter_by(booking_id=booking.id).first()
        if existing_rating:
            continue
        
        # STRATEGY: Only create rating for 60% of rateable bookings (40% will show "Rate User" button)
        if random.random() < 0.6:
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
                    "Good service, met expectations.",
                    "Wonderful time, very professional.",
                    "Exceeded expectations, will return.",
                    "Friendly and accommodating, perfect!",
                    "Great conversation and company."
                ]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(rating)
            rating_count += 1
    
    db.session.commit()
    
    # Print summary for testing guidance
    no_rating_count = len(rateable_bookings) - rating_count
    print(f"   ✅ Created {rating_count} ratings")
    print(f"   📊 Completed payments WITHOUT ratings: {no_rating_count} (will show 'Rate User')")
    print(f"   📊 Completed payments WITH ratings: {rating_count} (will show 'Rated')")

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

def clear_all_users():
    """Completely remove all users and associated data"""
    print("🗑️  Clearing all existing users and associated data...")
    
    try:
        # Delete in proper order to handle foreign key constraints
        print("   - Deleting ratings...")
        Rating.query.delete()
        
        print("   - Deleting messages...")
        Message.query.delete()
        
        print("   - Deleting reports...")
        Report.query.delete()
        
        print("   - Deleting payments...")
        Payment.query.delete()
        
        print("   - Deleting bookings...")
        Booking.query.delete()
        
        print("   - Deleting time slots...")
        TimeSlot.query.delete()
        
        print("   - Deleting favourites...")
        Favourite.query.delete()
        
        print("   - Deleting password history...")
        PasswordHistory.query.delete()
        
        print("   - Deleting audit logs...")
        AuditLog.query.delete()
        
        print("   - Deleting profiles...")
        Profile.query.delete()
        
        print("   - Deleting users...")
        User.query.delete()
        
        db.session.commit()
        print("   ✅ All users and data cleared successfully")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"   ❌ Error clearing users: {e}")
        return False

def get_user_count():
    """Get current user count"""
    return User.query.count()

def confirm_data_reset():
    """Ask for confirmation before clearing data"""
    current_users = get_user_count()
    
    if current_users == 0:
        print("📊 Database is empty - no users to clear")
        return True
    
    print(f"⚠️  WARNING: Found {current_users} existing users in database")
    print("   This operation will DELETE ALL existing users and their data!")
    print("   This includes: profiles, bookings, messages, payments, ratings, etc.")
    
    while True:
        response = input("\n🤔 Do you want to continue? Type 'DELETE_ALL' to confirm: ").strip()
        if response == 'DELETE_ALL':
            return True
        elif response.lower() in ['no', 'n', 'cancel', 'quit', 'exit']:
            print("❌ Operation cancelled")
            return False
        else:
            print("❌ Invalid response. Type 'DELETE_ALL' to confirm or 'no' to cancel.")

def setup_test_data(clear_existing=False, production_mode=False, force_clear=False):
    """Main function to set up all test data"""
    print("🎯 Setting up comprehensive test data for Safe Companions")
    print("=" * 60)
    
    if production_mode:
        print("🔒 PRODUCTION MODE: Using production-safe test data")
    
    try:
        with app.app_context():
            current_users = get_user_count()
            
            if clear_existing or current_users > 0:
                if not force_clear and not confirm_data_reset():
                    return False
                
                if not clear_all_users():
                    return False
            
            # Create users first
            users = create_test_users()
            
            # Create related data (skip some in production mode)
            if not production_mode:
                create_time_slots(users)
                create_bookings(users)
                create_payments(users)
                create_messages(users)
                create_favourites(users)
                create_reports(users)
                create_ratings(users)
                update_profile_ratings(users)
            else:
                print("🔒 Production mode: Only creating essential users")
            
            print("\n" + "=" * 60)
            print("✅ Test data setup completed successfully!")
            
            # Show summary
            final_count = get_user_count()
            print(f"📊 Total users created: {final_count}")
            
            if not production_mode:
                print(f"📊 Bookings: {Booking.query.count()}")
                print(f"📊 Messages: {Message.query.count()}")
                print(f"📊 Ratings: {Rating.query.count()}")
            
            return True
            
    except Exception as e:
        print(f"\n💥 Error setting up test data: {e}")
        return False

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Set up comprehensive test data for Safe Companions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_test_data.py                    # Interactive mode
  python setup_test_data.py --clear-all        # Clear all data and recreate
  python setup_test_data.py --production       # Production-safe mode
  python setup_test_data.py --clear-all --force  # Force clear without confirmation
        """
    )
    
    parser.add_argument('--clear-all', action='store_true',
                       help='Clear all existing data before creating new test data')
    parser.add_argument('--production', action='store_true',
                       help='Production mode - only create essential users')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompts (use with caution)')
    
    args = parser.parse_args()
    
    success = setup_test_data(
        clear_existing=args.clear_all,
        production_mode=args.production,
        force_clear=args.force
    )
    
    if success:
        print("\n🚀 Test data is ready! You can now test all features.")
    else:
        print("\n💥 Test data setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
