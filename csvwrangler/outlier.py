"""Outlier detection for CSV columns using IQR or z-score methods."""
from __future__ import annotations
import statistics
from typing import List, Dict, Any, Literal


def _numeric_values(rows: List[Dict[str, Any]], column: str) -> List[float]:
    result = []
    for row in rows:
        val = row.get(column, "")
        try:
            result.append(float(val))
        except (ValueError, TypeError):
            pass
    return result


def _iqr_bounds(values: List[float], factor: float = 1.5):
    q1 = statistics.quantiles(values, n=4)[0]
    q3 = statistics.quantiles(values, n=4)[2]
    iqr = q3 - q1
    return q1 - factor * iqr, q3 + factor * iqr


def _zscore_bounds(values: List[float], threshold: float = 3.0):
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    return mean, stdev, threshold


def flag_outliers(
    rows: List[Dict[str, Any]],
    column: str,
    method: Literal["iqr", "zscore"] = "iqr",
    factor: float = 1.5,
    flag_column: str = "_outlier",
) -> List[Dict[str, Any]]:
    """Return rows with an added flag column marking outliers."""
    values = _numeric_values(rows, column)
    if len(values) < 2:
        return [{**row, flag_column: ""} for row in rows]

    if method == "iqr":
        lo, hi = _iqr_bounds(values, factor)
        def is_outlier(v: str) -> bool:
            try:
                f = float(v)
                return f < lo or f > hi
            except (ValueError, TypeError):
                return False
    else:
        mean, stdev, threshold = _zscore_bounds(values, factor)
        def is_outlier(v: str) -> bool:
            try:
                f = float(v)
                return abs(f - mean) / stdev > threshold if stdev else False
            except (ValueError, TypeError):
                return False

    result = []
    for row in rows:
        flagged = is_outlier(row.get(column, ""))
        result.append({**row, flag_column: "1" if flagged else "0"})
    return result


def filter_outliers(
    rows: List[Dict[str, Any]],
    column: str,
    method: Literal["iqr", "zscore"] = "iqr",
    factor: float = 1.5,
    keep: bool = True,
) -> List[Dict[str, Any]]:
    """Return only outlier rows (keep=True) or non-outlier rows (keep=False)."""
    flagged = flag_outliers(rows, column, method, factor)
    return [
        {k: v for k, v in row.items() if k != "_outlier"}
        for row in flagged
        if (row["_outlier"] == "1") == keep
    ]
