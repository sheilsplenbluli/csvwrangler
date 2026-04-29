"""Replace sentinel/placeholder values with empty string or a custom value."""

from typing import Iterable, Iterator

_DEFAULT_SENTINELS = {"N/A", "NA", "n/a", "na", "NULL", "null", "None", "none", "-", "--", "N.A.", "?"}


def replace_sentinels(
    rows: Iterable[dict],
    columns: list[str] | None = None,
    sentinels: set[str] | None = None,
    replacement: str = "",
    strip: bool = True,
) -> Iterator[dict]:
    """Yield rows with sentinel values replaced.

    Args:
        rows: iterable of dicts.
        columns: columns to check; None means all columns.
        sentinels: set of strings to treat as missing; defaults to _DEFAULT_SENTINELS.
        replacement: value to substitute in place of a sentinel.
        strip: if True, strip whitespace before comparing.
    """
    sentinel_set = sentinels if sentinels is not None else _DEFAULT_SENTINELS

    for row in rows:
        new_row = dict(row)
        targets = columns if columns is not None else list(new_row.keys())
        for col in targets:
            if col not in new_row:
                continue
            val = new_row[col]
            cmp = val.strip() if strip else val
            if cmp in sentinel_set:
                new_row[col] = replacement
        yield new_row


def sentinel_report(
    rows: Iterable[dict],
    columns: list[str] | None = None,
    sentinels: set[str] | None = None,
    strip: bool = True,
) -> dict[str, int]:
    """Return a dict mapping column name -> count of sentinel values found."""
    sentinel_set = sentinels if sentinels is not None else _DEFAULT_SENTINELS
    counts: dict[str, int] = {}

    for row in rows:
        targets = columns if columns is not None else list(row.keys())
        for col in targets:
            if col not in row:
                continue
            val = row[col]
            cmp = val.strip() if strip else val
            if cmp in sentinel_set:
                counts[col] = counts.get(col, 0) + 1

    return counts
