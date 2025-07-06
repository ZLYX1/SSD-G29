import sys
import os
import pytest
import time
import html

# Add parent directory to sys.path so `app` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection during test
    with app.test_client() as client:
        yield client

def test_empty_fields(client):
    response = client.post('/auth?mode=register', data={
        'email': '',
        'password': '',
        'gender': '',
        'role': '',
        'age': '',
        'age_verify': '',
        'form_type': 'register',
        'g-recaptcha-response': 'dummy-token'
    }, follow_redirects=True)

    # Check if failure is handled gracefully
    assert response.status_code in [200, 302, 400, 422]
    assert (
        b"required" in response.data.lower()
        or b"missing" in response.data.lower()
        or b"please enter" in response.data.lower()
        or b"invalid" in response.data.lower()
    ), "No error message shown for empty input fields"

def test_sql_injection(client):
    payload = "' OR '1'='1"
    response = client.post('/auth?mode=register', data={
        'email': payload,
        'password': payload,
        'gender': 'Other',
        'role': 'escort',
        'age': '30',
        'age_verify': 'on',
        'form_type': 'register',
        'g-recaptcha-response': 'dummy-token'
    }, follow_redirects=True)

    assert response.status_code in [200, 302, 400, 422]
    assert any(keyword in response.data.lower() for keyword in [
        b"invalid", b"error", b"unauthorized", b"email", b"fail"
    ]), "No validation message shown for SQL injection input"

def test_xss_input(client):
    xss = "<script>alert(1)</script>"
    response = client.post('/auth?mode=register', data={
        'email': xss,
        'password': xss,
        'gender': 'Female',
        'role': 'escort',
        'age': '22',
        'age_verify': 'on',
        'form_type': 'register',
        'g-recaptcha-response': 'dummy-token'
    }, follow_redirects=True)

    # Assert raw XSS is NOT present
    assert xss.encode() not in response.data, "XSS payload reflected unsanitized!"

'''
def test_successful_registration(client):
    # Unique email per run
    email = f"testuser_{int(time.time())}@example.com"
    response = client.post('/auth?mode=register', data={
        'email': email,
        'password': 'StrongPass123!',
        'gender': 'Non-binary',
        'role': 'seeker',
        'age': '26',
        'age_verify': 'on',
        'form_type': 'register',
        'g-recaptcha-response': 'dummy-token'
    }, follow_redirects=True)

    assert response.status_code in [200, 302]
    assert any(keyword in response.data.lower() for keyword in [
        b"success", b"login", b"welcome", b"registered"
    ]), "Registration flow did not succeed"
'''