"""Filter engine for SpecFlow AI.

Applies filtering_rules.json thresholds to produce allowed, suppressed,
low-confidence, and not-detected item buckets.
"""

import json
from pathlib import Path
from typing import Any
from .confidence_scorer import ScoredTerm

RULES_PATH = Path(__file__).parents[2] / "knowledge_base" / "filtering_rules.json"
TEMPLATE_RULES_PATH = Path(__file__).parents[2] / "knowledge_base" / "template_rules.json"


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


THRESHOLDS = {
    "equipment_template": 0.70,
    "points_list": 0.70,
    "rfi_candidate": 0.60,
    "field_verification": 0.50,
    "cad_task": 0.60,
    "submittal_item": 0.60,
    "commissioning_item": 0.65,
    "ignore_below": 0.40,
}


def apply_filters(scored_terms: list[ScoredTerm]) -> dict[str, Any]:
    """Partition scored terms into workflow buckets."""
    allowed = []
    suppressed = []
    low_confidence = []
    not_detected = []

    for t in scored_terms:
        if not t.source_confirmed or t.confidence == 0.00:
            not_detected.append(t)
        elif t.confidence < THRESHOLDS["ignore_below"]:
            suppressed.append(t)
        elif t.confidence < 0.60:
            low_confidence.append(t)
        else:
            allowed.append(t)

    return {
        "allowed": allowed,
        "suppressed": suppressed,
        "low_confidence": low_confidence,
        "not_detected": not_detected,
    }


def evaluate_template_triggers(
    scored_terms: list[ScoredTerm],
) -> list[dict[str, Any]]:
    """Decide which templates trigger based on source-confirmed required terms."""
    rules = _load_json(TEMPLATE_RULES_PATH)
    term_map = {t.term.lower(): t for t in scored_terms}
    decisions = []

    for tmpl in rules["templates"]:
        required = tmpl["required_terms"]
        match_mode = tmpl.get("required_terms_match", "all")
        min_conf = tmpl["minimum_confidence"]

        if match_mode == "any":
            matched = [r for r in required if term_map.get(r.lower(), ScoredTerm(r, r, "", 0.0, "Not Detected")).confidence >= min_conf]
            triggered = len(matched) > 0
            trigger_conf = max(
                (term_map[r.lower()].confidence for r in required if r.lower() in term_map),
                default=0.0,
            )
        else:
            matched = [r for r in required if term_map.get(r.lower(), ScoredTerm(r, r, "", 0.0, "Not Detected")).confidence >= min_conf]
            triggered = len(matched) == len(required)
            trigger_conf = min(
                (term_map[r.lower()].confidence for r in required if r.lower() in term_map),
                default=0.0,
            ) if matched else 0.0

        decisions.append({
            "template_name": tmpl["template_name"],
            "description": tmpl["description"],
            "triggered": triggered,
            "confidence": round(trigger_conf, 2),
            "reason": (
                f"Required terms found: {matched}" if triggered
                else f"Required terms missing or below {min_conf}: {[r for r in required if r not in matched]}"
            ),
            "human_review_required": tmpl.get("human_review_required", False),
            "output_sections": tmpl.get("output_sections", []) if triggered else [],
        })

    return decisions


def build_filter_markdown(filter_results: dict[str, Any], template_decisions: list[dict]) -> str:
    """Render filtering summary as Markdown."""
    lines = ["# Filtering Summary\n"]

    lines.append("## Allowed Items\n")
    if filter_results["allowed"]:
        lines.append("| Term | Category | Confidence | Status |")
        lines.append("|---|---|---:|---|")
        for t in filter_results["allowed"]:
            lines.append(f"| {t.term} | {t.category} | {t.confidence:.2f} | {t.status} |")
    else:
        lines.append("_No items passed the workflow threshold._")

    lines.append("\n## Low-Confidence Items\n")
    if filter_results["low_confidence"]:
        lines.append("| Term | Category | Confidence | Status |")
        lines.append("|---|---|---:|---|")
        for t in filter_results["low_confidence"]:
            lines.append(f"| {t.term} | {t.category} | {t.confidence:.2f} | {t.status} |")
    else:
        lines.append("_None._")

    lines.append("\n## Suppressed Items\n")
    if filter_results["suppressed"]:
        for t in filter_results["suppressed"]:
            lines.append(f"- {t.term} (confidence {t.confidence:.2f} — below ignore threshold)")
    else:
        lines.append("_None._")

    lines.append("\n## Not Detected (0.00)\n")
    if filter_results["not_detected"]:
        for t in filter_results["not_detected"]:
            lines.append(f"- {t.term}")
    else:
        lines.append("_None._")

    lines.append("\n## Template Trigger Decisions\n")
    lines.append("| Template | Triggered | Confidence | Reason | Human Review |")
    lines.append("|---|:---:|---:|---|:---:|")
    for d in template_decisions:
        lines.append(
            f"| {d['template_name']} | {'Yes' if d['triggered'] else 'No'} | "
            f"{d['confidence']:.2f} | {d['reason'][:60]} | "
            f"{'Yes' if d['human_review_required'] else 'No'} |"
        )

    return "\n".join(lines) + "\n"
