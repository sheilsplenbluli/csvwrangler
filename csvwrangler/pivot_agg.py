"""Pivot aggregation: group rows by one column and spread another column's values as headers."""
from collections import defaultdict
from typing import List, Dict, Optional


def _numeric(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def pivot_agg(
    rows: List[Dict],
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "sum",
    fill_value: str = "",
) -> List[Dict]:
    """Pivot rows: index=row key, columns=col headers, values=cell values."""
    if not rows:
        return []

    # collect raw cell data: data[index_val][col_val] -> list of values
    data: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    col_order: List[str] = []
    seen_cols = set()

    for row in rows:
        idx_val = row.get(index, "")
        col_val = row.get(columns, "")
        val = row.get(values, "")
        data[idx_val][col_val].append(val)
        if col_val not in seen_cols:
            seen_cols.add(col_val)
            col_order.append(col_val)

    result = []
    for idx_val, col_map in data.items():
        out_row = {index: idx_val}
        for col_val in col_order:
            raw = col_map.get(col_val, [])
            if not raw:
                out_row[col_val] = fill_value
            else:
                out_row[col_val] = _aggregate(raw, aggfunc, fill_value)
        result.append(out_row)

    return result


def _aggregate(values: List[str], aggfunc: str, fill_value: str) -> str:
    if aggfunc == "count":
        return str(len(values))
    nums = [_numeric(v) for v in values]
    valid = [n for n in nums if n is not None]
    if not valid:
        return fill_value
    if aggfunc == "sum":
        return str(sum(valid))
    if aggfunc == "mean":
        return str(sum(valid) / len(valid))
    if aggfunc == "min":
        return str(min(valid))
    if aggfunc == "max":
        return str(max(valid))
    if aggfunc == "first":
        return values[0]
    if aggfunc == "last":
        return values[-1]
    return fill_value
