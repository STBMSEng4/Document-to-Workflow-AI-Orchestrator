"""Sequence of Operations (SOO) extractor for SpecFlow AI.

Extracts structured control steps from controls narrative prose.
Unlike equipment_extractor and points_list_extractor which parse Markdown
tables, this module works sentence-by-sentence on free-form text.

Only creates records for sentences that contain a recognizable control action.
Confidence is grounded in what the text actually says — no fabrication.
"""

from __future__ import annotations

import re

from app.extractors.source_labels import INFERRED, SOURCE_EXTRACTED, append_remark
from app.schemas.soo import SOOMode, SOORecord


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------

# Maps text patterns (lower-cased) → SOOMode literal.
# Checked against section headers and sentence content.
_MODE_SECTION_MAP: list[tuple[str, SOOMode]] = [
    ("morning warmup", "morning_warmup"),
    ("morning warm-up", "morning_warmup"),
    ("warm-up mode", "morning_warmup"),
    ("pre-occupancy", "morning_warmup"),
    ("pre occupancy", "morning_warmup"),
    ("unoccupied mode", "unoccupied"),
    ("unoccupied period", "unoccupied"),
    ("unoccupied operation", "unoccupied"),
    ("unoccupied hours", "unoccupied"),
    ("night setback", "unoccupied"),
    ("after hours", "unoccupied"),
    ("setback mode", "unoccupied"),
    ("occupied mode", "occupied"),
    ("occupied period", "occupied"),
    ("occupied operation", "occupied"),
    ("occupied hours", "occupied"),
    ("economizer mode", "economizer"),
    ("economizer sequence", "economizer"),
    ("free cooling mode", "economizer"),
    ("airside economizer", "economizer"),
    ("air-side economizer", "economizer"),
    ("heating mode", "heating"),
    ("heating sequence", "heating"),
    ("heat mode", "heating"),
    ("cooling mode", "cooling"),
    ("cooling sequence", "cooling"),
    ("mechanical cooling", "cooling"),
    ("deadband mode", "deadband"),
    ("dead band mode", "deadband"),
    ("deadband operation", "deadband"),
    ("freeze protection", "emergency"),
    ("freeze stat", "emergency"),
    ("emergency mode", "emergency"),
    ("smoke mode", "emergency"),
    ("smoke shutdown", "emergency"),
    ("life safety", "emergency"),
    ("emergency shutdown", "emergency"),
    ("sequence of operation", "general"),
    ("sequence of operations", "general"),
    ("control sequence", "general"),
    ("control narrative", "general"),
    ("system operation", "general"),
]


def _detect_mode(text: str) -> SOOMode | None:
    lower = text.lower()
    for phrase, mode in _MODE_SECTION_MAP:
        if phrase in lower:
            return mode
    return None


# ---------------------------------------------------------------------------
# Safety-critical detection
# ---------------------------------------------------------------------------

_SAFETY_PHRASES = {
    "freeze stat",
    "freeze protection",
    "freeze alarm",
    "low limit",
    "smoke detector",
    "smoke alarm",
    "smoke shutdown",
    "life safety",
    "emergency shutoff",
    "emergency shutdown",
    "high limit",
    "hard lockout",
    "safety interlock",
    "lockout",
    "hard shutoff",
}


def _is_safety_critical(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in _SAFETY_PHRASES)


# ---------------------------------------------------------------------------
# Setpoint extraction
# ---------------------------------------------------------------------------

# Matches a named setpoint with an optional numeric value.
# Examples: "cooling setpoint of 75°F", "discharge air temperature setpoint 55 F"
_NAMED_SETPOINT_RE = re.compile(
    r"((?:heating|cooling|discharge|supply air|return air|outdoor air|space|room|"
    r"duct static|mixed air|preheat|reheat|humidity|dewpoint|"
    r"supply air temperature|return air temperature|"
    r"discharge air temperature|space temperature|"
    r"setback heating|setback cooling|night setback)\s*setpoint)"
    r"(?:\s+of)?\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*(°?[Ff]|°?[Cc]|%|psi|in\.?\s*wc|inwc|cfm)?",
    re.IGNORECASE,
)

# Matches any bare numeric value + unit (fallback for unlabeled setpoints).
_BARE_VALUE_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(°F|°C|%|psi|in\.?\s*WC|in\.?\s*wc|inwc|cfm|fpm|°f|°c)",
    re.IGNORECASE,
)

_UNIT_NORMALIZE: dict[str, str] = {
    "f": "°F", "°f": "°F", "c": "°C", "°c": "°C",
    "%": "%", "psi": "psi",
    "in. wc": "in. WC", "in.wc": "in. WC", "inwc": "in. WC",
    "cfm": "CFM", "fpm": "FPM",
}


