"""Date parsing and extraction utilities for CSV columns."""
from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Optional

_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
]


def _parse(value: str) -> Optional[datetime]:
    for fmt in _FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def extract_parts(
    rows: List[Dict[str, str]],
    column: str,
    parts: List[str],
    prefix: str = "",
) -> List[Dict[str, str]]:
    """Add columns for requested date parts (year, month, day, weekday, quarter)."""
    valid_parts = {"year", "month", "day", "weekday", "quarter"}
    unknown = set(parts) - valid_parts
    if unknown:
        raise ValueError(f"Unknown date parts: {', '.join(sorted(unknown))}")

    result = []
    for row in rows:
        new_row = dict(row)
        dt = _parse(row.get(column, ""))
        for part in parts:
            dest = f"{prefix}{part}" if prefix else f"{column}_{part}"
            if dt is None:
                new_row[dest] = ""
            elif part == "year":
                new_row[dest] = str(dt.year)
            elif part == "month":
                new_row[dest] = str(dt.month)
            elif part == "day":
                new_row[dest] = str(dt.day)
            elif part == "weekday":
                new_row[dest] = dt.strftime("%A")
            elif part == "quarter":
                new_row[dest] = str((dt.month - 1) // 3 + 1)
        result.append(new_row)
    return result


def format_date(
    rows: List[Dict[str, str]],
    column: str,
    fmt: str,
    dest: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Reformat a date column using the given strftime format string."""
    dest = dest or column
    result = []
    for row in rows:
        new_row = dict(row)
        dt = _parse(row.get(column, ""))
        new_row[dest] = dt.strftime(fmt) if dt is not None else ""
        result.append(new_row)
    return result


def date_diff(
    rows: List[Dict[str, str]],
    col_a: str,
    col_b: str,
    unit: str = "days",
    dest: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Compute the difference between two date columns."""
    valid_units = {"days", "hours", "seconds"}
    if unit not in valid_units:
        raise ValueError(f"unit must be one of {valid_units}")
    dest = dest or f"{col_a}_minus_{col_b}"
    result = []
    for row in rows:
        new_row = dict(row)
        da = _parse(row.get(col_a, ""))
        db = _parse(row.get(col_b, ""))
        if da is not None and db is not None:
            delta = da - db
            if unit == "days":
                new_row[dest] = str(delta.days)
            elif unit == "hours":
                new_row[dest] = str(int(delta.total_seconds() // 3600))
            else:
                new_row[dest] = str(int(delta.total_seconds()))
        else:
            new_row[dest] = ""
        result.append(new_row)
    return result
