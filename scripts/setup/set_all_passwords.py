#!/usr/bin/env python3
"""
Set passwords for all escort users
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
    
    # Set passwords for all escort users
    escorts = [
        ('escort_alice@example.com', 'alice123'),
        ('escort_bob@example.com', 'bob123'),
        ('escort_eve@example.com', 'eve123')
    ]
    
    for email, password in escorts:
        password_hash = generate_password_hash(password)
        cursor.execute("""
            UPDATE "user" 
            SET password_hash = %s 
            WHERE email = %s
            RETURNING id, email
        """, (password_hash, email))
        
        user_data = cursor.fetchone()
        if user_data:
            user_id, email = user_data
            print(f"✅ Set password for: {email} (ID: {user_id}) → {password}")
    
    conn.commit()
    
    print(f"""
🎉 All escort login credentials are now set!

👩 ALICE (ID: 101)
📧 Email: escort_alice@example.com  
🔑 Password: alice123

👨 BOB (ID: 102)  
📧 Email: escort_bob@example.com
🔑 Password: bob123

👩 EVE (ID: 105)
📧 Email: escort_eve@example.com
🔑 Password: eve123
""")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
