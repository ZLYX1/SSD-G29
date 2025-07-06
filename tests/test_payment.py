# tests/test_payment.py

import pytest
from app import app as flask_app
from blueprint.payment import generate_payment_token, mark_token_used
from datetime import datetime, timedelta

# === Fixtures ===

@pytest.fixture
def seeker_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        fake_ua = "test-agent"
        fake_ip = "127.0.0.1"

        client.environ_base["HTTP_USER_AGENT"] = fake_ua
        client.environ_base["REMOTE_ADDR"] = fake_ip

        with client.session_transaction() as sess:
            sess["user_id"] = 3  # testuser@example.com
            sess["role"] = "seeker"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip

        with flask_app.app_context():
            yield client

# === Payment Security Tests ===

def test_invalid_payment_token(seeker_session):
    response = seeker_session.get("/payment/pay?token=invalid-token", follow_redirects=False)
    assert response.status_code == 403
    assert b"Invalid or expired payment token" in response.data

'''
def test_payment_initiate_requires_confirmed_booking(seeker_session):
    # Replace with an unconfirmed booking ID owned by user_id=3
    response = seeker_session.get("/payment/initiate/10", follow_redirects=False)
    assert response.status_code == 403
    assert b"not in a payable state" in response.data
    '''

'''
def test_reuse_token_should_fail(seeker_session):
    # Replace 999 with an actual confirmed booking owned by seeker ID 3
    valid_booking_id = 999  # <-- Replace this with real booking ID

    token = generate_payment_token(user_id=3, booking_id=valid_booking_id)

    # Simulate first use (success)
    response1 = seeker_session.post("/payment/pay", data={
        "csrf_token": "valid-token",  # Replace with real token if CSRF enforced
        "token": token,
        "card_number": "1234567812345678",
        "expiry": "12/25",
        "cvv": "123"
    }, follow_redirects=False)

    # Simulate marking the token as used
    mark_token_used(token)

    # Simulate reuse attempt
    response2 = seeker_session.get(f"/payment/pay?token={token}", follow_redirects=False)
    assert response2.status_code == 403
    assert b"Invalid or expired payment token" in response2.data
    '''
