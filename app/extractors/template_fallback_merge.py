"""Template fallback merge logic for structured point extraction."""

from __future__ import annotations

import re

from app.schemas import EquipmentRecord, PointRecord
from app.extractors.workflow_extractor import _POINTS


_POINT_TYPE_OBJECT_MAP = {
    "AI": "analogInput",
    "AO": "analogOutput",
    "DI": "binaryInput",
    "DO": "binaryOutput",
    "AV": "analogValue",
    "BV": "binaryValue",
    "BI": "binaryInput",
    "BO": "binaryOutput",
    "MSI": "multiStateInput",
    "MSO": "multiStateOutput",
    "MSV": "multiStateValue",
}


def _normalized_key(point_name: str, point_code: str | None) -> str:
    if point_code:
        return point_code.strip().upper()
    return re.sub(r"[^a-z0-9]+", " ", point_name.lower()).strip()


def _signal_type_for(point_type: str) -> str:
    if point_type in {"AI", "AO", "AV", "SP"}:
        return "analog"
    if point_type in {"DI", "DO", "BI", "BO", "Status", "Alarm"}:
        return "binary"
    if point_type in {"MSI", "MSO", "MSV"}:
        return "multistate"
    if point_type == "Network":
        return "network"
    if point_type == "Calc":
        return "calculated"
    return "text"


def _point_role_for(point_name: str, point_type: str) -> str:
    name = point_name.lower()
    if point_type == "SP" or "setpoint" in name:
        return "setpoint"
    if point_type in {"DO", "AO", "BO", "MSO"} or "command" in name or name.endswith(" cmd"):
        return "command"
    if point_type in {"DI", "BI", "Status"} or "status" in name or name.endswith(" sts"):
        return "status"
    if point_type == "Alarm" or "alarm" in name or "fault" in name:
        return "alarm"
    return "sensor"


def build_template_point_records(equipment_record: EquipmentRecord) -> list[PointRecord]:
    """Build template-default point rows for one equipment record."""
    template_rows = _POINTS.get(equipment_record.equipment_type.upper(), [])
    records: list[PointRecord] = []
    for row in template_rows:
        point_type = row["io"]
        records.append(
            PointRecord(
                equipment_tag=equipment_record.equipment_tag,
                equipment_type=equipment_record.equipment_type,
                point_name=row["name"],
                point_code=row["abbr"],
                point_type=point_type,
                signal_type=_signal_type_for(point_type),
                point_role=_point_role_for(row["name"], point_type),
                object_type=_POINT_TYPE_OBJECT_MAP.get(point_type),
                engineering_unit=row["unit"],
                description=row["desc"],
                source_reference=f"Template fallback / {equipment_record.equipment_type}",
                confidence=0.62,
                source_type="template_default",
            )
        )
    return records


def merge_point_records_with_template_defaults(
    point_records: list[PointRecord],
    equipment_records: list[EquipmentRecord],
) -> list[PointRecord]:
    """Keep extracted points primary and use template rows only to fill gaps."""
    merged: list[PointRecord] = list(point_records)
    existing_keys_by_equipment: dict[str, set[str]] = {}

    for point in point_records:
        if not point.equipment_tag:
            continue
        existing_keys_by_equipment.setdefault(point.equipment_tag, set()).add(
            _normalized_key(point.point_name, point.point_code)
        )

    for equipment in equipment_records:
        tag = equipment.equipment_tag
        existing_keys = existing_keys_by_equipment.setdefault(tag, set())
        template_points = build_template_point_records(equipment)
        for point in template_points:
            key = _normalized_key(point.point_name, point.point_code)
            if key in existing_keys:
                continue
            merged.append(point)
            existing_keys.add(key)

    return merged
