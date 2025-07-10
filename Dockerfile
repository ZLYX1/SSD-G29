# Use official Python image
FROM python:3.11-slim

# Create app user and group for security (non-root)
RUN groupadd -r app && useradd -r -g app app

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

# Copy application files with proper ownership and permissions
# Using COPY --chown to set ownership during copy for better security
COPY --chown=app:app app.py entrypoint.sh extensions.py db.py ./
COPY --chown=app:app migrations/ ./migrations/
COPY --chown=app:app config/ ./config/
COPY --chown=app:app entities/ ./entities/
COPY --chown=app:app data_sources/ ./data_sources/
COPY --chown=app:app controllers/ ./controllers/
COPY --chown=app:app utils/ ./utils/
COPY --chown=app:app static/ ./static/
COPY --chown=app:app templates/ ./templates/
COPY --chown=app:app scripts/ ./scripts/
COPY --chown=app:app blueprint/ ./blueprint/

# Create directory for persistent environment variables with proper ownership
RUN mkdir -p /app/persistent && chown app:app /app/persistent

# Set secure file permissions after all files are copied
# This consolidates permission setting and ensures security
RUN chmod 750 ./entrypoint.sh && \
    find ./scripts -name "*.sh" -exec chmod 750 {} \; && \
    find . -type f -name "*.py" -exec chmod 644 {} \; && \
    find . -type d -not -path "./persistent*" -exec chmod 755 {} \; && \
    chmod 750 ./persistent && \
    # Additional security hardening - remove group/other write permissions
    find . -type f -name "*.txt" -exec chmod 644 {} \; && \
    find . -type f -name "*.md" -exec chmod 644 {} \;

# Expose port used by Flask/Gunicorn
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user for security
USER app

# Health check to ensure the application is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Use entrypoint script to handle environment setup and app startup
ENTRYPOINT ["./entrypoint.sh"]