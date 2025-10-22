# Single-stage build for PWC Contract Analysis Worker
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1




# Set work directory
WORKDIR /app

# Set PATH for user's local bin and PYTHONPATH for shared library
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app/libs:$PYTHONPATH

# Copy requirements files
COPY  src/python/projects/analyze_contracts/requirements.txt ./worker_requirements.txt
COPY  src/python/libs/pwc/requirements.txt ./pwc_requirements.txt

# Install both worker and PWC library requirements
RUN pip install  -r worker_requirements.txt && \
    pip install  -r pwc_requirements.txt

# Copy shared library
COPY src/python/libs/pwc /app/libs/pwc

# Copy application code
COPY  src/python/projects/analyze_contracts/analyze_contracts /app/analyze_contracts

# Create storage directory (as non-root user)
RUN mkdir /app/storage

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD celery -A analyze_contracts.main inspect ping || exit 1

# Run the Celery worker
CMD ["celery", "-A", "analyze_contracts.main", "worker", "--loglevel=info", "--concurrency=2"]