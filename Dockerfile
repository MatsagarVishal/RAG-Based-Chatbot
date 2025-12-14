# Multi-stage build for optimized image size
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy as builder

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Install only Chromium browser (not all browsers)
RUN playwright install chromium --with-deps

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /tmp/rag_cache && \
    chown -R appuser:appuser /tmp/rag_cache

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Expose port
EXPOSE 8000

# Start application
# Use PORT env var with fallback to 8000
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"

