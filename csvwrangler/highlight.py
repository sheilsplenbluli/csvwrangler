"""highlight.py — mark rows that match a condition with a flag column."""

from typing import Any, Dict, Iterable, List, Optional


def _coerce(value: str) -> Any:
    """Try to return a numeric value, otherwise return the raw string."""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _matches(row: Dict[str, str], column: str, op: str, operand: str) -> bool:
    """Return True if the row satisfies the condition."""
    raw = row.get(column, "")
    if op in ("eq", "ne", "contains", "startswith", "endswith"):
        cell: Any = raw
        cmp: Any = operand
    else:
        cell = _coerce(raw)
        cmp = _coerce(operand)

    if op == "eq":
        return cell == cmp
    if op == "ne":
        return cell != cmp
    if op == "gt":
        try:
            return float(cell) > float(cmp)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
    if op == "gte":
        try:
            return float(cell) >= float(cmp)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
    if op == "lt":
        try:
            return float(cell) < float(cmp)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
    if op == "lte":
        try:
            return float(cell) <= float(cmp)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
    if op == "contains":
        return cmp in cell
    if op == "startswith":
        return cell.startswith(cmp)
    if op == "endswith":
        return cell.endswith(cmp)
    return False


def highlight_rows(
    rows: Iterable[Dict[str, str]],
    column: str,
    op: str,
    operand: str,
    flag_column: str = "_highlight",
    true_value: str = "1",
    false_value: str = "0",
) -> List[Dict[str, str]]:
    """Add *flag_column* to every row, set to *true_value* when the condition
    matches and *false_value* otherwise."""
    result: List[Dict[str, str]] = []
    for row in rows:
        out = dict(row)
        out[flag_column] = true_value if _matches(row, column, op, operand) else false_value
        result.append(out)
    return result


def highlight_any(
    rows: Iterable[Dict[str, str]],
    conditions: List[Dict[str, str]],
    flag_column: str = "_highlight",
    true_value: str = "1",
    false_value: str = "0",
) -> List[Dict[str, str]]:
    """Flag rows where ANY of *conditions* match.
    Each condition dict must have keys: column, op, operand.
    """
    result: List[Dict[str, str]] = []
    for row in rows:
        matched = any(
            _matches(row, c["column"], c["op"], c["operand"]) for c in conditions
        )
        out = dict(row)
        out[flag_column] = true_value if matched else false_value
        result.append(out)
    return result
