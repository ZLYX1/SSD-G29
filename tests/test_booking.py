# tests/test_booking.py

import pytest
from app import app as flask_app
from datetime import datetime, timedelta

# === Fixtures with bound User-Agent and IP ===

@pytest.fixture
def seeker_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        fake_ua = "test-agent"
        fake_ip = "127.0.0.1"

        client.environ_base["HTTP_USER_AGENT"] = fake_ua
        client.environ_base["REMOTE_ADDR"] = fake_ip

        with client.session_transaction() as sess:
            sess["user_id"] = 3
            sess["role"] = "seeker"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip

        with flask_app.app_context():
            yield client

@pytest.fixture
def escort_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        fake_ua = "test-agent"
        fake_ip = "127.0.0.1"

        client.environ_base["HTTP_USER_AGENT"] = fake_ua
        client.environ_base["REMOTE_ADDR"] = fake_ip

        with client.session_transaction() as sess:
            sess["user_id"] = 4
            sess["role"] = "escort"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip

        with flask_app.app_context():
            yield client

# === Booking Security Tests ===

'''
def test_booking_without_csrf(seeker_session):
    response = seeker_session.post("/booking/book/4", data={
        "start_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
        "duration": "60"
    }, follow_redirects=False)

    assert response.status_code == 403
    assert b"Invalid CSRF token" in response.data or b"CSRF token is missing" in response.data
'''

def test_create_slot_as_seeker_should_fail(seeker_session):
    response = seeker_session.post("/booking/slots/create", data={
        "csrf_token": "invalid-token",
        "start_time": "2025-07-10T12:00",
        "end_time": "2025-07-10T13:00"
    }, follow_redirects=False)

    assert response.status_code == 403
    assert b"Access denied" in response.data or b"Invalid CSRF token" in response.data


def test_handle_booking_action_wrong_owner(escort_session):
    response = escort_session.post("/booking/handle", data={
        "csrf_token": "invalid-token",
        "booking_id": "1000",
        "action": "accept"
    }, follow_redirects=False)

    assert response.status_code == 403
    assert b"Access denied" in response.data or b"Invalid CSRF token" in response.data

'''
def test_booking_page_filters_user_bookings(seeker_session):
    response = seeker_session.get("/booking/", follow_redirects=False)

    assert response.status_code == 200
    assert b"Booking #" in response.data
    '''
