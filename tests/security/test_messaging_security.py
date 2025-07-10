import sys
import os
import pytest
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app import app as flask_app
from blueprint.models import User, Message
from extensions import db

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
                email_verified=True,
                phone_verified=True,
                created_at=datetime.now(timezone.utc),
                password_hash=generate_password_hash("ValidPass123"),
                password_created_at=datetime.now(timezone.utc)
            )
            db.session.add(user)
            db.session.commit()

        client.environ_base["HTTP_USER_AGENT"] = "test-agent"
        client.environ_base["REMOTE_ADDR"] = "127.0.0.1"

        with client.session_transaction() as sess:
            sess["user_id"] = user.id
            sess["role"] = "seeker"
            sess["bound_ua"] = "test-agent"
            sess["bound_ip"] = "127.0.0.1"

        yield client, user

@pytest.fixture
def escort_user():
    with flask_app.app_context():
        user = User.query.filter_by(email="testescort@example.com").first()
        if not user:
            user = User(
                email="testescort@example.com",
                role="escort",
                gender="Male",
                active=True,
                email_verified=True,
                phone_verified=True,
                created_at=datetime.now(timezone.utc),
                password_hash=generate_password_hash("Test1234!"),
                password_created_at=datetime.now(timezone.utc)
            )
            db.session.add(user)
            db.session.commit()
        return user

# === Tests ===

def test_send_message_without_csrf(seeker_session, escort_user):
    client, _ = seeker_session
    response = client.post("/messaging/send", data={
        "recipient_id": escort_user.id,
        "content": "Hello world!"
    }, follow_redirects=False)

    assert response.status_code in [400, 403], f"Expected CSRF failure, got {response.status_code}"

def test_cannot_send_message_to_self(seeker_session, escort_user):
    client, user = seeker_session
    response = client.get(f"/messaging/conversation/{escort_user.id}")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    assert csrf_input is not None
    csrf_token = csrf_input["value"]

    response = client.post("/messaging/send", json={
        "recipient_id": user.id,
        "content": "This should not be allowed"
    }, headers={"X-CSRFToken": csrf_token})

    assert response.status_code == 200
    assert b"Cannot send message to yourself" in response.data