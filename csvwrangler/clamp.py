"""Clamp numeric values to a [min, max] range, with optional scaling."""

from __future__ import annotations

from typing import Any


def _try_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_column(
    rows: list[dict],
    column: str,
    low: float | None = None,
    high: float | None = None,
    dest: str | None = None,
) -> list[dict]:
    """Return new rows with *column* values clamped to [low, high].

    Non-numeric cells are passed through unchanged.  If *dest* is given the
    result is written to a new column and the original is kept intact.
    """
    if low is not None and high is not None and low > high:
        raise ValueError(f"low ({low}) must be <= high ({high})")

    out_col = dest if dest else column
    result = []
    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        num = _try_float(raw)
        if num is None:
            new_row[out_col] = raw
        else:
            clamped = num
            if low is not None:
                clamped = max(clamped, low)
            if high is not None:
                clamped = min(clamped, high)
            # Preserve int-like appearance when possible
            if clamped == int(clamped):
                new_row[out_col] = str(int(clamped))
            else:
                new_row[out_col] = str(clamped)
        result.append(new_row)
    return result


def clamp_many(
    rows: list[dict],
    specs: list[dict],
) -> list[dict]:
    """Apply multiple clamp operations sequentially.

    Each spec is a dict with keys: ``column``, optionally ``low``, ``high``,
    ``dest``.
    """
    for spec in specs:
        rows = clamp_column(
            rows,
            column=spec["column"],
            low=spec.get("low"),
            high=spec.get("high"),
            dest=spec.get("dest"),
        )
    return rows
