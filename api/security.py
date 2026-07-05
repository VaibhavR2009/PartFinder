"""
PartFinder — Input Sanitization Helpers
=========================================
A thin layer of defensive sanitization applied before data reaches
Pydantic validators or agent prompts.

Why both Pydantic validators AND this module?
  • Pydantic validates type and format (structure).
  • This module strips potentially dangerous content (injection).
  The two layers are complementary.
"""

import html
import re


def strip_html(text: str) -> str:
    """
    Remove HTML tags and unescape HTML entities.

    Threat mitigated: A user who submits <script>...</script> or
    HTML injection in the description field. While agents receive
    text prompts (not HTML), stripping prevents future issues if
    outputs are ever rendered as HTML in logs or reports.
    """
    # Remove tags
    text = re.sub(r"<[^>]+>", "", text)
    # Unescape entities (&amp; → &)
    text = html.unescape(text)
    return text


def sanitize_description(text: str, max_length: int = 2000) -> str:
    """
    Full sanitization pipeline for the project description.
    Applied before the text is embedded in agent prompts.
    """
    text = strip_html(text)
    # Collapse excessive whitespace (more than 2 consecutive newlines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text[:max_length]


def sanitize_string(text: str, max_length: int = 200) -> str:
    """Generic string sanitizer for short fields."""
    text = strip_html(str(text))
    return text.strip()[:max_length]
