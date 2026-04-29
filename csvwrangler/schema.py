"""Schema validation: check CSV columns against expected types and constraints."""

from __future__ import annotations

from typing import Any


_VALID_TYPES = {"int", "float", "str", "nonempty"}


def _is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _check_value(value: str, expected_type: str) -> bool:
    """Return True if value satisfies expected_type."""
    if expected_type == "int":
        return _is_int(value)
    if expected_type == "float":
        return _is_float(value)
    if expected_type == "nonempty":
        return value.strip() != ""
    if expected_type == "str":
        return True
    raise ValueError(f"Unknown type: {expected_type!r}")


def validate_schema(
    rows: list[dict[str, str]],
    schema: dict[str, str],
) -> list[dict[str, Any]]:
    """Validate each row against the schema.

    schema maps column name -> expected type (int, float, str, nonempty).
    Returns a list of error dicts with keys: row, column, value, expected.
    """
    errors: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows):
        for column, expected_type in schema.items():
            value = row.get(column, "")
            if not _check_value(value, expected_type):
                errors.append(
                    {
                        "row": row_index + 1,
                        "column": column,
                        "value": value,
                        "expected": expected_type,
                    }
                )
    return errors


def schema_summary(errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarise validation errors by column."""
    by_column: dict[str, int] = {}
    for err in errors:
        by_column[err["column"]] = by_column.get(err["column"], 0) + 1
    return {
        "total_errors": len(errors),
        "by_column": by_column,
        "passed": len(errors) == 0,
    }
