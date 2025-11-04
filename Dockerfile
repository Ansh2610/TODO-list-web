# Multi-stage build for production FastAPI deployment
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production runtime
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 skilllens && \
    mkdir -p /app && \
    chown -R skilllens:skilllens /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/skilllens/.local

# Copy application code
COPY --chown=skilllens:skilllens . .

# Switch to non-root user
USER skilllens

# Add local bin to PATH
ENV PATH=/home/skilllens/.local/bin:$PATH

# Production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/healthz', timeout=5)"

# Run with gunicorn + uvicorn workers
CMD gunicorn api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120 \
    --graceful-timeout 30 \
    --max-requests 1000 \
    --max-requests-jitter 50
