"""Structured equipment extraction from normalized Markdown."""

from __future__ import annotations

import re

from app.extractors._markdown_tables import MarkdownTable, parse_markdown_tables
from app.extractors.source_labels import INFERRED, SOURCE_EXTRACTED, append_remark
from app.normalizers.term_normalizer import get_term_models
from app.schemas import EquipmentRecord


_EQUIPMENT_HEADER_HINTS = {
    "equipment_tag",
    "tag",
    "equipment",
    "equipment_name",
    "equipment_type",
    "type",
    "model",
    "manufacturer",
}

_EQUIPMENT_STRONG_HINTS = {
    "equipment",
    "equipment_name",
    "equipment_type",
    "type",
    "model",
    "manufacturer",
}

_HEADER_MAP = {
    "equipment_tag": {"tag", "equipment_tag", "unit", "unit_tag", "device_tag", "equip_tag"},
    "equipment_name": {"equipment", "equipment_name", "name", "description", "unit_name"},
    "equipment_type": {"equipment_type", "type", "unit_type", "equip_type"},
    "location": {"location", "room", "area", "served_by_location"},
    "served_area": {"served_area", "served_space", "zone", "area_served", "serves"},
    "manufacturer": {"manufacturer", "mfr", "make", "vendor"},
    "model": {"model", "model_number", "catalog_number"},
    "serial_number": {"serial", "serial_number"},
    "quantity": {"qty", "quantity"},
    "service": {"service", "duty", "application"},
    "protocol": {"protocol", "network", "communications"},
    "system": {"system", "discipline"},
    "subsystem": {"subsystem"},
    "remarks": {"remarks", "notes", "comment", "comments"},
}

