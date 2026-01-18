# Dockerfile
# Multi-stage build for smaller, production-ready images

# ============ Build Stage ============
FROM python:3.11-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install dependencies to a virtual env (for copying to runtime)
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install .

# ============ Runtime Stage ============
FROM python:3.11-slim AS runtime

# Python optimizations for containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

WORKDIR /app

# Copy virtual env from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check using Python (curl not available in slim image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
