#!/usr/bin/env python3
"""
Database Initialization Script
This script creates all database tables and sets up the initial schema.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append('/app')

from blueprint.models import db, User, Profile, Booking, Payment, Report, Rating, PasswordHistory
from app import app

def initialize_database():
    """Initialize the database with all required tables."""
    print("🗃️  Database Initialization")
    print("=" * 60)
    
    try:
        with app.app_context():
            print("1. Creating all database tables...")
            
            # Create all tables
            db.create_all()
            
            print("   ✅ All tables created successfully!")
            
            # Verify tables were created
            print("\n2. Verifying table creation...")
            
            # Test each table by attempting a simple query
            tables_to_verify = [
                ('User', User),
                ('Profile', Profile),
                ('Booking', Booking),
                ('Payment', Payment),
                ('Report', Report),
                ('Rating', Rating),
                ('PasswordHistory', PasswordHistory)
            ]
            
            for table_name, model_class in tables_to_verify:
                try:
                    count = model_class.query.count()
                    print(f"   ✅ {table_name} table: {count} records")
                except Exception as e:
                    print(f"   ⚠️  {table_name} table verification failed: {e}")
            
            print("\n3. Creating test user...")
            
            # Check if test user exists
            test_user = User.query.filter_by(email='seeker@example.com').first()
            if not test_user:
                from werkzeug.security import generate_password_hash
                
                # Create test user with all required fields
                test_user = User(
                    email='seeker@example.com',
                    password_hash=generate_password_hash('password123'),
                    role='seeker',
                    active=True,
                    gender='Non-binary',  # Add required gender field
                    email_verified=True,  # Skip email verification for test user
                    phone_verified=True,   # Skip phone verification for test user
                    created_at=datetime.utcnow(),
                    password_created_at=datetime.utcnow(),
                    failed_login_attempts=0,
                    password_change_required=False
                )
                
                db.session.add(test_user)
                db.session.commit()
                print("   ✅ Test user 'seeker@example.com' created successfully!")
            else:
                print("   ℹ️  Test user 'seeker@example.com' already exists")
            
            print("\n✅ Database initialization completed successfully!")
            print("\n🔐 Test Login Credentials:")
            print("   Email: seeker@example.com")
            print("   Password: password123")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = initialize_database()
    if success:
        print("\n🚀 Database is ready! You can now start using the application.")
    else:
        print("\n💥 Database initialization failed. Please check the errors above.")
        sys.exit(1)
