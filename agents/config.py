"""
PartFinder — Agent Configuration
==================================
Centralizing all tuneable parameters in one place makes it easy to:
  • Document the rationale for each cap (required by capstone rubric).
  • Adjust limits without touching agent logic files.
  • Override via environment variables for different deployment tiers.
"""

import os

# ------------------------------------------------------------------
# Gemini model selection
#
# Primary: gemini-2.5-flash
#   - Free-tier eligible (AI Studio key, no billing required)
#   - Optimised for agentic/tool-use tasks
#   - Rate limits: ~15 RPM, ~1,500 RPD on free tier
#
# Fallback: gemini-2.0-flash
#   - Used automatically if 2.5-flash returns 404 or is unavailable
#
# Note: The model name is a plain string passed to ADK's LlmAgent.
# To override (e.g. for a paid tier), set GEMINI_MODEL env var.
# ------------------------------------------------------------------
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_MODEL_FALLBACK: str = "gemini-2.0-flash"

# ------------------------------------------------------------------
# Google API Key (for Gemini)
# ------------------------------------------------------------------
GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")

# ------------------------------------------------------------------
# MCP Server URL
#
# Local dev: the MCP server runs as a separate process on port 8001.
# Cloud Run / single-container: the MCP server is embedded in the
# FastAPI process and reachable at http://localhost:PORT/mcp.
# ------------------------------------------------------------------
MCP_SERVER_PORT: int = int(os.environ.get("MCP_SERVER_PORT", "8001"))
MCP_SERVER_URL: str = os.environ.get(
    "MCP_SERVER_URL", f"http://localhost:{MCP_SERVER_PORT}/mcp"
)

# ------------------------------------------------------------------
# Safety Caps — API Call Budget per Pipeline Run
#
# These caps exist to prevent a single user request from exhausting
# the SerpApi quota and running up unexpected costs. They are
# deliberately conservative for the free tier.
#
# Worst-case call count at these defaults:
#   HD search calls:    MAX_ITEMS (4) × 1       = 4
#   HD product calls:   MAX_ITEMS (4) × MAX_CANDS (1) = 4
#   Amazon search calls (fallback worst case):  = 4
#   Amazon product calls (fallback worst case): = 4
#   eBay search calls (fallback worst case):    = 4
#   eBay product calls (fallback worst case):   = 4
#   Total SerpApi calls (worst case):           = 24
#
# Gemini calls:
#   Feasibility: 1, Sourcing: 1, Verification: 1, Compiler: 1 = 4
#
# Note: 24 calls is a much safer ceiling for the free tier.
# It is highly recommended to use DEMO_MODE for iterative testing.
# To raise the ceiling for a paid tier, set the env vars.
# ------------------------------------------------------------------
MAX_ITEMS_PER_PROJECT: int = int(os.environ.get("MAX_ITEMS", "4"))
MAX_CANDIDATES_PER_ITEM: int = int(os.environ.get("MAX_CANDIDATES", "1"))

# ------------------------------------------------------------------
# Retry / rate-limit configuration (for 429 responses)
# ------------------------------------------------------------------
RETRY_MAX_ATTEMPTS: int = 4
RETRY_BASE_DELAY_S: float = 2.0   # first retry after 2s; doubles each time
RETRY_MAX_DELAY_S: float = 60.0   # never wait longer than 60s