def _normalize_unit(raw: str) -> str:
    return _UNIT_NORMALIZE.get(raw.strip().lower(), raw.strip())


def _extract_setpoint(sentence: str) -> tuple[str | None, float | None, str | None]:
    """Return (setpoint_name, setpoint_value, setpoint_unit) from a sentence."""
    match = _NAMED_SETPOINT_RE.search(sentence)
    if match:
        name = match.group(1).strip().lower()
        try:
            value = float(match.group(2))
        except (TypeError, ValueError):
            value = None
        unit = _normalize_unit(match.group(3) or "") or None
        return name, value, unit

    # Fallback: just a number + unit — no named setpoint
    match = _BARE_VALUE_RE.search(sentence)
    if match:
        try:
            value = float(match.group(1))
        except (TypeError, ValueError):
            value = None
        unit = _normalize_unit(match.group(2))
        return None, value, unit

    return None, None, None


# ---------------------------------------------------------------------------
# Condition / action split
# ---------------------------------------------------------------------------

# Trigger clauses that introduce a condition.
_CONDITION_RE = re.compile(
    r"^(?:when|if|upon|once|provided that|while|as long as|should|in the event)\s+(.+?)(?:[,;])",
    re.IGNORECASE,
)

# Action verbs that confirm this is a control step worth extracting.
_ACTION_VERBS = re.compile(
    r"\b(?:shall|will|enable|disable|modulate|open|close|start|stop|stage|energize|"
    r"de-energize|deenergize|activate|deactivate|generate|trigger|initiate|shut down|"
    r"shutdown|lock out|lockout|maintain|ramp|position|command|override)\b",
    re.IGNORECASE,
)


def _split_condition_action(sentence: str) -> tuple[str | None, str]:
    """Return (condition, action) from a sentence.

    Condition is the 'when/if' clause. Action is the consequence.
    If no condition is found, condition is None and action is the full sentence.
    """
    match = _CONDITION_RE.match(sentence.strip())
    if match:
        condition = match.group(1).strip().rstrip(",;")
        # Action is everything after the first comma/semicolon that ends the condition
        remainder = sentence[match.end():].strip().lstrip(",; ")
        action = remainder if remainder else sentence.strip()
        return condition, action
    return None, sentence.strip()


# ---------------------------------------------------------------------------
# Equipment tag detection
# ---------------------------------------------------------------------------

_EQUIP_TAG_RE = re.compile(r"\b([A-Z]{2,6}-\d{1,4}[A-Z]?)\b")

# Maps common equipment type abbreviations found in prose.
_EQUIP_TYPE_HINTS: dict[str, str] = {
    "rtu": "RTU", "rooftop unit": "RTU", "roof top unit": "RTU",
    "ahu": "AHU", "air handling unit": "AHU", "air handler": "AHU",
    "vav": "VAV", "variable air volume": "VAV",
    "fcu": "FCU", "fan coil": "FCU", "fan coil unit": "FCU",
    "mau": "MAU", "makeup air unit": "MAU", "make-up air": "MAU",
    "erv": "ERV", "energy recovery": "ERV",
    "hrv": "HRV",
    "chiller": "CHILLER", "chw": "CHILLER",
    "boiler": "BOILER", "hhw": "BOILER",
    "cooling tower": "CT",
    "pump": "PUMP",
    "exhaust fan": "EF", "exhaust unit": "EF",
    "supply fan": "SF",
}


def _detect_equipment_type(text: str) -> str | None:
    lower = text.lower()
    for phrase, eq_type in sorted(_EQUIP_TYPE_HINTS.items(), key=lambda x: -len(x[0])):
        if phrase in lower:
            return eq_type
    return None


def _detect_equipment_tag(text: str) -> str | None:
    match = _EQUIP_TAG_RE.search(text)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Section / sentence splitting
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(r"^#{1,6}\s+.+$")
_TABLE_ROW_RE = re.compile(r"^\s*\|")
_TABLE_SEP_RE = re.compile(r"^\s*\|?[-|: ]+\|")
_BULLET_RE = re.compile(r"^\s*[-*•]\s+(.+)$")
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")


def _is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if _TABLE_ROW_RE.match(stripped) or _TABLE_SEP_RE.match(stripped):
        return True
    if len(stripped) < 20:
        return True
    return False


def _extract_sentence_text(line: str) -> str:
    """Unwrap bullet/numbered list markers; return plain text."""
    m = _BULLET_RE.match(line)
    if m:
        return m.group(1).strip()
    m = _NUMBERED_RE.match(line)
    if m:
        return m.group(1).strip()
    return line.strip()


