# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.13-slim AS builder

# Set Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install System Dependencies for building
# build-essential: Compilation tools for C extensions
# libpq-dev: PostgreSQL headers needed to build psycopg2/asyncpg
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry Environment vars
# POETRY_NO_INTERACTION: No interaction mode for automated environments
# POETRY_VIRTUALENVS_IN_PROJECT: Creates .venv in /app directory
# POETRY_CACHE_DIR: Temporary cache location
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies into .venv
# --only=main: Install only production dependencies
# --no-root: Don't install the project itself yet
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# ============================================
# Stage 2: Runtime - Final lightweight image
# ============================================
FROM python:3.13-slim

# Set Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install only runtime dependencies (no build tools)
# libpq5: PostgreSQL client library (much smaller than libpq-dev)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --no-log-init --shell /bin/bash app

# Copy virtual environment from builder stage
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy application code with proper ownership
COPY --chown=app:app . .

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER app

# Add src to PYTHONPATH so imports work correctly
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8000

# Health check for monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/monitoring/health')"

# Use entrypoint script to run migrations before starting app
ENTRYPOINT ["/app/docker-entrypoint.sh"]




