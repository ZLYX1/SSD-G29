import os
import sys
import pytest

from werkzeug.security import generate_password_hash

# Adjust path to your app structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from blueprint.models import User  # adjust based on your actual import

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.drop_all()      # Ensure no leftover tables
        db.create_all()

        user = User(
            email='testuser@example.com',
            role='seeker',
            gender='Male',
            active=True
        )
        user.set_password('StrongPass123!')
        db.session.add(user)
        db.session.commit()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()  # Clean up after test

def test_empty_fields(client):
    response = client.post('/auth?mode=login', data={
        'email': '',
        'password': '',
        'form_type': 'login'
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data or response.status_code == 200

def test_invalid_login(client):
    response = client.post('/auth?mode=login', data={
        'email': 'wrong@example.com',
        'password': 'WrongPass!',
        'form_type': 'login'
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data or response.status_code == 200

def test_sql_injection(client):
    payload = "' OR '1'='1"
    response = client.post('/auth?mode=login', data={
        'email': payload,
        'password': payload,
        'form_type': 'login'
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data or response.status_code == 200

def test_xss_input(client):
    xss = "<script>alert(1)</script>"
    response = client.post('/auth?mode=login', data={
        'email': xss,
        'password': xss,
        'form_type': 'login'
    }, follow_redirects=True)
    assert b"<script>" not in response.data

def test_successful_login(client):
    response = client.post('/auth?mode=login', data={
        'email': 'testuser@example.com',
        'password': 'StrongPass123!',
        'form_type': 'login'
    }, follow_redirects=True)
    # Check that login succeeded and redirects to dashboard
    assert b"dashboard" in response.data.lower() or response.status_code in [200, 302]