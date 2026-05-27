"""AI workflow extraction utilities."""

from typing import Any


def extract_workflow_items(markdown_text: str) -> dict[str, Any]:
    """Extract engineering workflow items from Markdown text.

    Placeholder output keeps the demo structure stable while the AI layer is added.
    """
    return {
        "summary": "TODO: Generate project summary from document.",
        "scope_items": [],
        "rfis": [],
        "risks": [],
        "cad_tasks": [],
        "field_verifications": [],
        "equipment": [],
        "points": [],
        "source_length_chars": len(markdown_text),
    }
