import sys
import os
import pytest
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone  
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app import app as flask_app
from blueprint.models import User, Booking, Message, TimeSlot
from extensions import db

# === Fixtures ===

@pytest.fixture
def seeker_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client, flask_app.app_context():
        user = User.query.filter_by(email="testseeker@example.com").first()
        if user:
            Message.query.filter_by(sender_id=user.id).delete()
            Booking.query.filter_by(seeker_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()

        new_user = User(
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
        db.session.add(new_user)
        db.session.commit()

        client.environ_base["HTTP_USER_AGENT"] = "test-agent"
        client.environ_base["REMOTE_ADDR"] = "127.0.0.1"

        with client.session_transaction() as sess:
            sess["user_id"] = new_user.id
            sess["role"] = "seeker"
            sess["bound_ua"] = "test-agent"
            sess["bound_ip"] = "127.0.0.1"

        yield client, new_user

@pytest.fixture
def escort_user():
    with flask_app.app_context():
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
        return user.id

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

        client.environ_base["HTTP_USER_AGENT"] = "test-agent"
        client.environ_base["REMOTE_ADDR"] = "127.0.0.1"
        with client.session_transaction() as sess:
            sess["user_id"] = user.id
            sess["role"] = "escort"
            sess["bound_ua"] = "test-agent"
            sess["bound_ip"] = "127.0.0.1"

        yield client

# === Helper ===

def create_test_slot(escort_id):
    now = datetime.now(timezone.utc)
    slot = TimeSlot(
        user_id=escort_id,
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=1)
    )
    db.session.add(slot)
    db.session.flush()  
    db.session.refresh(slot) 
    db.session.commit()
    assert slot.id is not None and isinstance(slot.id, int), "Slot ID was not generated"
    return slot.id

# === Tests ===

def test_create_slot_as_seeker_should_fail(seeker_session):
    client, _ = seeker_session
    response = client.get("/booking/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]

    response = client.post("/booking/slots/create", data={
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