#!/usr/bin/env python3
"""
Set password for Alice so we can login as her
"""
import psycopg2
from werkzeug.security import generate_password_hash

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
    
    # Generate proper password hash for Alice
    password_hash = generate_password_hash('alice123')
    print(f"✅ Generated password hash for Alice")
    
    # Update Alice's password
    cursor.execute("""
        UPDATE "user" 
        SET password_hash = %s 
        WHERE email = %s
        RETURNING id, email
    """, (password_hash, 'escort_alice@example.com'))
    
    user_data = cursor.fetchone()
    if user_data:
        user_id, email = user_data
        print(f"✅ Updated password for: {email} (ID: {user_id})")
    
    conn.commit()
    
    print(f"""
🎉 Alice's login credentials are now set!
📧 Email: escort_alice@example.com  
🔑 Password: alice123
👤 Role: escort
🆔 User ID: 101
""")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
