"""coalesce.py – fill empty values from the first non-empty sibling column."""
from __future__ import annotations
from typing import Iterable


def coalesce_columns(
    rows: list[dict],
    sources: list[str],
    dest: str,
    keep_sources: bool = True,
) -> list[dict]:
    """For each row, set *dest* to the first non-empty value among *sources*.

    Args:
        rows: input rows.
        sources: ordered list of column names to check.
        dest: name of the output column.
        keep_sources: when False, drop the source columns from the output.

    Returns:
        New list of dicts; originals are not mutated.
    """
    out: list[dict] = []
    for row in rows:
        new_row = dict(row)
        value = ""
        for col in sources:
            v = new_row.get(col, "")
            if v is not None and str(v).strip() != "":
                value = v
                break
        new_row[dest] = value
        if not keep_sources and dest not in sources:
            for col in sources:
                new_row.pop(col, None)
        out.append(new_row)
    return out


def coalesce_with_default(
    rows: list[dict],
    sources: list[str],
    dest: str,
    default: str = "",
    keep_sources: bool = True,
) -> list[dict]:
    """Like coalesce_columns but fills with *default* when all sources are empty."""
    result = coalesce_columns(rows, sources, dest, keep_sources=keep_sources)
    for row in result:
        if str(row.get(dest, "")).strip() == "":
            row[dest] = default
    return result
