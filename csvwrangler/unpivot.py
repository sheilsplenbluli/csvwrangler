"""Unpivot (melt) wide CSV rows into long format."""
from typing import List, Dict, Any, Optional


def unpivot_rows(
    rows: List[Dict[str, Any]],
    id_cols: List[str],
    value_cols: Optional[List[str]] = None,
    var_name: str = "variable",
    val_name: str = "value",
) -> List[Dict[str, Any]]:
    """Melt wide rows into long format.

    Args:
        rows: input rows.
        id_cols: columns to keep as identifiers.
        value_cols: columns to unpivot; defaults to all non-id columns.
        var_name: name for the new variable column.
        val_name: name for the new value column.

    Returns:
        List of melted rows.
    """
    if not rows:
        return []

    all_cols = list(rows[0].keys())

    if value_cols is None:
        value_cols = [c for c in all_cols if c not in id_cols]

    result: List[Dict[str, Any]] = []
    for row in rows:
        id_part = {col: row.get(col, "") for col in id_cols}
        for vc in value_cols:
            new_row = dict(id_part)
            new_row[var_name] = vc
            new_row[val_name] = row.get(vc, "")
            result.append(new_row)

    return result


def unpivot_summary(rows: List[Dict[str, Any]], id_cols: List[str]) -> Dict[str, Any]:
    """Return basic info about an unpivot operation before running it."""
    if not rows:
        return {"id_cols": id_cols, "value_cols": [], "input_rows": 0, "output_rows": 0}

    all_cols = list(rows[0].keys())
    value_cols = [c for c in all_cols if c not in id_cols]
    output_rows = len(rows) * len(value_cols)

    return {
        "id_cols": id_cols,
        "value_cols": value_cols,
        "input_rows": len(rows),
        "output_rows": output_rows,
    }
