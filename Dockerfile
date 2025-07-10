# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and clean up in one layer to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement files first for better layer caching
COPY requirements.txt requirements-prod.txt ./

# Build argument to select requirements (default to dev requirements)
ARG REQ_FILE=requirements.txt

# Install dependencies based on build arg and clean up cache in one step
# This reduces the image size by not storing cache in intermediate layers
RUN pip install --no-cache-dir -r $REQ_FILE && \
    rm -rf /root/.cache/pip /tmp/* && \
    echo "Installed Python dependencies from $REQ_FILE"

# Copy only essential application code
# First copy the smaller individual files for better layer caching
COPY app.py entrypoint.sh extensions.py db.py ./

# Then copy directories, organized by change frequency
# (most frequently changed directories last for better caching)
COPY migrations/ ./migrations/
COPY config/ ./config/
COPY entities/ ./entities/
COPY data_sources/ ./data_sources/
COPY controllers/ ./controllers/
COPY utils/ ./utils/
COPY static/ ./static/
COPY templates/ ./templates/
COPY scripts/ ./scripts/
COPY blueprint/ ./blueprint/

# Make sure the entrypoint script and all shell scripts are executable with minimal permissions
RUN chmod 750 ./entrypoint.sh && \
    find ./scripts -name "*.sh" -exec chmod 750 {} \;

# Create directory for persistent environment variables with restrictive permissions
RUN mkdir -p /app/persistent && chmod 750 /app/persistent

# Expose port used by Flask/Gunicorn
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check to ensure the application is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Use entrypoint script to handle environment setup and app startup
ENTRYPOINT ["./entrypoint.sh"]