"""Resample time-series CSV rows by a date column and frequency."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional


_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
]


def _parse_date(value: str) -> Optional[datetime]:
    for fmt in _FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def _bucket_key(dt: datetime, freq: str) -> str:
    freq = freq.upper()
    if freq == "Y":
        return dt.strftime("%Y")
    if freq == "M":
        return dt.strftime("%Y-%m")
    if freq == "W":
        iso = dt.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    if freq == "D":
        return dt.strftime("%Y-%m-%d")
    raise ValueError(f"Unknown frequency '{freq}'. Use Y, M, W, or D.")


def resample_rows(
    rows: List[Dict[str, str]],
    date_col: str,
    freq: str,
    agg_col: str,
    agg: str = "sum",
    dest: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Group rows by date bucket and aggregate a numeric column."""
    buckets: Dict[str, List[float]] = defaultdict(list)

    for row in rows:
        raw = row.get(date_col, "")
        dt = _parse_date(raw)
        if dt is None:
            continue
        key = _bucket_key(dt, freq)
        try:
            buckets[key].append(float(row.get(agg_col, "")))
        except (ValueError, TypeError):
            pass

    out_col = dest or f"{agg_col}_{agg}"
    result = []
    for bucket in sorted(buckets):
        vals = buckets[bucket]
        if not vals:
            continue
        if agg == "sum":
            agg_val = sum(vals)
        elif agg == "mean":
            agg_val = sum(vals) / len(vals)
        elif agg == "count":
            agg_val = float(len(vals))
        elif agg == "min":
            agg_val = min(vals)
        elif agg == "max":
            agg_val = max(vals)
        else:
            raise ValueError(f"Unknown aggregation '{agg}'. Use sum, mean, count, min, or max.")
        result.append({date_col: bucket, out_col: str(agg_val)})

    return result
