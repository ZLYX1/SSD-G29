#!/bin/sh

# Wait until PostgreSQL is accepting connections.
echo "⏳ Waiting for PostgreSQL at db:5432..."
while ! nc -z db 5432; do
  sleep 1
done

echo "✅ PostgreSQL is up"

# Launch based on environment.
if [ "$FLASK_ENV" = "production" ]; then
  echo "🚀 Starting Gunicorn"
  exec gunicorn -w 4 -b 0.0.0.0:5000 app:app
else
  echo "🧪 Starting Flask development server"
  exec flask run --host=0.0.0.0
fi