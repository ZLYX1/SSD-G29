#!/bin/sh

# Wait until PostgreSQL is accepting connections.
echo "⏳ Waiting for PostgreSQL at db:5432..."
while ! nc -z db 5432; do
  sleep 1
done

echo "✅ PostgreSQL is up - starting Flask app"
exec flask run --host=0.0.0.0