"""Column validation: check types, nulls, and allowed values."""
from __future__ import annotations

from typing import Iterable


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def validate_column(
    rows: list[dict],
    column: str,
    dtype: str | None = None,
    allow_empty: bool = True,
    allowed: list[str] | None = None,
) -> list[dict]:
    """Return a list of violation dicts for the given column."""
    violations = []
    for i, row in enumerate(rows):
        value = row.get(column, "")
        if not allow_empty and value.strip() == "":
            violations.append({"row": i, "column": column, "value": value, "reason": "empty value"})
            continue
        if value.strip() == "":
            continue
        if dtype == "numeric" and not _is_numeric(value):
            violations.append({"row": i, "column": column, "value": value, "reason": "not numeric"})
        if allowed is not None and value not in allowed:
            violations.append({"row": i, "column": column, "value": value, "reason": f"not in allowed values"})
    return violations


def validate_all(
    rows: list[dict],
    rules: list[dict],
) -> dict[str, list[dict]]:
    """Apply multiple validation rules. rules is a list of dicts with keys:
    column, dtype (optional), allow_empty (optional), allowed (optional)."""
    results = {}
    for rule in rules:
        col = rule["column"]
        viols = validate_column(
            rows,
            column=col,
            dtype=rule.get("dtype"),
            allow_empty=rule.get("allow_empty", True),
            allowed=rule.get("allowed"),
        )
        if viols:
            results[col] = viols
    return results
