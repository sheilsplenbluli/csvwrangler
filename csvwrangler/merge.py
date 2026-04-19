"""Merge multiple CSV row-lists vertically (union/stack)."""
from typing import List, Dict, Optional

Row = Dict[str, str]


def _align_row(row: Row, fieldnames: List[str], fill: str = "") -> Row:
    """Return a new row containing exactly the given fieldnames."""
    return {f: row.get(f, fill) for f in fieldnames}


def merge_rows(
    datasets: List[List[Row]],
    fill: str = "",
    fieldnames: Optional[List[str]] = None,
) -> List[Row]:
    """Stack multiple datasets vertically.

    Args:
        datasets: list of row-lists to merge.
        fill: value to use for missing columns.
        fieldnames: explicit column order; if None, union of all columns in
                    order of first appearance.
    Returns:
        Single flat list of aligned rows.
    """
    if not datasets:
        return []

    if fieldnames is None:
        seen: dict = {}
        for ds in datasets:
            for row in ds:
                for k in row:
                    seen[k] = None
        fieldnames = list(seen)

    result: List[Row] = []
    for ds in datasets:
        for row in ds:
            result.append(_align_row(row, fieldnames, fill))
    return result


def merge_summary(datasets: List[List[Row]]) -> Dict[str, int]:
    """Return per-dataset row counts and total."""
    counts = {f"dataset_{i}": len(ds) for i, ds in enumerate(datasets)}
    counts["total"] = sum(counts.values())
    return counts
