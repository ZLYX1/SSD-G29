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

## others

dropdb safe_companions_db
createdb safe_companions_db
flask db upgrade
flask seed
db.session.commit()

## When there is changes to DB. Eg: add modify or edit

flask db migrate -m "Add Message"
flask db upgrade

## Env for Flask secret key and WTF_CSRF
Type the 2 liens below and save in env

### Generate Flask SECRET_KEY and Generate WTF_CSRF_SECRET_KEY

openssl rand -hex 32
