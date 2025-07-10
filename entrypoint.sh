#!/bin/bash

# Load persisted environment variables if they exist
PERSIST_FILE="/app/persistent/env.sh"
if [ -f "${PERSIST_FILE}" ]; then
  echo "🔄 Loading persisted environment variables from ${PERSIST_FILE}"
  source "${PERSIST_FILE}"
  echo "✅ Environment variables loaded successfully"
else
  echo "ℹ️ No persisted environment variables found"
fi

# Check and set critical environment variables
# This ensures the application works even if CI/CD overwrites .env.production with empty values

# Generate a random secret key if not set
if [ -z "$FLASK_SECRET_KEY" ]; then
  echo "⚠️ No FLASK_SECRET_KEY environment variable found, generating a random one"
  export FLASK_SECRET_KEY=$(openssl rand -hex 32)
  echo "✅ Generated secret key: ${FLASK_SECRET_KEY:0:8}..."
fi

# Set CSRF secret key if not set
if [ -z "$CSRF_SECRET_KEY" ]; then
  echo "⚠️ No CSRF_SECRET_KEY environment variable found, generating a random one"
  export CSRF_SECRET_KEY=$(openssl rand -hex 32)
  echo "✅ Generated CSRF key: ${CSRF_SECRET_KEY:0:8}..."
fi

# Set default database password if empty
if [ -z "$DATABASE_PASSWORD" ]; then
  echo "⚠️ No DATABASE_PASSWORD found, setting a default for production"
  export DATABASE_PASSWORD="ssd_production_password"
  # Also update the DATABASE_URL to include the password
  if [[ "$DATABASE_URL" == *":@"* ]]; then
    export DATABASE_URL=${DATABASE_URL/:@/:$DATABASE_PASSWORD@}
    echo "✅ Updated DATABASE_URL with password"
  fi
fi

# Set AWS region if empty
if [ -z "$AWS_REGION" ]; then
  echo "⚠️ No AWS_REGION found, defaulting to us-east-1"
  export AWS_REGION="us-east-1"
fi

# Check if we have AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "⚠️ AWS credentials not found. Email verification will not work."
fi

# Set SES sender if empty
if [ -z "$SES_SENDER_EMAIL" ]; then
  echo "⚠️ No SES_SENDER_EMAIL found, defaulting to a placeholder"
  export SES_SENDER_EMAIL="Safe Companion <noreply@example.com>"
fi

# Validate required environment variables
if [ -z "$SITEKEY" ] || [ -z "$RECAPTCHA_SECRET_KEY" ]; then
  echo "❌ ERROR: reCAPTCHA keys not found in environment variables."
  echo "Please ensure SITEKEY and RECAPTCHA_SECRET_KEY are set in your .env file."
  exit 1
fi

# Wait until PostgreSQL is accepting connections.
echo "⏳ Waiting for PostgreSQL at db:5432..."
max_attempts=30
attempt=0

while ! nc -z db 5432; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "❌ Failed to connect to PostgreSQL after $max_attempts attempts"
    echo "🔄 Starting without database connection..."
    break
  fi
  echo "🔄 Attempt $attempt/$max_attempts - PostgreSQL not ready, waiting..."
  sleep 2
done

if nc -z db 5432; then
  echo "✅ PostgreSQL is up and running!"
  
  # Check if the PostgreSQL user and database exist, create if they don't
  echo "🔄 Checking PostgreSQL user and database..."
  
  # Use the postgres user to check if our user exists
  export PGPASSWORD=${POSTGRES_PASSWORD:-postgres}
  
  if ! psql -h db -U postgres -c "\du" | grep -q "${DATABASE_USERNAME:-ssd_user}"; then
    echo "🔧 Creating PostgreSQL user '${DATABASE_USERNAME:-ssd_user}'..."
    psql -h db -U postgres -c "CREATE USER ${DATABASE_USERNAME:-ssd_user} WITH PASSWORD '${DATABASE_PASSWORD:-ssd_production_password}';" || echo "⚠️ Failed to create user"
    echo "✅ PostgreSQL user created"
  else
    echo "✅ PostgreSQL user already exists"
  fi
  
  # Check if our database exists
  if ! psql -h db -U postgres -c "\l" | grep -q "${DATABASE_NAME:-ssd_database}"; then
    echo "🔧 Creating PostgreSQL database '${DATABASE_NAME:-ssd_database}'..."
    psql -h db -U postgres -c "CREATE DATABASE ${DATABASE_NAME:-ssd_database} OWNER ${DATABASE_USERNAME:-ssd_user};" || echo "⚠️ Failed to create database"
    echo "✅ PostgreSQL database created"
  else
    echo "✅ PostgreSQL database already exists"
  fi
  
  # Grant privileges to the user
  echo "🔧 Ensuring database privileges..."
  psql -h db -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${DATABASE_NAME:-ssd_database} TO ${DATABASE_USERNAME:-ssd_user};" || echo "⚠️ Failed to grant privileges"
  
  # Now switch to our app's database user for further operations
  export PGPASSWORD=${DATABASE_PASSWORD:-ssd_production_password}
  
  # Check if database tables exist, if not create them
  echo "🔄 Checking database schema..."
  python -c "
