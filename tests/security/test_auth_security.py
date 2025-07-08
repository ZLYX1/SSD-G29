
'''
import sys
import os
# Ensure app is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
import re
from app import app as flask_app
from extensions import db
from blueprint.models import User
from datetime import datetime
from werkzeug.security import generate_password_hash


# === Helper to extract CSRF token ===
def extract_csrf_token(html_data):
    html = html_data.decode()
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    return match.group(1) if match else None

# === Fixtures ===
@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

# === Register Page Security Tests ===

def test_register_xss_email(client):
    response = client.get('/auth/?mode=register')
    csrf_token = extract_csrf_token(response.data)
    payload = "<script>alert(1)</script>"
    response = client.post('/auth/?mode=register', data={
        "form_type": "register",
        "email": payload,
        "password": "ValidPass123",
        "age": "20",
        "phone_number": "91234567",
        "gender": "Other",
        "role": "seeker",
        "preference": "Any",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert payload.encode() not in response.data

def test_register_xss_password(client):
    response = client.get('/auth/?mode=register')
    csrf_token = extract_csrf_token(response.data)
    payload = "<script>alert(1)</script>"
    response = client.post('/auth/?mode=register', data={
        "form_type": "register",
        "email": "xss@example.com",
        "password": payload,
        "age": "20",
        "phone_number": "91234567",
        "gender": "Other",
        "role": "seeker",
        "preference": "Any",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert payload.encode() not in response.data

def test_register_sql_injection_password(client):
    response = client.get('/auth/?mode=register')
    csrf_token = extract_csrf_token(response.data)
    response = client.post('/auth/?mode=register', data={
        "form_type": "register",
        "email": "sqltest@example.com",
        "password": "' OR '1'='1",
        "age": "20",
        "phone_number": "1234567890",
        "gender": "Other",
        "role": "seeker",
        "preference": "Any",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert b"Register" in response.data or b"Invalid" in response.data

def test_register_missing_csrf(client):
    response = client.post('/auth/?mode=register', data={
        "form_type": "register",
        "email": "nocsrf@example.com",
        "password": "ValidPass123",
        "age": "20",
        "phone_number": "91234567",
        "gender": "Other",
        "role": "seeker",
        "preference": "Any"
    })
    assert response.status_code in [400, 403]

def test_register_min_password_length(client):
    response = client.get('/auth/?mode=register')
    csrf_token = extract_csrf_token(response.data)
    response = client.post('/auth/?mode=register', data={
        "form_type": "register",
        "email": "shortpass@example.com",
        "password": "123",
        "age": "20",
        "phone_number": "91234567",
        "gender": "Other",
        "role": "seeker",
        "preference": "Any",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert b"Register" in response.data and response.status_code == 200

def test_register_invalid_phone(client):
    response = client.get('/auth/?mode=register')
    csrf_token = extract_csrf_token(response.data)
    response = client.post('/auth/?mode=register', data={
        "form_type": "register",
        "email": "invalidphone@example.com",
        "password": "ValidPass123",
        "age": "20",
        "phone_number": "ABC123XYZ",
        "gender": "Other",
        "role": "seeker",
        "preference": "Any",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert b"Register" in response.data

def test_register_age_verification(client):
    response = client.get('/auth/?mode=register')
    csrf_token = extract_csrf_token(response.data)
    response = client.post('/auth/?mode=register', data={
        "form_type": "register",
        "email": "young@example.com",
        "password": "ValidPass123",
        "age": "15",
        "phone_number": "91234567",
        "gender": "Other",
        "role": "seeker",
        "preference": "Any",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert b"You must be at least 18 years old" in response.data

# === Login Page Security Tests ===

def test_login_xss_in_email(client):
    response = client.get('/auth/?mode=login')
    csrf_token = extract_csrf_token(response.data)
    payload = "<script>alert(1)</script>"
    response = client.post('/auth/?mode=login', data={
        "form_type": "login",
        "email": payload,
        "password": "ValidPass123",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert payload.encode() not in response.data

def test_login_sql_injection_password(client):
    response = client.get('/auth/?mode=login')
    csrf_token = extract_csrf_token(response.data)
    response = client.post('/auth/?mode=login', data={
        "form_type": "login",
        "email": "test@example.com",
        "password": "' OR '1'='1",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data

def test_login_missing_csrf(client):
    response = client.post('/auth/?mode=login', data={
        "form_type": "login",
        "email": "test@example.com",
        "password": "ValidPass123"
    })
    assert response.status_code in [400, 403]

def test_login_invalid_email_format(client):
    response = client.get('/auth/?mode=login')
    csrf_token = extract_csrf_token(response.data)
    response = client.post('/auth/?mode=login', data={
        "form_type": "login",
        "email": "invalid-email-format",
        "password": "ValidPass123",
        "csrf_token": csrf_token
    }, follow_redirects=True)
    assert b"Invalid" in response.data or b"credentials" in response.data

'''
def test_login_rate_limiting(client):
    for _ in range(10):
        response = client.get('/auth/?mode=login')
        csrf_token = extract_csrf_token(response.data)
        response = client.post('/auth/?mode=login', data={
            "form_type": "login",
            "email": "test@example.com",
            "password": "wrongpass",
            "csrf_token": csrf_token
        }, follow_redirects=True)
    assert response.status_code != 500
'''
'''