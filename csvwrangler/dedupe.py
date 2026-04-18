"""Deduplication utilities for CSV rows."""
from typing import Iterator, List, Optional


def _row_key(row: dict, columns: Optional[List[str]] = None) -> tuple:
    """Build a hashable key from a row, optionally limited to specific columns."""
    if columns:
        return tuple(row.get(col, "") for col in columns)
    return tuple(sorted(row.items()))


def dedupe_rows(
    rows: List[dict],
    columns: Optional[List[str]] = None,
    keep: str = "first",
) -> List[dict]:
    """Remove duplicate rows.

    Args:
        rows: list of row dicts.
        columns: columns to consider for uniqueness; None means all columns.
        keep: 'first' keeps first occurrence, 'last' keeps last occurrence.

    Returns:
        Deduplicated list of row dicts.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    if keep == "last":
        rows = list(reversed(rows))

    seen = set()
    result = []
    for row in rows:
        key = _row_key(row, columns)
        if key not in seen:
            seen.add(key)
            result.append(row)

    if keep == "last":
        result = list(reversed(result))

    return result


def count_duplicates(rows: List[dict], columns: Optional[List[str]] = None) -> int:
    """Return the number of duplicate rows (total rows minus unique rows)."""
    return len(rows) - len(dedupe_rows(rows, columns=columns))
