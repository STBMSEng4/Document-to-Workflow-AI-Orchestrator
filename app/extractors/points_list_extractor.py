"""Structured points-list extraction from normalized Markdown."""

from __future__ import annotations

import re

from app.extractors._markdown_tables import MarkdownTable, parse_markdown_tables
from app.extractors.grouping import map_point_to_equipment
from app.extractors.source_labels import INFERRED, SOURCE_EXTRACTED, append_remark
from app.schemas import EquipmentRecord, PointRecord


_POINT_HEADER_HINTS = {
    "point",
    "point_name",
    "point_description",
    "io",
    "io_type",
    "type",
    "unit",
    "signal",
    "equipment_tag",
    "controller",
}

_POINT_HEADER_MAP = {
    "equipment_tag": {"equipment_tag", "equipment", "tag", "device_tag", "unit_tag"},
    "equipment_type": {"equipment_type", "unit_type", "device_type"},
    "controller_tag": {"controller", "controller_tag", "ddc_controller"},
    "controller_model": {"controller_model"},
    "location": {"location", "room", "area"},
    "point_name": {"point_name", "point", "name", "description", "point_description"},
    "normalized_point_name": {"normalized_point_name"},
    "point_code": {"point_code", "abbr", "abbreviation", "code", "point_id"},
    "point_type": {"io", "io_type", "point_type", "type", "object_type_short"},
    "signal_type": {"signal", "signal_type"},
    "engineering_unit": {"unit", "units", "engineering_unit"},
    "object_type": {"object_type", "bacnet_object_type"},
    "object_instance": {"instance", "object_instance", "bacnet_instance", "bacnet_device_instance"},
    "protocol": {"protocol", "network"},
    "network_address": {"register", "address", "network_address", "mac", "ip"},
    "display_precision": {"precision", "display_precision"},
    "range_min": {"min", "range_min", "low_limit"},
    "range_max": {"max", "range_max", "high_limit"},
    "default_value": {"default", "default_value", "setpoint", "value"},
    "description": {"description", "sequence_note", "notes", "remarks"},
}

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

_ANALOG_UNITS = {"°f", "f", "%", "cfm", "psi", "in. wc", "inwc", "ppm", "kw", "gpm", "hz", "ms"}


def _find_header(row: dict[str, str], aliases: set[str]) -> str | None:
    for key in row:
        if key in aliases:
            return key
    return None


def _coerce_number(value: str) -> float | int | None:
    text = value.strip()
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    if not match:
        return None
    number = float(match.group(0))
    return int(number) if number.is_integer() else number


def _coerce_bool(value: str) -> bool | None:
    text = value.strip().lower()
    if text in {"yes", "true", "y", "required"}:
        return True
    if text in {"no", "false", "n", "not required"}:
        return False
    return None


def _looks_like_point_table(table: MarkdownTable) -> bool:
    score = 0
    for header in table.headers:
        if header in _POINT_HEADER_HINTS:
            score += 1
        if "point" in header or header in {"ai", "ao", "di", "do"}:
            score += 1
    return score >= 2


def _infer_point_type(raw_type: str, point_name: str, unit: str) -> str:
    text = (raw_type or "").strip().upper()
    if text in _POINT_TYPE_OBJECT_MAP or text in {"SP", "STATUS", "ALARM", "CALC", "NETWORK"}:
        return text
    name_lower = point_name.lower()
    unit_lower = unit.strip().lower()
    if "setpoint" in name_lower or name_lower.endswith(" sp"):
        return "SP"
    if "alarm" in name_lower:
        return "Alarm"
    if "status" in name_lower or name_lower.endswith(" sts"):
        return "Status"
    if unit_lower in _ANALOG_UNITS:
        return "AI"
    return "AV"


def _infer_signal_type(point_type: str, unit: str) -> str:
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
    return "analog" if unit.strip() else "text"


def _infer_point_role(point_name: str, point_type: str) -> str:
    name = point_name.lower()
    if point_type == "SP" or "setpoint" in name:
        return "setpoint"
    if point_type in {"DO", "AO", "BO", "MSO"} or "command" in name or name.endswith(" cmd"):
        return "command"
    if point_type in {"DI", "BI", "Status"} or "status" in name or name.endswith(" sts"):
        return "status"
    if point_type == "Alarm" or "alarm" in name or "fault" in name:
        return "alarm"
    if "interlock" in name or "proof" in name or "safety" in name:
        return "interlock"
    if point_type == "Network":
        return "network"
    if point_type == "Calc":
        return "calculated"
    return "sensor"


