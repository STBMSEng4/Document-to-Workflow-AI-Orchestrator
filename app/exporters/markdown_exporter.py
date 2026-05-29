"""Markdown export utilities for SpecFlow AI.

Provides human-readable Markdown serializers for the three primary
deliverables: equipment schedule, I/O list, and sequence of operations.
"""

from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------------------------
# Raw file write
# ---------------------------------------------------------------------------

def export_markdown_report(content: str, output_path: str) -> str:
    """Write arbitrary Markdown content to a file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# Equipment schedule → Markdown
# ---------------------------------------------------------------------------

def equipment_records_to_markdown(records: list) -> str:
    """Serialize a list of EquipmentRecord (or dicts) to a Markdown table.

    Columns: Tag | Type | Name | Location | Manufacturer | Model | Protocol | Source | Confidence
    """
    lines = [
        "# Equipment Schedule\n",
        "| Tag | Type | Name | Location | Manufacturer | Model | Protocol | Source | Confidence |",
        "|---|---|---|---|---|---|---|---|---:|",
    ]
    for rec in records:
        d = rec.model_dump(mode="json") if hasattr(rec, "model_dump") else rec
        lines.append(
            f"| {d.get('equipment_tag') or ''} "
            f"| {d.get('equipment_type') or ''} "
            f"| {d.get('equipment_name') or ''} "
            f"| {d.get('location') or ''} "
            f"| {d.get('manufacturer') or ''} "
            f"| {d.get('model') or ''} "
            f"| {d.get('protocol') or ''} "
            f"| {d.get('source_type') or ''} "
            f"| {d.get('confidence', 0):.2f} |"
        )
    if len(lines) == 3:
        lines.append("| — | — | — | — | — | — | — | — | — |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# I/O list → Markdown
# ---------------------------------------------------------------------------

def point_records_to_markdown(records: list) -> str:
    """Serialize a list of PointRecord (or dicts) to a Markdown table.

    Columns: Equipment | Point Name | Code | Type | Unit | Role | Alarmed | Trended | Source | Confidence
    """
    lines = [
        "# I/O List\n",
        "| Equipment | Point Name | Code | Type | Unit | Role | Alarmed | Trended | Source | Confidence |",
        "|---|---|---|---|---|---|:---:|:---:|---|---:|",
    ]
    for rec in records:
        d = rec.model_dump(mode="json") if hasattr(rec, "model_dump") else rec
        alarmed = "Y" if d.get("alarmed") else ""
        trended = "Y" if d.get("trended") else ""
        lines.append(
            f"| {d.get('equipment_tag') or ''} "
            f"| {d.get('point_name') or ''} "
            f"| {d.get('point_code') or ''} "
            f"| {d.get('point_type') or ''} "
            f"| {d.get('engineering_unit') or ''} "
            f"| {d.get('point_role') or ''} "
            f"| {alarmed} "
            f"| {trended} "
            f"| {d.get('source_type') or ''} "
            f"| {d.get('confidence', 0):.2f} |"
        )
    if len(lines) == 3:
        lines.append("| — | — | — | — | — | — | — | — | — | — |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Sequence of operations → Markdown
# ---------------------------------------------------------------------------

def soo_records_to_markdown(records: list) -> str:
    """Serialize a list of SOORecord (or dicts) to a Markdown table.

    Columns: Step | Equipment | Mode | Condition | Action | Setpoint | Safety | Source | Confidence
    """
    lines = [
        "# Sequence of Operations\n",
        "| Step | Equipment | Mode | Condition | Action | Setpoint | Safety | Source | Confidence |",
        "|---:|---|---|---|---|---|:---:|---|---:|",
    ]
    for rec in records:
        d = rec.model_dump(mode="json") if hasattr(rec, "model_dump") else rec
        sp_val = d.get("setpoint_value")
        sp_unit = d.get("setpoint_unit") or ""
        sp = f"{sp_val}{sp_unit}" if sp_val is not None else ""
        safety = "Y" if d.get("safety_critical") else ""
        condition = (d.get("condition") or "").replace("|", "\\|")
        action = (d.get("action") or "").replace("|", "\\|")
        # Truncate long fields for readability in the table
        if len(condition) > 60:
            condition = condition[:57] + "..."
        if len(action) > 70:
            action = action[:67] + "..."
        lines.append(
            f"| {d.get('step_index') or ''} "
            f"| {d.get('equipment_tag') or ''} "
            f"| {d.get('mode') or ''} "
            f"| {condition} "
            f"| {action} "
            f"| {sp} "
            f"| {safety} "
            f"| {d.get('source_type') or ''} "
            f"| {d.get('confidence', 0):.2f} |"
        )
    if len(lines) == 3:
        lines.append("| — | — | — | — | — | — | — | — | — |")
    return "\n".join(lines) + "\n"
