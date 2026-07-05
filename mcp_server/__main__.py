"""
Convenience entry point — run the MCP server as a module:
  python -m mcp_server
"""
import os

# Load .env BEFORE importing server.py, because server.py reads
# env vars at module level (SERPAPI_KEY check happens on import).
from dotenv import load_dotenv
load_dotenv()

from mcp_server.server import mcp

if __name__ == "__main__":
    port = int(os.environ.get("MCP_SERVER_PORT", "8001"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
