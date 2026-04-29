"""Convert wide-format rows to long format (unpivot by value columns)."""
from typing import List, Dict, Any, Optional


def wide_to_long(
    rows: List[Dict[str, Any]],
    id_cols: List[str],
    value_cols: Optional[List[str]] = None,
    var_name: str = "variable",
    val_name: str = "value",
) -> List[Dict[str, Any]]:
    """Reshape rows from wide to long format.

    Each value column becomes a separate row with a variable/value pair.
    id_cols are repeated for every value column.
    If value_cols is None, all columns not in id_cols are used.
    """
    if not rows:
        return []

    all_cols = list(rows[0].keys())

    if value_cols is None:
        id_set = set(id_cols)
        value_cols = [c for c in all_cols if c not in id_set]

    result: List[Dict[str, Any]] = []
    for row in rows:
        base = {col: row.get(col, "") for col in id_cols}
        for vc in value_cols:
            new_row = dict(base)
            new_row[var_name] = vc
            new_row[val_name] = row.get(vc, "")
            result.append(new_row)

    return result


def long_to_wide(
    rows: List[Dict[str, Any]],
    id_cols: List[str],
    var_col: str,
    val_col: str,
    fill: str = "",
) -> List[Dict[str, Any]]:
    """Reshape rows from long to wide format.

    Groups by id_cols, pivots var_col values into columns.
    """
    if not rows:
        return []

    # Collect unique variable values (preserving order of first appearance)
    seen_vars: List[str] = []
    seen_set: set = set()
    for row in rows:
        v = row.get(var_col, "")
        if v not in seen_set:
            seen_vars.append(v)
            seen_set.add(v)

    # Group rows by id key
    from collections import OrderedDict
    groups: Dict[tuple, Dict[str, str]] = OrderedDict()
    for row in rows:
        key = tuple(row.get(c, "") for c in id_cols)
        if key not in groups:
            groups[key] = {c: row.get(c, "") for c in id_cols}
        var = row.get(var_col, "")
        groups[key][var] = row.get(val_col, "")

    result = []
    for key, wide_row in groups.items():
        for v in seen_vars:
            if v not in wide_row:
                wide_row[v] = fill
        result.append(wide_row)

    return result
