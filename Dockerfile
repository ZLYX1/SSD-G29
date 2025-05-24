# Use official Python image
FROM python:3.11-slim

# Install netcat (OpenBSD version) for database wait script
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirement and source files.
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code.
COPY . .

# Make sure the entrypoint script is executable.
RUN chmod +x ./entrypoint.sh

# Set environment variable for Flask.
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000 for Flask
EXPOSE 5000

# Run the entrypoint script that waits for the database.
ENTRYPOINT ["./entrypoint.sh"]

# Run the Flask app (Development)
#CMD ["flask", "run"]
# Run the Flask app (Production)
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]