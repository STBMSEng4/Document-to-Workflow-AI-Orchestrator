"""Detection matrix builder for SpecFlow AI.

Converts scored terms into Markdown and JSON detection matrix outputs.
"""

import json
from typing import Any
from .confidence_scorer import ScoredTerm


def build_markdown_matrix(scored_terms: list[ScoredTerm], mode: str = "workflow") -> str:
    """Build a Markdown detection matrix table.

    mode='workflow'    — only source-confirmed terms above ignore threshold (0.40)
    mode='raw'         — all terms including 0.00
    """
    header = (
        "| Term | Normalized Term | Category | Confidence | Status | "
        "Evidence | Source Confirmed | Template Triggered |\n"
        "|---|---|---|---:|---|---|:---:|:---:|\n"
    )
    rows = []
    for t in scored_terms:
        if mode == "workflow" and not t.source_confirmed:
            continue
        if mode == "workflow" and t.confidence < 0.40:
            continue

        excerpt = t.evidence[0].excerpt[:60].replace("|", "\\|") if t.evidence else "—"
        rows.append(
            f"| {t.term} | {t.normalized_term} | {t.category} | "
            f"{t.confidence:.2f} | {t.status} | {excerpt} | "
            f"{'Yes' if t.source_confirmed else 'No'} | "
            f"{'Yes' if t.template_triggered else 'No'} |"
        )

    if not rows:
        return header + "| — | — | — | 0.00 | No terms detected | — | No | No |\n"
    return header + "\n".join(rows) + "\n"


def build_json_matrix(scored_terms: list[ScoredTerm]) -> dict[str, Any]:
    """Build a JSON-serialisable detection matrix."""
    return {
        "detected_terms": [
            {
                "term": t.term,
                "normalized_term": t.normalized_term,
                "category": t.category,
                "confidence": t.confidence,
                "status": t.status,
                "evidence": [
                    {
                        "excerpt": e.excerpt,
                        "page": e.page,
                        "section": e.section,
                        "match_type": e.match_type,
                        "source_reference": e.source_reference,
                    }
                    for e in t.evidence
                ],
                "source_confirmed": t.source_confirmed,
                "inferred": t.inferred,
                "template_triggered": t.template_triggered,
            }
            for t in scored_terms
        ]
    }