def _build_point_record(
    row: dict[str, str],
    source_reference: str,
    equipment_records: list[EquipmentRecord],
) -> PointRecord | None:
    data: dict[str, object] = {
        "source_reference": source_reference,
        "confidence": 0.88,
        "source_type": SOURCE_EXTRACTED,
    }
    inference_notes: list[str] = []

    for target, aliases in _POINT_HEADER_MAP.items():
        header = _find_header(row, aliases)
        if not header:
            continue
        raw_value = row.get(header, "").strip()
        if not raw_value:
            continue
        if target in {"object_instance", "display_precision", "range_min", "range_max"}:
            data[target] = _coerce_number(raw_value)
        else:
            data[target] = raw_value

    point_name = str(data.get("point_name") or "")
    if not point_name:
        return None
    explicit_equipment_tag = bool(data.get("equipment_tag"))

    raw_point_type = str(data.get("point_type") or "")
    unit = str(data.get("engineering_unit") or "")
    point_type = _infer_point_type(raw_point_type, point_name, unit)
    data["point_type"] = point_type
    if not raw_point_type:
        inference_notes.append("point_type inferred from point name/unit context")
    data["signal_type"] = data.get("signal_type") or _infer_signal_type(point_type, unit)
    data["point_role"] = _infer_point_role(point_name, point_type)
    data["object_type"] = data.get("object_type") or _POINT_TYPE_OBJECT_MAP.get(point_type)

    description_text = str(data.get("description") or "").lower()
    data["writable"] = data.get("writable")
    if data["writable"] is None:
        data["writable"] = point_type in {"AO", "AV", "BO", "BV", "MSO", "MSV", "SP"}
    data["commandable"] = data.get("commandable")
    if data["commandable"] is None:
        data["commandable"] = point_type in {"AO", "DO", "BO", "MSO", "SP"} or "command" in point_name.lower()
    data["alarmed"] = data.get("alarmed")
    if data["alarmed"] is None:
        data["alarmed"] = point_type == "Alarm" or "alarm" in point_name.lower() or "fault" in point_name.lower()
    data["trended"] = data.get("trended")
    if data["trended"] is None:
        data["trended"] = point_type in {"AI", "AO", "AV"} or unit.strip() != ""
    data["required"] = data.get("required")
    if data["required"] is None:
        data["required"] = True
    data["safety_interlock"] = data.get("safety_interlock")
    if data["safety_interlock"] is None:
        data["safety_interlock"] = any(keyword in description_text or keyword in point_name.lower() for keyword in ["freeze", "smoke", "safety", "proof"])

    if inference_notes:
        data["source_type"] = INFERRED
        data["remarks"] = append_remark(
            str(data.get("remarks") or "") or None,
            "; ".join(inference_notes),
        )

    record = PointRecord.model_validate(data)
    had_equipment_link = bool(record.equipment_tag and record.equipment_type)
    equipment_tag, equipment_type = map_point_to_equipment(record, equipment_records, source_hint=source_reference)
    if equipment_tag and not record.equipment_tag:
        record.equipment_tag = equipment_tag
    if equipment_type and not record.equipment_type:
        record.equipment_type = equipment_type
    if not explicit_equipment_tag and (equipment_tag or equipment_type) and not had_equipment_link:
        record.source_type = INFERRED
        record.remarks = append_remark(record.remarks, "equipment link inferred from source context")
    return record


def extract_point_records(markdown_text: str, equipment_records: list[EquipmentRecord] | None = None) -> list[PointRecord]:
    """Extract structured point records from normalized Markdown."""
    equipment_records = equipment_records or []
    records: list[PointRecord] = []
    seen: set[tuple[str | None, str, str]] = set()

    for table in parse_markdown_tables(markdown_text):
        if not _looks_like_point_table(table):
            continue
        for row in table.rows:
            record = _build_point_record(row, table.source_reference, equipment_records)
            if not record:
                continue
            key = (record.equipment_tag, record.point_name, record.source_reference)
            if key in seen:
                continue
            seen.add(key)
            records.append(record)

    return records


def extract_point_dicts(markdown_text: str, equipment_records: list[EquipmentRecord] | None = None) -> list[dict]:
    return [
        record.model_dump(mode="json")
        for record in extract_point_records(markdown_text, equipment_records=equipment_records)
    ]
