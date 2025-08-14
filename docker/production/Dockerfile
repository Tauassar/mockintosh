# Production Dockerfile for Mockintosh
# Based on cookiecutter-django pattern

ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION} as python

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        librdkafka-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies stage
FROM python as python-deps

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements/production.txt

# Production stage
FROM python as production

# Install runtime dependencies only
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        librdkafka1 \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && update-ca-certificates

# Create mockintosh user
RUN groupadd -r mockintosh && useradd -r -g mockintosh -s /bin/false mockintosh

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PYTHONHASHSEED=random \
    MOCKINTOSH_DATA_DIR=/app/data \
    MOCKINTOSH_DEBUG=false

# Set work directory
WORKDIR /app

# Copy Python dependencies from python-deps stage
COPY --from=python-deps /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=python-deps /usr/local/bin/ /usr/local/bin/

# Copy project
COPY --chown=mockintosh:mockintosh . .

# Install project
RUN pip install . && \
    # Verify installation
    mockintosh --help && \
    # Clean up pip cache and remove unnecessary files
    pip cache purge && \
    find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + && \
    find /usr/local/lib/python3.11/site-packages -type d -name "*.dist-info" -exec rm -rf {} + && \
    find /usr/local/lib/python3.11/site-packages -type d -name "tests" -exec rm -rf {} + && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.pyc" -delete

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R mockintosh:mockintosh /app

# Switch to non-root user
USER mockintosh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/__admin || exit 1

# Expose ports
EXPOSE 8000 8001

# Default command
ENTRYPOINT ["mockintosh"]
CMD ["--help"]
