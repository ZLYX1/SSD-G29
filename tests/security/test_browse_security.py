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

@pytest.fixture
def escort_user(app_context):
    """Create an escort user for testing."""
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
    return user

@pytest.fixture
def escort_session(client, escort_user):
    """Create an authenticated escort session."""
    with client.session_transaction() as sess:
        sess["user_id"] = escort_user.id
        sess["role"] = "escort"
        sess["bound_ua"] = "test-agent"
        sess["bound_ip"] = "127.0.0.1"

    client.environ_base["HTTP_USER_AGENT"] = "test-agent"
    client.environ_base["REMOTE_ADDR"] = "127.0.0.1"
    
    return client

# === Test Cases ===

def test_access_browse_without_login(client):
    response = client.get('/browse/browse')
    assert response.status_code == 302

def test_cache_poisoning_attempt(escort_session):
    dangerous_input = '<script>alert("poison")</script>'
    response = escort_session.get(f'/browse/browse?min_age={dangerous_input}')
    assert dangerous_input.encode() not in response.data
