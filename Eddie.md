## Set the Flask app environment variable

export FLASK_APP=app.py  # (On Windows, use: set FLASK_APP=app.py)

1. Initialize the migrations directory
flask db init

2. Create the first migration script based on your models.py
flask db migrate -m "Initial migration with all models"

3. Apply the migration to your PostgreSQL database
flask db upgrade

flask seed

flask run

## Seeding process


(Set FLASK_APP if you haven't already)
export FLASK_APP=app.py
flask db upgrade

flask seed

## Check DB

brew services start postgresql

## start

watchmedo auto-restart --patterns="*.py" --recursive -- python3 app.py

## populate data

flask seed

## if changes to model

flask db migrate -m "Message"
flask db upgrade

## drop db and restart

Force disconnect all sessions from the database:
psql -U postgres -d postgres

In postgres:
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'safe_companions_db'
  AND pid <> pg_backend_pid();
\q

Recreate the database:
dropdb safe_companions_db
createdb safe_companions_db

initialize migrations:
flask db init

Create and apply migratons:
flask db migrate -m "Add report table"
flask db upgrade

Seed the database:
flask seed

Commit:
db.session.commit()

## When there is changes to DB (model). Eg: add modify or edit

After modifying your model srun:
flask db migrate -m "Add Message"

Run this to update your actual PostgreSQL or SQLite database:
flask db upgrade

## Env for Flask secret key and WTF_CSRF
Type the 2 liens below and save in env

### Generate Flask SECRET_KEY and Generate WTF_CSRF_SECRET_KEY

openssl rand -hex 32

### Runinng

pip install watchdog
flask run --reload --debugger --with-threads


### Reseting db:

drop:
flask reset-db

seed:
flask seed

run:
flask run --reload --debugger --with-threads


### Test script

pytest -s tests/EddieTestScripts/testscript.py