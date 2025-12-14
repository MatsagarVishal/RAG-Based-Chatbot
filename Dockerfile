# Use official Playwright image
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy code
COPY . .

# Render sets the PORT env var. We must listen on it.
# We use shell expansion to default to 8000 if PORT is not set.
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"
