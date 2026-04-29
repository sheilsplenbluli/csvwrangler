"""Reshape rows from long format to wide format by spreading a key column."""
from typing import List, Dict, Any, Optional


def _collect_keys(rows: List[Dict[str, Any]], key_col: str) -> List[str]:
    """Return ordered unique values from key_col across all rows."""
    seen = {}
    for row in rows:
        v = row.get(key_col, "")
        if v not in seen:
            seen[v] = True
    return list(seen.keys())


def spread_rows(
    rows: List[Dict[str, Any]],
    index_col: str,
    key_col: str,
    value_col: str,
    fill: str = "",
    agg: str = "first",
) -> List[Dict[str, Any]]:
    """Spread key/value pairs into wide format.

    Args:
        rows: Input rows in long format.
        index_col: Column whose values identify each output row.
        key_col: Column whose values become new column headers.
        value_col: Column whose values populate the new columns.
        fill: Value used when a combination is missing.
        agg: How to handle duplicate index+key pairs: 'first', 'last', 'sum'.

    Returns:
        List of dicts in wide format.
    """
    keys = _collect_keys(rows, key_col)

    # Accumulate values per (index_value, key_value)
    buckets: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    for row in rows:
        idx = row.get(index_col, "")
        k = row.get(key_col, "")
        v = row.get(value_col, "")

        if idx not in buckets:
            buckets[idx] = {}
            order.append(idx)

        if k not in buckets[idx]:
            buckets[idx][k] = v
        else:
            if agg == "last":
                buckets[idx][k] = v
            elif agg == "sum":
                try:
                    buckets[idx][k] = str(float(buckets[idx][k]) + float(v))
                except (ValueError, TypeError):
                    buckets[idx][k] = v
            # 'first' — keep existing

    result = []
    for idx in order:
        out_row = {index_col: idx}
        for k in keys:
            out_row[k] = buckets[idx].get(k, fill)
        result.append(out_row)

    return result


def spread_summary(rows: List[Dict[str, Any]], key_col: str) -> Dict[str, Any]:
    """Return metadata about the spread operation."""
    keys = _collect_keys(rows, key_col)
    return {"new_columns": keys, "column_count": len(keys)}
