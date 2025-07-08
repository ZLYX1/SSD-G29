import sys
import os
import pytest
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# Ensure app is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app import app as flask_app
from blueprint.models import User
from extensions import db

# === Client Fixture ===

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

# === Seeker Session Fixture ===

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
                email_verified=True,
                phone_verified=True,
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
            sess["username"] = user.email

        yield client

# === Escort Session Fixture ===

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
                email_verified=True,
                phone_verified=True,
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
            sess["username"] = user.email

        yield client

# === Admin Session Fixture ===

@pytest.fixture
def admin_session():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client, flask_app.app_context():
        user = User.query.filter_by(email="testadmin@example.com").first()
        if not user:
            user = User(
                email="testadmin@example.com",
                role="admin",
                gender="Other",
                active=True,
                activate=True,
                deleted=False,
                email_verified=True,
                phone_verified=True,
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
            sess["role"] = "admin"
            sess["bound_ua"] = fake_ua
            sess["bound_ip"] = fake_ip
            sess["username"] = user.email

        yield client

# === Dashboard Access Tests ===

def test_dashboard_access_seeker(seeker_session):
    response = seeker_session.get('/dashboard', follow_redirects=True)
    assert b"Welcome, Seeker!" in response.data

def test_dashboard_access_escort(escort_session):
    response = escort_session.get('/dashboard', follow_redirects=True)
    assert b"Welcome, Escort!" in response.data
    
'''
def test_dashboard_access_admin(admin_session):
    response = admin_session.get('/dashboard', follow_redirects=True)
    assert b"Welcome, Admin!" in response.data
'''

# === Admin Page RBAC Tests ===

def test_admin_access_admin(admin_session):
    response = admin_session.get('/admin', follow_redirects=True)
    assert b"Admin Panel" in response.data

def test_admin_access_seeker(seeker_session):
    response = seeker_session.get('/admin', follow_redirects=False)
    assert response.status_code == 302  # redirected to dashboard
    assert "/dashboard" in response.headers["Location"]

def test_admin_access_escort(escort_session):
    response = escort_session.get('/admin', follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

def test_admin_access_anon(client):
    response = client.get('/admin', follow_redirects=False)
    assert response.status_code in [302, 403]  # unauthenticated redirect or deny
    # optionally: assert response.headers["Location"] == "/auth/" or similar
