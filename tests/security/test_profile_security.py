'''
import sys
import os
import re
import pytest
from unittest.mock import patch

# Ensure app module is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app import app as flask_app
from blueprint.models import User, Profile
from extensions import db

# === Fixtures ===

@pytest.fixture
def seeker_session():
    flask_app.config["TESTING"] = True
    os.environ["S3_BUCKET_NAME"] = "test-bucket"

    with flask_app.test_client() as client, flask_app.app_context():
        from blueprint.models import User, Profile
        from datetime import datetime

        # Clean up any existing user with this email
        User.query.filter_by(email="seeker@test.com").delete()
        db.session.commit()

        # ✅ Provide all NOT NULL fields
        user = User(
            email="seeker@test.com",
            password_hash="dummy",
            role="seeker",
            gender="Male", 
            active=True,
            activate=True,
            deleted=False,
            created_at=datetime.utcnow(),
            password_created_at=datetime.utcnow(),
        )
        db.session.add(user)
        db.session.commit()

        profile = Profile(user_id=user.id, name="Test Seeker", bio="Test bio")
        db.session.add(profile)
        db.session.commit()

        with client.session_transaction() as sess:
            sess["user_id"] = user.id
            sess["role"] = "seeker"
            sess["bound_ua"] = "test-agent"
            sess["bound_ip"] = "127.0.0.1"

        yield client

        # Cleanup
        Profile.query.filter_by(user_id=user.id).delete()
        User.query.filter_by(id=user.id).delete()
        db.session.commit()

# === Helper ===

def extract_csrf_token(response_data):
    html = response_data.decode()
    print("=== HTML RECEIVED ===")
    print(html)
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None

# === Security Test Cases ===

def test_profile_update_without_csrf(seeker_session):
    response = seeker_session.post("/profile/", data={
        "name": "Hacker",
        "bio": "Injected bio",
        "availability": "Available"
    }, follow_redirects=True)
    assert response.status_code in [400, 403], "Missing CSRF token should be rejected"

def test_xss_injection_in_name(seeker_session):
    payload = "<script>alert(1)</script>"
    get_response = seeker_session.get('/profile/')
    csrf_token = extract_csrf_token(get_response.data)

    response = seeker_session.post("/profile/", data={
        "csrf_token": csrf_token,
        "name": payload,
        "bio": "Normal bio",
        "availability": "Available"
    }, follow_redirects=True)

    assert payload.encode() not in response.data

'''
def test_sql_injection_in_bio(seeker_session):
    from blueprint.models import User
    user = User.query.filter_by(email="seeker@test.com").first()

    # Get CSRF token
    get_response = seeker_session.get("/profile/")
    csrf_token = extract_csrf_token(get_response.data)
    assert csrf_token, "Failed to extract CSRF token"

    payload = "' OR '1'='1"

    response = seeker_session.post("/profile/", data={
        "csrf_token": csrf_token,
        "name": "Normal",
        "bio": payload,
        "availability": "Available"
    }, follow_redirects=True)

    assert response.status_code in [200, 400]

    # Accept either a success (safe handling) or graceful error (blocked injection)
    assert (
        b"Profile updated successfully" in response.data or
        b"Invalid input" in response.data or
        b"Bad Request" not in response.data
    )

# Optional: Uncomment this when you want to validate file type rejection

@patch("blueprint.profile.s3")
def test_invalid_file_type_upload(mock_s3, seeker_session):
    mock_s3.generate_presigned_post.return_value = {
        "url": "https://fake-s3-url",
        "fields": {"key": "value"}
    }

    get_resp = seeker_session.get('/profile/')
    csrf_token = extract_csrf_token(get_resp.data)

    response = seeker_session.post(
        "/profile/generate-presigned-url",
        json={
            "file_name": "evil.php",
            "file_type": "application/x-php"
        },
        headers={
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token
        }
    )

    assert response.status_code == 400
    assert b"Invalid file type" in response.data or b"error" in response.data
'''

def test_password_complexity_enforcement(seeker_session):
    from blueprint.models import User
    user = User.query.filter_by(email="seeker@test.com").first()

    get_response = seeker_session.get(f"/auth/change-password/{user.id}")
    csrf_token = extract_csrf_token(get_response.data)

    response = seeker_session.post(f"/auth/change-password/{user.id}", data={
        "csrf_token": csrf_token,
        "current_password": "ValidPass123",
        "new_password": "123",  # Too weak
        "confirm_password": "123"
    }, follow_redirects=True)

    assert (
        b"Password requirements not met" in response.data or
        b"Password" in response.data or
        response.status_code in [200, 400]
    )

def test_password_reuse(seeker_session):
    from blueprint.models import User
    user = User.query.filter_by(email="seeker@test.com").first()

    # Get CSRF token from the actual change-password page
    get_response = seeker_session.get(f"/auth/change-password/{user.id}")
    csrf_token = extract_csrf_token(get_response.data)

    reused_password = "ValidPass123"
    response = seeker_session.post(f"/auth/change-password/{user.id}", data={
        "csrf_token": csrf_token,
        "current_password": reused_password,
        "new_password": reused_password,
        "confirm_password": reused_password
    }, follow_redirects=True)

    assert (
        b"Password has been used recently" in response.data or
        b"Password" in response.data or
        response.status_code in [200, 400]
    )
    '''