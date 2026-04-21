"""Lag and lead column operations for CSV rows."""

from typing import List, Dict, Any, Optional


def lag_column(
    rows: List[Dict[str, Any]],
    column: str,
    periods: int = 1,
    dest: Optional[str] = None,
    fill: str = "",
) -> List[Dict[str, Any]]:
    """Add a lagged version of *column* (shifted forward by *periods* rows)."""
    if periods < 1:
        raise ValueError("periods must be >= 1")
    dest = dest or f"{column}_lag{periods}"
    result = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        src_index = i - periods
        if src_index < 0:
            new_row[dest] = fill
        else:
            new_row[dest] = rows[src_index].get(column, fill)
        result.append(new_row)
    return result


def lead_column(
    rows: List[Dict[str, Any]],
    column: str,
    periods: int = 1,
    dest: Optional[str] = None,
    fill: str = "",
) -> List[Dict[str, Any]]:
    """Add a lead version of *column* (shifted backward by *periods* rows)."""
    if periods < 1:
        raise ValueError("periods must be >= 1")
    dest = dest or f"{column}_lead{periods}"
    result = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        src_index = i + periods
        if src_index >= len(rows):
            new_row[dest] = fill
        else:
            new_row[dest] = rows[src_index].get(column, fill)
        result.append(new_row)
    return result


def lag_many(
    rows: List[Dict[str, Any]],
    specs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply multiple lag/lead specs in sequence.

    Each spec: {"column": str, "periods": int, "direction": "lag"|"lead",
                "dest": str (optional), "fill": str (optional)}
    """
    for spec in specs:
        col = spec["column"]
        periods = int(spec.get("periods", 1))
        direction = spec.get("direction", "lag")
        dest = spec.get("dest")
        fill = spec.get("fill", "")
        if direction == "lead":
            rows = lead_column(rows, col, periods=periods, dest=dest, fill=fill)
        else:
            rows = lag_column(rows, col, periods=periods, dest=dest, fill=fill)
    return rows
