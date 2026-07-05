"""
PartFinder — Retry Utilities
==============================
Exponential backoff with jitter for both Gemini (429 rate-limit) and
SerpApi (429 quota-exceeded) responses.

Design choices:
  • Jitter (random fraction of delay) prevents the "thundering herd"
    problem where multiple concurrent requests retry simultaneously.
  • We do NOT retry 400/401/422 — those indicate bad requests or bad
    credentials and retrying them wastes quota.
  • Max delay capped at RETRY_MAX_DELAY_S to avoid unbounded waits.
"""

import asyncio
import logging
import random
from typing import TypeVar, Callable, Awaitable

from agents.config import RETRY_MAX_ATTEMPTS, RETRY_BASE_DELAY_S, RETRY_MAX_DELAY_S

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retry(
    coro_fn: Callable[[], Awaitable[T]],
    label: str = "call",
) -> T:
    """
    Execute an async coroutine with exponential backoff on rate-limit errors.

    Args:
        coro_fn: A zero-argument callable returning an awaitable.
        label:   A short description used in log messages.

    Returns:
        The result of the coroutine on success.

    Raises:
        The last exception if all retries are exhausted.
    """
    last_exc: Exception | None = None
    for attempt in range(1, RETRY_MAX_ATTEMPTS + 1):
        try:
            return await coro_fn()
        except Exception as exc:
            last_exc = exc
            exc_str = str(exc)

            # Distinguish rate-limit errors from hard failures
            is_rate_limit = any(code in exc_str for code in ["429", "RESOURCE_EXHAUSTED", "quota"])
            is_retriable = is_rate_limit or any(code in exc_str for code in ["503", "500", "empty response", "interrupted"])

            if not is_retriable or attempt == RETRY_MAX_ATTEMPTS:
                logger.error("%s failed (attempt %d/%d): %s", label, attempt, RETRY_MAX_ATTEMPTS, exc)
                raise

            # Exponential backoff with full jitter:
            # delay = random(0, min(cap, base * 2^attempt))
            raw_delay = RETRY_BASE_DELAY_S * (2 ** (attempt - 1))
            delay = random.uniform(0, min(RETRY_MAX_DELAY_S, raw_delay))
            
            if is_rate_limit:
                msg = f"{label} rate-limited"
            else:
                msg = f"{label} connection/tool error (MCP server might be unreachable at configured URL)"

            logger.warning(
                "%s (attempt %d/%d). Retrying in %.1fs ...",
                msg,
                attempt,
                RETRY_MAX_ATTEMPTS,
                delay,
            )
            await asyncio.sleep(delay)

    raise RuntimeError(f"Exhausted retries for {label}") if last_exc is None else last_exc
