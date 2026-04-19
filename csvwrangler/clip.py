"""Clip numeric values in CSV columns to a specified range."""
from __future__ import annotations
from typing import List, Dict, Optional

Row = Dict[str, str]


def _try_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def clip_column(
    rows: List[Row],
    column: str,
    lower: Optional[float] = None,
    upper: Optional[float] = None,
) -> List[Row]:
    """Clip values in *column* to [lower, upper]. Non-numeric values are left unchanged."""
    if lower is not None and upper is not None and lower > upper:
        raise ValueError(f"lower ({lower}) must be <= upper ({upper})")

    result = []
    for row in rows:
        new_row = dict(row)
        val = _try_float(row.get(column, ""))
        if val is not None:
            if lower is not None:
                val = max(val, lower)
            if upper is not None:
                val = min(val, upper)
            # Preserve int-like appearance when possible
            new_row[column] = str(int(val)) if val == int(val) else str(val)
        result.append(new_row)
    return result


def clip_many(
    rows: List[Row],
    specs: List[Dict],  # [{"column": str, "lower": float|None, "upper": float|None}]
) -> List[Row]:
    """Apply clip_column for multiple column specs in sequence."""
    for spec in specs:
        rows = clip_column(
            rows,
            column=spec["column"],
            lower=spec.get("lower"),
            upper=spec.get("upper"),
        )
    return rows
