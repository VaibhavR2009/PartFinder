#!/bin/sh
# ============================================================
# PartFinder — Docker Entrypoint
# Starts the FastAPI backend (with embedded MCP in Cloud Run mode)
# and optionally serves the React static build.
# ============================================================
set -e

echo "Starting PartFinder backend on port ${BACKEND_PORT:-8000} ..."
echo "Demo mode: ${DEMO_MODE:-false}"
echo "Embedded MCP: ${EMBED_MCP:-false}"

exec uvicorn api.main:app \
    --host 0.0.0.0 \
    --port "${BACKEND_PORT:-8000}" \
    --workers 1
