'''
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
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

def test_report_missing_required_fields(seeker_session):
    response = seeker_session.post("/messaging/report", json={
        # 'reported_id': missing
        'reason': '',  # Empty
        'details': 'Some details'
    })

    assert response.status_code in [400, 422]
    json_data = response.get_json()
    assert json_data is not None, f"Expected JSON but got: {response.data}"
    assert not json_data["success"]
    assert "missing" in json_data["error"].lower()
  '''