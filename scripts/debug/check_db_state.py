#!/usr/bin/env python3

from app import app
from flask import g
import psycopg2.extras

def check_database_state():
    with app.app_context():
        # This will trigger the before_request and set up g.db_conn
        app.preprocess_request()
        conn = g.db_conn
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Check reports
    cur.execute('SELECT * FROM reports ORDER BY created_at DESC')
    reports = cur.fetchall()
    print(f'Found {len(reports)} reports:')
    for r in reports:
        print(f"- ID: {r['id']}, Type: {r['report_type']}, Severity: {r['severity']}, Status: {r['status']}, Reporter: {r['reporter_email']}")

    # Check users
    cur.execute('SELECT id, email, role FROM users ORDER BY id')
    users = cur.fetchall()
    print(f'\nFound {len(users)} users:')
    for u in users:
        print(f"- ID: {u['id']}, Email: {u['email']}, Role: {u['role']}")

    cur.close()
    conn.close()

if __name__ == '__main__':
    check_database_state()
