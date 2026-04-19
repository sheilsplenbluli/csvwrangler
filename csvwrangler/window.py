"""Rolling/window calculations over CSV rows."""
from typing import List, Dict, Optional


def _numeric_values(rows: List[Dict], col: str, idx: int, window: int) -> List[float]:
    start = max(0, idx - window + 1)
    vals = []
    for r in rows[start:idx + 1]:
        try:
            vals.append(float(r[col]))
        except (ValueError, TypeError, KeyError):
            pass
    return vals


def rolling_mean(rows: List[Dict], col: str, window: int, dest: Optional[str] = None) -> List[Dict]:
    out_col = dest or f"{col}_rolling_mean"
    result = []
    for i, row in enumerate(rows):
        vals = _numeric_values(rows, col, i, window)
        new_row = dict(row)
        new_row[out_col] = str(round(sum(vals) / len(vals), 6)) if vals else ""
        result.append(new_row)
    return result


def rolling_sum(rows: List[Dict], col: str, window: int, dest: Optional[str] = None) -> List[Dict]:
    out_col = dest or f"{col}_rolling_sum"
    result = []
    for i, row in enumerate(rows):
        vals = _numeric_values(rows, col, i, window)
        new_row = dict(row)
        new_row[out_col] = str(round(sum(vals), 6)) if vals else ""
        result.append(new_row)
    return result


def rolling_min(rows: List[Dict], col: str, window: int, dest: Optional[str] = None) -> List[Dict]:
    out_col = dest or f"{col}_rolling_min"
    result = []
    for i, row in enumerate(rows):
        vals = _numeric_values(rows, col, i, window)
        new_row = dict(row)
        new_row[out_col] = str(min(vals)) if vals else ""
        result.append(new_row)
    return result


def rolling_max(rows: List[Dict], col: str, window: int, dest: Optional[str] = None) -> List[Dict]:
    out_col = dest or f"{col}_rolling_max"
    result = []
    for i, row in enumerate(rows):
        vals = _numeric_values(rows, col, i, window)
        new_row = dict(row)
        new_row[out_col] = str(max(vals)) if vals else ""
        result.append(new_row)
    return result
