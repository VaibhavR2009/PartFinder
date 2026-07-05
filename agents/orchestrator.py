"""
PartFinder — Pipeline Orchestrator
=====================================
This module wires together the four ADK LlmAgents into a sequential
multi-agent pipeline and streams progress events to the caller.

== Architecture Decision: Custom BaseAgent vs SequentialAgent ==
We use a custom BaseAgent (OrchestratorAgent) rather than ADK's built-in
SequentialAgent for two reasons:

1. STREAMING: SequentialAgent doesn't expose per-stage completion events
   suitable for SSE streaming to a frontend. Our custom orchestrator yields
   typed ProgressEvent objects after each stage so the UI can update live.

2. CONDITIONAL ROUTING: After the Feasibility stage, we need to branch:
   if the project is infeasible, skip the remaining three agents entirely
   (no wasted API calls). SequentialAgent has no built-in early-exit.
   A custom _run_async_impl handles this cleanly.

The four sub-agents (Feasibility, Sourcing, Verification, Compiler) are
genuine ADK LlmAgent instances — each with its own system prompt, model
binding, and tool access. The orchestrator doesn't do reasoning itself;
it only routes data between agents and enforces the pipeline contract.

== State Passing Between Agents ==
ADK's InMemorySessionService accumulates conversation history across calls.
Each agent sees the prior agents' messages as part of its context. The
orchestrator also extracts structured JSON from each agent's response and
injects it as a clean "context block" into the next agent's prompt so that
agents don't have to search through long history to find their inputs.

== Input Validation ==
Validation happens here (at the pipeline entry point) rather than inside
individual agents. This prevents invalid data from reaching the LLM at all,
which saves tokens and avoids prompt-injection via crafted inputs.
"""

import json
import logging
import re
from typing import AsyncGenerator, Any

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai.types import Content, Part

from agents.config import (
    GEMINI_MODEL,
    GEMINI_MODEL_FALLBACK,
    MCP_SERVER_URL,
    MAX_ITEMS_PER_PROJECT,
    GOOGLE_API_KEY,
)
from agents.prompts import (
    FEASIBILITY_PROMPT,
    SOURCING_PROMPT,
    VERIFICATION_PROMPT,
    COMPILER_PROMPT,
)
from agents.retry import with_retry

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Pipeline stage names (also used as SSE event type identifiers)
# ------------------------------------------------------------------
STAGE_FEASIBILITY = "feasibility"
STAGE_SOURCING = "sourcing"
STAGE_VERIFICATION = "verification"
STAGE_COMPILER = "compiler"
STAGE_COMPLETE = "complete"
STAGE_ERROR = "error"


# ==================================================================
# Input validation
# ==================================================================

class ValidationError(ValueError):
    """Raised when user-supplied input fails validation checks."""


def validate_project_input(data: dict) -> dict:
    """
    Validate and sanitize the project input dict.

    Security rationale:
      - budget_usd: must be a positive number; prevents negative/zero
        inputs from confusing the feasibility agent and ensures the
        over-budget calculation is meaningful.
      - zip_code: must match US ZIP format; prevents injection of
        arbitrary strings into SerpApi delivery_zip parameter.
      - description: length-capped to prevent prompt-injection attacks
        via enormous inputs that could hijack agent instructions.
      - skill_level: whitelisted to prevent arbitrary strings entering
        the prompt.

    Returns the sanitized dict (strings trimmed, budget rounded).
    Raises ValidationError with a user-friendly message on failure.
    """
    # -- budget --
    try:
        budget = float(data.get("budget_usd", 0))
    except (TypeError, ValueError):
        raise ValidationError("Budget must be a number.")
    if budget <= 0:
        raise ValidationError("Budget must be greater than $0.")
    if budget > 1_000_000:
        raise ValidationError("Budget exceeds $1,000,000 — please check your input.")

    # -- zip_code --
    zip_code = str(data.get("zip_code", "")).strip()
    if not re.fullmatch(r"\d{5}(-\d{4})?", zip_code):
        raise ValidationError(
            "ZIP code must be a valid US ZIP (e.g. 90210 or 90210-1234)."
        )

    # -- description --
    description = str(data.get("description", "")).strip()
    if not description:
        raise ValidationError("Project description cannot be empty.")
    # 2000-char cap: generous for any real description; blocks injection payloads.
    description = description[:2000]

    # -- skill_level --
    allowed_skills = {"beginner", "intermediate", "advanced"}
    skill_level = str(data.get("skill_level", "beginner")).lower().strip()
    if skill_level not in allowed_skills:
        skill_level = "beginner"  # safe default

    # -- tools_on_hand --
    tools_raw = data.get("tools_on_hand", [])
    if not isinstance(tools_raw, list):
        tools_raw = []
    # Trim each tool name; cap the list length
    tools_on_hand = [str(t)[:100].strip() for t in tools_raw[:50] if str(t).strip()]

    return {
        "budget_usd": round(budget, 2),
        "zip_code": zip_code,
        "description": description,
        "skill_level": skill_level,
        "tools_on_hand": tools_on_hand,
    }


