
# Set the Flask app environment variable
export FLASK_APP=app.py  # (On Windows, use: set FLASK_APP=app.py)

# 1. Initialize the migrations directory
flask db init

# 2. Create the first migration script based on your models.py
flask db migrate -m "Initial migration with all models"

# 3. Apply the migration to your PostgreSQL database
flask db upgrade

flask seed

flask run

# Seeding process

# (Set FLASK_APP if you haven't already)
# export FLASK_APP=app.py
flask db upgrade

flask seed
