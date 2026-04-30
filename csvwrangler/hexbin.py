"""Numeric binning into equal-width or custom-width hex/decimal buckets."""
from __future__ import annotations

from typing import Any


def _try_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def equal_width_bins(
    rows: list[dict[str, Any]],
    column: str,
    n_bins: int,
    dest: str | None = None,
    fill: str = "",
) -> list[dict[str, Any]]:
    """Assign each row to one of *n_bins* equal-width numeric buckets."""
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1")

    dest = dest or f"{column}_eqbin"
    values = [_try_float(r[column]) for r in rows if _try_float(r.get(column, "")) is not None]

    if not values:
        return [{**r, dest: fill} for r in rows]

    lo, hi = min(values), max(values)
    span = hi - lo

    result = []
    for row in rows:
        v = _try_float(row.get(column, ""))
        if v is None:
            result.append({**row, dest: fill})
            continue
        if span == 0:
            label = "1"
        else:
            idx = int((v - lo) / span * n_bins)
            idx = min(idx, n_bins - 1)  # clamp upper edge
            label = str(idx + 1)
        result.append({**row, dest: label})
    return result


def custom_width_bins(
    rows: list[dict[str, Any]],
    column: str,
    width: float,
    dest: str | None = None,
    fill: str = "",
) -> list[dict[str, Any]]:
    """Assign each row to a bucket of fixed *width* starting from the minimum value."""
    if width <= 0:
        raise ValueError("width must be > 0")

    dest = dest or f"{column}_cwbin"
    values = [_try_float(r.get(column, "")) for r in rows]
    numeric = [v for v in values if v is not None]

    if not numeric:
        return [{**r, dest: fill} for r in rows]

    lo = min(numeric)

    result = []
    for row in rows:
        v = _try_float(row.get(column, ""))
        if v is None:
            result.append({**row, dest: fill})
            continue
        idx = int((v - lo) / width)
        bucket_start = lo + idx * width
        bucket_end = bucket_start + width
        label = f"[{bucket_start:.4g},{bucket_end:.4g})"
        result.append({**row, dest: label})
    return result
