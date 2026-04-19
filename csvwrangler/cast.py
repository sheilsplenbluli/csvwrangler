"""Column type inference and auto-casting."""
from __future__ import annotations
from typing import List, Dict, Any
import re

_INT_RE = re.compile(r'^-?\d+$')
_FLOAT_RE = re.compile(r'^-?\d+\.\d*$|^-?\.\d+$')


def _infer_type(values: List[str]) -> str:
    """Return 'int', 'float', or 'str' based on non-empty values."""
    non_empty = [v for v in values if v.strip() != '']
    if not non_empty:
        return 'str'
    if all(_INT_RE.match(v.strip()) for v in non_empty):
        return 'int'
    if all(_FLOAT_RE.match(v.strip()) or _INT_RE.match(v.strip()) for v in non_empty):
        return 'float'
    return 'str'


def infer_types(rows: List[Dict[str, str]]) -> Dict[str, str]:
    """Return a mapping of column -> inferred type."""
    if not rows:
        return {}
    columns = list(rows[0].keys())
    return {col: _infer_type([r.get(col, '') for r in rows]) for col in columns}


def _cast_value(value: str, typ: str) -> Any:
    if value.strip() == '':
        return value
    try:
        if typ == 'int':
            return str(int(value.strip()))
        if typ == 'float':
            return str(float(value.strip()))
    except (ValueError, TypeError):
        pass
    return value


def auto_cast(rows: List[Dict[str, str]], columns: List[str] | None = None) -> List[Dict[str, str]]:
    """Auto-detect and cast columns. If columns is None, apply to all."""
    if not rows:
        return rows
    target = columns if columns is not None else list(rows[0].keys())
    types = {col: _infer_type([r.get(col, '') for r in rows]) for col in target}
    result = []
    for row in rows:
        new_row = dict(row)
        for col in target:
            if col in new_row:
                new_row[col] = _cast_value(new_row[col], types[col])
        result.append(new_row)
    return result
