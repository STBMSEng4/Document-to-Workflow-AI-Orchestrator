"""PDF parsing utilities for SpecFlow AI."""

from pathlib import Path


def pdf_to_markdown(pdf_path: str) -> str:
    """Convert a PDF file to Markdown.

    This placeholder should be replaced with PyMuPDF4LLM / Docling / Marker logic.
    """
    path = Path(pdf_path)
    return f"# Parsed PDF\n\nSource file: {path.name}\n\nTODO: Add PDF-to-Markdown parser."
