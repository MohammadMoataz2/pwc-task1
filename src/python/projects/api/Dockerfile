# Single-stage build for PWC Contract Analysis API
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies as root
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user from the beginning
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Switch to non-root user immediately
USER appuser

# Set work directory            
WORKDIR /app

# Set PATH for user's local bin and PYTHONPATH for shared library
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app/libs:$PYTHONPATH

# Copy requirements and install as non-root user
COPY --chown=appuser:appuser src/python/projects/api/requirements.txt .
RUN pip install --user -r requirements.txt

# Copy shared library
COPY --chown=appuser:appuser src/python/libs/pwc /app/libs/pwc

# Copy application code
COPY --chown=appuser:appuser src/python/projects/api/api /app/api

# Create storage directory (as non-root user)
RUN mkdir -p /app/storage

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]