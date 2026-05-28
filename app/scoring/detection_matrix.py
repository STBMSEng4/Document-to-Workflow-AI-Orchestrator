"""Detection matrix builder for SpecFlow AI.

Converts scored terms into Markdown and JSON detection matrix outputs.
"""

from __future__ import annotations

import re
from typing import Any

from .confidence_scorer import ScoredTerm


def _sanitize_excerpt(excerpt: str) -> str:
    cleaned = re.sub(r"\s+", " ", excerpt).strip()
    return cleaned.replace("|", "\\|")


def build_markdown_matrix(scored_terms: list[ScoredTerm], mode: str = "workflow") -> str:
    """Build a Markdown detection matrix table.

    mode='workflow' -> only source-confirmed terms above ignore threshold (0.40)
    mode='raw'      -> all terms including 0.00
    """
    header = (
        "| Term | Normalized Term | Category | Confidence | Status | "
        "Evidence | Source Confirmed | Template Triggered |\n"
        "|---|---|---|---:|---|---|:---:|:---:|\n"
    )
    rows = []
    for term in scored_terms:
        if mode == "workflow" and not term.source_confirmed:
            continue
        if mode == "workflow" and term.confidence < 0.40:
            continue

        excerpt = _sanitize_excerpt(term.evidence[0].excerpt[:60]) if term.evidence else "-"
        rows.append(
            f"| {term.term} | {term.normalized_term} | {term.category} | "
            f"{term.confidence:.2f} | {term.status} | {excerpt} | "
            f"{'Yes' if term.source_confirmed else 'No'} | "
            f"{'Yes' if term.template_triggered else 'No'} |"
        )

    if not rows:
        return header + "| - | - | - | 0.00 | No terms detected | - | No | No |\n"
    return header + "\n".join(rows) + "\n"


def build_json_matrix(scored_terms: list[ScoredTerm]) -> dict[str, Any]:
    """Build a JSON-serializable detection matrix."""
    return {
        "detected_terms": [
            {
                "term": term.term,
                "normalized_term": term.normalized_term,
                "category": term.category,
                "confidence": term.confidence,
                "status": term.status,
                "evidence": [
                    {
                        "excerpt": evidence.excerpt,
                        "page": evidence.page,
                        "section": evidence.section,
                        "match_type": evidence.match_type,
                        "source_reference": evidence.source_reference,
                    }
                    for evidence in term.evidence
                ],
                "source_confirmed": term.source_confirmed,
                "inferred": term.inferred,
                "template_triggered": term.template_triggered,
            }
            for term in scored_terms
        ]
    }
