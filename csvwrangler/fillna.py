"""Fill missing/empty values in CSV rows."""
from typing import List, Dict, Any, Optional

Row = Dict[str, str]


def fill_value(rows: List[Row], column: str, value: str) -> List[Row]:
    """Replace empty strings in *column* with *value*."""
    out = []
    for row in rows:
        r = dict(row)
        if r.get(column, "").strip() == "":
            r[column] = value
        out.append(r)
    return out


def fill_forward(rows: List[Row], column: str) -> List[Row]:
    """Propagate last seen non-empty value forward in *column*."""
    out = []
    last: Optional[str] = None
    for row in rows:
        r = dict(row)
        if r.get(column, "").strip() != "":
            last = r[column]
        elif last is not None:
            r[column] = last
        out.append(r)
    return out


def fill_backward(rows: List[Row], column: str) -> List[Row]:
    """Propagate next seen non-empty value backward in *column*."""
    reversed_rows = fill_forward(list(reversed(rows)), column)
    return list(reversed(reversed_rows))


def fill_many(
    rows: List[Row],
    fills: List[Dict[str, Any]],
) -> List[Row]:
    """Apply multiple fill operations sequentially.

    Each entry in *fills* should have:
      - ``column``: column name
      - ``method``: 'value', 'forward', or 'backward'
      - ``value``: required when method == 'value'
    """
    for spec in fills:
        col = spec["column"]
        method = spec.get("method", "value")
        if method == "value":
            rows = fill_value(rows, col, spec.get("value", ""))
        elif method == "forward":
            rows = fill_forward(rows, col)
        elif method == "backward":
            rows = fill_backward(rows, col)
        else:
            raise ValueError(f"Unknown fill method: {method!r}")
    return rows
