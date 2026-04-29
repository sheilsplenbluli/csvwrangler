"""Truncate rows: keep only the first N or last N rows matching a condition,
or hard-limit the total row count of a dataset."""

from __future__ import annotations

from typing import List, Dict, Optional

Row = Dict[str, str]


def limit_rows(rows: List[Row], n: int) -> List[Row]:
    """Return at most *n* rows from the beginning of *rows*."""
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return list(rows[:n])


def offset_rows(rows: List[Row], offset: int) -> List[Row]:
    """Skip the first *offset* rows and return the rest."""
    if offset < 0:
        raise ValueError(f"offset must be >= 0, got {offset}")
    return list(rows[offset:])


def limit_offset(rows: List[Row], limit: int, offset: int = 0) -> List[Row]:
    """Apply *offset* then *limit* — SQL-style pagination."""
    return limit_rows(offset_rows(rows, offset), limit)


def keep_while(rows: List[Row], column: str, value: str) -> List[Row]:
    """Return rows from the start while *column* equals *value*.

    Stops at the first row that does not match (like itertools.takewhile).
    """
    result: List[Row] = []
    for row in rows:
        if row.get(column, "") == value:
            result.append(dict(row))
        else:
            break
    return result


def drop_while(rows: List[Row], column: str, value: str) -> List[Row]:
    """Skip rows from the start while *column* equals *value*, then keep the rest."""
    dropping = True
    result: List[Row] = []
    for row in rows:
        if dropping and row.get(column, "") == value:
            continue
        else:
            dropping = False
            result.append(dict(row))
    return result


def truncate_rows_summary(rows: List[Row], limit: Optional[int], offset: int = 0) -> Dict[str, int]:
    """Return a small summary dict describing what limit/offset would do."""
    total = len(rows)
    after_offset = max(0, total - offset)
    kept = after_offset if limit is None else min(after_offset, limit)
    return {"total": total, "offset": offset, "kept": kept, "dropped": total - kept}
