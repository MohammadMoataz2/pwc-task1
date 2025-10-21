# Single-stage build for PWC Contract Analysis Frontend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies as root
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user from the beginning
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Switch to non-root user immediately
USER appuser

# Set work directory
WORKDIR /app

# Set PATH for user's local bin
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy requirements and install as non-root user
COPY --chown=appuser:appuser src/python/projects/frontend/requirements.txt .
RUN pip install --user -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser src/python/projects/frontend/ /app/

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]