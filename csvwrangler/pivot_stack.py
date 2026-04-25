"""Stack and unstack operations for reshaping wide/long CSV data."""
from typing import List, Dict, Any, Optional


def stack_columns(
    rows: List[Dict[str, Any]],
    id_cols: List[str],
    value_cols: List[str],
    var_col: str = "variable",
    val_col: str = "value",
) -> List[Dict[str, Any]]:
    """Stack selected value columns into two columns: variable and value.

    Each input row produces one output row per value column.
    id_cols are repeated for each stacked row.
    """
    if not rows:
        return []
    result = []
    for row in rows:
        for vc in value_cols:
            new_row = {col: row.get(col, "") for col in id_cols}
            new_row[var_col] = vc
            new_row[val_col] = row.get(vc, "")
            result.append(new_row)
    return result


def unstack_column(
    rows: List[Dict[str, Any]],
    id_cols: List[str],
    var_col: str,
    val_col: str,
    fill: str = "",
) -> List[Dict[str, Any]]:
    """Unstack a variable/value pair back to wide format.

    Groups rows by id_cols and pivots unique values of var_col into columns.
    """
    if not rows:
        return []

    # Collect all unique variable names (preserving first-seen order)
    seen_vars: list = []
    for row in rows:
        v = row.get(var_col, "")
        if v not in seen_vars:
            seen_vars.append(v)

    # Build index keyed by tuple of id values
    index: Dict[tuple, Dict[str, Any]] = {}
    order: list = []
    for row in rows:
        key = tuple(row.get(c, "") for c in id_cols)
        if key not in index:
            index[key] = {c: row.get(c, "") for c in id_cols}
            order.append(key)
        index[key][row.get(var_col, "")] = row.get(val_col, "")

    result = []
    for key in order:
        base = index[key]
        for v in seen_vars:
            if v not in base:
                base[v] = fill
        result.append(base)
    return result


def stack_summary(rows: List[Dict[str, Any]], id_cols: List[str], value_cols: List[str]) -> Dict[str, Any]:
    """Return a brief summary of a stack operation."""
    return {
        "input_rows": len(rows),
        "output_rows": len(rows) * len(value_cols),
        "id_cols": id_cols,
        "value_cols": value_cols,
    }
