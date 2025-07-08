'''
import sys
import os
import pytest
# Ensure app module is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app import app as flask_app
from blueprint.payment import generate_payment_token, mark_token_used
from blueprint.models import Booking, User
from extensions import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash



# === Fixtures ===

@pytest.fixture
def seeker_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client, flask_app.app_context():
        # Create dynamic test seeker
        seeker = User.query.filter_by(email="testseeker@example.com").first()
        if seeker:
            Booking.query.filter_by(seeker_id=seeker.id).delete()
            db.session.delete(seeker)
            db.session.commit()

        seeker = User(
            email="testseeker@example.com",
            role="seeker",
            active=True,
            gender="Other",
            password_hash=generate_password_hash("ValidPass123")
        )
        db.session.add(seeker)
        db.session.commit()

        fake_ua = "test-agent"
        fake_ip = "127.0.0.1"

        client.environ_base["HTTP_USER_AGENT"] = fake_ua
        client.environ_base["REMOTE_ADDR"] = fake_ip

        with client.session_transaction() as sess:
            sess["user_id"] = seeker.id
            sess["role"] = "seeker"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip

        yield client, seeker  # Return both the client and the user


# === Helpers ===

def create_test_booking(seeker_id, escort_id, status="Confirmed"):
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking = Booking(
        seeker_id=seeker_id,
        escort_id=escort_id,
        start_time=start_time,
        end_time=end_time,
        status=status
    )
    db.session.add(booking)
    db.session.commit()
    return booking.id


def ensure_test_escort():
    escort = User.query.filter_by(email="testescort@example.com").first()
    if not escort:
        escort = User(
            email="testescort@example.com",
            role="escort",
            active=True,
            gender="Male"
        )
        escort.set_password("test1234")
        db.session.add(escort)
        db.session.commit()
    return escort.id


# === Tests ===

def test_invalid_payment_token(seeker_session):
    client, _ = seeker_session
    response = client.get("/payment/pay?token=invalid-token", follow_redirects=False)
    assert response.status_code == 403
    assert b"Invalid or expired payment token" in response.data


def test_payment_initiate_requires_confirmed_booking(seeker_session):
    client, seeker = seeker_session
    with client.application.app_context():
        escort_id = ensure_test_escort()
        booking_id = create_test_booking(seeker_id=seeker.id, escort_id=escort_id, status="Pending")

    response = client.get(f"/payment/initiate/{booking_id}", follow_redirects=False)
    assert response.status_code == 403
    assert b"not in a payable state" in response.data


def test_reuse_token_should_fail(seeker_session):
    client, seeker = seeker_session
    with client.application.app_context():
        escort_id = ensure_test_escort()
        booking_id = create_test_booking(seeker_id=seeker.id, escort_id=escort_id, status="Confirmed")

        token = generate_payment_token(user_id=seeker.id, booking_id=booking_id)

    # Simulate first usage (assume success)
    response1 = client.post("/payment/pay", data={
        "csrf_token": "valid-token",  # Update if CSRF is enforced
        "token": token,
        "card_number": "1234567812345678",
        "expiry": "12/25",
        "cvv": "123"
    }, follow_redirects=False)

    # Mark token as used
    mark_token_used(token)

    # Simulate reuse
    response2 = client.get(f"/payment/pay?token={token}", follow_redirects=False)
    assert response2.status_code == 403
    assert b"Invalid or expired payment token" in response2.data
  '''