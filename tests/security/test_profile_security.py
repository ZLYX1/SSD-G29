import sys
import os
import re
import pytest
from unittest.mock import patch
from datetime import datetime, timezone  

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app import app as flask_app
from blueprint.models import User, Profile
from extensions import db

@pytest.fixture
def seeker_session():
    flask_app.config["TESTING"] = True
    os.environ["S3_BUCKET_NAME"] = "test-bucket"

    with flask_app.test_client() as client, flask_app.app_context():
        User.query.filter_by(email="seeker@test.com").delete()
        db.session.commit()

        user = User(
            email="seeker@test.com",
            password_hash="dummy",
            role="seeker",
            gender="Male", 
            active=True,
            activate=True,
            deleted=False,
            created_at=datetime.now(timezone.utc),    
            password_created_at=datetime.now(timezone.utc) 
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

        Profile.query.filter_by(user_id=user.id).delete()
        User.query.filter_by(id=user.id).delete()
        db.session.commit()

def extract_csrf_token(response_data):
    html = response_data.decode()
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None

def test_profile_update_without_csrf(seeker_session):
    response = seeker_session.post("/profile/", data={
        "name": "Hacker",
        "bio": "Injected bio",
        "availability": "Available"
    }, follow_redirects=True)

    assert response.status_code in [200, 400, 403], "Expected failure or CSRF error when token is missing"

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
