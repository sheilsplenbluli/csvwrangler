"""Transpose rows to columns and columns to rows."""
from typing import List, Dict


def transpose_rows(
    rows: List[Dict[str, str]],
    header_col: str = "field",
) -> List[Dict[str, str]]:
    """Transpose a CSV so each original column becomes a row.

    The first output column is the field name (header_col).
    Remaining columns are row_0, row_1, ... for each original row.
    """
    if not rows:
        return []

    fields = list(rows[0].keys())
    row_labels = [f"row_{i}" for i in range(len(rows))]
    out_fields = [header_col] + row_labels

    result = []
    for field in fields:
        new_row: Dict[str, str] = {header_col: field}
        for i, row in enumerate(rows):
            new_row[f"row_{i}"] = row.get(field, "")
        result.append(new_row)
    return result


def pivot_transpose(
    rows: List[Dict[str, str]],
    key_col: str,
    value_col: str,
) -> List[Dict[str, str]]:
    """Pivot a two-column key/value CSV into a single wide row.

    Each unique value in key_col becomes a column in the output.
    If key_col appears multiple times the last value wins.
    """
    if not rows:
        return []

    wide: Dict[str, str] = {}
    for row in rows:
        k = row.get(key_col, "")
        v = row.get(value_col, "")
        if k:
            wide[k] = v
    return [wide]
