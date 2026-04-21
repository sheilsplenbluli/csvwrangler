"""Column-level comparison utilities for CSV rows."""
from __future__ import annotations

from typing import Any


def _try_numeric(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def compare_columns(
    rows: list[dict],
    col_a: str,
    col_b: str,
    dest: str = "_cmp",
    mode: str = "diff",
) -> list[dict]:
    """Add a derived column comparing col_a and col_b.

    mode options:
      diff   – numeric difference (a - b); empty if non-numeric
      ratio  – a / b; empty if non-numeric or b==0
      eq     – '1' if equal (case-insensitive string), else '0'
      gt     – '1' if a > b numerically, else '0'
      lt     – '1' if a < b numerically, else '0'
    """
    if mode not in {"diff", "ratio", "eq", "gt", "lt"}:
        raise ValueError(f"Unknown mode: {mode!r}")

    result = []
    for row in rows:
        new_row = dict(row)
        a_raw = row.get(col_a, "")
        b_raw = row.get(col_b, "")
        a_num = _try_numeric(a_raw)
        b_num = _try_numeric(b_raw)

        if mode == "diff":
            new_row[dest] = str(a_num - b_num) if a_num is not None and b_num is not None else ""
        elif mode == "ratio":
            if a_num is not None and b_num is not None and b_num != 0:
                new_row[dest] = str(a_num / b_num)
            else:
                new_row[dest] = ""
        elif mode == "eq":
            new_row[dest] = "1" if a_raw.strip().lower() == b_raw.strip().lower() else "0"
        elif mode == "gt":
            new_row[dest] = "1" if a_num is not None and b_num is not None and a_num > b_num else "0"
        elif mode == "lt":
            new_row[dest] = "1" if a_num is not None and b_num is not None and a_num < b_num else "0"

        result.append(new_row)
    return result


def compare_many(
    rows: list[dict],
    specs: list[dict],
) -> list[dict]:
    """Apply multiple compare_columns specs in sequence.

    Each spec is a dict with keys: col_a, col_b, dest (optional), mode (optional).
    """
    for spec in specs:
        rows = compare_columns(
            rows,
            col_a=spec["col_a"],
            col_b=spec["col_b"],
            dest=spec.get("dest", "_cmp"),
            mode=spec.get("mode", "diff"),
        )
    return rows
