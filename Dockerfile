# CryptVault Dockerfile
# Multi-stage build for optimized image size

# ============================================================================
# Stage 1: Builder - Install dependencies and prepare application
# ============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements/base.txt requirements/base.txt

# Install Python dependencies to a local directory
RUN pip install --no-cache-dir --user -r requirements/base.txt

# ============================================================================
# Stage 2: Runtime - Create minimal runtime image
# ============================================================================
FROM python:3.11-slim

# Set metadata labels
LABEL maintainer="MeridianAlgo Algorithmic Research Team"
LABEL description="CryptVault - Advanced AI-Powered Cryptocurrency Analysis Platform"
LABEL version="4.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CRYPTVAULT_ENV=production

# Create non-root user for security
RUN groupadd -r cryptvault && \
    useradd -r -g cryptvault -u 1000 -m -s /bin/bash cryptvault

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/cryptvault/.local

# Copy application code
COPY --chown=cryptvault:cryptvault cryptvault/ ./cryptvault/
COPY --chown=cryptvault:cryptvault cryptvault_cli.py ./
COPY --chown=cryptvault:cryptvault config/ ./config/
COPY --chown=cryptvault:cryptvault README.md LICENSE ./

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/.cryptvault_predictions && \
    chown -R cryptvault:cryptvault /app/logs /app/data /app/.cryptvault_predictions

# Switch to non-root user
USER cryptvault

# Add local Python packages to PATH
ENV PATH=/home/cryptvault/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import cryptvault; print('OK')" || exit 1

# Set entrypoint
ENTRYPOINT ["python", "cryptvault_cli.py"]

# Default command (can be overridden)
CMD ["--help"]
