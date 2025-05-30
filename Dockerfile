# Use official Python image
FROM python:3.11-slim

# Install netcat (OpenBSD version) for database wait script
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirement files.
COPY requirements.txt requirements-prod.txt ./

# Build argument to select requirements.
ARG REQ_FILE=requirements.txt

# Install dependencies based on build arg
RUN pip install --no-cache-dir -r $REQ_FILE

# Copy application code.
COPY . .

# Make sure the entrypoint script is executable.
RUN chmod +x ./entrypoint.sh

# Expose port used by Flask/Gunicorn
EXPOSE 5000

# Set environment variable for Flask.
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Use entrypoint to handle both dev and prod
ENTRYPOINT ["./entrypoint.sh"]