import os
os.environ['FLASK_SECRET_KEY'] = '${FLASK_SECRET_KEY}'
os.environ['CSRF_SECRET_KEY'] = '${CSRF_SECRET_KEY}'
from app import app, db
with app.app_context():
    try:
        # Try to query a table to see if it exists
        from blueprint.models import User
        User.query.first()
        print('📋 Database tables already exist')
    except Exception as e:
        print(f'🔧 Creating database tables... ({str(e)})')
        db.create_all()
        print('✅ Database tables created successfully')
" || echo "⚠️ Database schema check failed"
  
  # Run Alembic migrations
  echo "🔄 Running database migrations..."
  FLASK_SECRET_KEY="${FLASK_SECRET_KEY}" CSRF_SECRET_KEY="${CSRF_SECRET_KEY}" flask db upgrade || echo "⚠️ Database migrations failed or no migrations found"
  
  # Initialize database with sample data if needed
  echo "🔄 Database initialization complete"
fi

# Persist environment variables for future use
if [ "$FLASK_ENV" = "production" ]; then
  echo "🔄 Persisting environment variables for future deployments..."
  bash /app/scripts/persist_env.sh
fi

# Launch based on environment.
# Make sure all environment variables are passed to the Flask application
if [ "$FLASK_ENV" = "production" ]; then
  echo "🚀 Starting Gunicorn for production with all environment variables set"
  # Export all environment variables to ensure they're available to Gunicorn
  exec env \
    FLASK_SECRET_KEY="${FLASK_SECRET_KEY}" \
    CSRF_SECRET_KEY="${CSRF_SECRET_KEY}" \
    DATABASE_URL="${DATABASE_URL}" \
    DATABASE_USERNAME="${DATABASE_USERNAME}" \
    DATABASE_PASSWORD="${DATABASE_PASSWORD}" \
    DATABASE_NAME="${DATABASE_NAME}" \
    AWS_REGION="${AWS_REGION}" \
    AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    S3_BUCKET_NAME="${S3_BUCKET_NAME}" \
    SES_SENDER_EMAIL="${SES_SENDER_EMAIL}" \
    SITEKEY="${SITEKEY}" \
    RECAPTCHA_SECRET_KEY="${RECAPTCHA_SECRET_KEY}" \
    gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --keep-alive 2 app:app
else
  echo "🧪 Starting Flask development server with all environment variables set"
  # Export all environment variables to ensure they're available to Flask
  exec env \
    FLASK_SECRET_KEY="${FLASK_SECRET_KEY}" \
    CSRF_SECRET_KEY="${CSRF_SECRET_KEY}" \
    DATABASE_URL="${DATABASE_URL}" \
    DATABASE_USERNAME="${DATABASE_USERNAME}" \
    DATABASE_PASSWORD="${DATABASE_PASSWORD}" \
    DATABASE_NAME="${DATABASE_NAME}" \
    AWS_REGION="${AWS_REGION}" \
    AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    S3_BUCKET_NAME="${S3_BUCKET_NAME}" \
    SES_SENDER_EMAIL="${SES_SENDER_EMAIL}" \
    SITEKEY="${SITEKEY}" \
    RECAPTCHA_SECRET_KEY="${RECAPTCHA_SECRET_KEY}" \
    flask run --host=0.0.0.0 --port=5000 --debug
fi