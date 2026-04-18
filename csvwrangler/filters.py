"""Row filtering logic for csvwrangler."""

import operator
from typing import Callable

OPS = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "lt": operator.lt,
    "gte": operator.ge,
    "lte": operator.le,
    "contains": lambda a, b: b in a,
    "startswith": lambda a, b: a.startswith(b),
    "endswith": lambda a, b: a.endswith(b),
}


def _coerce(value: str, other: str):
    """Try to compare as numbers, fall back to strings."""
    try:
        return float(value), float(other)
    except ValueError:
        return value, other


def build_filter(column: str, op: str, value: str) -> Callable[[dict], bool]:
    """Return a predicate that tests a CSV row (dict) against the given condition."""
    if op not in OPS:
        raise ValueError(f"Unknown operator '{op}'. Choose from: {', '.join(OPS)}.")

    fn = OPS[op]

    def predicate(row: dict) -> bool:
        if column not in row:
            raise KeyError(f"Column '{column}' not found in row.")
        cell = row[column]
        # string-only ops skip coercion
        if op in ("contains", "startswith", "endswith"):
            return fn(cell, value)
        a, b = _coerce(cell, value)
        return fn(a, b)

    return predicate


def apply_filters(rows: list[dict], filters: list[Callable[[dict], bool]]) -> list[dict]:
    """Return only rows that satisfy every filter."""
    result = []
    for row in rows:
        if all(f(row) for f in filters):
            result.append(row)
    return result
