"""PDF Inspector parser for SpecFlow AI.

Uses pymupdf4llm for local PDF inspection and Markdown extraction.
Does NOT use the Firecrawl web crawling API.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

OUTPUTS_RAW = Path(__file__).parents[2] / "outputs" / "markdown" / "raw"


def _classify_pdf(pages_text: list[str]) -> str:
    """Heuristic classification based on extracted text density."""
    total_chars = sum(len(p) for p in pages_text)
    avg_per_page = total_chars / max(len(pages_text), 1)

    if avg_per_page == 0:
        return "scanned_pdf"
    if avg_per_page < 100:
        return "image_heavy_pdf"
    if avg_per_page < 400:
        return "mixed_pdf"
    return "text_pdf"


def requires_ocr(result: dict) -> bool:
    return result.get("pdf_classification") in ("scanned_pdf",)


def save_raw_markdown(markdown: str, filename: str) -> str:
    OUTPUTS_RAW.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUTS_RAW / f"{Path(filename).stem}_raw.md"
    out_path.write_text(markdown, encoding="utf-8")
    return str(out_path)


def build_pdf_metadata(file_path: str, raw_markdown: str, classification: str) -> dict:
    path = Path(file_path)
    file_hash = hashlib.md5(path.read_bytes()).hexdigest() if path.exists() else ""
    return {
        "source_file": path.name,
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
        "file_hash_md5": file_hash,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "pdf_classification": classification,
        "char_count": len(raw_markdown),
        "word_count": len(raw_markdown.split()),
    }


def inspect_pdf(file_path: str) -> dict:
    """Inspect and extract Markdown from a local PDF using pymupdf4llm."""
    path = Path(file_path)
    errors: list[str] = []
    raw_markdown = ""
    classification = "empty_or_failed_parse"

    if not path.exists():
        return {
            "source_type": "pdf",
            "source_file": str(file_path),
            "ingestion_engine": "pdf-inspector",
            "pdf_classification": "empty_or_failed_parse",
            "raw_markdown": "",
            "metadata": {},
            "ocr_required": False,
            "status": "failed",
            "errors": [f"File not found: {file_path}"],
        }

    try:
        import pymupdf4llm  # type: ignore
        raw_markdown = pymupdf4llm.to_markdown(str(path))
        pages_preview = [raw_markdown[i: i + 500] for i in range(0, min(len(raw_markdown), 5000), 500)]
        classification = _classify_pdf(pages_preview)
    except ImportError:
        errors.append("pymupdf4llm not installed — install with: pip install pymupdf4llm")
        classification = "empty_or_failed_parse"
    except Exception as exc:
        errors.append(f"Extraction error: {exc}")
        classification = "empty_or_failed_parse"

    if not raw_markdown.strip():
        classification = "empty_or_failed_parse" if not errors else classification

    ocr_needed = requires_ocr({"pdf_classification": classification})
    status = "ocr_required" if ocr_needed else ("failed" if not raw_markdown.strip() else "success")
    metadata = build_pdf_metadata(file_path, raw_markdown, classification)

    if raw_markdown:
        save_raw_markdown(raw_markdown, path.name)

    return {
        "source_type": "pdf",
        "source_file": path.name,
        "ingestion_engine": "pdf-inspector",
        "pdf_classification": classification,
        "raw_markdown": raw_markdown,
        "metadata": metadata,
        "ocr_required": ocr_needed,
        "status": status,
        "errors": errors,
    }


def parse_pdf_to_markdown(file_path: str) -> dict:
    """Convenience wrapper — alias for inspect_pdf."""
    return inspect_pdf(file_path)
