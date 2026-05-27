"""Markdown normalizer for SpecFlow AI.

Cleans raw PDF-extracted Markdown: removes artifacts, normalizes headers,
preserves technical content, and adds YAML frontmatter.
"""

import re
from datetime import datetime, timezone


def remove_page_artifacts(text: str) -> str:
    """Strip common PDF extraction artifacts: page numbers, repeated headers/footers."""
    # Remove bare page numbers like "Page 1 of 12" or just "1"
    text = re.sub(r"(?m)^Page\s+\d+\s+of\s+\d+\s*$", "", text)
    text = re.sub(r"(?m)^\d+\s*$", "", text)
    # Remove long horizontal rules that are artifacts
    text = re.sub(r"-{10,}", "", text)
    text = re.sub(r"_{10,}", "", text)
    return text


def normalize_headers(text: str) -> str:
    """Ensure consistent Markdown header formatting."""
    # Fix headers with no space after #
    text = re.sub(r"(?m)^(#{1,6})([^\s#])", r"\1 \2", text)
    return text


def collapse_blank_lines(text: str) -> str:
    """Reduce 3+ consecutive blank lines to 2."""
    return re.sub(r"\n{3,}", "\n\n", text)


def normalize_tables(text: str) -> str:
    """Light normalization — preserve existing tables as-is."""
    return text


def normalize_text(raw_markdown: str) -> str:
    """Apply all normalization steps."""
    text = raw_markdown
    text = remove_page_artifacts(text)
    text = normalize_headers(text)
    text = collapse_blank_lines(text)
    text = normalize_tables(text)
    return text.strip()


def build_frontmatter(
    source_file: str = "",
    source_type: str = "pdf",
    pdf_classification: str = "unknown",
    ocr_required: bool = False,
    confidence: float = 0.0,
    document_domain: str = "BMS/Controls",
    document_type: str = "unknown",
    tags: list[str] | None = None,
    template_triggers: list[str] | None = None,
    filtering_mode: str = "workflow",
) -> str:
    now = datetime.now(timezone.utc).isoformat()
    tag_str = ", ".join(tags or [])
    trigger_str = ", ".join(template_triggers or [])
    return f"""---
title: {source_file}
source_type: {source_type}
source_file: {source_file}
ingested_at: {now}
processed_by: SpecFlow AI
ingestion_engine: pdf-inspector
document_domain: {document_domain}
document_type: {document_type}
pdf_classification: {pdf_classification}
ocr_required: {str(ocr_required).lower()}
confidence: {confidence:.2f}
tags: [{tag_str}]
template_triggers: [{trigger_str}]
filtering_mode: {filtering_mode}
---
"""


def build_agent_ready_skeleton() -> str:
    """Return the section headings for agent-ready Markdown output."""
    sections = [
        "# Document Summary",
        "# Source Metadata",
        "# PDF Inspection Results",
        "# Detection Matrix",
        "# Normalized Technical Terms",
        "# Extracted Equipment",
        "# Extracted Controls Requirements",
        "# Extracted Network Requirements",
        "# Potential Points List",
        "# RFIs / Clarifications",
        "# Risks / Gaps",
        "# Field Verification Items",
        "# CAD / Drawing Tasks",
        "# Submittal Items",
        "# Commissioning / Checkout Items",
        "# Template Triggers",
        "# Low-Confidence Items",
        "# Excluded / Not Detected Terms",
        "# Agent Notes",
    ]
    return "\n\n".join(s + "\n\n_To be populated by SpecFlow AI._" for s in sections)
