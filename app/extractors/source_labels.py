"""Source label helpers for structured extraction."""

from __future__ import annotations

from app.schemas.review import SourceType


SOURCE_EXTRACTED: SourceType = "source_extracted"
TEMPLATE_DEFAULT: SourceType = "template_default"
INFERRED: SourceType = "inferred"


def append_remark(existing: str | None, note: str) -> str:
    text = (existing or "").strip()
    return f"{text}; {note}" if text else note
