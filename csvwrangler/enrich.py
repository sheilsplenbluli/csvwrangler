"""Add computed columns to CSV rows."""
from __future__ import annotations

import re
from typing import Callable, Iterable


_FIELD_RE = re.compile(r"\{(\w+)\}")


def _make_template_fn(template: str) -> Callable[[dict], str]:
    fields = _FIELD_RE.findall(template)

    def _fn(row: dict) -> str:
        result = template
        for f in fields:
            result = result.replace(f"{{{f}}}", row.get(f, ""))
        return result

    return _fn


def _make_math_fn(expr: str) -> Callable[[dict], str]:
    fields = _FIELD_RE.findall(expr)

    def _fn(row: dict) -> str:
        local: dict = {}
        for f in fields:
            try:
                local[f] = float(row.get(f, 0))
            except (ValueError, TypeError):
                local[f] = 0.0
        try:
            safe_expr = _FIELD_RE.sub(lambda m: m.group(1), expr)
            return str(eval(safe_expr, {"__builtins__": {}}, local))  # noqa: S307
        except Exception:
            return ""

    return _fn


def add_column(
    rows: Iterable[dict],
    new_col: str,
    template: str,
    mode: str = "template",
) -> list[dict]:
    """Return rows with *new_col* appended.

    mode='template' — string interpolation using {field} placeholders.
    mode='math'     — arithmetic expression using {field} placeholders.
    """
    if mode == "math":
        fn = _make_math_fn(template)
    else:
        fn = _make_template_fn(template)

    result = []
    for row in rows:
        new_row = dict(row)
        new_row[new_col] = fn(row)
        result.append(new_row)
    return result


def add_row_number(
    rows: Iterable[dict],
    col_name: str = "row_num",
    start: int = 1,
) -> list[dict]:
    """Prepend a sequential row-number column."""
    result = []
    for i, row in enumerate(rows, start=start):
        new_row = {col_name: str(i)}
        new_row.update(row)
        result.append(new_row)
    return result
