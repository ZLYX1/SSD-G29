
import sys
import os
import re
import pytest
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone  
from werkzeug.security import generate_password_hash

# Ensure app is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app import app as flask_app
from blueprint.models import User
from extensions import db

# === Fixtures ===

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
                created_at=datetime.now(timezone.utc),  
                password_hash=generate_password_hash("ValidPass123"),
                password_created_at=datetime.now(timezone.utc) 
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

@pytest.fixture
def escort_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client, flask_app.app_context():
        user = User.query.filter_by(email="testescort@example.com").first()
        if not user:
            user = User(
                email="testescort@example.com",
                role="escort",
                gender="Non-binary",
                active=True,
                activate=True,
                deleted=False,
                created_at=datetime.now(timezone.utc), 
                password_hash=generate_password_hash("ValidPass123"),
                password_created_at=datetime.now(timezone.utc) 
            )
            db.session.add(user)
            db.session.commit()

        fake_ua = "test-agent"
        fake_ip = "127.0.0.1"
        client.environ_base["HTTP_USER_AGENT"] = fake_ua
        client.environ_base["REMOTE_ADDR"] = fake_ip

        with client.session_transaction() as sess:
            sess["user_id"] = user.id
            sess["role"] = "escort"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip

        yield client

# === Booking Security Tests ===

def test_booking_without_csrf(seeker_session):
    response = seeker_session.post("/booking/book/4", data={
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"), 
        "duration": "60"
    }, follow_redirects=False)

    assert response.status_code in [400, 403]
    assert b"CSRF" in response.data or b"token is missing" in response.data


def test_create_slot_as_seeker_should_fail(seeker_session):
    response = seeker_session.get("/booking/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]

    response = seeker_session.post("/booking/slots/create", data={
        "csrf_token": csrf_token,
        "start_time": "2025-07-10T12:00",
        "end_time": "2025-07-10T13:00"
    }, follow_redirects=True)

    assert response.status_code in [403, 302, 400]
    assert b"Access denied" in response.data or b"not authorized" in response.data


def test_handle_booking_action_wrong_owner(escort_session):
    response = escort_session.get("/booking/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]

    response = escort_session.post("/booking/handle", data={
        "csrf_token": csrf_token,
        "booking_id": "1000",
        "action": "accept"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Booking not found" in response.data or b"Access denied" in response.data
    