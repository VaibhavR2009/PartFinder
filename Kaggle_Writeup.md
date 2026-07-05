# PartFinder: A Multi-Agent DIY Parts-Sourcing Assistant
**Automating Feasibility, Sourcing, and Verification for Makers using Google ADK and MCP**

**Track:** Concierge Agents Track

---

## 1. Introduction & The Problem Space

DIY builders, makers, and homeowners face a recurring problem: bridging the gap between a vague project idea and a concrete, actionable bill of materials. Traditional tutorials provide generic materials lists (e.g., "wood screws"), but the actual purchasing process requires highly specific knowledge (e.g., "#8 2-1/2 in. Deck Plus Exterior Wood Screws"). 

Furthermore, parts availability and pricing vary wildly by region, making budgeting difficult. A builder needs to know three things before starting:
1. Is my project feasible within my budget?
2. What exact parts do I need?
3. Where can I buy them locally right now?

**PartFinder** is a Concierge Agent designed to solve this. By taking a simple natural-language description, a budget, and a ZIP code, PartFinder employs a multi-agent system to break down the project, verify its feasibility, source the exact parts from local retailers, and compile a finalized, priced shopping list with caveats for any substitutions.

## 2. Multi-Agent Architecture

The core of PartFinder is built using the **Google Agent Development Kit (ADK)**. Rather than relying on a single, monolithic LLM prompt—which often struggles to juggle tool-use, deep reasoning, and formatting simultaneously—PartFinder splits the workload across a sequential, four-stage agent pipeline.

### The Pipeline

1. **Feasibility Agent (Pure Reasoning)**
   - **Role:** Analyzes the user's project description, skill level, and budget to determine if the project is structurally and financially viable. 
   - **Agentic Pattern:** *Guardrail / Early Exit*. If a user asks to "build a robotic arm for $5", the Feasibility Agent immediately halts the pipeline, preventing wasted API calls and providing an explanation of why the project fails feasibility, along with alternative suggestions.

2. **Sourcing Agent (Tool-Use)**
   - **Role:** Takes the validated requirements and performs broad searches across retailers.
   - **Agentic Pattern:** *Information Gathering*. It connects to an MCP (Model Context Protocol) server to search Home Depot's inventory based on the user's specific ZIP code, gathering multiple candidate products for each required part.

3. **Verification Agent (Reflection & Fallback)**
   - **Role:** The critical "quality control" layer. It analyzes the candidates provided by the Sourcing Agent and verifies them against the project's strict specifications.
   - **Agentic Pattern:** *Reflection & Routing*. If Home Depot's candidates are inadequate (e.g., specialized electronics components), the Verification Agent dynamically falls back to query Amazon. If an exact match cannot be found on either platform, it intelligently selects a "closest match" and logs the discrepancy.

4. **Compiler Agent (Aggregation)**
   - **Role:** Assembles the verified products into a clean, itemized list. It calculates total costs, identifies budget deltas, and surfaces the Verification Agent's "closest match" warnings as user-facing caveats.

## 3. Tool Integration via Model Context Protocol (MCP)

To connect the ADK agents to live retail data, PartFinder implements a robust **FastMCP** server utilizing the Server-Sent Events (SSE) transport protocol. 

### SerpApi Integration
The MCP server exposes four discrete tools powered by SerpApi:
- `search_home_depot`
- `get_home_depot_product`
- `search_amazon`
- `get_amazon_product`

### Why MCP?
By offloading tool definitions to an MCP server, the ADK agents remain decoupled from the underlying API logic. The `MCPToolset` standardizes the execution of these tools, allowing the Verification Agent to seamlessly switch between Home Depot and Amazon toolsets purely based on the LLM's reasoning and fallback logic.

## 4. Technical Implementation & Deployment

### Backend (FastAPI + SSE)
The pipeline is orchestrated by a FastAPI backend. Because agentic workflows can take 15–30 seconds to complete multiple API hops, traditional blocking HTTP requests lead to poor UX. PartFinder utilizes **Server-Sent Events (SSE)** to stream real-time progress updates (e.g., "Checking feasibility...", "Searching for parts...") directly to the client as each ADK agent completes its task.

For deployment efficiency (e.g., on Google Cloud Run), the FastMCP server is mounted directly as an ASGI sub-application within the FastAPI process (`EMBED_MCP=true`). This allows both the web API and the MCP server to run concurrently in a single container.

### Frontend (React + Vite)
The UI is a sleek, modern React application. It visually tracks the progress of the multi-agent pipeline and renders the final output. Crucially, the UI parses the data provided by the Compiler Agent to badge items appropriately—flagging items with a `🔶 Closest Match` badge if the Verification Agent had to make a substitution, ensuring the user is never misled about what they are buying.

## 5. Safety, Security, and Cost Control

Building agents that autonomously query paid APIs requires strict guardrails:
- **Cost Caps:** The agent prompt logic is structured to enforce a strict sequential fallback (Home Depot first, Amazon only if necessary). This caps the absolute worst-case SerpApi call volume at 36 calls per run, keeping the application well within budget.
- **Input Sanitization:** User inputs (budget, ZIP code) are validated via strict Pydantic schemas and regex patterns before ever touching the agent context or the MCP tools, preventing prompt injection or malicious API querying.
- **Resiliency:** Network failures and rate limits (HTTP 429) from both Gemini and SerpApi are handled transparently via custom exponential backoff wrappers within the pipeline.

## 6. Conclusion

PartFinder demonstrates the power of specialized, sequential AI agents. By dividing a complex task into discrete phases—Feasibility, Sourcing, Verification, and Compilation—the system achieves a level of accuracy and reliability that a single-prompt solution cannot match. Integrated with live MCP tools and presented through a streaming, reactive frontend, PartFinder serves as a highly capable, autonomous Concierge Agent for the DIY community.
