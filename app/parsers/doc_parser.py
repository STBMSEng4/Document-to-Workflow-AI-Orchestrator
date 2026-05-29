"""Legacy .doc parser for SpecFlow AI.

Extracts text from Word 97-2003 binary (.doc) files using the antiword
command-line tool, which must be available in the runtime environment:

    apt-get install antiword          # Debian/Ubuntu (Docker image)

The parser returns the same result-dict shape used by every other SpecFlow
parser so that all downstream extractors, scorers, and the OCR gate receive
consistent input regardless of file type.

Falls back gracefully with a clear status="failed" and actionable error message
if antiword is not installed.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUTPUTS_RAW = Path(__file__).parents[2] / "outputs" / "markdown" / "raw"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _antiword_available() -> bool:
    return shutil.which("antiword") is not None


def _run_antiword(file_path: Path) -> str:
    """Invoke antiword and return its plain-text output.

    ``-w 0`` disables line-wrapping so long lines are not broken mid-word.
    Raises RuntimeError if antiword exits non-zero.
    """
    result = subprocess.run(
        ["antiword", "-w", "0", str(file_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(
            f"antiword exited with code {result.returncode}"
            + (f": {stderr}" if stderr else "")
        )
    return result.stdout


def _plain_text_to_markdown(text: str) -> str:
    """Convert antiword plain-text output to minimal Markdown.

    Heuristic: short lines that are ALL-CAPS or Title-Case with no trailing
    punctuation and ≤ 10 words are treated as section headings (## prefix).
    Everything else is preserved as paragraph text.
    """
    lines = text.splitlines()
    md_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            md_lines.append("")
            continue

        words = stripped.split()
        is_heading = (
            len(stripped) < 80
            and not stripped[-1] in ".,:;?!"
            and len(words) <= 10
            and (stripped.isupper() or stripped.istitle())
        )
        md_lines.append(f"## {stripped}" if is_heading else stripped)

    # Collapse runs of blank lines to a single blank line
    result_lines: list[str] = []
    prev_blank = False
    for line in md_lines:
        if line == "":
            if not prev_blank:
                result_lines.append("")
            prev_blank = True
        else:
            result_lines.append(line)
            prev_blank = False

    return "\n".join(result_lines).strip()


def _classify_doc(markdown: str) -> str:
    words = len(markdown.split())
    if words < 50:
        return "empty_or_failed_parse"
    if words < 300:
        return "image_heavy_pdf"   # reuse existing label — sparse content
    return "text_pdf"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_doc_to_markdown(file_path: str) -> dict:
    """Parse a legacy .doc file and return a SpecFlow-compatible result dict.

    Parameters
    ----------
    file_path:
        Absolute or relative path to the .doc file.

    Returns
    -------
    dict with keys: source_type, source_file, ingestion_engine,
    pdf_classification, raw_markdown, metadata, ocr_required, status, errors.
    """
    path = Path(file_path)
    errors: list[str] = []
    raw_markdown = ""
    classification = "empty_or_failed_parse"

    # ── Guard: file must exist ─────────────────────────────────────────────
    if not path.exists():
        return {
            "source_type": "doc",
            "source_file": str(file_path),
            "ingestion_engine": "antiword",
            "pdf_classification": "empty_or_failed_parse",
            "raw_markdown": "",
            "metadata": {},
            "ocr_required": False,
            "status": "failed",
            "errors": [f"File not found: {file_path}"],
        }

    # ── Guard: antiword must be installed ─────────────────────────────────
    if not _antiword_available():
        return {
            "source_type": "doc",
            "source_file": path.name,
            "ingestion_engine": "antiword",
            "pdf_classification": "empty_or_failed_parse",
            "raw_markdown": "",
            "metadata": {},
            "ocr_required": False,
            "status": "failed",
            "errors": [
                "Legacy .doc support requires antiword, which is not installed. "
                "In the Docker image: apt-get install antiword. "
                "Alternatively, convert the file to .docx and re-upload."
            ],
        }

    # ── Extract ────────────────────────────────────────────────────────────
    try:
        plain_text = _run_antiword(path)
        raw_markdown = _plain_text_to_markdown(plain_text)
        classification = _classify_doc(raw_markdown)
    except Exception as exc:
        errors.append(f"DOC extraction error: {exc}")
        classification = "empty_or_failed_parse"

    # ── Metadata ──────────────────────────────────────────────────────────
    file_hash = hashlib.md5(path.read_bytes()).hexdigest()
    metadata = {
        "source_file": path.name,
        "file_size_bytes": path.stat().st_size,
        "file_hash_md5": file_hash,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "pdf_classification": classification,
        "char_count": len(raw_markdown),
        "word_count": len(raw_markdown.split()),
    }

    # ── Persist raw output ─────────────────────────────────────────────────
    if raw_markdown:
        OUTPUTS_RAW.mkdir(parents=True, exist_ok=True)
        out_path = OUTPUTS_RAW / f"{path.stem}_raw.md"
        out_path.write_text(raw_markdown, encoding="utf-8")

    status = "failed" if not raw_markdown.strip() else "success"

    return {
        "source_type": "doc",
        "source_file": path.name,
        "ingestion_engine": "antiword",
        "pdf_classification": classification,
        "raw_markdown": raw_markdown,
        "metadata": metadata,
        "ocr_required": False,
        "status": status,
        "errors": errors,
    }
