# Single-stage build for PWC Contract Analysis Frontend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1



# Set work directory
WORKDIR /app

# Set PATH for user's local bin
ENV PATH=/home/appuser/.local/bin:$PATH
# Set PATH for user's local bin and PYTHONPATH for shared library
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app/libs:$PYTHONPATH

# Copy requirements and install as non-root user
COPY  src/python/projects/frontend/requirements.txt .
COPY src/python/libs/pwc/requirements.txt ./pwc_requirements.txt

RUN pip install  -r requirements.txt && \
    pip install  -r pwc_requirements.txt
# Copy application code
COPY  src/python/projects/frontend/ /app/
COPY src/python/libs/pwc /app/libs/pwc

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]