"""Term normalizer for SpecFlow AI.

Parses knowledge_base/bms_ics_plc_terms.md and builds the term list
for the confidence scorer. Add a row to the MD table — it auto-loads here.

Table format expected:
  ## term_type
  | Term | Weight | Scope | Variants | Notes |
  | ... |  0.90  | all   | alias1, alias2 | ... |
"""

import re
from pathlib import Path

from app.schemas import VocabularyTerm

KB_PATH = Path(__file__).parents[2] / "knowledge_base" / "bms_ics_plc_terms.md"

# term_types that should be skipped during workflow scoring
SKIP_CATEGORIES = {"skip_term"}

# term_types treated as skip/suppress signals (matched terms suppress output)
SUPPRESS_CATEGORIES = {"skip_term"}


def _parse_table_row(line: str) -> list[str] | None:
    """Parse a single Markdown table row into cells."""
    line = line.strip()
    if not line.startswith("|") or line.startswith("| Term") or line.startswith("|---"):
        return None
    cells = [c.strip() for c in line.strip("|").split("|")]
    return cells if len(cells) >= 2 else None


def parse_kb_file(path: Path) -> list[dict]:
    """Parse bms_ics_plc_terms.md into a list of validated term dicts."""
    terms: list[dict] = []
    current_type = "unknown"

    with open(path, encoding="utf-8") as f:
        for line in f:
            # Detect machine-readable KB section header: ## equipment_type
            # Ignore human-facing headers like "## Term Type Index".
            header_match = re.match(r"^##\s+([a-z0-9_]+)\s*$", line.strip())
            if header_match:
                current_type = header_match.group(1).lower()
                continue

            if current_type == "unknown":
                continue

            row = _parse_table_row(line)
            if row is None:
                continue

            # Columns: Term | Weight | Scope | Variants | Notes
            term = row[0] if len(row) > 0 else ""
            weight = float(row[1]) if len(row) > 1 and row[1] else 0.5
            scope = row[2] if len(row) > 2 else "all"
            variants_raw = row[3] if len(row) > 3 else ""
            notes = row[4] if len(row) > 4 else ""

            if not term or term.startswith("---"):
                continue

            term_model = VocabularyTerm.from_kb_row(
                term=term,
                weight=weight,
                category=current_type,
                scope=scope,
                variants=variants_raw,
                notes=notes,
                is_skip=current_type in SUPPRESS_CATEGORIES,
            )
            terms.append(term_model.model_dump())

    return terms


def load_kb_models() -> list[VocabularyTerm]:
    """Load terms from KB file as validated schema models."""
    return [VocabularyTerm.model_validate(t) for t in load_kb_terms()]


def get_term_models() -> list[VocabularyTerm]:
    """Return non-suppressing KB terms as validated schema models."""
    return [VocabularyTerm.model_validate(t) for t in get_term_list()]


def load_kb_terms() -> list[dict]:
    """Load terms from KB file. Returns parsed list or fallback if file missing."""
    if KB_PATH.exists():
        try:
            terms = parse_kb_file(KB_PATH)
            if terms:
                return terms
        except Exception:
            pass
    return _fallback_terms()


def get_term_list() -> list[dict]:
    """Return the full scored term list (excludes skip_terms from workflow scoring)."""
    return [t for t in load_kb_terms() if not t.get("is_skip")]


def get_skip_terms() -> list[str]:
    """Return list of term strings that should suppress output when matched."""
    all_terms = load_kb_terms()
    skip = []
    for t in all_terms:
        if t.get("is_skip"):
            skip.append(t["term"].lower())
            skip.extend(a.lower() for a in t.get("aliases", []))
    return skip


def _fallback_terms() -> list[dict]:
    """Minimal fallback if KB file is missing or unparseable."""
    fallback = [
        VocabularyTerm(term="BAS", normalized_term="BAS", category="platform", weight=1.0, aliases=["building automation system", "BMS"]),
        VocabularyTerm(term="DDC", normalized_term="DDC", category="platform", weight=0.9, aliases=["direct digital control"]),
        VocabularyTerm(term="ahu", normalized_term="AHU", category="equipment_type", weight=1.0, aliases=["air handling unit", "air handler", "AHU"]),
        VocabularyTerm(term="rtu", normalized_term="RTU", category="equipment_type", weight=1.0, aliases=["rooftop unit", "packaged unit", "RTU"]),
        VocabularyTerm(term="vav", normalized_term="VAV", category="equipment_type", weight=1.0, aliases=["variable air volume", "VAV box", "VAV"]),
        VocabularyTerm(term="PLC", normalized_term="PLC", category="plc_hardware", weight=1.0, aliases=["programmable logic controller"]),
        VocabularyTerm(term="BACnet", normalized_term="BACnet", category="protocol", weight=1.0, aliases=["BACnet/IP", "BACnet MS/TP", "BACnet MSTP"]),
        VocabularyTerm(term="Modbus", normalized_term="Modbus", category="protocol", weight=0.9, aliases=["Modbus TCP", "Modbus RTU"]),
        VocabularyTerm(term="point list", normalized_term="Point List", category="doc_signal", weight=1.0, aliases=["points list", "I/O list", "IO list"]),
        VocabularyTerm(term="commissioning", normalized_term="Commissioning", category="doc_signal", weight=0.9, aliases=["Cx", "functional testing", "checkout"]),
    ]
    return [item.model_dump() for item in fallback]
