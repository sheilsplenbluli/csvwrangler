"""Top-N and bottom-N row selection by a numeric column."""
from __future__ import annotations

from typing import List, Dict, Any, Optional


def _try_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def top_n(
    rows: List[Dict[str, Any]],
    column: str,
    n: int,
    *,
    keep_ties: bool = False,
) -> List[Dict[str, Any]]:
    """Return the top *n* rows sorted by *column* descending.

    If *keep_ties* is True, all rows that share the nth value are included,
    which may return more than *n* rows.
    """
    if n < 0:
        raise ValueError("n must be >= 0")

    scored = [(row, _try_float(row.get(column, ""))) for row in rows]
    valid = [(row, v) for row, v in scored if v is not None]
    valid.sort(key=lambda x: x[1], reverse=True)

    if not keep_ties:
        return [row for row, _ in valid[:n]]

    if n == 0:
        return []

    cutoff = valid[n - 1][1] if n <= len(valid) else None
    if cutoff is None:
        return [row for row, _ in valid]
    return [row for row, v in valid if v >= cutoff]


def bottom_n(
    rows: List[Dict[str, Any]],
    column: str,
    n: int,
    *,
    keep_ties: bool = False,
) -> List[Dict[str, Any]]:
    """Return the bottom *n* rows sorted by *column* ascending."""
    if n < 0:
        raise ValueError("n must be >= 0")

    scored = [(row, _try_float(row.get(column, ""))) for row in rows]
    valid = [(row, v) for row, v in scored if v is not None]
    valid.sort(key=lambda x: x[1])

    if not keep_ties:
        return [row for row, _ in valid[:n]]

    if n == 0:
        return []

    cutoff = valid[n - 1][1] if n <= len(valid) else None
    if cutoff is None:
        return [row for row, _ in valid]
    return [row for row, v in valid if v <= cutoff]
