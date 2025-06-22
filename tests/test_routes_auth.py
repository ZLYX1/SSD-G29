import sys
import os
import pytest

# Set environment variables so app.py can load without error.
# DO CHANGE IT IF TESTING WITH A TEST DATABASE.
os.environ["DATABASE_HOST"] = "localhost"
os.environ["DATABASE_PORT"] = "5432"
os.environ["DATABASE_NAME"] = "testdb"
os.environ["DATABASE_USERNAME"] = "testuser"
os.environ["DATABASE_PASSWORD"] = "testpassword"

# Allow importing app.py from parent directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_register_password_mismatch(client):
    """Test that the register route handles password mismatch correctly"""
    response = client.post(
        "/register",
        data={
            "email": "edwin@example.com",
            "password": "edwin123",
            "confirm_password": "leak",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data
