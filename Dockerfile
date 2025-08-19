# Multi-stage build for Python microservices
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash simviator
USER simviator
WORKDIR /home/simviator

# Copy requirements and install dependencies
COPY --chown=simviator:simviator requirements.txt .
RUN pip install --user -r requirements.txt

# Copy source code
COPY --chown=simviator:simviator . .

# Add user's local bin to PATH
ENV PATH="/home/simviator/.local/bin:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command (override in docker-compose)
CMD ["python", "launch_services.py"]