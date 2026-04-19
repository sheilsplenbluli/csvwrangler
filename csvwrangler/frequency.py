"""Value frequency / distribution analysis for CSV columns."""
from collections import Counter
from typing import List, Dict, Any


def frequency_table(
    rows: List[Dict[str, Any]],
    column: str,
    top_n: int | None = None,
    sort_by: str = "count",  # "count" | "value"
) -> List[Dict[str, Any]]:
    """Return frequency counts for values in *column*.

    Each result row has keys: value, count, percent.
    """
    if not rows:
        return []

    counts: Counter = Counter(row.get(column, "") for row in rows)
    total = sum(counts.values())

    table = [
        {"value": val, "count": cnt, "percent": round(cnt / total * 100, 2)}
        for val, cnt in counts.items()
    ]

    if sort_by == "value":
        table.sort(key=lambda r: str(r["value"]))
    else:
        table.sort(key=lambda r: r["count"], reverse=True)

    if top_n is not None:
        table = table[:top_n]

    return table


def frequency_all(
    rows: List[Dict[str, Any]],
    top_n: int | None = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Run frequency_table for every column in *rows*."""
    if not rows:
        return {}
    columns = list(rows[0].keys())
    return {col: frequency_table(rows, col, top_n=top_n) for col in columns}
