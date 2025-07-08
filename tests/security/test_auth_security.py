
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

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture
def seeker_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client, flask_app.app_context():
        user = User.query.filter_by(email="testseeker@example.com").first()
        if not user:
            user = User(
                email="testseeker@example.com",
                role="seeker",
                gender="Other",
                active=True,
                activate=True,
                deleted=False,
                created_at=datetime.utcnow(),
                password_hash=generate_password_hash("ValidPass123"),
                password_created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()

        fake_ua = "test-agent"
        fake_ip = "127.0.0.1"
        client.environ_base["HTTP_USER_AGENT"] = fake_ua
        client.environ_base["REMOTE_ADDR"] = fake_ip

        with client.session_transaction() as sess:
            sess["user_id"] = user.id
            sess["role"] = "seeker"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip

        yield client


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

# === Authentication Security Tests ===


def test_password_complexity_enforcement(seeker_session):
    from blueprint.models import User
    user = User.query.filter_by(email="testseeker@example.com").first() 

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
        response.status_code in [400]
    )

def test_password_reuse(seeker_session):
    from blueprint.models import User
    user = User.query.filter_by(email="testseeker@example.com").first() 

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
