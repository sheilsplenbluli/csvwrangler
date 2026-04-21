"""Stringify: format numeric columns as strings with optional formatting options."""

from __future__ import annotations

from typing import Any


def _format_value(value: str, fmt: str | None, prefix: str, suffix: str, decimals: int | None) -> str:
    """Apply formatting to a single cell value."""
    if value == "":
        return value

    if decimals is not None:
        try:
            numeric = float(value)
            value = f"{numeric:.{decimals}f}"
        except (ValueError, TypeError):
            pass

    if fmt == "comma":
        try:
            numeric = float(value)
            if numeric == int(numeric) and decimals is None:
                value = f"{int(numeric):,}"
            else:
                dp = decimals if decimals is not None else 2
                value = f"{numeric:,.{dp}f}"
        except (ValueError, TypeError):
            pass
    elif fmt == "percent":
        try:
            numeric = float(value)
            dp = decimals if decimals is not None else 1
            value = f"{numeric * 100:.{dp}f}%"
        except (ValueError, TypeError):
            pass
    elif fmt == "scientific":
        try:
            numeric = float(value)
            dp = decimals if decimals is not None else 2
            value = f"{numeric:.{dp}e}"
        except (ValueError, TypeError):
            pass

    return f"{prefix}{value}{suffix}"


def stringify_column(
    rows: list[dict[str, Any]],
    column: str,
    *,
    fmt: str | None = None,
    prefix: str = "",
    suffix: str = "",
    decimals: int | None = None,
    dest: str | None = None,
) -> list[dict[str, Any]]:
    """Format values in *column* as strings and return new rows."""
    out_col = dest if dest else column
    result = []
    for row in rows:
        new_row = dict(row)
        raw = str(row.get(column, ""))
        new_row[out_col] = _format_value(raw, fmt, prefix, suffix, decimals)
        result.append(new_row)
    return result


def stringify_many(
    rows: list[dict[str, Any]],
    specs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply multiple stringify specs sequentially.

    Each spec is a dict with 'column' and optional keys:
    fmt, prefix, suffix, decimals, dest.
    """
    for spec in specs:
        column = spec["column"]
        rows = stringify_column(
            rows,
            column,
            fmt=spec.get("fmt"),
            prefix=spec.get("prefix", ""),
            suffix=spec.get("suffix", ""),
            decimals=spec.get("decimals"),
            dest=spec.get("dest"),
        )
    return rows
