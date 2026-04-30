"""String case conversion utilities for CSV columns."""

import re
from typing import List, Dict


def _to_snake(value: str) -> str:
    """Convert a string to snake_case."""
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', value)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    s = re.sub(r'[\s\-]+', '_', s)
    return s.lower().strip('_')


def _to_camel(value: str) -> str:
    """Convert a string to camelCase."""
    parts = re.split(r'[\s_\-]+', value.strip())
    if not parts:
        return value
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])


def _to_pascal(value: str) -> str:
    """Convert a string to PascalCase."""
    parts = re.split(r'[\s_\-]+', value.strip())
    return ''.join(p.capitalize() for p in parts if p)


def _to_kebab(value: str) -> str:
    """Convert a string to kebab-case."""
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', value)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1-\2', s)
    s = re.sub(r'[\s_]+', '-', s)
    return s.lower().strip('-')


_CONVERTERS = {
    'snake': _to_snake,
    'camel': _to_camel,
    'pascal': _to_pascal,
    'kebab': _to_kebab,
}


def strcase_column(
    rows: List[Dict[str, str]],
    column: str,
    mode: str,
    dest: str = None,
) -> List[Dict[str, str]]:
    """Apply a case conversion to *column*, writing result to *dest*."""
    if mode not in _CONVERTERS:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(_CONVERTERS)}.")
    fn = _CONVERTERS[mode]
    dest = dest or column
    result = []
    for row in rows:
        new_row = dict(row)
        raw = row.get(column, '')
        new_row[dest] = fn(raw) if raw else raw
        result.append(new_row)
    return result


def strcase_many(
    rows: List[Dict[str, str]],
    specs: List[Dict],
) -> List[Dict[str, str]]:
    """Apply multiple strcase transformations in sequence.

    Each spec: {'column': str, 'mode': str, 'dest': str (optional)}
    """
    for spec in specs:
        rows = strcase_column(
            rows,
            column=spec['column'],
            mode=spec['mode'],
            dest=spec.get('dest'),
        )
    return rows