def _split_into_sentences(paragraph: str) -> list[str]:
    """Split a paragraph into individual sentences."""
    # Split on period-space, semicolons between clauses, and newlines.
    parts = re.split(r"(?<=[.;])\s+|\n", paragraph)
    sentences = []
    for part in parts:
        text = part.strip()
        if len(text) >= 20:
            sentences.append(text)
    return sentences


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

def _is_soo_section_header(line: str) -> bool:
    lower = line.lower().strip().lstrip("#").strip()
    soo_header_phrases = {
        "sequence of operation",
        "sequence of operations",
        "control sequence",
        "control narrative",
        "system operation",
        "occupied mode",
        "unoccupied mode",
        "heating mode",
        "cooling mode",
        "deadband",
        "economizer mode",
        "emergency mode",
        "freeze protection",
        "morning warmup",
        "night setback",
    }
    return any(phrase in lower for phrase in soo_header_phrases)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_soo_records(markdown_text: str) -> list[SOORecord]:
    """Extract structured SOO steps from normalized Markdown text.

    Scans for SOO section headers, then processes each line as a potential
    control step. Only lines containing a recognizable control action verb
    are converted to records. Returns an empty list if no SOO content is found.
    """
    lines = markdown_text.splitlines()
    records: list[SOORecord] = []

    current_mode: SOOMode = "general"
    current_section_ref = "SOO"
    in_soo_section = False
    step_index = 0
    # Track equipment from section context (header lines like "RTU-1: Occupied Mode")
    context_equip_tag: str | None = None
    context_equip_type: str | None = None

    for line in lines:
        stripped = line.strip()

        # --- Section header detection ---
        if _HEADER_RE.match(stripped) or (stripped.endswith(":") and len(stripped) < 80):
            detected_mode = _detect_mode(stripped)
            if detected_mode:
                current_mode = detected_mode
                in_soo_section = True
                # Use the header text as the source reference
                current_section_ref = stripped.lstrip("#").strip().rstrip(":")
                # Try to pick up equipment tag from header (e.g. "## RTU-1 — Occupied Mode")
                tag = _detect_equipment_tag(stripped)
                if tag:
                    context_equip_tag = tag
                    context_equip_type = _detect_equipment_type(stripped) or context_equip_type
            continue

        if _is_noise_line(line):
            continue

        # If we haven't hit a SOO section yet, check if this line has SOO signals
        if not in_soo_section:
            if _detect_mode(stripped):
                in_soo_section = True
                current_mode = _detect_mode(stripped) or "general"
                current_section_ref = stripped[:60]
            else:
                continue

        sentence = _extract_sentence_text(stripped)

        # Must contain an action verb to be worth extracting
        if not _ACTION_VERBS.search(sentence):
            continue

        condition, action = _split_condition_action(sentence)
        setpoint_name, setpoint_value, setpoint_unit = _extract_setpoint(sentence)
        safety = _is_safety_critical(sentence)

        # Equipment tag: prefer inline over context
        equip_tag = _detect_equipment_tag(sentence) or context_equip_tag
        equip_type = _detect_equipment_type(sentence) or context_equip_type

        # Mode is set by section headers only — inline mentions (e.g. "disable mechanical
        # cooling" inside an unoccupied-mode paragraph) must not override the section mode.
        effective_mode: SOOMode = current_mode

        # Confidence scoring
        has_condition = condition is not None
        has_setpoint = setpoint_value is not None
        if has_condition and has_setpoint:
            confidence = 0.88
        elif has_condition:
            confidence = 0.80
        elif has_setpoint:
            confidence = 0.75
        else:
            confidence = 0.65

        # Inferred if no explicit condition and no setpoint (pure inference from action verb alone)
        source_type = SOURCE_EXTRACTED if (has_condition or has_setpoint) else INFERRED

        remarks: list[str] = []
        if not has_condition:
            remarks.append("no condition clause detected; action only")
        if not equip_tag:
            remarks.append("equipment tag not identified in source text")

        step_index += 1

        record = SOORecord(
            equipment_tag=equip_tag,
            equipment_type=equip_type,
            mode=effective_mode,
            step_index=step_index,
            condition=condition,
            action=action,
            setpoint_name=setpoint_name,
            setpoint_value=setpoint_value,
            setpoint_unit=setpoint_unit,
            safety_critical=safety,
            source_text=sentence,
            source_reference=current_section_ref,
            confidence=confidence,
            source_type=source_type,
            remarks="; ".join(remarks) if remarks else None,
        )
        records.append(record)

    return records


def extract_soo_dicts(markdown_text: str) -> list[dict]:
    """Convenience wrapper — returns plain dicts instead of Pydantic models."""
    return [record.model_dump(mode="json") for record in extract_soo_records(markdown_text)]
