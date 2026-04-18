"""Pivot and unpivot (melt) operations for CSV rows."""
from collections import defaultdict
from typing import List, Dict, Any, Optional


def pivot_rows(
    rows: List[Dict[str, Any]],
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "first",
) -> List[Dict[str, Any]]:
    """Pivot rows: unique values of `columns` become new column headers."""
    if aggfunc not in ("first", "last", "sum", "count"):
        raise ValueError(f"Unknown aggfunc: {aggfunc!r}")

    buckets: Dict[str, Dict[str, List[Any]]] = defaultdict(lambda: defaultdict(list))
    col_order: List[str] = []

    for row in rows:
        idx_val = row.get(index, "")
        col_val = str(row.get(columns, ""))
        val = row.get(values, "")
        buckets[idx_val][col_val].append(val)
        if col_val not in col_order:
            col_order.append(col_val)

    result = []
    for idx_val, col_map in buckets.items():
        out: Dict[str, Any] = {index: idx_val}
        for col_val in col_order:
            vals = col_map.get(col_val, [])
            if not vals:
                out[col_val] = ""
            elif aggfunc == "first":
                out[col_val] = vals[0]
            elif aggfunc == "last":
                out[col_val] = vals[-1]
            elif aggfunc == "sum":
                try:
                    out[col_val] = sum(float(v) for v in vals)
                except (ValueError, TypeError):
                    out[col_val] = ""
            elif aggfunc == "count":
                out[col_val] = len(vals)
        result.append(out)
    return result


def melt_rows(
    rows: List[Dict[str, Any]],
    id_vars: List[str],
    value_vars: Optional[List[str]] = None,
    var_name: str = "variable",
    value_name: str = "value",
) -> List[Dict[str, Any]]:
    """Unpivot rows: turn columns into rows."""
    if not rows:
        return []
    if value_vars is None:
        value_vars = [c for c in rows[0].keys() if c not in id_vars]

    result = []
    for row in rows:
        base = {k: row[k] for k in id_vars if k in row}
        for var in value_vars:
            result.append({**base, var_name: var, value_name: row.get(var, "")})
    return result
