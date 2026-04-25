"""Conditional column assignment: set a column value based on a condition."""
from typing import Any, Dict, List, Optional


def _eval_condition(row: Dict[str, str], column: str, op: str, value: str) -> bool:
    """Evaluate a simple condition against a row."""
    cell = row.get(column, "")
    op = op.strip().lower()

    # Try numeric comparison first
    try:
        cell_num = float(cell)
        val_num = float(value)
        if op == "eq":
            return cell_num == val_num
        if op == "ne":
            return cell_num != val_num
        if op == "gt":
            return cell_num > val_num
        if op == "gte":
            return cell_num >= val_num
        if op == "lt":
            return cell_num < val_num
        if op == "lte":
            return cell_num <= val_num
    except (ValueError, TypeError):
        pass

    # String comparisons
    if op == "eq":
        return cell == value
    if op == "ne":
        return cell != value
    if op == "contains":
        return value in cell
    if op == "startswith":
        return cell.startswith(value)
    if op == "endswith":
        return cell.endswith(value)
    if op == "empty":
        return cell.strip() == ""
    if op == "notempty":
        return cell.strip() != ""

    return False


def conditional_set(
    rows: List[Dict[str, str]],
    dest: str,
    column: str,
    op: str,
    value: str,
    then_val: str,
    else_val: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Return new rows with dest set to then_val or else_val based on condition."""
    result = []
    for row in rows:
        new_row = dict(row)
        if _eval_condition(row, column, op, value):
            new_row[dest] = then_val
        else:
            new_row[dest] = else_val if else_val is not None else row.get(dest, "")
        result.append(new_row)
    return result


def conditional_many(
    rows: List[Dict[str, str]],
    specs: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Apply multiple conditional_set specs in sequence.

    Each spec dict: {dest, column, op, value, then_val, else_val (optional)}
    """
    for spec in specs:
        rows = conditional_set(
            rows,
            dest=spec["dest"],
            column=spec["column"],
            op=spec["op"],
            value=spec.get("value", ""),
            then_val=spec["then_val"],
            else_val=spec.get("else_val"),
        )
    return rows
