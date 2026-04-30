"""Word count and character count utilities for CSV columns."""
from __future__ import annotations

from typing import Iterable


def _split_words(value: str, sep: str | None = None) -> list[str]:
    """Split value into words, stripping empty tokens."""
    if sep is None:
        return value.split()
    return [w for w in value.split(sep) if w]


def word_count(
    rows: Iterable[dict],
    column: str,
    dest: str | None = None,
    sep: str | None = None,
) -> list[dict]:
    """Add a column with the number of whitespace-delimited words in *column*."""
    dest = dest or f"{column}_word_count"
    result = []
    for row in rows:
        value = row.get(column, "")
        count = len(_split_words(value, sep)) if value else 0
        result.append({**row, dest: str(count)})
    return result


def char_count(
    rows: Iterable[dict],
    column: str,
    dest: str | None = None,
    strip: bool = True,
) -> list[dict]:
    """Add a column with the character count of *column* (optionally stripped)."""
    dest = dest or f"{column}_char_count"
    result = []
    for row in rows:
        value = row.get(column, "")
        measured = value.strip() if strip else value
        result.append({**row, dest: str(len(measured))})
    return result


def wordcount_many(
    rows: Iterable[dict],
    specs: list[dict],
) -> list[dict]:
    """Apply multiple word/char count operations.

    Each spec dict may have keys:
      column (str), mode ('word'|'char'), dest (str|None),
      sep (str|None), strip (bool).
    """
    rows = list(rows)
    for spec in specs:
        col = spec["column"]
        mode = spec.get("mode", "word")
        dest = spec.get("dest")
        if mode == "word":
            rows = word_count(rows, col, dest=dest, sep=spec.get("sep"))
        elif mode == "char":
            rows = char_count(rows, col, dest=dest, strip=spec.get("strip", True))
        else:
            raise ValueError(f"Unknown mode: {mode!r}. Use 'word' or 'char'.")
    return rows
