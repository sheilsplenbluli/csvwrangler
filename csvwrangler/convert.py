"""Type conversion utilities for CSV columns."""
from __future__ import annotations
from typing import List, Dict, Iterable


def _to_int(value: str) -> str:
    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return value


def _to_float(value: str, decimals: int | None = None) -> str:
    try:
        f = float(value)
        if decimals is not None:
            return f"{f:.{decimals}f}"
        return str(f)
    except (ValueError, TypeError):
        return value


def _to_upper(value: str) -> str:
    return value.upper()


def _to_lower(value: str) -> str:
    return value.lower()


def _to_strip(value: str) -> str:
    return value.strip()


_CONVERTERS = {
    "int": _to_int,
    "float": _to_float,
    "upper": _to_upper,
    "lower": _to_lower,
    "strip": _to_strip,
}


def convert_column(
    rows: List[Dict[str, str]],
    column: str,
    conversion: str,
    decimals: int | None = None,
) -> List[Dict[str, str]]:
    """Apply a named conversion to a single column across all rows."""
    if conversion not in _CONVERTERS:
        raise ValueError(f"Unknown conversion '{conversion}'. Choose from: {list(_CONVERTERS)}.")
    fn = _CONVERTERS[conversion]
    result = []
    for row in rows:
        new_row = dict(row)
        if column in new_row:
            if conversion == "float" and decimals is not None:
                new_row[column] = _to_float(new_row[column], decimals)
            else:
                new_row[column] = fn(new_row[column])
        result.append(new_row)
    return result


def convert_all(
    rows: List[Dict[str, str]],
    conversions: Dict[str, str],
) -> List[Dict[str, str]]:
    """Apply multiple column conversions given a mapping of column->conversion."""
    for column, conversion in conversions.items():
        rows = convert_column(rows, column, conversion)
    return rows
