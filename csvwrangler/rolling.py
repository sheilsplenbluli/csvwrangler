"""Cumulative (running) aggregations over CSV rows."""
from __future__ import annotations

from typing import List, Dict


def _try_float(value: str):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def cumulative_sum(rows: List[Dict], column: str, dest: str = "") -> List[Dict]:
    """Add a running-total column for *column*."""
    dest = dest or f"{column}_cumsum"
    total = 0.0
    out = []
    for row in rows:
        v = _try_float(row.get(column, ""))
        if v is not None:
            total += v
            out.append({**row, dest: str(total)})
        else:
            out.append({**row, dest: ""})
    return out


def cumulative_min(rows: List[Dict], column: str, dest: str = "") -> List[Dict]:
    """Add a running-minimum column for *column*."""
    dest = dest or f"{column}_cummin"
    current_min = None
    out = []
    for row in rows:
        v = _try_float(row.get(column, ""))
        if v is not None:
            current_min = v if current_min is None else min(current_min, v)
            out.append({**row, dest: str(current_min)})
        else:
            out.append({**row, dest: ""})
    return out


def cumulative_max(rows: List[Dict], column: str, dest: str = "") -> List[Dict]:
    """Add a running-maximum column for *column*."""
    dest = dest or f"{column}_cummax"
    current_max = None
    out = []
    for row in rows:
        v = _try_float(row.get(column, ""))
        if v is not None:
            current_max = v if current_max is None else max(current_max, v)
            out.append({**row, dest: str(current_max)})
        else:
            out.append({**row, dest: ""})
    return out


def cumulative_mean(rows: List[Dict], column: str, dest: str = "") -> List[Dict]:
    """Add a running-mean column for *column*."""
    dest = dest or f"{column}_cummean"
    total = 0.0
    count = 0
    out = []
    for row in rows:
        v = _try_float(row.get(column, ""))
        if v is not None:
            total += v
            count += 1
            out.append({**row, dest: str(total / count)})
        else:
            out.append({**row, dest: ""})
    return out
