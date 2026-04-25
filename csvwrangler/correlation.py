"""Compute pairwise Pearson correlation between numeric columns."""
from __future__ import annotations

import math
from typing import List, Dict, Any


def _numeric_values(rows: List[Dict[str, Any]], col: str) -> List[float]:
    out = []
    for r in rows:
        v = r.get(col, "")
        try:
            out.append(float(v))
        except (ValueError, TypeError):
            out.append(None)
    return out


def _pearson(xs: List[float], ys: List[float]) -> str:
    """Return Pearson r for paired lists, skipping rows where either is None."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 2:
        return ""
    sx = sum(p[0] for p in pairs)
    sy = sum(p[1] for p in pairs)
    mx, my = sx / n, sy / n
    cov = sum((p[0] - mx) * (p[1] - my) for p in pairs)
    std_x = math.sqrt(sum((p[0] - mx) ** 2 for p in pairs))
    std_y = math.sqrt(sum((p[1] - my) ** 2 for p in pairs))
    if std_x == 0 or std_y == 0:
        return ""
    r = cov / (std_x * std_y)
    return f"{r:.6f}"


def correlate_pair(
    rows: List[Dict[str, Any]], col_a: str, col_b: str
) -> Dict[str, str]:
    """Return a single-row result with col_a, col_b, and r."""
    xs = _numeric_values(rows, col_a)
    ys = _numeric_values(rows, col_b)
    return {"col_a": col_a, "col_b": col_b, "r": _pearson(xs, ys)}


def correlate_matrix(
    rows: List[Dict[str, Any]], columns: List[str]
) -> List[Dict[str, str]]:
    """Return all pairwise correlations for the given columns."""
    results = []
    for i, a in enumerate(columns):
        for b in columns[i + 1 :]:
            results.append(correlate_pair(rows, a, b))
    return results


def correlate_all(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Auto-detect numeric columns and compute all pairwise correlations."""
    if not rows:
        return []
    numeric_cols = [
        col
        for col in rows[0].keys()
        if any(
            _try_float(r.get(col, "")) is not None for r in rows
        )
    ]
    return correlate_matrix(rows, numeric_cols)


def _try_float(v: Any):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None
