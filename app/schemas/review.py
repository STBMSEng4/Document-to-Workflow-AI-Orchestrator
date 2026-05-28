"""Shared confidence / review flag helpers for schema records."""

from __future__ import annotations

from typing import Literal


SourceType = Literal["source_extracted", "template_default", "inferred"]
ConfidenceBand = Literal["confirmed", "high", "medium", "low", "weak"]


def confidence_band_for(score: float) -> ConfidenceBand:
    if score >= 0.90:
        return "confirmed"
    if score >= 0.75:
        return "high"
    if score >= 0.60:
        return "medium"
    if score >= 0.40:
        return "low"
    return "weak"


def default_review_reason(source_type: SourceType, confidence: float) -> str | None:
    if source_type == "template_default":
        return "template fallback row requires source verification"
    if source_type == "inferred":
        return "record contains inferred fields that should be reviewed"
    if confidence < 0.75:
        return "confidence below high-confidence threshold"
    return None
