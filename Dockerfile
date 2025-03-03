FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR $APP_HOME

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser \
    && mkdir -p $APP_HOME \
    && chown -R appuser:appuser $APP_HOME


COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create data directory for logs
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Switch to non-root user
USER appuser

# Set default environment variables
ENV ENV="production" \
    LOG_LEVEL="INFO" \
    APP_VERSION="1.0.0" \
    PROMETHEUS_METRICS="true"

EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "60", "app:app"]
