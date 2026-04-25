"""Streak detection: count consecutive runs of matching values in a column."""

from typing import List, Dict, Any, Optional


def _matches(value: str, target: str, case_sensitive: bool) -> bool:
    if case_sensitive:
        return value == target
    return value.lower() == target.lower()


def streak_column(
    rows: List[Dict[str, Any]],
    column: str,
    target: str,
    dest: Optional[str] = None,
    case_sensitive: bool = True,
) -> List[Dict[str, Any]]:
    """Add a column counting the current consecutive streak of *target* in *column*.

    The counter resets to 0 whenever the value does not match.
    """
    dest = dest or f"{column}_streak"
    result = []
    count = 0
    for row in rows:
        val = row.get(column, "")
        if _matches(str(val), target, case_sensitive):
            count += 1
        else:
            count = 0
        out = dict(row)
        out[dest] = str(count)
        result.append(out)
    return result


def streak_any(
    rows: List[Dict[str, Any]],
    specs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply multiple streak specs sequentially.

    Each spec is a dict with keys: column, target, dest (optional),
    case_sensitive (optional, default True).
    """
    for spec in specs:
        rows = streak_column(
            rows,
            column=spec["column"],
            target=spec["target"],
            dest=spec.get("dest"),
            case_sensitive=spec.get("case_sensitive", True),
        )
    return rows
