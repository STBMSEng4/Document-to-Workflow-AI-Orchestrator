"""CSV export utilities."""

from pathlib import Path
import pandas as pd


def export_table_to_csv(rows: list[dict], output_path: str) -> str:
    """Export a list of dictionaries to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return str(path)
