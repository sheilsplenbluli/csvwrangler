"""capwords.py – capitalize / title-case / sentence-case transformations for CSV columns."""
from __future__ import annotations

from typing import Dict, List


def _cap_sentence(value: str) -> str:
    """Capitalize only the first character, lower-case the rest."""
    if not value:
        return value
    return value[0].upper() + value[1:].lower()


def capwords_column(
    rows: List[Dict[str, str]],
    column: str,
    mode: str = "title",
    dest: str | None = None,
) -> List[Dict[str, str]]:
    """Return new rows with *column* transformed.

    Args:
        rows:   Input rows.
        column: Column to transform.
        mode:   One of ``'title'``, ``'upper'``, ``'lower'``, ``'sentence'``.
        dest:   Destination column name.  Defaults to *column* (in-place).

    Returns:
        New list of row dicts; originals are not mutated.
    """
    if mode not in ("title", "upper", "lower", "sentence"):
        raise ValueError(f"Unknown mode {mode!r}. Choose title/upper/lower/sentence.")

    target = dest if dest else column
    out: List[Dict[str, str]] = []
    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        if mode == "title":
            new_row[target] = raw.title()
        elif mode == "upper":
            new_row[target] = raw.upper()
        elif mode == "lower":
            new_row[target] = raw.lower()
        else:  # sentence
            new_row[target] = _cap_sentence(raw)
        out.append(new_row)
    return out


def capwords_many(
    rows: List[Dict[str, str]],
    specs: List[Dict],
) -> List[Dict[str, str]]:
    """Apply multiple capwords transformations in sequence.

    Each spec is a dict with keys ``column``, ``mode`` (optional), ``dest`` (optional).
    """
    result = rows
    for spec in specs:
        result = capwords_column(
            result,
            column=spec["column"],
            mode=spec.get("mode", "title"),
            dest=spec.get("dest"),
        )
    return result
