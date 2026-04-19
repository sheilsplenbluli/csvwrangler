"""Truncate string values in CSV columns to a maximum length."""

from typing import List, Dict, Optional

Row = Dict[str, str]


def _truncate_value(value: str, max_len: int, suffix: str = "") -> str:
    if len(value) <= max_len:
        return value
    cut = max_len - len(suffix)
    if cut < 0:
        cut = 0
    return value[:cut] + suffix


def truncate_column(
    rows: List[Row],
    column: str,
    max_len: int,
    suffix: str = "",
) -> List[Row]:
    """Truncate values in a single column."""
    if max_len < 0:
        raise ValueError("max_len must be >= 0")
    result = []
    for row in rows:
        new_row = dict(row)
        if column in new_row:
            new_row[column] = _truncate_value(new_row[column], max_len, suffix)
        result.append(new_row)
    return result


def truncate_many(
    rows: List[Row],
    columns: List[str],
    max_len: int,
    suffix: str = "",
) -> List[Row]:
    """Truncate values across multiple columns."""
    for col in columns:
        rows = truncate_column(rows, col, max_len, suffix)
    return rows


def truncate_all(
    rows: List[Row],
    max_len: int,
    suffix: str = "",
) -> List[Row]:
    """Truncate every column in every row."""
    if not rows:
        return []
    columns = list(rows[0].keys())
    return truncate_many(rows, columns, max_len, suffix)
