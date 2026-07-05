"""
PartFinder — FastAPI Backend
==============================
This is the HTTP layer between the React frontend and the ADK agent pipeline.

Endpoints:
  POST /api/run   — Accepts a project request, streams progress events via SSE.
  GET  /api/health — Health check for Docker/Cloud Run readiness probe.

== SSE Streaming Design ==
Using Server-Sent Events (SSE) rather than WebSockets because:
  • SSE is unidirectional (server → client) which matches our use case.
  • SSE works through most proxies and firewalls without special config.
  • The browser's EventSource API handles reconnection automatically.
  • No WebSocket upgrade handshake needed — simpler to deploy on Cloud Run.

Each SSE event is a JSON-serialized ProgressEvent:
  data: {"stage": "...", "status": "...", "message": "...", "data": {...}}

== Deployment Note ==
For Cloud Run single-container deployment, the MCP server (FastMCP) is
mounted as an ASGI sub-application at /mcp. This means agents can reach
the MCP server at http://localhost:{PORT}/mcp/sse without a second
container. See README.md "Cloud Run Deployment" section.

For local development, run the MCP server separately (see docker-compose.yml).
"""

import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables before ADK / agent imports
load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api.models import ProjectRequest, HealthResponse, ProgressEvent
from api.security import sanitize_description
from agents.config import GEMINI_MODEL, MCP_SERVER_URL
from agents.orchestrator import run_pipeline

# Load environment variables from .env file if present
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Determine if we're in embedded MCP mode (Cloud Run single container)
# or standalone mode (local dev with separate MCP process).
# ------------------------------------------------------------------
EMBED_MCP: bool = os.environ.get("EMBED_MCP", "false").lower() == "true"
DEMO_MODE: bool = os.environ.get("DEMO_MODE", "false").lower() == "true"


# ==================================================================
# Application lifespan — mount MCP server if embedded
# ==================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown lifecycle hook.
    In embedded mode, starts the FastMCP SSE server within the same
    process so only one Cloud Run service is needed.
    """
    if EMBED_MCP:
        logger.info("Starting embedded MCP server at /mcp ...")
        mcp_context = None
        try:
            from mcp_server.server import mcp_app_embedded
            # Mount the MCP ASGI app at /mcp
            app.mount("/mcp", mcp_app_embedded)
            logger.info("MCP server mounted at /mcp")
            mcp_context = mcp_app_embedded.router.lifespan_context(app)
        except Exception as e:
            logger.error("Failed to start embedded MCP server: %s", e)
            # Non-fatal in demo mode
            if not DEMO_MODE:
                raise
        
        if mcp_context:
            async with mcp_context:
                yield
        else:
            yield
    else:
        yield
    logger.info("Shutdown complete.")


# ==================================================================
# FastAPI app
# ==================================================================

app = FastAPI(
    title="PartFinder API",
    description="Multi-agent DIY parts-sourcing assistant backend.",
    version="1.0.0",
    lifespan=lifespan,
)

# ------------------------------------------------------------------
# CORS — restrict to frontend origin in production.
# In dev, allow localhost:5173 (Vite default).
# ------------------------------------------------------------------
ALLOWED_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ==================================================================
# Health check endpoint
# ==================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Readiness probe for Docker / Cloud Run.
    Returns 200 if the service is up.
    """
    return HealthResponse(
        status="ok",
        demo_mode=DEMO_MODE,
        model=GEMINI_MODEL,
    )


# ==================================================================
# Main pipeline endpoint — SSE streaming
# ==================================================================

@app.post("/api/run")
async def run_partfinder(request: ProjectRequest):
    """
    Accept a project request and stream progress events via SSE.

    The response is a text/event-stream. Each event is a JSON object:
      data: {"stage": "...", "status": "...", "message": "...", "data": {...}}\n\n

    Stages in order:
      feasibility → sourcing → verification → compiler → complete

    If the project is infeasible, the stream ends after the feasibility
    stage with status "infeasible" — no sourcing/verification calls happen.
    """
    # MCP Connectivity check
    if not DEMO_MODE:
        import httpx
        from fastapi import HTTPException
        try:
            async with httpx.AsyncClient() as client:
                health_url = f"{MCP_SERVER_URL.rstrip('/')}/health"
                await client.get(health_url, timeout=3.0)
        except Exception as e:
            logger.error("Startup check failed - MCP server unreachable: %s", e)
            raise HTTPException(status_code=503, detail=f"MCP server unreachable at {MCP_SERVER_URL} - check transport config")

    # Sanitize the free-text description (supplementary to Pydantic validation)
    sanitized = request.to_agent_dict()
    sanitized["description"] = sanitize_description(sanitized["description"])

    async def event_stream():
        """
        Generator that runs the agent pipeline and yields SSE-formatted strings.

        Why a nested generator: FastAPI's StreamingResponse requires an
        async generator. By nesting it here, we keep the endpoint function
        itself clean and testable.
        """
        try:
            async for event in run_pipeline(sanitized):
                # Emit a named SSE event so the frontend client can route by
                # event type without parsing the full JSON body first.
                # Format: event: {stage}\ndata: {json}\n\n
                #
                # The frontend's client.js reads the named event field and
                # passes it as the first argument to usePartFinder's handleEvent.
                stage = event.get("stage", "message")
                event_json = json.dumps(event, ensure_ascii=False)
                yield f"event: {stage}\ndata: {event_json}\n\n"
        except Exception as e:
            logger.error("Unhandled pipeline error: %s", e, exc_info=True)
            error_event = ProgressEvent(
                stage="error",
                status="error",
                message=f"An unexpected error occurred: {str(e)[:200]}",
                data=None,
            )
            yield f"data: {error_event.model_dump_json()}\n\n"
        finally:
            # Signal stream end to the client
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for SSE
        },
    )


# ==================================================================
# Entry point
# ==================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
