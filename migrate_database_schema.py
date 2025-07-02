#!/usr/bin/env python3
"""
Database schema migration for Password Security features
This script adds the new columns to the existing database
"""
import os
import sys
from flask import Flask
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app for migration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-development-secret-key')

# Import after Flask app creation
from extensions import db
from sqlalchemy import text

# Initialize the database with the app
db.init_app(app)

def execute_sql(sql, description):
    """Execute SQL and handle errors"""
    try:
        db.session.execute(text(sql))
        print(f"   ✅ {description}")
        return True
    except Exception as e:
        if "already exists" in str(e) or "duplicate column" in str(e):
            print(f"   ℹ️  {description} (already exists)")
            return True
        else:
            print(f"   ❌ {description}: {e}")
            return False

def migrate_database_schema():
    """Add password security columns to existing tables"""
    print("🔄 Starting Database Schema Migration")
    print("=" * 60)
    
    with app.app_context():
        try:
            print("1. Adding password security columns to User table...")
            
            # Add password security columns to User table
            migrations = [
                ("ALTER TABLE \"user\" ADD COLUMN password_created_at TIMESTAMP;", 
                 "Add password_created_at column"),
                ("ALTER TABLE \"user\" ADD COLUMN password_expires_at TIMESTAMP;", 
                 "Add password_expires_at column"),
                ("ALTER TABLE \"user\" ADD COLUMN password_change_required BOOLEAN DEFAULT FALSE;", 
                 "Add password_change_required column"),
                ("ALTER TABLE \"user\" ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;", 
                 "Add failed_login_attempts column"),
                ("ALTER TABLE \"user\" ADD COLUMN account_locked_until TIMESTAMP;", 
                 "Add account_locked_until column"),
            ]
            
            success_count = 0
            for sql, description in migrations:
                if execute_sql(sql, description):
                    success_count += 1
            
            print(f"\n2. Creating PasswordHistory table...")
            
            # Create PasswordHistory table
            password_history_sql = """
            CREATE TABLE IF NOT EXISTS password_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE
            );
            """
            
            execute_sql(password_history_sql, "Create PasswordHistory table")
            
            print(f"\n3. Setting default values for existing users...")
            
            # Set default values for existing users
            default_updates = [
                ("UPDATE \"user\" SET password_created_at = created_at WHERE password_created_at IS NULL;",
                 "Set password_created_at to user creation date"),
                ("UPDATE \"user\" SET password_expires_at = password_created_at + INTERVAL '90 days' WHERE password_expires_at IS NULL AND password_created_at IS NOT NULL;",
                 "Set password expiration to 90 days from creation"),
                ("UPDATE \"user\" SET password_change_required = FALSE WHERE password_change_required IS NULL;",
                 "Set password_change_required default"),
                ("UPDATE \"user\" SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL;",
                 "Set failed_login_attempts default"),
            ]
            
            for sql, description in default_updates:
                execute_sql(sql, description)
            
            # Commit all changes
            db.session.commit()
            print(f"\n✅ Schema migration completed successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Schema migration failed: {e}")
            db.session.rollback()
            return False

def verify_schema():
    """Verify that the schema migration was successful"""
    print("\n🔍 Verifying Schema Migration...")
    print("-" * 40)
    
    with app.app_context():
        try:
            # Check if columns exist by querying them
            test_queries = [
                ("SELECT password_created_at FROM \"user\" LIMIT 1;", "password_created_at column"),
                ("SELECT password_expires_at FROM \"user\" LIMIT 1;", "password_expires_at column"),
                ("SELECT password_change_required FROM \"user\" LIMIT 1;", "password_change_required column"),
                ("SELECT failed_login_attempts FROM \"user\" LIMIT 1;", "failed_login_attempts column"),
                ("SELECT account_locked_until FROM \"user\" LIMIT 1;", "account_locked_until column"),
                ("SELECT COUNT(*) FROM password_history;", "PasswordHistory table"),
            ]
            
            for sql, description in test_queries:
                try:
                    db.session.execute(text(sql))
                    print(f"✅ {description} exists and accessible")
                except Exception as e:
                    print(f"❌ {description} error: {e}")
                    return False
            
            # Check data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM \"user\" WHERE password_created_at IS NOT NULL;")).fetchone()
            users_with_dates = result[0] if result else 0
            
            result = db.session.execute(text("SELECT COUNT(*) as count FROM \"user\";")).fetchone()
            total_users = result[0] if result else 0
            
            print(f"✅ Users with password dates: {users_with_dates}/{total_users}")
            
            return True
            
        except Exception as e:
            print(f"❌ Schema verification failed: {e}")
            return False

if __name__ == '__main__':
    print("🗃️  Database Schema Migration for Password Security")
    print("This will add new columns and tables for password security features.")
    print()
    
    # Run schema migration
    if migrate_database_schema():
        # Verify schema
        if verify_schema():
            print("\n🎯 Schema Migration Complete!")
            print("You can now run the full password security migration:")
            print("python migrate_password_security.py")
        else:
            print("\n⚠️  Schema migration completed but verification failed.")
    else:
        print("\n❌ Schema migration failed. Please check errors and try again.")
