# Single-stage build for resource-constrained environments (EC2 20GB)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements-docker.txt .
# --no-cache-dir is crucial to save space
RUN pip install --no-cache-dir -r requirements-docker.txt

# Install only Chromium to save space
RUN playwright install chromium --with-deps

# Copy application code
COPY . .

# Set permissions for UID 1000 (exists in base image as pwuser)
RUN chown -R 1000:1000 /app && \
    mkdir -p /tmp/rag_cache && \
    chown -R 1000:1000 /tmp/rag_cache

# Switch to non-root user (UID 1000)
USER 1000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"

