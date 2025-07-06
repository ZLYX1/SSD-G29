#!/bin/bash

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
  # Run Alembic migrations
  echo "🔄 Running database migrations..."
  flask db upgrade || echo "⚠️ Database migrations failed or no migrations found"

  # Initialize database tables if needed (optional safety)
  echo "🔄 Initializing database tables (if any)..."
  python -c "
  
  # Initialize database with sample data if needed
  echo "🔄 Initializing database..."
  python -c "
from app import app
from blueprint.models import db
with app.app_context():
    try:
        db.create_all()
        print('✅ Database tables created successfully')
    except Exception as e:
        print(f'⚠️  Database initialization: {e}')
" || echo "⚠️  Database initialization completed with warnings"
else
  echo "⚠️  Starting without database connection"
fi

# Launch based on environment.
if [ "$FLASK_ENV" = "production" ]; then
  echo "🚀 Starting Gunicorn for production"
  exec gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --keep-alive 2 app:app
else
  echo "🧪 Starting Flask development server"
  exec flask run --host=0.0.0.0 --port=5000 --debug
fi