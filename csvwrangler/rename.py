"""Column renaming helpers (bulk / pattern-based)."""
from __future__ import annotations

import re
from typing import Dict, List


def _apply_map(row: Dict[str, str], mapping: Dict[str, str]) -> Dict[str, str]:
    return {mapping.get(k, k): v for k, v in row.items()}


def rename_columns(
    rows: List[Dict[str, str]],
    mapping: Dict[str, str],
) -> List[Dict[str, str]]:
    """Rename columns using an explicit old->new mapping."""
    return [_apply_map(r, mapping) for r in rows]


def rename_prefix(
    rows: List[Dict[str, str]],
    prefix: str,
    columns: List[str] | None = None,
) -> List[Dict[str, str]]:
    """Add a prefix to column names (optionally restricted to *columns*)."""
    def _map(row: Dict[str, str]) -> Dict[str, str]:
        return {
            (prefix + k if (columns is None or k in columns) else k): v
            for k, v in row.items()
        }
    return [_map(r) for r in rows]


def rename_strip(
    rows: List[Dict[str, str]],
    chars: str | None = None,
) -> List[Dict[str, str]]:
    """Strip leading/trailing whitespace (or *chars*) from every column name."""
    def _map(row: Dict[str, str]) -> Dict[str, str]:
        return {k.strip(chars): v for k, v in row.items()}
    return [_map(r) for r in rows]


def rename_pattern(
    rows: List[Dict[str, str]],
    pattern: str,
    replacement: str,
) -> List[Dict[str, str]]:
    """Rename columns by applying a regex substitution to every column name."""
    compiled = re.compile(pattern)

    def _map(row: Dict[str, str]) -> Dict[str, str]:
        return {compiled.sub(replacement, k): v for k, v in row.items()}

    return [_map(r) for r in rows]
