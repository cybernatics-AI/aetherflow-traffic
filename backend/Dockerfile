# Multi-stage Docker build for AetherFlow Backend
FROM python:3.11.9-slim-bookworm as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Production stage
FROM python:3.11.9-slim-bookworm as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create application directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY .env.example ./

# Create necessary directories
RUN mkdir -p logs data backups && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "aetherflow.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM production as development

# Switch back to root for development tools
USER root

# Install development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Switch back to app user
USER appuser

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "aetherflow.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
