#!/usr/bin/env python3
"""
Create test escort users and profiles for browsing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from blueprint.models import User, Profile
from datetime import datetime, timedelta
import random

def create_test_escorts():
    """Create test escort users and profiles"""
    with app.app_context():
        print("🔧 Creating test escort users and profiles...")
        
        # Test escort data
        test_escorts = [
            {
                'email': 'escort1@example.com',
                'password': 'password123',
                'role': 'escort',
                'gender': 'female',
                'name': 'Sarah Johnson',
                'bio': 'Professional companion with 5 years experience. Elegant, sophisticated, and well-educated.',
                'age': 25,
                'availability': 'Weekdays 6PM-12AM, Weekends 2PM-2AM',
                'preference': 'Dinner dates, social events, theater'
            },
            {
                'email': 'escort2@example.com',
                'password': 'password123',
                'role': 'escort',
                'gender': 'male',
                'name': 'David Chen',
                'bio': 'Athletic and charming companion. Perfect for business events and social gatherings.',
                'age': 28,
                'availability': 'Evenings and weekends',
                'preference': 'Business events, fitness, cultural events'
            },
            {
                'email': 'escort3@example.com',
                'password': 'password123',
                'role': 'escort',
                'gender': 'female',
                'name': 'Emily Rodriguez',
                'bio': 'Multilingual companion fluent in English, Spanish, and French. Art enthusiast.',
                'age': 24,
                'availability': 'Flexible schedule',
                'preference': 'Art galleries, museums, fine dining'
            },
            {
                'email': 'escort4@example.com',
                'password': 'password123',
                'role': 'escort',
                'gender': 'male',
                'name': 'Michael Thompson',
                'bio': 'Professional model and companion. Experienced in high-profile social events.',
                'age': 30,
                'availability': 'Weekends primarily',
                'preference': 'Fashion events, luxury experiences'
            }
        ]
        
        created_users = []
        
        for escort_data in test_escorts:
            # Check if user already exists
            existing_user = User.query.filter_by(email=escort_data['email']).first()
            if existing_user:
                print(f"⚠️  User {escort_data['email']} already exists, skipping...")
                continue
            
            # Create user
            user = User(
                email=escort_data['email'],
                role=escort_data['role'],
                gender=escort_data['gender'],
                active=True,
                email_verified=True,
                phone_verified=True,
                created_at=datetime.utcnow(),
                password_created_at=datetime.utcnow(),
                password_change_required=False,
                failed_login_attempts=0,
                otp_attempts=0
            )
            
            # Set password
            success, message = user.set_password(escort_data['password'], check_history=False)
            if not success:
                print(f"❌ Failed to set password for {escort_data['email']}: {message}")
                continue
            
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                name=escort_data['name'],
                bio=escort_data['bio'],
                age=escort_data['age'],
                availability=escort_data['availability'],
                preference=escort_data['preference'],
                photo='default.jpg',  # Default photo
                rating=round(random.uniform(4.0, 5.0), 1)  # Random rating between 4.0-5.0
            )
            
            db.session.add(profile)
            created_users.append(user)
            
            print(f"✅ Created escort: {escort_data['name']} ({escort_data['email']})")
        
        # Commit all changes
        db.session.commit()
        print(f"\n🎉 Successfully created {len(created_users)} escort users and profiles!")
        
        # Verify creation
        total_escorts = User.query.filter_by(role='escort').count()
        total_profiles = Profile.query.count()
        print(f"📊 Total escorts in database: {total_escorts}")
        print(f"📊 Total profiles in database: {total_profiles}")
        
        return True

if __name__ == "__main__":
    try:
        create_test_escorts()
        print("\n✅ Test escorts created successfully!")
    except Exception as e:
        print(f"\n❌ Error creating test escorts: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
