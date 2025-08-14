# Local development Dockerfile for Mockintosh
# Based on cookiecutter-django pattern

ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION}

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        librdkafka-dev \
        pkg-config \
        vim \
        less \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MOCKINTOSH_DATA_DIR=/app/data \
    MOCKINTOSH_DEBUG=true

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements/local.txt

# Create mockintosh user
RUN groupadd -r mockintosh && useradd -r -g mockintosh -s /bin/bash mockintosh

# Copy project
COPY --chown=mockintosh:mockintosh . .

# Install project in development mode
RUN pip install -e . && \
    # Verify installation
    mockintosh --help

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R mockintosh:mockintosh /app

# Switch to non-root user
USER mockintosh

# Expose ports
EXPOSE 8000 8001

# Default command
CMD ["mockintosh", "--help"]
