"""Regex-based find-and-replace for CSV columns."""

import re
from typing import Dict, List, Optional


def _compile(pattern: str, ignore_case: bool) -> re.Pattern:
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def regex_replace(
    rows: List[Dict],
    column: str,
    pattern: str,
    replacement: str,
    dest: Optional[str] = None,
    ignore_case: bool = False,
    count: int = 0,
) -> List[Dict]:
    """Replace regex matches in *column* with *replacement*.

    Args:
        rows: input rows.
        column: column to search.
        pattern: regex pattern string.
        replacement: replacement string (supports backreferences like \\1).
        dest: destination column name; defaults to *column* (in-place).
        ignore_case: compile pattern case-insensitively.
        count: max substitutions per value (0 = all).

    Returns:
        New list of rows with replacements applied.
    """
    dest = dest or column
    rx = _compile(pattern, ignore_case)
    result = []
    for row in rows:
        new_row = dict(row)
        value = row.get(column, "")
        new_row[dest] = rx.sub(replacement, value, count=count)
        result.append(new_row)
    return result


def regex_replace_many(
    rows: List[Dict],
    specs: List[Dict],
) -> List[Dict]:
    """Apply multiple regex replacements in sequence.

    Each spec dict must have keys: column, pattern, replacement.
    Optional keys: dest, ignore_case, count.
    """
    for spec in specs:
        rows = regex_replace(
            rows,
            column=spec["column"],
            pattern=spec["pattern"],
            replacement=spec["replacement"],
            dest=spec.get("dest"),
            ignore_case=spec.get("ignore_case", False),
            count=spec.get("count", 0),
        )
    return rows
