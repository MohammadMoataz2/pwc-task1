# Single-stage build for PWC Contract Analysis API
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
COPY src/python/projects/api/requirements.txt ./api_requirements.txt
COPY src/python/libs/pwc/requirements.txt ./pwc_requirements.txt

# Install both API and PWC library requirements
RUN pip install  -r api_requirements.txt && \
    pip install  -r pwc_requirements.txt

# Copy shared library
COPY  src/python/libs/pwc /app/libs/pwc

# Copy application code
COPY  src/python/projects/api/api /app/api

# Create storage directory (as non-root user)
RUN mkdir  /app/storage

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]