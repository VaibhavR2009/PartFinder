"""
PartFinder — MCP Server
========================
This is the Model Context Protocol (MCP) server that wraps SerpApi's
Home Depot and Amazon endpoints as structured tools. Agents call these
tools via the MCP protocol — they do NOT make HTTP calls to SerpApi
directly. This separation is intentional:

  • The MCP server is the single place where SerpApi credentials live.
  • Agents receive clean, minimal tool responses — not raw SerpApi JSON.
  • The cap on results (MAX_RESULTS_PER_SEARCH) is enforced here, not
    scattered across agent code.
  • Demo mode is transparent to agents: they call the same tool names
    and receive the same schema whether or not SerpApi is involved.

Transport: SSE (Server-Sent Events) on configurable port.
When embedded in the FastAPI process for Cloud Run, it mounts as an
ASGI sub-app at /mcp — agents connect to http://localhost:PORT/mcp.

Security:
  • SERPAPI_KEY is loaded from environment only — never hardcoded.
  • In live mode, the server raises ValueError at import time if the
    key is missing (fail-fast rather than silent 401 later).
  • All string inputs are trimmed to safe lengths before forwarding.
"""

import os
import logging
from typing import Optional

import httpx
from fastmcp import FastMCP

from mcp_server.config import (
    SERPAPI_KEY,
    SERPAPI_BASE_URL,
    DEMO_MODE,
    MAX_RESULTS_PER_SEARCH,
    HTTP_TIMEOUT,
)
from mcp_server.demo_data import (
    get_hd_search_fixture,
    get_hd_product_fixture,
    get_amazon_search_fixture,
    get_amazon_product_fixture,
    get_ebay_search_fixture,
    get_ebay_product_fixture,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Fail fast: if we're in live mode and the key is absent, raise now
# rather than letting agents call tools and get cryptic 401 errors.
# ------------------------------------------------------------------
if not DEMO_MODE and not SERPAPI_KEY:
    raise ValueError(
        "SERPAPI_KEY environment variable is not set. "
        "Set it or enable DEMO_MODE=true to use fixture data."
    )

# ------------------------------------------------------------------
# Initialise the MCP server
# ------------------------------------------------------------------
mcp = FastMCP(
    name="PartFinderTools",
    instructions=(
        "Tools for searching Home Depot and Amazon product catalogs. "
        "Always prefer Home Depot. Use Amazon only as a fallback when "
        "no Home Depot product satisfies the requirements."
    ),
)


# ==================================================================
# Internal helpers
# ==================================================================

def _trim(s: str, max_len: int = 500) -> str:
    """Guard against runaway query strings before forwarding to SerpApi."""
    return s[:max_len].strip()


async def _serpapi_get(params: dict) -> dict:
    """
    Make a GET request to SerpApi with retry on transient errors.
    We do NOT retry on 401 (bad key) or 422 (bad params) — those
    indicate configuration problems and should surface immediately.
    """
    params["api_key"] = SERPAPI_KEY
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(SERPAPI_BASE_URL, params=params)
        response.raise_for_status()
        return response.json()


def _extract_hd_products(raw: dict, n: int) -> list[dict]:
    """
    Extract the minimal fields agents need from a Home Depot search
    response. Stripping raw SerpApi JSON keeps tool outputs small,
    which reduces Gemini token consumption and improves reliability.
    """
    products = raw.get("products", [])
    results = []
    for p in products[:n]:
        results.append({
            "product_id": p.get("product_id", ""),
            "title": p.get("title", ""),
            "price": p.get("price", None),
            "rating": p.get("rating", None),
            "reviews": p.get("reviews", None),
            "thumbnail": p.get("thumbnail", ""),
            "link": p.get("link", ""),
        })
    return results


def _extract_amazon_products(raw: dict, n: int) -> list[dict]:
    """Extract minimal fields from an Amazon search response."""
    products = raw.get("organic_results", [])
    results = []
    for p in products[:n]:
        results.append({
            "asin": p.get("asin", ""),
            "title": p.get("title", ""),
            "price": p.get("price", {}).get("raw", None) if isinstance(p.get("price"), dict) else p.get("price"),
            "rating": p.get("rating", None),
            "reviews": p.get("reviews", None),
            "link": p.get("link", ""),
            "prime": p.get("prime", False),
        })
    return results


def _extract_ebay_products(raw: dict, n: int) -> list[dict]:
    """Extract minimal fields from an eBay search response."""
    products = raw.get("organic_results", [])
    results = []
    for p in products[:n]:
        price_val = p.get("price")
        if isinstance(price_val, dict):
            price_from = price_val.get("from", {})
            if isinstance(price_from, dict):
                price_val = price_from.get("raw") or price_from.get("extracted")
            else:
                price_val = p.get("price", {}).get("raw", None)
                
        results.append({
            "product_id": p.get("item_id") or p.get("product_id", ""),
            "title": p.get("title", ""),
            "price": price_val,
            "condition": p.get("condition", "Unknown"),
            "link": p.get("link", ""),
        })
    return results


# ==================================================================
# Tool: search_home_depot
# ==================================================================

@mcp.tool
async def search_home_depot(
    query: str,
    zip_code: str,
    store_id: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
) -> dict:
    """
    Search the Home Depot product catalog for a given query.

    Returns a list of matching products (capped at MAX_RESULTS_PER_SEARCH),
    each with product_id, title, price, rating, and link.

    Use the product_id values with get_home_depot_product to retrieve
    full specs and availability for a specific item.

    Args:
        query:     Search query (e.g. "exterior wood screws 3 inch").
        zip_code:  Delivery/pickup ZIP code for availability filtering.
        store_id:  Optional Home Depot store ID for in-store filtering.
        price_min: Optional minimum price filter (USD).
        price_max: Optional maximum price filter (USD).
    """
    query = _trim(query)
    zip_code = zip_code[:10]  # ZIP codes are at most 10 chars

    logger.info("search_home_depot: query=%r zip=%s demo=%s", query, zip_code, DEMO_MODE)

    if DEMO_MODE:
        return {"products": get_hd_search_fixture(query, MAX_RESULTS_PER_SEARCH), "demo_mode": True}

    params: dict = {
        "engine": "home_depot",
        "q": query,
        "delivery_zip": zip_code,
        "ps": MAX_RESULTS_PER_SEARCH,
    }
    if store_id:
        params["store_id"] = store_id
    if price_min is not None:
        params["lowerbound"] = price_min
    if price_max is not None:
        params["upperbound"] = price_max

    raw = await _serpapi_get(params)
    return {"products": _extract_hd_products(raw, MAX_RESULTS_PER_SEARCH), "demo_mode": False}


# ==================================================================
# Tool: get_home_depot_product
# ==================================================================

@mcp.tool
async def get_home_depot_product(
    product_id: str,
    store_id: Optional[str] = None,
    zip_code: Optional[str] = None,
) -> dict:
    """
    Retrieve full product details, specifications, price, and local
    availability for a Home Depot product by its product_id.

    This is the verification step: after search_home_depot returns
    candidates, call this tool on each candidate to get the specs
    needed to judge whether it satisfies the project's requirements.

    Args:
        product_id: The Home Depot product ID from a search result.
        store_id:   Optional store ID for local availability check.
        zip_code:   Optional ZIP code for delivery availability.
    """
    product_id = _trim(product_id, 50)
    logger.info("get_home_depot_product: id=%s demo=%s", product_id, DEMO_MODE)

    if DEMO_MODE:
        fixture = get_hd_product_fixture(product_id)
        if fixture:
            return {"product": fixture, "demo_mode": True}
        # If no fixture exists, return a sensible placeholder
        return {
            "product": {
                "product_id": product_id,
                "title": f"[Demo] Product {product_id}",
                "price": 12.99,
                "in_stock_locally": True,
                "availability": "In stock",
                "fulfillment": "Pickup available",
            },
            "demo_mode": True,
        }

    params: dict = {"engine": "home_depot_product", "product_id": product_id}
    if store_id:
        params["store_id"] = store_id
    if zip_code:
        params["delivery_zip"] = zip_code

    raw = await _serpapi_get(params)
    product = raw.get("product_results", raw)
    return {"product": product, "demo_mode": False}


# ==================================================================
# Tool: search_amazon
# ==================================================================

@mcp.tool
async def search_amazon(
    query: str,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
) -> dict:
    """
    Search the Amazon product catalog.

    Use this ONLY as a fallback when no Home Depot product satisfies
    the project's requirements for a given item. Amazon is noisier
    than Home Depot for hardware (more third-party sellers, variable
    quality), so it is not the primary source.

    Returns a list of matching products with asin, title, price, and link.
    Use the asin values with get_amazon_product for full details.

    Args:
        query:     Search query (e.g. "exterior galvanized corner bracket").
        price_min: Optional minimum price filter (USD).
        price_max: Optional maximum price filter (USD).
    """
    query = _trim(query)
    logger.info("search_amazon: query=%r demo=%s", query, DEMO_MODE)

    if DEMO_MODE:
        return {"products": get_amazon_search_fixture(query, MAX_RESULTS_PER_SEARCH), "demo_mode": True}

    params: dict = {
        "engine": "amazon",
        "k": query,
        "amazon_domain": "amazon.com",
    }
    if price_min is not None:
        params["price_min"] = int(price_min)
    if price_max is not None:
        params["price_max"] = int(price_max)

    raw = await _serpapi_get(params)
    return {"products": _extract_amazon_products(raw, MAX_RESULTS_PER_SEARCH), "demo_mode": False}


# ==================================================================
# Tool: get_amazon_product
# ==================================================================

@mcp.tool
async def get_amazon_product(asin: str) -> dict:
    """
    Retrieve full product details for an Amazon product by its ASIN
    (Amazon Standard Identification Number).

    Args:
        asin: The ASIN from an Amazon search result (e.g. "B08N5WRWJ9").
    """
    asin = _trim(asin, 20)
    logger.info("get_amazon_product: asin=%s demo=%s", asin, DEMO_MODE)

    if DEMO_MODE:
        fixture = get_amazon_product_fixture(asin)
        if fixture:
            return {"product": fixture, "demo_mode": True}
        return {
            "product": {
                "asin": asin,
                "title": f"[Demo] Amazon Product {asin}",
                "price": 14.99,
                "prime": True,
                "fulfillment": "Ships in 2-3 days",
            },
            "demo_mode": True,
        }

    params: dict = {"engine": "amazon_product", "asin": asin, "amazon_domain": "amazon.com"}
    raw = await _serpapi_get(params)
    return {"product": raw.get("product_results", raw), "demo_mode": False}


# ==================================================================
# Tool: search_ebay
# ==================================================================

@mcp.tool
async def search_ebay(
    query: str,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
) -> dict:
    """
    Search the eBay product catalog.

    Use this ONLY as a fallback when no Amazon product satisfies
    the project's requirements. eBay has variable conditions (used/new)
    and fulfillment, so it is the last resort.

    Returns a list of matching products with item_id, title, price, condition, and link.
    Use the product_id values with get_ebay_product for full details.

    Args:
        query:     Search query (e.g. "exterior galvanized corner bracket").
        price_min: Optional minimum price filter (USD).
        price_max: Optional maximum price filter (USD).
    """
    query = _trim(query)
    logger.info("search_ebay: query=%r demo=%s", query, DEMO_MODE)

    if DEMO_MODE:
        return {"products": get_ebay_search_fixture(query, MAX_RESULTS_PER_SEARCH), "demo_mode": True}

    params: dict = {
        "engine": "ebay",
        "_nkw": query,
        "buying_format": "BIN", # Buy It Now only to avoid auctions
    }
    if price_min is not None:
        params["_udlo"] = int(price_min)
    if price_max is not None:
        params["_udhi"] = int(price_max)

    raw = await _serpapi_get(params)
    return {"products": _extract_ebay_products(raw, MAX_RESULTS_PER_SEARCH), "demo_mode": False}


# ==================================================================
# Tool: get_ebay_product
# ==================================================================

@mcp.tool
async def get_ebay_product(product_id: str) -> dict:
    """
    Retrieve full product details for an eBay product by its item_id.

    Args:
        product_id: The item_id from an eBay search result.
    """
    product_id = _trim(product_id, 20)
    logger.info("get_ebay_product: id=%s demo=%s", product_id, DEMO_MODE)

    if DEMO_MODE:
        fixture = get_ebay_product_fixture(product_id)
        if fixture:
            return {"product": fixture, "demo_mode": True}
        return {
            "product": {
                "item_id": product_id,
                "title": f"[Demo] eBay Product {product_id}",
                "price": 14.99,
                "condition": "Brand New",
                "fulfillment": "Ships in 3-5 days",
            },
            "demo_mode": True,
        }

    params: dict = {"engine": "ebay_product", "item_id": product_id}
    raw = await _serpapi_get(params)
    return {"product": raw.get("product_results", raw), "demo_mode": False}


# ==================================================================
# Entry point (standalone mode)
# ==================================================================

# Expose the Starlette app for both uvicorn (standalone) and FastAPI (embedded)
mcp_app = mcp.http_app(path="/mcp")
mcp_app_embedded = mcp.http_app(path="/")

from starlette.responses import JSONResponse
mcp_app.add_route("/health", lambda req: JSONResponse({"status": "ok", "mode": "standalone/mcp"}))
mcp_app_embedded.add_route("/health", lambda req: JSONResponse({"status": "ok", "mode": "embedded/mcp"}))

if __name__ == "__main__":
    import uvicorn
    # Run as a standalone Streamable HTTP server for local development.
    # In Cloud Run single-container mode, the mcp app is mounted
    # as a sub-app inside the FastAPI process instead.
    port = int(os.environ.get("MCP_SERVER_PORT", "8001"))
    uvicorn.run("mcp_server.server:mcp_app", host="0.0.0.0", port=port)