_ATTRIBUTE_HEADER_MAP = {
    "electrical": {
        "voltage": {"voltage", "v", "power"},
        "phase": {"phase", "ph"},
        "frequency_hz": {"frequency", "hz"},
        "minimum_circuit_ampacity_amps": {"mca", "minimum_circuit_ampacity"},
        "maximum_overcurrent_protection_amps": {"mop", "mocp", "maximum_overcurrent_protection"},
        "full_load_amps": {"fla", "full_load_amps"},
        "fan_motor_hp": {"fan_motor_hp", "fan_hp", "supply_fan_hp"},
        "fan_motor_kw": {"fan_motor_kw", "fan_kw"},
        "compressor_motor_hp": {"compressor_hp"},
        "compressor_motor_kw": {"compressor_kw"},
        "power_kw": {"kw", "power_kw"},
        "starter_type": {"starter", "starter_type"},
    },
    "airflow": {
        "airflow_cfm": {"cfm", "airflow", "supply_airflow"},
        "minimum_airflow_cfm": {"min_cfm", "minimum_cfm"},
        "maximum_airflow_cfm": {"max_cfm", "maximum_cfm"},
        "outdoor_air_cfm": {"oa_cfm", "outdoor_air"},
        "return_air_cfm": {"ra_cfm", "return_air"},
        "exhaust_air_cfm": {"ea_cfm", "exhaust_air"},
        "relief_air_cfm": {"relief_cfm", "relief_air"},
        "external_static_in_wg": {"esp", "external_static", "external_static_in_wg"},
        "total_static_in_wg": {"tsp", "total_static", "total_static_in_wg"},
        "fan_type": {"fan_type"},
        "fan_quantity": {"fan_qty", "fan_quantity"},
        "filter_type": {"filter_type"},
        "filter_merv": {"merv", "filter_merv"},
        "filter_face_size": {"filter_size", "filter_face_size"},
    },
    "cooling": {
        "cooling_type": {"cooling_type"},
        "cooling_capacity_tons": {"tons", "cooling_tons"},
        "cooling_capacity_btuh": {"cooling_btuh", "cooling_capacity"},
        "sensible_capacity_btuh": {"sensible_btuh", "sensible_capacity"},
        "latent_capacity_btuh": {"latent_btuh", "latent_capacity"},
        "eer": {"eer"},
        "ieer": {"ieer"},
        "seer": {"seer"},
        "cop": {"cop"},
        "refrigerant": {"refrigerant"},
        "compressor_quantity": {"compressor_qty", "number_of_compressors"},
        "compressor_stages": {"compressor_stages", "cooling_stages"},
        "compressor_type": {"compressor_type"},
        "condenser_type": {"condenser_type"},
    },
    "heating": {
        "heating_type": {"heating_type"},
        "heating_capacity_btuh": {"heating_btuh", "heating_capacity"},
        "heating_capacity_mbh": {"mbh", "heating_mbh"},
        "heating_input_btuh": {"heating_input", "input_btuh"},
        "heating_output_btuh": {"heating_output", "output_btuh"},
        "thermal_efficiency_pct": {"efficiency", "thermal_efficiency"},
        "heating_stages": {"heating_stages"},
        "electric_heat_kw": {"electric_heat_kw", "heat_kw"},
        "fuel_type": {"fuel", "fuel_type"},
        "reheat_type": {"reheat_type"},
        "reheat_capacity_btuh": {"reheat_btuh", "reheat_capacity"},
    },
    "hydronic": {
        "chilled_water_gpm": {"chw_gpm"},
        "heating_hot_water_gpm": {"hhw_gpm", "hw_gpm"},
        "condenser_water_gpm": {"cw_gpm", "condenser_water_gpm"},
        "fluid_type": {"fluid", "fluid_type"},
        "pipe_size": {"pipe_size", "line_size"},
        "pressure_drop_ft_head": {"head_ft", "pressure_drop_ft"},
        "pressure_drop_psi": {"pressure_drop_psi", "delta_p_psi"},
        "valve_type": {"valve", "valve_type"},
        "valve_size": {"valve_size"},
        "valve_cv": {"cv", "valve_cv"},
        "actuator_type": {"actuator", "actuator_type"},
    },
    "ventilation": {
        "heat_recovery_type": {"heat_recovery_type", "recovery_type"},
        "sensible_effectiveness_pct": {"sensible_effectiveness"},
        "latent_effectiveness_pct": {"latent_effectiveness"},
        "frost_control_type": {"frost_control"},
    },
    "dampers_and_economizer": {
        "damper_type": {"damper", "damper_type"},
        "damper_size": {"damper_size"},
        "damper_leakage_class": {"damper_leakage", "leakage_class"},
        "blade_type": {"blade_type"},
        "economizer_type": {"economizer", "economizer_type"},
        "actuator_fail_position": {"fail_position", "actuator_fail_position"},
    },
    "controls": {
        "controller_manufacturer": {"controller_manufacturer", "controller_make"},
        "controller_model": {"controller_model", "controller"},
        "network_type": {"network_type"},
        "bacnet_instance": {"bacnet_instance", "device_instance"},
        "mstp_mac": {"mstp_mac", "mac"},
        "ip_addressing": {"ip", "ip_address", "ip_addressing"},
        "points_count_di": {"di_count"},
        "points_count_do": {"do_count"},
        "points_count_ai": {"ai_count"},
        "points_count_ao": {"ao_count"},
    },
    "mechanical": {
        "dimensions": {"dimensions", "dim"},
        "cabinet_size": {"cabinet_size"},
        "weight_lb": {"weight", "weight_lb"},
        "sound_level_db": {"sound", "sound_db"},
        "installation_orientation": {"orientation"},
        "mounting_type": {"mounting", "mounting_type"},
        "inlet_size": {"inlet_size"},
        "outlet_size": {"outlet_size"},
        "coil_type": {"coil", "coil_type"},
        "drain_pan_type": {"drain_pan"},
    },
    "vrf": {
        "system_type": {"vrf_type", "system_type"},
        "outdoor_unit_count": {"outdoor_units"},
        "indoor_unit_count": {"indoor_units"},
        "connected_capacity_ratio_pct": {"connection_ratio", "connected_capacity_ratio"},
        "branch_selector_required": {"branch_selector"},
        "total_piping_length_ft": {"total_pipe_length"},
        "longest_run_length_ft": {"longest_run"},
        "vertical_separation_ft": {"vertical_separation"},
        "heat_recovery_configuration": {"heat_recovery_configuration"},
    },
}

_STRING_ATTRIBUTE_FIELDS = {
    "voltage",
    "phase",
    "power_source",
    "disconnect_type",
    "starter_type",
    "fan_type",
    "fan_drive_type",
    "fan_arrangement",
    "filter_type",
    "filter_merv",
    "filter_face_size",
    "cooling_type",
    "refrigerant",
    "compressor_type",
    "condenser_type",
    "cooling_coil_type",
    "heating_type",
    "fuel_type",
    "preheat_coil_type",
    "reheat_type",
    "fluid_type",
    "pipe_size",
    "valve_type",
    "valve_size",
    "valve_closeoff_pressure",
    "actuator_type",
    "heat_recovery_type",
    "frost_control_type",
    "damper_type",
    "damper_size",
    "damper_leakage_class",
    "blade_type",
    "economizer_type",
    "actuator_fail_position",
    "controller_manufacturer",
    "controller_model",
    "network_type",
    "ip_addressing",
    "sequence_reference",
    "dimensions",
    "cabinet_size",
    "installation_orientation",
    "mounting_type",
    "inlet_size",
    "outlet_size",
    "coil_type",
    "access_section",
    "drain_pan_type",
    "system_type",
    "heat_recovery_configuration",
}


