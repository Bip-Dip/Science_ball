# ── Build stage ─────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy dependency manifests
COPY pyproject.toml .

# Install dependencies directly into the system
RUN pip install --no-cache-dir \
    "fastapi>=0.110,<1.0" \
    "uvicorn[standard]>=0.29,<1.0" \
    "pydantic-settings>=2.2,<3.0" \
    "celery>=5.3,<6.0" \
    "redis>=5.0,<6.0" \
    "sqlalchemy[asyncio]>=2.0,<3.0" \
    "asyncpg>=0.29,<1.0", \
    "psycopg2-binary>=2.9,<3.0", \
    "elasticsearch[async]>=8.12,<9.0" \
    "neo4j>=5.18,<6.0" \
    "minio>=7.2,<8.0" \
    "pymupdf>=1.24,<2.0" \
    "python-docx>=1.1,<2.0" \
    "pandas>=2.2,<3.0" \
    "openpyxl>=3.1,<4.0" \
    "python-multipart>=0.0.9", \
    "httpx>=0.27,<1.0"

# Copy application code
COPY app/ ./app/
COPY pyproject.toml .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Default command (overridden in compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
