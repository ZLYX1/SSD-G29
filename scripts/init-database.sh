#!/bin/bash

# This script runs when the PostgreSQL container initializes.
# It will run with postgres user privileges inside the container.
set -e

# Log initialization start
echo "🔧 Database initialization script starting..."

# Ensure variables are set
DB_NAME=${POSTGRES_DB:-ssd_database}
DB_USER=${POSTGRES_USER:-ssd_user}
DB_PASS=${POSTGRES_PASSWORD:-password}

echo "🔧 Setting up user ${DB_USER} with full access to database ${DB_NAME}"

# Create the user and database if they don't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    -- Create the user if it doesn't exist
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
            CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
        END IF;
    END
    \$\$;
    
    -- Create the database if it doesn't exist
    SELECT 'CREATE DATABASE $DB_NAME' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME');
    
    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
    ALTER USER $DB_USER CREATEDB;
EOSQL

# Log completion
echo "✅ Database initialization completed successfully!"
