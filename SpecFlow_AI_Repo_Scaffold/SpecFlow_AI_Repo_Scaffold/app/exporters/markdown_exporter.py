"""Markdown export utilities."""

from pathlib import Path


def export_markdown_report(content: str, output_path: str) -> str:
    """Export Markdown report content."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)
