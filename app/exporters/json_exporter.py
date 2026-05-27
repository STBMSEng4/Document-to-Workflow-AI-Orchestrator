"""JSON export utilities for SpecFlow AI."""

import json
from pathlib import Path


def export_to_json(data: dict | list, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)
