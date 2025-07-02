# Use official Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirement files first for better caching
COPY requirements.txt requirements-prod.txt ./

# Build argument to select requirements file
ARG REQ_FILE=requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r $REQ_FILE

# Copy application code
COPY . .

# Make sure the entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/static/images/profiles

# Expose port used by Flask
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Use entrypoint to handle both dev and prod
ENTRYPOINT ["./entrypoint.sh"]