"""OCR quality gate for SpecFlow AI.

Evaluates a parse-result dict and returns a quality level and human-readable
message. All structured extraction tabs and the Exports tab use this to decide
whether to show results, warn the user, or block exports entirely.

Quality levels
--------------
"ok"      — text extracted cleanly; no OCR concerns.
"warn"    — OCR was applied and returned usable text, but accuracy may be lower
            than a text-layer PDF. Show a banner; do not block.
"blocked" — OCR was needed but failed, returned too little text, or the parse
            failed entirely. Block structured exports; show a clear reason.
"""

from __future__ import annotations

# Minimum thresholds for OCR output to be considered usable.
_MIN_CHAR_COUNT = 200
_MIN_WORD_COUNT = 30


def ocr_quality(parse_result: dict | None) -> tuple[str, str]:
    """Return (level, message) describing the OCR/parse quality of a result.

    Parameters
    ----------
    parse_result:
        The dict returned by inspect_pdf / parse_docx_to_markdown / etc.
        May be None if no document has been processed yet.

    Returns
    -------
    level : "ok" | "warn" | "blocked"
    message : Human-readable explanation. Empty string when level is "ok".
    """
    if not parse_result:
        return "ok", ""

    status = parse_result.get("status", "")
    ocr_required: bool = bool(parse_result.get("ocr_required", False))
    ocr_applied: bool = bool(parse_result.get("ocr_applied", False))
    metadata: dict = parse_result.get("metadata") or {}
    char_count: int = int(metadata.get("char_count") or 0)
    word_count: int = int(metadata.get("word_count") or 0)
    classification: str = parse_result.get("pdf_classification") or ""

    # --- Hard block cases ---

    if status == "failed":
        return "blocked", (
            "Document parsing failed — no text was extracted. "
            "Check the Inspection tab for parser errors."
        )

    if ocr_required and not ocr_applied:
        return "blocked", (
            "This PDF is scanned or image-heavy and OCR was not available or did not run. "
            "Structured extraction cannot proceed on image-only content. "
            "Provide a text-layer PDF, or install Tesseract and re-upload."
        )

    if ocr_applied and char_count < _MIN_CHAR_COUNT:
        return "blocked", (
            f"OCR ran but recovered only {char_count} characters ({word_count} words) — "
            f"below the minimum threshold ({_MIN_CHAR_COUNT} chars / {_MIN_WORD_COUNT} words). "
            "The scan quality is too low for reliable extraction. "
            "Provide a higher-resolution scan or a text-layer PDF."
        )

    if ocr_applied and word_count < _MIN_WORD_COUNT:
        return "blocked", (
            f"OCR ran but recovered only {word_count} words — "
            f"below the minimum threshold ({_MIN_WORD_COUNT} words). "
            "The scan quality is too low. "
            "Provide a higher-resolution scan or a text-layer PDF."
        )

    # --- Warn cases ---

    if ocr_applied:
        return "warn", (
            "OCR was applied to recover text from a scanned or image-heavy PDF. "
            "Extracted records may contain recognition errors — review all outputs before use."
        )

    if classification in ("mixed_pdf",):
        return "warn", (
            "This PDF contains a mix of text and image pages. "
            "Some content may not have been extracted. "
            "Review the Raw Markdown tab before relying on structured outputs."
        )

    return "ok", ""


def is_blocked(parse_result: dict | None) -> bool:
    """Convenience helper — True when exports should be blocked."""
    level, _ = ocr_quality(parse_result)
    return level == "blocked"


def is_warned(parse_result: dict | None) -> bool:
    """Convenience helper — True when a quality warning should be shown."""
    level, _ = ocr_quality(parse_result)
    return level == "warn"
