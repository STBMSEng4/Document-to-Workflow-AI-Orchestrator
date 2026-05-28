"""Equipment-tag detection, grouping, and point mapping helpers."""

from __future__ import annotations

import re

from app.schemas import EquipmentRecord, PointRecord


_TAG_PATTERN = re.compile(r"\b([A-Za-z]{2,8})[-_ ]?(\d{1,4}[A-Za-z]?)\b")


def canonicalize_equipment_tag(tag: str | None) -> str | None:
    if not tag:
        return None
    text = tag.strip().upper().replace("_", "-")
    text = re.sub(r"\s+", "-", text)
    return text or None


def detect_equipment_tags(text: str) -> list[str]:
    """Detect likely HVAC/BMS equipment tags from free text."""
    found: list[str] = []
    for prefix, suffix in _TAG_PATTERN.findall(text):
        tag = canonicalize_equipment_tag(f"{prefix}-{suffix}")
        if tag and tag not in found:
            found.append(tag)
    return found


def index_equipment_by_tag(equipment_records: list[EquipmentRecord]) -> dict[str, EquipmentRecord]:
    index: dict[str, EquipmentRecord] = {}
    for record in equipment_records:
        tag = canonicalize_equipment_tag(record.equipment_tag)
        if tag:
            index[tag] = record
    return index


def group_equipment_records(equipment_records: list[EquipmentRecord]) -> dict[str, list[EquipmentRecord]]:
    grouped: dict[str, list[EquipmentRecord]] = {}
    for record in equipment_records:
        tag = canonicalize_equipment_tag(record.equipment_tag) or "UNASSIGNED"
        grouped.setdefault(tag, []).append(record)
    return grouped


def map_point_to_equipment(
    point: PointRecord,
    equipment_records: list[EquipmentRecord],
    source_hint: str = "",
) -> tuple[str | None, str | None]:
    """Return the best equipment tag/type match for a point record."""
    equipment_index = index_equipment_by_tag(equipment_records)

    direct_tag = canonicalize_equipment_tag(point.equipment_tag)
    if direct_tag and direct_tag in equipment_index:
        record = equipment_index[direct_tag]
        return record.equipment_tag, record.equipment_type

    point_tags = detect_equipment_tags(
        " ".join(
            filter(
                None,
                [
                    point.point_name,
                    point.description or "",
                    point.location or "",
                    source_hint,
                ],
            )
        )
    )
    for tag in point_tags:
        if tag in equipment_index:
            record = equipment_index[tag]
            return record.equipment_tag, record.equipment_type

    if direct_tag and not point.equipment_type:
        inferred_type = direct_tag.split("-")[0]
        return direct_tag, inferred_type

    return point.equipment_tag, point.equipment_type


def group_points_by_equipment(
    point_records: list[PointRecord],
    equipment_records: list[EquipmentRecord],
) -> dict[str, list[PointRecord]]:
    grouped: dict[str, list[PointRecord]] = {}
    for point in point_records:
        tag, equipment_type = map_point_to_equipment(point, equipment_records)
        if tag and point.equipment_tag != tag:
            point.equipment_tag = tag
        if equipment_type and point.equipment_type != equipment_type:
            point.equipment_type = equipment_type
        group_key = canonicalize_equipment_tag(point.equipment_tag) or "UNASSIGNED"
        grouped.setdefault(group_key, []).append(point)
    return grouped
