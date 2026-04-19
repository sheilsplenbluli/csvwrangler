"""Flatten repeated delimiter-separated values in a column into multiple rows."""
from typing import List, Dict, Optional


def flatten_column(
    rows: List[Dict[str, str]],
    column: str,
    delimiter: str = "|",
    strip: bool = True,
) -> List[Dict[str, str]]:
    """Expand rows so each split value of *column* becomes its own row.

    Rows where the column is empty or missing are passed through unchanged.
    """
    if not rows:
        return []
    result: List[Dict[str, str]] = []
    for row in rows:
        raw = row.get(column, "")
        if not raw:
            result.append(dict(row))
            continue
        parts = raw.split(delimiter)
        if strip:
            parts = [p.strip() for p in parts]
        parts = [p for p in parts if p] or [""]
        for part in parts:
            new_row = dict(row)
            new_row[column] = part
            result.append(new_row)
    return result


def flatten_many(
    rows: List[Dict[str, str]],
    columns: List[str],
    delimiter: str = "|",
    strip: bool = True,
) -> List[Dict[str, str]]:
    """Apply flatten_column sequentially for each column in *columns*."""
    for col in columns:
        rows = flatten_column(rows, col, delimiter=delimiter, strip=strip)
    return rows
