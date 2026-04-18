"""Summarization helpers for CSV columns."""

from collections import Counter
from typing import Any


def _numeric_values(rows: list[dict], col: str) -> list[float]:
    values = []
    for row in rows:
        try:
            values.append(float(row[col]))
        except (ValueError, KeyError):
            pass
    return values


def summarize_column(rows: list[dict], col: str) -> dict[str, Any]:
    """Return summary stats for a single column."""
    if not rows:
        return {"column": col, "count": 0}

    raw = [row.get(col, "") for row in rows]
    numeric = _numeric_values(rows, col)

    result: dict[str, Any] = {
        "column": col,
        "count": len(raw),
        "missing": sum(1 for v in raw if v == "" or v is None),
    }

    if numeric:
        result["min"] = min(numeric)
        result["max"] = max(numeric)
        result["mean"] = round(sum(numeric) / len(numeric), 4)
        sorted_n = sorted(numeric)
        mid = len(sorted_n) // 2
        if len(sorted_n) % 2 == 0:
            result["median"] = (sorted_n[mid - 1] + sorted_n[mid]) / 2
        else:
            result["median"] = sorted_n[mid]
    else:
        counter = Counter(raw)
        result["unique"] = len(counter)
        result["top"] = counter.most_common(1)[0][0] if counter else None
        result["top_count"] = counter.most_common(1)[0][1] if counter else 0

    return result


def summarize_all(rows: list[dict]) -> list[dict[str, Any]]:
    """Summarize every column in the dataset."""
    if not rows:
        return []
    return [summarize_column(rows, col) for col in rows[0].keys()]
