# ============================================================
# PartFinder — MCP Server Configuration
#
# Design note: Constants are centralized here so the API-call
# cap is visible in one place and easy to audit / tune.
# ============================================================

import os

# ----------------------------------------------------------
# SerpApi
# ----------------------------------------------------------
# Fail fast on startup if the key is missing (in live mode).
# This prevents silent quota leaks from bad configuration.
SERPAPI_KEY: str = os.environ.get("SERPAPI_KEY", "")
SERPAPI_BASE_URL: str = "https://serpapi.com/search"

# ----------------------------------------------------------
# Demo mode
# When True, all tool calls return fixture data from
# demo_data.py instead of calling SerpApi.
# This lets the author record demo videos without quota.
# ----------------------------------------------------------
DEMO_MODE: bool = os.environ.get("DEMO_MODE", "false").lower() == "true"

# ----------------------------------------------------------
# API Call Safety Caps
#
# MAX_RESULTS_PER_SEARCH caps how many candidates the MCP
# server returns per search call. Even if SerpApi returns 20,
# we slice to this number to keep agent context small and
# token cost bounded.
#
# Rationale for 1: In the worst case the orchestrator calls:
#   search_home_depot × MAX_ITEMS (4) = 4 HD search calls
#   get_home_depot_product × (4 × 1) = 4 HD product calls
#   search_amazon × 4 fallback = 4 Amazon search calls
#   get_amazon_product × (4 × 1) = 4 Amazon product calls
#   search_ebay × 4 fallback = 4 eBay search calls
#   get_ebay_product × (4 × 1) = 4 eBay product calls
#   Total: 24 SerpApi calls maximum — much safer for free tier.
#
# Raising MAX_RESULTS_PER_SEARCH increases candidate quality
# but multiplies product-detail calls. Change here, not in
# individual agent files.
# ----------------------------------------------------------
MAX_RESULTS_PER_SEARCH: int = int(os.environ.get("MAX_RESULTS_PER_SEARCH", "1"))

# ----------------------------------------------------------
# HTTP request timeout (seconds)
# ----------------------------------------------------------
HTTP_TIMEOUT: float = 15.0
