"""Moving / expanding window aggregations (sum, mean, min, max, count)."""

from __future__ import annotations

from typing import Iterable, List, Dict


def _try_float(value: str):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _expanding_agg(rows: List[Dict], column: str, agg: str, dest: str) -> List[Dict]:
    results = []
    numeric_so_far = []

    for row in rows:
        val = _try_float(row.get(column, ""))
        if val is not None:
            numeric_so_far.append(val)

        if not numeric_so_far:
            out_val = ""
        elif agg == "sum":
            out_val = str(sum(numeric_so_far))
        elif agg == "mean":
            out_val = str(sum(numeric_so_far) / len(numeric_so_far))
        elif agg == "min":
            out_val = str(min(numeric_so_far))
        elif agg == "max":
            out_val = str(max(numeric_so_far))
        elif agg == "count":
            out_val = str(len(numeric_so_far))
        else:
            raise ValueError(f"Unknown aggregation: {agg!r}")

        new_row = dict(row)
        new_row[dest] = out_val
        results.append(new_row)

    return results


def expanding_agg(rows: Iterable[Dict], column: str, agg: str = "sum", dest: str = "") -> List[Dict]:
    """Compute an expanding-window aggregation over *column*.

    Parameters
    ----------
    rows:   iterable of dicts
    column: source column name
    agg:    one of sum | mean | min | max | count
    dest:   destination column name (defaults to '<column>_exp_<agg>')
    """
    rows = list(rows)
    if not dest:
        dest = f"{column}_exp_{agg}"
    return _expanding_agg(rows, column, agg, dest)


def expanding_many(rows: Iterable[Dict], specs: List[Dict]) -> List[Dict]:
    """Apply multiple expanding aggregations in sequence.

    Each spec dict must have keys: column, agg, and optionally dest.
    """
    result = list(rows)
    for spec in specs:
        col = spec["column"]
        agg = spec.get("agg", "sum")
        dest = spec.get("dest", "")
        result = expanding_agg(result, col, agg, dest)
    return result