# ==================================================================
# JSON extraction helper
# ==================================================================

def _extract_json(text: str) -> dict | list:
    """
    Extract JSON from an agent response that may contain prose or
    markdown fences around the JSON block.

    Agents are instructed to return raw JSON, but LLMs sometimes wrap
    it in ```json ... ``` fences. This handles both cases.
    """
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strip markdown fences
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    # Last resort: find the outermost { } or [ ]
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass

    raise ValueError(f"Could not extract JSON from agent response: {text[:200]!r}")


# ==================================================================
# Agent runner helper
# ==================================================================

async def _run_agent_once(
    agent: LlmAgent,
    session_service: InMemorySessionService,
    session_id: str,
    user_id: str,
    message: str,
    app_name: str = "partfinder",
) -> str:
    """
    Run a single LlmAgent for one turn and return the text response.

    Wraps the ADK Runner pattern:
      Runner → run_async → collect events → return final text

    The with_retry wrapper handles 429s from the Gemini API.
    """
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service,
    )

    async def _call():
        response_parts = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(role="user", parts=[Part(text=message)]),
        ):
            # Collect text from all response events (text might arrive separately from the final marker)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_parts.append(part.text)
            logger.info(f"Runner yielded event: type={type(event)}, is_final={getattr(event, 'is_final_response', lambda: False)()}, content={event.content}")
        
        result = "".join(response_parts)
        if not result.strip():
            raise RuntimeError("Agent returned an empty response. The MCP session might have been interrupted.")
        return result

    return await with_retry(_call, label=f"{agent.name} call")


# ==================================================================
# Main pipeline function
# ==================================================================

