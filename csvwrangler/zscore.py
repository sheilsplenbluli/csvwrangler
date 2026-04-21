"""Z-score standardization for numeric columns."""
from __future__ import annotations

import math
from typing import Any


def _numeric_values(rows: list[dict], col: str) -> list[float]:
    out = []
    for r in rows:
        v = r.get(col, "")
        try:
            out.append(float(v))
        except (ValueError, TypeError):
            pass
    return out


def zscore_column(
    rows: list[dict],
    col: str,
    dest: str | None = None,
    decimals: int = 4,
) -> list[dict]:
    """Add a z-score column for *col*.  Non-numeric cells become empty string."""
    dest = dest or f"{col}_zscore"
    nums = _numeric_values(rows, col)
    if len(nums) < 2:
        return [{**r, dest: ""} for r in rows]

    mean = sum(nums) / len(nums)
    variance = sum((x - mean) ** 2 for x in nums) / len(nums)
    std = math.sqrt(variance)

    result = []
    for r in rows:
        v = r.get(col, "")
        try:
            z = (float(v) - mean) / std if std else 0.0
            result.append({**r, dest: round(z, decimals)})
        except (ValueError, TypeError):
            result.append({**r, dest: ""})
    return result


def zscore_many(
    rows: list[dict],
    specs: list[dict[str, Any]],
) -> list[dict]:
    """Apply zscore_column for each spec dict (keys: col, dest, decimals)."""
    for spec in specs:
        rows = zscore_column(
            rows,
            col=spec["col"],
            dest=spec.get("dest"),
            decimals=spec.get("decimals", 4),
        )
    return rows
