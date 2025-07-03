#!/usr/bin/env python3
"""
Create admin user and test data for the reporting system
"""
import psycopg2
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json

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
    
    # Create admin user
    admin_password_hash = generate_password_hash('admin123')
    cursor.execute("""
        INSERT INTO "user" (email, password_hash, role, active, gender, email_verified)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE SET
        password_hash = EXCLUDED.password_hash,
        role = EXCLUDED.role
        RETURNING id, email
    """, ('admin@safecompanions.com', admin_password_hash, 'admin', True, 'Other', True))
    
    admin_result = cursor.fetchone()
    admin_id = admin_result[0]
    print(f"✅ Created admin user: {admin_result[1]} (ID: {admin_id})")
    
    # Create admin profile
    cursor.execute("""
        INSERT INTO profile (user_id, name, bio, age)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
        name = EXCLUDED.name,
        bio = EXCLUDED.bio,
        age = EXCLUDED.age
    """, (admin_id, 'System Administrator', 'Platform administrator responsible for user safety and moderation.', 30))
    
    print(f"✅ Created admin profile")
    
    # Get existing users for creating test reports
    cursor.execute("SELECT id, email FROM \"user\" WHERE role IN ('seeker', 'escort') LIMIT 5")
    users = cursor.fetchall()
    print(f"✅ Found {len(users)} users for test reports")
    
    # Create sample reports
    report_data = [
        {
            'reporter_id': users[0][0],  # testuser
            'reported_id': users[1][0],  # alice
            'report_type': 'inappropriate_behavior',
            'title': 'Inappropriate messages during booking',
            'description': 'The escort sent inappropriate messages that made me uncomfortable. They were persistent despite being asked to stop.',
            'severity': 'High',
            'evidence_urls': ['https://example.com/screenshot1.jpg', 'https://example.com/screenshot2.jpg']
        },
        {
            'reporter_id': users[2][0],  # charlie  
            'reported_id': users[3][0],  # diana
            'report_type': 'fraud',
            'title': 'Payment requested but service not provided',
            'description': 'User requested payment upfront but then became unreachable. No service was provided despite payment.',
            'severity': 'High',
            'evidence_urls': ['https://example.com/payment_proof.jpg']
        },
        {
            'reporter_id': users[1][0],  # alice
            'reported_id': users[0][0],  # testuser
            'report_type': 'harassment',
            'title': 'Persistent unwanted contact',
            'description': 'User continues to contact me despite being told I am not interested. Messages are becoming threatening.',
            'severity': 'Critical'
        },
        {
            'reporter_id': users[2][0],  # charlie
            'reported_id': users[4][0],  # eve
            'report_type': 'fake_profile',
            'title': 'Profile photos are not of the actual person',
            'description': 'Met this person and they look completely different from their profile photos. Appears to be using stolen photos.',
            'severity': 'Medium'
        }
    ]
    
    # Insert sample reports
    for i, report in enumerate(report_data):
        evidence_json = json.dumps(report.get('evidence_urls')) if report.get('evidence_urls') else None
        created_time = datetime.now() - timedelta(days=i+1, hours=i*2)
        
        cursor.execute("""
            INSERT INTO report (reporter_id, reported_id, report_type, title, description, 
                              evidence_urls, severity, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            report['reporter_id'], report['reported_id'], report['report_type'],
            report['title'], report['description'], evidence_json,
            report['severity'], 'Pending Review', created_time
        ))
        
        report_id = cursor.fetchone()[0]
        print(f"✅ Created report #{report_id}: {report['title']}")
    
    # Update one report to show admin handling
    cursor.execute("""
        UPDATE report 
        SET status = 'Under Investigation',
            assigned_admin_id = %s,
            admin_notes = 'Started investigation. Requested additional evidence from reporter.',
            updated_at = %s
        WHERE id = (SELECT id FROM report ORDER BY id LIMIT 1)
        RETURNING id, title
    """, (admin_id, datetime.now()))
    
    updated_report = cursor.fetchone()
    if updated_report:
        print(f"✅ Updated report #{updated_report[0]} to 'Under Investigation'")
    
    # Resolve one report
    cursor.execute("""
        UPDATE report 
        SET status = 'Resolved',
            assigned_admin_id = %s,
            admin_notes = 'Investigation completed. User warned and profile updated.',
            resolution = 'User has been given a formal warning. Profile photos have been verified and updated. No further action required at this time.',
            resolved_at = %s,
            updated_at = %s
        WHERE id = (SELECT id FROM report ORDER BY id LIMIT 1 OFFSET 1)
        RETURNING id, title
    """, (admin_id, datetime.now(), datetime.now()))
    
    resolved_report = cursor.fetchone()
    if resolved_report:
        print(f"✅ Resolved report #{resolved_report[0]}")
    
    conn.commit()
    
    # Display summary
    cursor.execute("SELECT COUNT(*) FROM report")
    total_reports = cursor.fetchone()[0]
    
    cursor.execute("SELECT status, COUNT(*) FROM report GROUP BY status")
    status_counts = cursor.fetchall()
    
    print(f"""
🎉 Report System Setup Complete!

👤 ADMIN CREDENTIALS:
📧 Email: admin@safecompanions.com
🔑 Password: admin123
👥 Role: admin

📊 REPORT STATISTICS:
📝 Total Reports: {total_reports}
""")
    
    for status, count in status_counts:
        print(f"   {status}: {count}")
    
    print(f"""
🔗 ADMIN URLS TO TEST:
• Admin Dashboard: http://localhost:5000/report/admin
• Report Statistics: http://localhost:5000/report/admin/statistics
• View Specific Report: http://localhost:5000/report/admin/report/1

🔗 USER URLS TO TEST:
• Submit Report: http://localhost:5000/report/submit
• My Reports: http://localhost:5000/report/my-reports
• Quick Report User: http://localhost:5000/report/report-user/101

📋 TESTING WORKFLOW:
1. Login as admin to manage reports
2. Login as regular user to submit reports
3. Test report status updates
4. Test search and filtering
5. Test evidence handling
""")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