async def run_pipeline(
    project_input: dict,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Execute the four-agent PartFinder pipeline sequentially, yielding
    progress events suitable for SSE streaming.

    Yielded event schema:
      { "stage": str, "status": "running"|"done"|"error"|"infeasible",
        "message": str, "data": dict | None }

    The caller (FastAPI SSE endpoint) serializes these to JSON and
    sends them to the frontend.

    Args:
        project_input: Raw dict from the API request. Will be validated
                       before any agent is invoked.
    """
    # ------------------------------------------------------------------
    # 1. Validate input — before any agent/API call
    # ------------------------------------------------------------------
    try:
        safe_input = validate_project_input(project_input)
    except ValidationError as e:
        yield {"stage": STAGE_ERROR, "status": "error", "message": str(e), "data": None}
        return

    user_id = "partfinder_user"
    app_name = "partfinder"

    # Shared session service — accumulates conversation history across
    # all four agents so each agent can see what previous ones said.
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    session_id = session.id

    # ------------------------------------------------------------------
    # 2. Create MCP toolset (new ADK API: constructor, not from_server)
    # ------------------------------------------------------------------
    # McpToolset manages the connection lifecycle internally. It is passed
    # directly to LlmAgent(tools=[...]) and the framework handles connect/
    # disconnect. We create one instance and share it across agents.
    try:
        mcp_toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL)
        )
    except Exception as e:
        logger.error("Failed to create MCP toolset for %s: %s", MCP_SERVER_URL, e)
        yield {
            "stage": STAGE_ERROR,
            "status": "error",
            "message": (
                f"Could not reach the PartFinder tools server at {MCP_SERVER_URL}. "
                "Is the MCP server running?"
            ),
            "data": None,
        }
        return

    try:
        # ------------------------------------------------------------------
        # STAGE 1: Feasibility Agent (no tools — pure reasoning)
        # ------------------------------------------------------------------
        yield {
            "stage": STAGE_FEASIBILITY,
            "status": "running",
            "message": "Checking project feasibility...",
            "data": None,
        }

        feasibility_agent = LlmAgent(
            model=GEMINI_MODEL,
            name="feasibility_agent",
            description="Assesses DIY project feasibility without external tool calls.",
            instruction=FEASIBILITY_PROMPT,
            tools=[],  # Explicitly no tools — see module docstring
        )

        feasibility_prompt = (
            f"Please assess this DIY project:\n\n{json.dumps(safe_input, indent=2)}"
        )

        try:
            feasibility_response = await _run_agent_once(
                feasibility_agent, session_service, session_id, user_id, feasibility_prompt
            )
            feasibility_data = _extract_json(feasibility_response)
        except Exception as e:
            logger.error("Feasibility agent error: %s", e)
            yield {
                "stage": STAGE_ERROR,
                "status": "error",
                "message": f"Feasibility check failed: {e}",
                "data": None,
            }
            return

        yield {
            "stage": STAGE_FEASIBILITY,
            "status": "done",
            "message": "Feasibility check complete.",
            "data": feasibility_data,
        }

        # ------------------------------------------------------------------
        # EARLY EXIT: if infeasible, stop here (no SerpApi calls wasted)
        # ------------------------------------------------------------------
        if not feasibility_data.get("feasible", False):
            yield {
                "stage": STAGE_COMPLETE,
                "status": "infeasible",
                "message": "Project assessed as infeasible.",
                "data": {
                    "feasibility": feasibility_data,
                    "input": safe_input,
                },
            }
            return

        # Enforce the items cap after feasibility returns
        items = feasibility_data.get("items", [])
        if len(items) > MAX_ITEMS_PER_PROJECT:
            logger.warning(
                "Feasibility returned %d items; capping to %d", len(items), MAX_ITEMS_PER_PROJECT
            )
            feasibility_data["items"] = items[:MAX_ITEMS_PER_PROJECT]

        # ------------------------------------------------------------------
        # STAGE 2: Sourcing Agent (Home Depot search via MCP)
        # ------------------------------------------------------------------
        yield {
            "stage": STAGE_SOURCING,
            "status": "running",
            "message": "Searching Home Depot for parts...",
            "data": None,
        }

        sourcing_agent = LlmAgent(
            model=GEMINI_MODEL,
            name="sourcing_agent",
            description="Searches Home Depot for candidate products for each required item.",
            instruction=SOURCING_PROMPT,
            tools=[mcp_toolset],
        )

        sourcing_prompt = (
            "Here is the project context from the Feasibility Agent:\n\n"
            f"zip_code: {safe_input['zip_code']}\n"
            f"budget_usd: {safe_input['budget_usd']}\n\n"
            f"Items to source:\n{json.dumps(feasibility_data['items'], indent=2)}\n\n"
            "Please search Home Depot for candidates for each item and return the sourced_items JSON."
        )

        try:
            sourcing_response = await _run_agent_once(
                sourcing_agent, session_service, session_id, user_id, sourcing_prompt
            )
            sourcing_data = _extract_json(sourcing_response)
        except Exception as e:
            logger.error("Sourcing agent error: %s", e)
            yield {
                "stage": STAGE_ERROR,
                "status": "error",
                "message": f"Sourcing failed: {e}",
                "data": None,
            }
            return

        yield {
            "stage": STAGE_SOURCING,
            "status": "done",
            "message": "Home Depot search complete.",
            "data": sourcing_data,
        }

        # ------------------------------------------------------------------
        # STAGE 3: Verification Agent (product specs + Amazon fallback)
        # ------------------------------------------------------------------
        yield {
            "stage": STAGE_VERIFICATION,
            "status": "running",
            "message": "Verifying product specifications...",
            "data": None,
        }

        verification_agent = LlmAgent(
            model=GEMINI_MODEL,
            name="verification_agent",
            description=(
                "Verifies product specs against functional requirements. "
                "Falls back to Amazon when Home Depot products don't qualify."
            ),
            instruction=VERIFICATION_PROMPT,
            tools=[mcp_toolset],
        )

        verification_prompt = (
            "Please verify product candidates against the project requirements.\n\n"
            f"zip_code: {safe_input['zip_code']}\n\n"
            f"Functional requirements (from Feasibility Agent):\n"
            f"{json.dumps(feasibility_data['items'], indent=2)}\n\n"
            f"Candidates to verify (from Sourcing Agent):\n"
            f"{json.dumps(sourcing_data.get('sourced_items', []), indent=2)}\n\n"
            "Return the verified_items JSON."
        )

        try:
            verification_response = await _run_agent_once(
                verification_agent, session_service, session_id, user_id, verification_prompt
            )
            verification_data = _extract_json(verification_response)
        except Exception as e:
            logger.error("Verification agent error: %s", e)
            yield {
                "stage": STAGE_ERROR,
                "status": "error",
                "message": f"Verification failed: {e}",
                "data": None,
            }
            return

        yield {
            "stage": STAGE_VERIFICATION,
            "status": "done",
            "message": "Product verification complete.",
            "data": verification_data,
        }

        # ------------------------------------------------------------------
        # STAGE 4: Compiler Agent (assemble final parts list)
        # ------------------------------------------------------------------
        yield {
            "stage": STAGE_COMPILER,
            "status": "running",
            "message": "Compiling your parts list...",
            "data": None,
        }

        compiler_agent = LlmAgent(
            model=GEMINI_MODEL,
            name="compiler_agent",
            description="Assembles final parts list, computes cost, and writes caveats.",
            instruction=COMPILER_PROMPT,
            tools=[],  # No external calls needed — pure data assembly
        )

        compiler_prompt = (
            "Please compile the final parts list and budget analysis.\n\n"
            f"budget_usd: {safe_input['budget_usd']}\n"
            f"Feasibility caveats: {json.dumps(feasibility_data.get('caveats', []))}\n\n"
            f"Verified items:\n"
            f"{json.dumps(verification_data.get('verified_items', []), indent=2)}\n\n"
            "Return the complete parts list JSON."
        )

        try:
            compiler_response = await _run_agent_once(
                compiler_agent, session_service, session_id, user_id, compiler_prompt
            )
            compiler_data = _extract_json(compiler_response)
        except Exception as e:
            logger.error("Compiler agent error: %s", e)
            yield {
                "stage": STAGE_ERROR,
                "status": "error",
                "message": f"Compilation failed: {e}",
                "data": None,
            }
            return

        yield {
            "stage": STAGE_COMPILER,
            "status": "done",
            "message": "Parts list ready.",
            "data": compiler_data,
        }

        # ------------------------------------------------------------------
        # Final complete event
        # ------------------------------------------------------------------
        yield {
            "stage": STAGE_COMPLETE,
            "status": "done",
            "message": "PartFinder complete.",
            "data": {
                "input": safe_input,
                "feasibility": feasibility_data,
                "result": compiler_data,
            },
        }

    finally:
        # Always clean up the MCP connection — even on error
        await mcp_toolset.close()
