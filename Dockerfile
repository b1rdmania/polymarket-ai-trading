# Dockerfile for Polymarket Trading System
# Runs all 3 models + dashboard

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    pydantic \
    python-dotenv \
    pyyaml \
    openai \
    py-clob-client \
    web3

# Install local packages
RUN cd /app/toolkit/execution-engine && pip install -e . || true
RUN cd /app/toolkit/mean-reversion && pip install -e . || true
RUN cd /app/toolkit/polymarket-data && pip install -e . || true
RUN cd /app/toolkit/volatility-alerts && pip install -e . || true

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/data/recordings_conservative \
    /app/data/recordings_moderate /app/data/recordings_aggressive

# Initialize databases
RUN python3 /app/scripts/init_databases.py || true

# Expose dashboard port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command (can be overridden)
CMD ["python3", "api/dashboard_api.py"]
