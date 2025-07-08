"""
Pytest configuration and shared fixtures for the Safe Companions test suite.
"""
import os
import pytest
import tempfile
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# Set test environment variables before importing app
# Only override if not already set (for CI/CD compatibility)
if "FLASK_ENV" not in os.environ:
    os.environ["FLASK_ENV"] = "testing"
if "TESTING" not in os.environ:
    os.environ["TESTING"] = "True"
if "FLASK_SECRET_KEY" not in os.environ:
    os.environ["FLASK_SECRET_KEY"] = "test-secret-key-for-testing-only"
if "CSRF_SECRET_KEY" not in os.environ:
    os.environ["CSRF_SECRET_KEY"] = "test-csrf-secret-key-for-testing"

# For local testing, use SQLite; for CI/CD, keep the existing DATABASE_URL
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"  # Use in-memory SQLite for local tests

# Set AWS environment variables if not already set
if "S3_BUCKET_NAME" not in os.environ:
    os.environ["S3_BUCKET_NAME"] = "test-bucket"
if "AWS_ACCESS_KEY_ID" not in os.environ:
    os.environ["AWS_ACCESS_KEY_ID"] = "test-access-key"
if "AWS_SECRET_ACCESS_KEY" not in os.environ:
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret-key"
if "AWS_REGION" not in os.environ:
    os.environ["AWS_REGION"] = "us-east-1"

# Import app after setting environment variables
from app import app as flask_app
from extensions import db
from blueprint.models import User, Profile, Booking, Payment, Report, Rating, Message, TimeSlot

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    # Store original config
    original_config = {}
    config_keys = ['TESTING', 'SECRET_KEY', 'CSRF_SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 
                   'SQLALCHEMY_TRACK_MODIFICATIONS', 'WTF_CSRF_ENABLED']
    
    for key in config_keys:
        if key in flask_app.config:
            original_config[key] = flask_app.config[key]
    
    # Set test configuration
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key-for-testing-only'
    flask_app.config['CSRF_SECRET_KEY'] = 'test-csrf-secret-key-for-testing'
    flask_app.config['WTF_CSRF_ENABLED'] = True  # Keep CSRF enabled for security tests
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Use the DATABASE_URL from environment (set by CI/CD or local default)
    if os.environ.get("DATABASE_URL"):
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
    else:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # For SQLite, create a temporary file; for PostgreSQL, use existing database
    db_fd = None
    if flask_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite://'):
        db_fd, flask_app.config['DATABASE'] = tempfile.mkstemp()
    
    with flask_app.app_context():
        # Create all tables
        db.create_all()
        
        yield flask_app
        
        # Clean up test data
        try:
            # Drop all tables to clean up
            db.drop_all()
        except Exception as e:
            print(f"Warning: Could not drop tables during cleanup: {e}")
    
    # Restore original config
    for key, value in original_config.items():
        flask_app.config[key] = value
    
    # Clean up temporary file for SQLite
    if db_fd is not None:
        os.close(db_fd)
        if 'DATABASE' in flask_app.config:
            try:
                os.unlink(flask_app.config['DATABASE'])
            except FileNotFoundError:
                pass

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def app_context(app):
    """Create an application context."""
    with app.app_context():
        yield

@pytest.fixture(autouse=True)
def clean_database(app):
    """Clean the database before each test."""
    with app.app_context():
        # Clean up in reverse order of dependencies
        Message.query.delete()
        Rating.query.delete() 
        Report.query.delete()
        Payment.query.delete()
        Booking.query.delete()
        TimeSlot.query.delete()
        Profile.query.delete()
        User.query.delete()
        db.session.commit()
        yield
        # Clean up after test
        Message.query.delete()
        Rating.query.delete()
        Report.query.delete() 
        Payment.query.delete()
        Booking.query.delete()
        TimeSlot.query.delete()
        Profile.query.delete()
        User.query.delete()
        db.session.commit()

@pytest.fixture
def test_user(app_context):
    """Create a test user for authentication tests."""
    user = User(
        email="testuser@example.com",
        password_hash=generate_password_hash("TestPassword123"),
        role="seeker",
        gender="Other",
        active=True,
        activate=True,
        deleted=False,
        created_at=datetime.now(timezone.utc),
        password_created_at=datetime.now(timezone.utc)
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_escort(app_context):
    """Create a test escort user."""
    user = User(
        email="testescort@example.com", 
        password_hash=generate_password_hash("TestPassword123"),
        role="escort",
        gender="Female",
        active=True,
        activate=True,
        deleted=False,
        created_at=datetime.now(timezone.utc),
        password_created_at=datetime.now(timezone.utc)
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['role'] = test_user.role
        sess['bound_ua'] = 'test-agent'
        sess['bound_ip'] = '127.0.0.1'
    
    client.environ_base['HTTP_USER_AGENT'] = 'test-agent'
    client.environ_base['REMOTE_ADDR'] = '127.0.0.1'
    
    return client

@pytest.fixture 
def escort_client(client, test_escort):
    """Create an authenticated escort test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_escort.id
        sess['role'] = test_escort.role
        sess['bound_ua'] = 'test-agent'
        sess['bound_ip'] = '127.0.0.1'
    
    client.environ_base['HTTP_USER_AGENT'] = 'test-agent'
    client.environ_base['REMOTE_ADDR'] = '127.0.0.1'
    
    return client
