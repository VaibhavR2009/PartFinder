"""
PartFinder — API Data Models & Input Validators
================================================
Pydantic models provide automatic type coercion + validation.
All security-relevant validators are annotated with comments
explaining the threat they mitigate.
"""

import re
from typing import Any, Optional
from pydantic import BaseModel, field_validator, Field


# ==================================================================
# Request model
# ==================================================================

class ProjectRequest(BaseModel):
    """
    The user's project submission from the frontend form.
    Pydantic validates types before the data reaches any agent.
    """

    description: str = Field(..., description="What the user wants to build or repair.")
    budget_usd: float = Field(..., description="Total budget in US dollars.", gt=0)
    zip_code: str = Field(..., description="US ZIP code for local availability.")
    skill_level: str = Field(default="beginner", description="beginner | intermediate | advanced")
    tools_on_hand: list[str] = Field(
        default_factory=list,
        description="Tools the user already owns.",
    )

    @field_validator("description")
    @classmethod
    def description_not_empty_and_capped(cls, v: str) -> str:
        """
        Security: cap description length to prevent prompt-injection via
        enormous inputs designed to exceed the agent's context window or
        override its system prompt.
        """
        v = v.strip()
        if not v:
            raise ValueError("Project description cannot be empty.")
        return v[:2000]

    @field_validator("budget_usd")
    @classmethod
    def budget_must_be_positive(cls, v: float) -> float:
        """
        Security: a zero or negative budget would produce meaningless
        results (everything is "over budget") and could confuse the
        feasibility agent's cost comparison logic.
        """
        if v <= 0:
            raise ValueError("Budget must be greater than $0.")
        if v > 1_000_000:
            raise ValueError("Budget exceeds $1,000,000 — please check your input.")
        return round(v, 2)

    @field_validator("zip_code")
    @classmethod
    def zip_code_format(cls, v: str) -> str:
        """
        Security: the zip_code value is forwarded to SerpApi's
        delivery_zip parameter. A regex check prevents injecting
        arbitrary query strings through this field.
        """
        v = v.strip()
        if not re.fullmatch(r"\d{5}(-\d{4})?", v):
            raise ValueError("ZIP code must be a valid US ZIP (e.g. 90210 or 90210-1234).")
        return v

    @field_validator("skill_level")
    @classmethod
    def skill_level_whitelist(cls, v: str) -> str:
        """
        Security: skill_level is embedded in the agent prompt. Whitelisting
        prevents injection of arbitrary instructions through this field.
        """
        allowed = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed:
            return "beginner"
        return v

    @field_validator("tools_on_hand")
    @classmethod
    def tools_list_caps(cls, v: list[str]) -> list[str]:
        """Cap list length and individual string length to bound input size."""
        return [str(t)[:100].strip() for t in v[:50] if str(t).strip()]

    def to_agent_dict(self) -> dict:
        """Convert to the dict format expected by the orchestrator."""
        return {
            "description": self.description,
            "budget_usd": self.budget_usd,
            "zip_code": self.zip_code,
            "skill_level": self.skill_level,
            "tools_on_hand": self.tools_on_hand,
        }


# ==================================================================
# SSE Event model
# ==================================================================

class ProgressEvent(BaseModel):
    """
    A single Server-Sent Event emitted during the pipeline run.
    Each event corresponds to a stage transition.
    """
    stage: str
    status: str   # "running" | "done" | "error" | "infeasible"
    message: str
    data: Optional[Any] = None


# ==================================================================
# Health check
# ==================================================================

class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    model: str
