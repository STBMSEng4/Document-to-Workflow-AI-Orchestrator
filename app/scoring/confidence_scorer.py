"""Confidence scoring engine for SpecFlow AI.

Scores each detected term from 0.00 to 1.00 based on weighted source evidence.
Knowledge-base presence alone always contributes 0.00.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

RULES_PATH = Path(__file__).parents[2] / "knowledge_base" / "confidence_rules.json"

# Scoring weights (mirror confidence_rules.json)
WEIGHTS = {
    "exact_term_match": 0.35,
    "alias_synonym_match": 0.20,
    "nearby_technical_context": 0.20,
    "source_frequency_repetition": 0.10,
    "document_section_relevance": 0.10,
    "cross_reference_support": 0.05,
}

TECHNICAL_SECTION_KEYWORDS = {
    "sequence of operation", "points list", "i/o schedule", "control narrative",
    "controls specification", "section 25", "bas", "bms", "controls", "instrumentation",
}


@dataclass
class EvidenceRecord:
    excerpt: str
    page: Optional[int] = None
    section: str = ""
    match_type: str = "exact"  # exact | alias | inferred | cross_reference
    source_reference: str = ""


@dataclass
class ScoredTerm:
    term: str
    normalized_term: str
    category: str
    confidence: float
    status: str
    evidence: list[EvidenceRecord] = field(default_factory=list)
    source_confirmed: bool = False
    inferred: bool = False
    template_triggered: bool = False


def _status_label(confidence: float) -> str:
    if confidence >= 0.90:
        return "Confirmed"
    if confidence >= 0.75:
        return "High Confidence"
    if confidence >= 0.60:
        return "Medium Confidence"
    if confidence >= 0.40:
        return "Low Confidence"
    if confidence > 0.00:
        return "Weak"
    return "Not Detected"


def _count_occurrences(term: str, text: str) -> int:
    return len(_term_pattern(term).findall(text))


def _term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)


def _in_technical_section(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in TECHNICAL_SECTION_KEYWORDS)


def score_term(
    term: str,
    normalized_term: str,
    category: str,
    aliases: list[str],
    source_text: str,
) -> ScoredTerm:
    """Score a single term against the source document text."""
    score = 0.0
    evidence: list[EvidenceRecord] = []
    inferred = False

    lower_text = source_text.lower()
    lower_term = term.lower()

    # Exact match
    exact_count = _count_occurrences(lower_term, lower_text)
    if exact_count > 0:
        score += WEIGHTS["exact_term_match"]
        # Grab first occurrence as excerpt
        match = _term_pattern(lower_term).search(lower_text)
        if match:
            start = max(0, match.start() - 40)
            end = min(len(source_text), match.end() + 40)
            evidence.append(EvidenceRecord(
                excerpt=source_text[start:end].strip(),
                match_type="exact",
            ))

    # Alias match (only if no exact match yet to avoid double-counting)
    elif aliases:
        for alias in aliases:
            alias_count = _count_occurrences(alias.lower(), lower_text)
            if alias_count > 0:
                score += WEIGHTS["alias_synonym_match"]
                match = _term_pattern(alias.lower()).search(lower_text)
                if match:
                    start = max(0, match.start() - 40)
                    end = min(len(source_text), match.end() + 40)
                    evidence.append(EvidenceRecord(
                        excerpt=source_text[start:end].strip(),
                        match_type="alias",
                    ))
                break

    # Stop here if nothing found — no nonzero score without evidence
    if score == 0.0:
        return ScoredTerm(
            term=term,
            normalized_term=normalized_term,
            category=category,
            confidence=0.00,
            status="Not Detected",
            evidence=[],
            source_confirmed=False,
            inferred=False,
        )

    # Repetition bonus
    total_occurrences = exact_count + sum(
        _count_occurrences(a.lower(), lower_text) for a in aliases
    )
    if total_occurrences >= 3:
        score += WEIGHTS["source_frequency_repetition"]
    elif total_occurrences == 2:
        score += WEIGHTS["source_frequency_repetition"] * 0.5

    # Section relevance bonus
    if _in_technical_section(source_text):
        score += WEIGHTS["document_section_relevance"]

    # Nearby technical context — simple heuristic: are related BMS terms nearby?
    nearby_count = sum(
        1 for kw in ["controller", "sensor", "bacnet", "bms", "bas", "sequence", "point", "alarm"]
        if kw in lower_text
    )
    if nearby_count >= 3:
        score += WEIGHTS["nearby_technical_context"]
    elif nearby_count >= 1:
        score += WEIGHTS["nearby_technical_context"] * 0.5

    score = round(min(score, 1.00), 2)
    status = _status_label(score)
    source_confirmed = score > 0.00

    return ScoredTerm(
        term=term,
        normalized_term=normalized_term,
        category=category,
        confidence=score,
        status=status,
        evidence=evidence,
        source_confirmed=source_confirmed,
        inferred=inferred,
    )


def score_all_terms(
    kb_terms: list[dict],
    source_text: str,
) -> list[ScoredTerm]:
    """Score all knowledge-base terms against source text. Returns full list including 0.00."""
    results = []
    for entry in kb_terms:
        result = score_term(
            term=entry["term"],
            normalized_term=entry.get("normalized_term", entry["term"]),
            category=entry.get("category", "Unknown"),
            aliases=entry.get("aliases", []),
            source_text=source_text,
        )
        results.append(result)
    return results
