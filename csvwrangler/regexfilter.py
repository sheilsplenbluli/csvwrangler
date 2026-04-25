"""Regex-based row filtering for CSV data."""
import re
from typing import List, Dict, Optional


def _compile(pattern: str, ignore_case: bool) -> re.Pattern:
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def regex_filter(
    rows: List[Dict[str, str]],
    column: str,
    pattern: str,
    ignore_case: bool = False,
    invert: bool = False,
) -> List[Dict[str, str]]:
    """Keep rows where column value matches the regex pattern.

    Args:
        rows: list of row dicts.
        column: column name to match against.
        pattern: regular expression string.
        ignore_case: if True, match is case-insensitive.
        invert: if True, keep rows that do NOT match.

    Returns:
        Filtered list of row dicts.
    """
    compiled = _compile(pattern, ignore_case)
    result = []
    for row in rows:
        value = row.get(column, "")
        matched = bool(compiled.search(value))
        if invert:
            matched = not matched
        if matched:
            result.append(row)
    return result


def regex_extract(
    rows: List[Dict[str, str]],
    column: str,
    pattern: str,
    dest: Optional[str] = None,
    ignore_case: bool = False,
    group: int = 0,
) -> List[Dict[str, str]]:
    """Extract a regex match (or group) from column into a new dest column.

    Non-matching rows get an empty string in dest.

    Args:
        rows: list of row dicts.
        column: source column.
        pattern: regular expression string.
        dest: destination column name; defaults to '<column>_match'.
        ignore_case: if True, match is case-insensitive.
        group: capture group index (0 = full match).

    Returns:
        New list of row dicts with dest column added.
    """
    compiled = _compile(pattern, ignore_case)
    dest_col = dest if dest else f"{column}_match"
    result = []
    for row in rows:
        new_row = dict(row)
        value = row.get(column, "")
        m = compiled.search(value)
        if m:
            try:
                new_row[dest_col] = m.group(group)
            except IndexError:
                new_row[dest_col] = ""
        else:
            new_row[dest_col] = ""
        result.append(new_row)
    return result
