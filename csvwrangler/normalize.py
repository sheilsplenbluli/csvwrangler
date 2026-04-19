"""Normalize numeric columns to a 0-1 range or z-score."""
from __future__ import annotations

from typing import List, Dict


def _numeric_values(rows: List[Dict], column: str) -> List[float]:
    result = []
    for row in rows:
        try:
            result.append(float(row[column]))
        except (ValueError, TypeError, KeyError):
            pass
    return result


def minmax_normalize(rows: List[Dict], column: str, dest: str | None = None) -> List[Dict]:
    """Scale values in column to [0, 1]. Non-numeric cells become empty string."""
    dest = dest or column
    vals = _numeric_values(rows, column)
    if not vals:
        return [{**r, dest: ""} for r in rows]
    lo, hi = min(vals), max(vals)
    out = []
    for row in rows:
        new = dict(row)
        try:
            v = float(row[column])
            new[dest] = "" if hi == lo else str(round((v - lo) / (hi - lo), 6))
        except (ValueError, TypeError, KeyError):
            new[dest] = ""
        out.append(new)
    return out


def zscore_normalize(rows: List[Dict], column: str, dest: str | None = None) -> List[Dict]:
    """Replace values with z-scores. Non-numeric cells become empty string."""
    dest = dest or column
    vals = _numeric_values(rows, column)
    if not vals:
        return [{**r, dest: ""} for r in rows]
    mean = sum(vals) / len(vals)
    variance = sum((v - mean) ** 2 for v in vals) / len(vals)
    std = variance ** 0.5
    out = []
    for row in rows:
        new = dict(row)
        try:
            v = float(row[column])
            new[dest] = "" if std == 0 else str(round((v - mean) / std, 6))
        except (ValueError, TypeError, KeyError):
            new[dest] = ""
        out.append(new)
    return out


def normalize_many(rows: List[Dict], specs: List[Dict]) -> List[Dict]:
    """Apply multiple normalization specs. Each spec: {column, method, dest}."""
    for spec in specs:
        col = spec["column"]
        method = spec.get("method", "minmax")
        dest = spec.get("dest", col)
        if method == "zscore":
            rows = zscore_normalize(rows, col, dest)
        else:
            rows = minmax_normalize(rows, col, dest)
    return rows
