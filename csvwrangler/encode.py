"""One-hot encoding and label encoding for categorical columns."""
from typing import List, Dict, Any, Optional


def _unique_values(rows: List[Dict[str, Any]], column: str) -> List[str]:
    seen = []
    for row in rows:
        val = row.get(column, "")
        if val not in seen:
            seen.append(val)
    return seen


def onehot_encode(
    rows: List[Dict[str, Any]],
    column: str,
    prefix: Optional[str] = None,
    drop_original: bool = False,
) -> List[Dict[str, Any]]:
    """Add a binary column for each unique value in *column*.

    New columns are named ``<prefix>_<value>`` (prefix defaults to column name).
    """
    if not rows:
        return []
    pfx = prefix if prefix is not None else column
    categories = _unique_values(rows, column)
    result = []
    for row in rows:
        new_row = dict(row)
        val = row.get(column, "")
        for cat in categories:
            new_row[f"{pfx}_{cat}"] = "1" if val == cat else "0"
        if drop_original:
            new_row.pop(column, None)
        result.append(new_row)
    return result


def label_encode(
    rows: List[Dict[str, Any]],
    column: str,
    dest: Optional[str] = None,
    mapping: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
    """Replace *column* values with integer labels.

    If *mapping* is not provided, labels are assigned in order of first
    appearance (0-based). The encoded values are written to *dest* (defaults
    to ``<column>_encoded``).
    """
    if not rows:
        return []
    dest_col = dest if dest is not None else f"{column}_encoded"
    if mapping is None:
        categories = _unique_values(rows, column)
        mapping = {v: i for i, v in enumerate(categories)}
    result = []
    for row in rows:
        new_row = dict(row)
        val = row.get(column, "")
        new_row[dest_col] = str(mapping.get(val, ""))
        result.append(new_row)
    return result


def encode_many(
    rows: List[Dict[str, Any]],
    columns: List[str],
    mode: str = "onehot",
    drop_original: bool = False,
) -> List[Dict[str, Any]]:
    """Apply encoding to multiple columns sequentially."""
    for col in columns:
        if mode == "label":
            rows = label_encode(rows, col)
        else:
            rows = onehot_encode(rows, col, drop_original=drop_original)
    return rows
