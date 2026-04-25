"""Mask (redact) column values — full, partial, or pattern-based."""
from __future__ import annotations

import re
from typing import Iterable


def _mask_full(value: str, char: str = "*") -> str:
    """Replace every character with *mask_char*."""
    return char * len(value) if value else value


def _mask_partial(value: str, keep_start: int, keep_end: int, char: str = "*") -> str:
    """Keep *keep_start* chars at start and *keep_end* chars at end; mask middle."""
    if not value:
        return value
    n = len(value)
    if keep_start + keep_end >= n:
        return value  # nothing to mask
    masked_len = n - keep_start - keep_end
    return value[:keep_start] + char * masked_len + value[n - keep_end:] if keep_end else value[:keep_start] + char * masked_len


def _mask_regex(value: str, pattern: re.Pattern, replacement: str = "***") -> str:
    """Replace every regex match in *value* with *replacement*."""
    if not value:
        return value
    return pattern.sub(replacement, value)


def mask_column(
    rows: list[dict],
    column: str,
    *,
    mode: str = "full",
    keep_start: int = 0,
    keep_end: int = 0,
    pattern: str | None = None,
    replacement: str = "***",
    char: str = "*",
) -> list[dict]:
    """Return new rows with *column* values masked.

    Modes:
      - ``full``    – replace every character with *char*.
      - ``partial`` – keep *keep_start* / *keep_end* chars, mask the rest.
      - ``regex``   – replace matches of *pattern* with *replacement*.
    """
    compiled = re.compile(pattern) if mode == "regex" and pattern else None
    result = []
    for row in rows:
        new_row = dict(row)
        value = row.get(column, "")
        if mode == "full":
            new_row[column] = _mask_full(value, char)
        elif mode == "partial":
            new_row[column] = _mask_partial(value, keep_start, keep_end, char)
        elif mode == "regex" and compiled:
            new_row[column] = _mask_regex(value, compiled, replacement)
        result.append(new_row)
    return result


def mask_many(
    rows: list[dict],
    specs: list[dict],
) -> list[dict]:
    """Apply multiple mask specs sequentially.

    Each spec is a dict with ``column`` plus any keyword args accepted by
    :func:`mask_column`.
    """
    for spec in specs:
        spec = dict(spec)
        column = spec.pop("column")
        rows = mask_column(rows, column, **spec)
    return rows
