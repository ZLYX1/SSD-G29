#!/usr/bin/env python3
"""
Database Migration: Add OTP System Fields
Adds phone verification fields to existing user table
"""

import psycopg2
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ssd_database',
    'user': 'ssd_user',
    'password': 'ssd_password'
}

def migrate_database():
    """Add OTP system fields to the user table"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔧 DATABASE MIGRATION: Adding OTP System Fields")
        print("=" * 50)
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name IN (
                'phone_number', 'phone_verified', 'otp_code', 'otp_expires', 'otp_attempts'
            )
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add missing columns
        new_columns = [
            ("phone_number", "VARCHAR(20)"),
            ("phone_verified", "BOOLEAN DEFAULT FALSE NOT NULL"),
            ("otp_code", "VARCHAR(6)"),
            ("otp_expires", "TIMESTAMP"),
            ("otp_attempts", "INTEGER DEFAULT 0 NOT NULL")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE "user" ADD COLUMN {column_name} {column_type}')
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"⚠️  Column {column_name} might already exist: {e}")
        
        # Update existing users to have phone_verified = True for backward compatibility
        # (so existing users can still log in while new users need phone verification)
        cursor.execute("""
            UPDATE "user" 
            SET phone_verified = TRUE 
            WHERE phone_verified IS NULL OR phone_verified = FALSE
        """)
        
        updated_count = cursor.rowcount
        print(f"✅ Updated {updated_count} existing users to phone_verified = TRUE")
        
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        print("📋 New OTP System fields added:")
        print("   - phone_number: User's phone number")
        print("   - phone_verified: Phone verification status")
        print("   - otp_code: Current OTP code")
        print("   - otp_expires: OTP expiration time")
        print("   - otp_attempts: Failed OTP attempts counter")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration Error: {e}")
        return False
    
    return True

def verify_migration():
    """Verify the migration was successful"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name IN ('phone_number', 'phone_verified', 'otp_code', 'otp_expires', 'otp_attempts')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        
        print("\n🔍 MIGRATION VERIFICATION")
        print("=" * 50)
        print("📋 New OTP System columns:")
        for column_name, data_type, is_nullable, default_value in columns:
            print(f"   - {column_name}: {data_type} (nullable: {is_nullable}, default: {default_value})")
        
        # Check user counts
        cursor.execute('SELECT COUNT(*) FROM "user"')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM "user" WHERE phone_verified = TRUE')
        phone_verified_users = cursor.fetchone()[0]
        
        print(f"\n📊 User Statistics:")
        print(f"   - Total users: {total_users}")
        print(f"   - Phone verified users: {phone_verified_users}")
        print(f"   - Pending phone verification: {total_users - phone_verified_users}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Verification Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OTP SYSTEM DATABASE MIGRATION")
    print("=" * 50)
    
    if migrate_database():
        verify_migration()
        print("\n✅ Migration completed successfully!")
        print("🔧 The OTP System is now ready for use.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
