# Multi-platform Dockerfile for AI Studio Proxy API
# Supports linux/amd64 and linux/arm64

# Stage 1: Build Stage
FROM python:3.10-slim-bookworm AS builder

# Prevent python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VERSION=1.8.3
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /app_builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (without dev dependencies)
RUN poetry install --no-root --no-directory --no-interaction --no-ansi

# Stage 2: Final Stage
FROM python:3.10-slim-bookworm

LABEL maintainer="AI Studio Proxy API contributors"
LABEL description="Multi-platform AI Studio Proxy API"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright \
    CAMOUFOX_CACHE_DIR=/app/.cache/camoufox \
    HOME=/app

WORKDIR /app

# Install system dependencies for Playwright and Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libu2f-udev \
    supervisor \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/bash -d /app appuser

# Copy installed python packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application source code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/logs \
    /app/auth_profiles/active \
    /app/auth_profiles/saved \
    /app/certs \
    /app/.cache/ms-playwright \
    /app/.cache/camoufox \
    && chown -R appuser:appgroup /app

# Install browser binaries and fetch camoufox data
# This part runs during the build on the target architecture, fetching correct binaries
RUN camoufox fetch && \
    python -m playwright install firefox && \
    python scripts/update_browserforge_data.py

# Final environment settings
ENV DEFAULT_FASTAPI_PORT=2048 \
    DEFAULT_CAMOUFOX_PORT=9222 \
    STREAM_PORT=3120 \
    SERVER_LOG_LEVEL=INFO \
    DEBUG_LOGS_ENABLED=false \
    AUTO_CONFIRM_LOGIN=true \
    INTERNAL_CAMOUFOX_PROXY=""

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/app.conf

EXPOSE 2048 3120

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:2048/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/app.conf"]