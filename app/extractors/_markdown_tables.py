"""Shared Markdown table parsing helpers for structured extractors."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class MarkdownTable:
    headers: list[str]
    rows: list[dict[str, str]]
    source_reference: str


def _clean_header(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w%/]+", "_", value)
    return value.strip("_")


def _split_cells(line: str) -> list[str] | None:
    text = line.strip()
    if not text.startswith("|"):
        return None
    cells = [cell.strip() for cell in text.strip("|").split("|")]
    return cells


def _expand_inline_table_rows(markdown_text: str) -> list[str]:
    expanded_lines: list[str] = []
    pattern = re.compile(r"\|.*?\|(?=\s+\||$)")

    for raw_line in markdown_text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("|") and " | |" in raw_line:
            segments = [segment.strip() for segment in pattern.findall(raw_line) if segment.strip()]
            if len(segments) > 1:
                expanded_lines.extend(segments)
                continue
        expanded_lines.append(raw_line)

    return expanded_lines


def parse_markdown_tables(markdown_text: str) -> list[MarkdownTable]:
    """Parse Markdown tables and associate them with the closest heading."""
    lines = _expand_inline_table_rows(markdown_text)
    tables: list[MarkdownTable] = []
    current_heading = "Document"
    i = 0
    table_counter = 0

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#"):
            current_heading = line.lstrip("#").strip() or current_heading
            i += 1
            continue

        header_cells = _split_cells(lines[i]) if i < len(lines) else None
        divider_cells = _split_cells(lines[i + 1]) if i + 1 < len(lines) else None
        is_divider = bool(
            divider_cells
            and all(cell.replace("-", "").replace(":", "") == "" for cell in divider_cells)
        )

        if header_cells and divider_cells and is_divider:
            table_counter += 1
            normalized_headers = [_clean_header(h) or f"column_{idx+1}" for idx, h in enumerate(header_cells)]
            rows: list[dict[str, str]] = []
            i += 2

            while i < len(lines):
                row_cells = _split_cells(lines[i])
                if not row_cells:
                    break
                if len(row_cells) < len(normalized_headers):
                    row_cells.extend([""] * (len(normalized_headers) - len(row_cells)))
                elif len(row_cells) > len(normalized_headers):
                    row_cells = row_cells[: len(normalized_headers)]
                row = {
                    normalized_headers[idx]: row_cells[idx].strip()
                    for idx in range(len(normalized_headers))
                }
                if any(value for value in row.values()):
                    rows.append(row)
                i += 1

            tables.append(
                MarkdownTable(
                    headers=normalized_headers,
                    rows=rows,
                    source_reference=f"{current_heading} / Table {table_counter}",
                )
            )
            continue

        i += 1

    return tables