def _canonical_equipment_types() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for term in get_term_models():
        if term.category != "equipment_type":
            continue
        canonical = term.normalized_term.upper()
        mapping[term.term.lower()] = canonical
        mapping[canonical.lower()] = canonical
        for alias in term.aliases:
            mapping[alias.lower()] = canonical
    return mapping


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


def _infer_equipment_type(raw: str, mapping: dict[str, str]) -> str | None:
    text = raw.strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in mapping:
        return mapping[lowered]
    for phrase, canonical in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(phrase)}\b", lowered):
            return canonical
    tag_match = re.match(r"([A-Za-z]{2,6})[-\s_]?\d+", text)
    if tag_match:
        prefix = tag_match.group(1).lower()
        if prefix in mapping:
            return mapping[prefix]
    return None


def _looks_like_equipment_table(table: MarkdownTable) -> bool:
    header_set = set(table.headers)
    hint_count = len(header_set & _EQUIPMENT_HEADER_HINTS)
    strong_hint_count = len(header_set & _EQUIPMENT_STRONG_HINTS)
    return hint_count >= 2 and strong_hint_count >= 1


def _build_equipment_record(row: dict[str, str], source_reference: str, mapping: dict[str, str]) -> EquipmentRecord | None:
    data: dict[str, object] = {
        "source_reference": source_reference,
        "confidence": 0.85,
        "attributes": {},
        "source_type": SOURCE_EXTRACTED,
    }
    inference_notes: list[str] = []

    for target, aliases in _HEADER_MAP.items():
        header = _find_header(row, aliases)
        if header and row.get(header, "").strip():
            value = row[header].strip()
            if target == "quantity":
                coerced = _coerce_number(value)
                data[target] = int(coerced) if isinstance(coerced, (int, float)) else None
            else:
                data[target] = value

    explicit_equipment_type = bool(data.get("equipment_type"))
    type_candidate_parts = [
        str(data.get("equipment_type") or ""),
        str(data.get("equipment_name") or ""),
        str(data.get("equipment_tag") or ""),
        str(data.get("service") or ""),
    ]
    inferred_type = _infer_equipment_type(" ".join(type_candidate_parts), mapping)
    if inferred_type:
        data["equipment_type"] = inferred_type
        if not explicit_equipment_type:
            inference_notes.append("equipment_type inferred from name/tag/service context")

    if not data.get("equipment_tag"):
        name = str(data.get("equipment_name") or "")
        tag_match = re.search(r"\b[A-Za-z]{2,6}[-_ ]?\d+\b", name)
        if tag_match:
            data["equipment_tag"] = tag_match.group(0).replace(" ", "-").upper()
            inference_notes.append("equipment_tag inferred from equipment name")

    attributes: dict[str, dict[str, object]] = {}
    for bucket, field_map in _ATTRIBUTE_HEADER_MAP.items():
        bucket_data: dict[str, object] = {}
        for field_name, aliases in field_map.items():
            header = _find_header(row, aliases)
            if not header:
                continue
            raw_value = row.get(header, "").strip()
            if not raw_value:
                continue
            if field_name in {"branch_selector_required", "low_leakage_damper", "purge_section_present"}:
                bucket_data[field_name] = _coerce_bool(raw_value)
            else:
                coerced = _coerce_number(raw_value)
                if field_name in _STRING_ATTRIBUTE_FIELDS:
                    bucket_data[field_name] = raw_value
                else:
                    bucket_data[field_name] = coerced if coerced is not None and any(ch.isdigit() for ch in raw_value) else raw_value
        if bucket_data:
            attributes[bucket] = bucket_data

    data["attributes"] = attributes

    if not data.get("equipment_tag") or not data.get("equipment_type"):
        return None

    if inference_notes:
        data["source_type"] = INFERRED
        data["remarks"] = append_remark(
            str(data.get("remarks") or "") or None,
            "; ".join(inference_notes),
        )

    return EquipmentRecord.model_validate(data)


def extract_equipment_records(markdown_text: str) -> list[EquipmentRecord]:
    """Extract structured equipment records from normalized Markdown."""
    mapping = _canonical_equipment_types()
    records: list[EquipmentRecord] = []
    seen: set[tuple[str, str, str]] = set()

    for table in parse_markdown_tables(markdown_text):
        if not _looks_like_equipment_table(table):
            continue
        for row in table.rows:
            record = _build_equipment_record(row, table.source_reference, mapping)
            if not record:
                continue
            key = (record.equipment_tag, record.equipment_type, record.source_reference)
            if key in seen:
                continue
            seen.add(key)
            records.append(record)

    return records


def extract_equipment_dicts(markdown_text: str) -> list[dict]:
    return [record.model_dump(mode="json") for record in extract_equipment_records(markdown_text)]
