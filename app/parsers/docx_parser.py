"""DOCX parser for SpecFlow AI.

Converts .docx files to Markdown-like text using python-docx.
Preserves headings, tables, and paragraph structure.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

OUTPUTS_RAW = Path(__file__).parents[2] / "outputs" / "markdown" / "raw"


def _heading_prefix(level: int) -> str:
    return "#" * min(level, 6) + " "


def _table_to_markdown(table) -> str:
    """Convert a python-docx Table to a Markdown table string."""
    rows = []
    for i, row in enumerate(table.rows):
        cells = [cell.text.strip().replace("|", "\\|") for cell in row.cells]
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            rows.append("|" + "|".join(["---"] * len(cells)) + "|")
    return "\n".join(rows)


def _docx_to_markdown(path: Path) -> str:
    """Extract text from a .docx file and return as Markdown string."""
    import docx  # type: ignore

    doc = docx.Document(str(path))
    lines: list[str] = []

    for element in doc.element.body:
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        if tag == "p":
            # Paragraph
            from docx.oxml.ns import qn  # type: ignore
            style_name = ""
            try:
                style_elem = element.find(f".//{{{element.nsmap.get('w', '')}}}" + "pStyle") if hasattr(element, "nsmap") else None
            except Exception:
                style_elem = None

            # Use python-docx Paragraph for style access
            import docx.text.paragraph as _para  # type: ignore
            para = _para.Paragraph(element, doc)
            text = para.text.strip()
            if not text:
                continue

            style = para.style.name if para.style else ""
            if style.startswith("Heading"):
                try:
                    level = int(style.split()[-1])
                except ValueError:
                    level = 1
                lines.append(f"{_heading_prefix(level)}{text}")
            elif style.startswith("List"):
                lines.append(f"- {text}")
            else:
                lines.append(text)

        elif tag == "tbl":
            import docx.table as _tbl  # type: ignore
            table = _tbl.Table(element, doc)
            lines.append("")
            lines.append(_table_to_markdown(table))
            lines.append("")

    return "\n\n".join(lines)


def _classify_docx(markdown: str) -> str:
    """Classify DOCX by content density."""
    words = len(markdown.split())
    if words < 50:
        return "empty_or_failed_parse"
    if words < 300:
        return "image_heavy_pdf"  # sparse — likely mostly diagrams
    return "text_pdf"


def parse_docx_to_markdown(file_path: str) -> dict:
    """Parse a .docx file and return SpecFlow-compatible result dict."""
    path = Path(file_path)
    errors: list[str] = []
    raw_markdown = ""
    classification = "empty_or_failed_parse"

    if not path.exists():
        return {
            "source_type": "docx",
            "source_file": str(file_path),
            "ingestion_engine": "python-docx",
            "pdf_classification": "empty_or_failed_parse",
            "raw_markdown": "",
            "metadata": {},
            "ocr_required": False,
            "status": "failed",
            "errors": [f"File not found: {file_path}"],
        }

    try:
        raw_markdown = _docx_to_markdown(path)
        classification = _classify_docx(raw_markdown)
    except ImportError:
        errors.append("python-docx not installed. Run: pip install python-docx")
        classification = "empty_or_failed_parse"
    except Exception as exc:
        errors.append(f"DOCX extraction error: {exc}")
        classification = "empty_or_failed_parse"

    file_hash = hashlib.md5(path.read_bytes()).hexdigest() if path.exists() else ""
    metadata = {
        "source_file": path.name,
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
        "file_hash_md5": file_hash,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "pdf_classification": classification,
        "char_count": len(raw_markdown),
        "word_count": len(raw_markdown.split()),
    }

    if raw_markdown:
        OUTPUTS_RAW.mkdir(parents=True, exist_ok=True)
        out_path = OUTPUTS_RAW / f"{path.stem}_raw.md"
        out_path.write_text(raw_markdown, encoding="utf-8")

    status = "failed" if not raw_markdown.strip() else "success"

    return {
        "source_type": "docx",
        "source_file": path.name,
        "ingestion_engine": "python-docx",
        "pdf_classification": classification,
        "raw_markdown": raw_markdown,
        "metadata": metadata,
        "ocr_required": False,
        "status": status,
        "errors": errors,
    }
