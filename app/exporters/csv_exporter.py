"""Tabular export utilities for structured records."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


def _normalize_record(record: object) -> dict:
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")  # type: ignore[call-arg]
    if isinstance(record, dict):
        return record
    raise TypeError(f"Unsupported record type: {type(record)!r}")


def _flatten_dict(data: dict, prefix: str = "") -> dict[str, object]:
    flat: dict[str, object] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten_dict(value, prefix=full_key))
        else:
            flat[full_key] = value
    return flat


def flatten_records(records: list[object]) -> list[dict[str, object]]:
    """Convert schema records or dictionaries into flat table rows."""
    return [_flatten_dict(_normalize_record(record)) for record in records]


def rows_to_dataframe(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def rows_to_csv_bytes(rows: list[dict[str, object]]) -> bytes:
    return rows_to_dataframe(rows).to_csv(index=False).encode("utf-8")


def tables_to_xlsx_bytes(sheets: dict[str, list[dict[str, object]]]) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, rows in sheets.items():
            rows_to_dataframe(rows).to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return buffer.getvalue()


def export_table_to_csv(rows: list[dict], output_path: str) -> str:
    """Export a list of dictionaries to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(rows_to_csv_bytes(rows))
    return str(path)


def export_tables_to_xlsx(sheets: dict[str, list[dict[str, object]]], output_path: str) -> str:
    """Export multiple flat row tables to a workbook."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tables_to_xlsx_bytes(sheets))
    return str(path)
