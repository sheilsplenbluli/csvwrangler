"""Generate a duplicate report showing which rows are duplicates and how many times they appear."""
from __future__ import annotations

from collections import Counter
from typing import Iterable


def _row_key(row: dict, columns: list[str] | None) -> tuple:
    if columns:
        return tuple(row.get(c, "") for c in columns)
    return tuple(sorted(row.items()))


def duplicate_report(
    rows: list[dict],
    columns: list[str] | None = None,
    count_col: str = "_dup_count",
    rank_col: str = "_dup_rank",
    include_unique: bool = False,
) -> list[dict]:
    """Return rows annotated with duplicate count and occurrence rank.

    Args:
        rows: input rows.
        columns: columns to consider for grouping; None means all columns.
        count_col: name of the column that will hold the total duplicate count.
        rank_col: name of the column that will hold the occurrence rank (1-based).
        include_unique: if False, rows that appear only once are excluded.

    Returns:
        Annotated rows, preserving original order.
    """
    counts: Counter = Counter()
    for row in rows:
        counts[_row_key(row, columns)] += 1

    seen: Counter = Counter()
    result = []
    for row in rows:
        key = _row_key(row, columns)
        total = counts[key]
        if not include_unique and total < 2:
            continue
        seen[key] += 1
        annotated = dict(row)
        annotated[count_col] = str(total)
        annotated[rank_col] = str(seen[key])
        result.append(annotated)
    return result


def duplicate_summary(rows: list[dict], columns: list[str] | None = None) -> dict:
    """Return a summary dict with total rows, unique rows, and duplicate rows."""
    counts: Counter = Counter()
    for row in rows:
        counts[_row_key(row, columns)] += 1

    total = len(rows)
    unique = sum(1 for c in counts.values() if c == 1)
    dup_groups = sum(1 for c in counts.values() if c > 1)
    dup_rows = sum(c for c in counts.values() if c > 1)
    return {
        "total_rows": total,
        "unique_rows": unique,
        "duplicate_groups": dup_groups,
        "duplicate_rows": dup_rows,
    }
