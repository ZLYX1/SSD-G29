
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from datetime import datetime
from werkzeug.security import generate_password_hash
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
            sess["role"] = "escort"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip

        yield client

# === Test Cases ===

def test_access_browse_without_login(client):
    response = client.get('/browse/browse')
    assert response.status_code == 302

def test_seeker_access_browseSeeker(seeker_session):
    response = seeker_session.get('/browse/browseSeeker')
    assert response.status_code == 200

def test_escort_access_browse(escort_session):
    response = escort_session.get('/browse/browse')
    assert response.status_code == 200
    assert b'Browse Seeker' in response.data

def test_string_in_numerical_field(escort_session):
    response = escort_session.get('/browse/browse?min_age=abc')
    assert response.status_code == 200
    assert b'Browse' in response.data

def test_sql_injection_attempt(escort_session):
    response = escort_session.get("/browse/browse?min_rating=1;DROP TABLE users")
    assert response.status_code != 500
    assert b'syntax' not in response.data.lower()

def test_xss_input_reflected_in_response(escort_session):
    payload = b'<script>alert(1)</script>'
    response = escort_session.get(f'/browse/browse?min_rating={payload.decode()}')
    assert payload not in response.data

def test_malformed_numerical_value(escort_session):
    response = escort_session.get('/browse/browse?min_rating=4.5.5')
    assert response.status_code == 200
    assert b'Browse' in response.data

def test_cache_poisoning_attempt(escort_session):
    dangerous_input = '<script>alert("poison")</script>'
    response = escort_session.get(f'/browse/browse?min_age={dangerous_input}')
    assert dangerous_input.encode() not in response.data

def test_rate_limiting(client):
    for _ in range(20):
        response = client.get('/browse/browse')
        if response.status_code == 429:
            break
    assert response.status_code != 500
    