"""Bulk type-casting of CSV columns."""
from __future__ import annotations
from typing import List, Dict, Callable

_CASTERS: Dict[str, Callable[[str], str]] = {
    "int": lambda v: str(int(float(v))) if v.strip() != "" else v,
    "float": lambda v: str(float(v)) if v.strip() != "" else v,
    "upper": lambda v: v.upper(),
    "lower": lambda v: v.lower(),
    "strip": lambda v: v.strip(),
    "bool": lambda v: str(bool(v.strip())) if v.strip() != "" else v,
}


def _cast_value(value: str, cast_type: str) -> str:
    fn = _CASTERS.get(cast_type)
    if fn is None:
        raise ValueError(f"Unknown cast type: {cast_type!r}")
    try:
        return fn(value)
    except (ValueError, TypeError):
        return value


def typecast_column(
    rows: List[Dict[str, str]],
    column: str,
    cast_type: str,
) -> List[Dict[str, str]]:
    """Return new rows with *column* values cast to *cast_type*."""
    result = []
    for row in rows:
        new_row = dict(row)
        if column in new_row:
            new_row[column] = _cast_value(new_row[column], cast_type)
        result.append(new_row)
    return result


def typecast_many(
    rows: List[Dict[str, str]],
    spec: Dict[str, str],
) -> List[Dict[str, str]]:
    """Apply multiple column→cast_type mappings in one pass."""
    result = []
    for row in rows:
        new_row = dict(row)
        for col, cast_type in spec.items():
            if col in new_row:
                new_row[col] = _cast_value(new_row[col], cast_type)
        result.append(new_row)
    return result
