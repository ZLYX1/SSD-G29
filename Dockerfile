# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and clean up in one layer to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirement files first for better layer caching
COPY requirements.txt requirements-prod.txt ./

# Build argument to select requirements
ARG REQ_FILE=requirements.txt

# Install dependencies based on build arg
RUN pip install --no-cache-dir -r $REQ_FILE && \
    rm -rf /root/.cache/pip

# Copy only essential application code
COPY app.py entrypoint.sh ./
COPY blueprint/ ./blueprint/
COPY config/ ./config/
COPY controllers/ ./controllers/
COPY data_sources/ ./data_sources/
COPY entities/ ./entities/
COPY extensions.py ./
COPY db.py ./
COPY static/ ./static/
COPY templates/ ./templates/
COPY utils/ ./utils/
COPY scripts/ ./scripts/
COPY migrations/ ./migrations/

# Make sure the entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Expose port used by Flask/Gunicorn
EXPOSE 5000

# Set environment variable for Flask.
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Use entrypoint to handle both dev and prod
ENTRYPOINT ["./entrypoint.sh"]