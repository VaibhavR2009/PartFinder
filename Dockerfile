# ============================================================
# PartFinder — Dockerfile
#
# Multi-stage build:
#   Stage 1 (builder):  Install Python deps + build React app
#   Stage 2 (runtime):  Minimal Python runtime image
#
# Single container strategy for Cloud Run:
#   The MCP server is embedded in the FastAPI process via
#   EMBED_MCP=true (see api/main.py). This avoids needing a
#   second Cloud Run service and simplifies deployment.
#   For local dev, use docker-compose.yml which runs the MCP
#   server as a separate service for easier debugging.
#
# Usage:
#   docker build -t partfinder .
#   docker run -p 8000:8000 \
#     -e GOOGLE_API_KEY=... \
#     -e SERPAPI_KEY=... \
#     -e EMBED_MCP=true \
#     partfinder
# ============================================================

# ---------- Stage 1: Python dependencies ----------
FROM python:3.12-slim AS python-deps

WORKDIR /app

# Install system dependencies needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Stage 2: Node build (React frontend) ----------
FROM node:20-slim AS frontend-build

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install npm dependencies
RUN npm ci --prefer-offline 2>/dev/null || npm install

# Copy frontend source
COPY frontend/ .

# Build production bundle
RUN npm run build

# ---------- Stage 3: Production runtime ----------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed Python packages from python-deps stage
COPY --from=python-deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy application source
COPY agents/ ./agents/
COPY mcp_server/ ./mcp_server/
COPY api/ ./api/

# Copy built frontend into a static directory
# The FastAPI app serves static files from /app/static/
COPY --from=frontend-build /frontend/dist ./static/

# Copy startup script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# ⚠️  SECURITY: No API keys baked into the image.
# Pass secrets at runtime via environment variables or a secret manager.
# Cloud Run: use Secret Manager references in the service configuration.

# Expose the single port
EXPOSE 8000

# Serve static files and run backend on the same port
ENV EMBED_MCP=true
ENV BACKEND_PORT=8000

CMD ["./docker-entrypoint.sh"]
