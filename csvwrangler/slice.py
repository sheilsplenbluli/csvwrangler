"""Row slicing by index range."""
from typing import List, Dict, Optional

Row = Dict[str, str]


def slice_rows(
    rows: List[Row],
    start: Optional[int] = None,
    stop: Optional[int] = None,
    step: Optional[int] = None,
) -> List[Row]:
    """Return rows[start:stop:step] using standard Python slice semantics."""
    return rows[slice(start, stop, step)]


def slice_between(
    rows: List[Row],
    start: int = 0,
    stop: Optional[int] = None,
) -> List[Row]:
    """Return rows from *start* (inclusive) up to *stop* (exclusive).

    Negative indices are supported and follow Python conventions.
    """
    if stop is None:
        return rows[start:]
    return rows[start:stop]


def every_nth(rows: List[Row], n: int) -> List[Row]:
    """Return every nth row (1-based: n=1 returns all, n=2 returns every other)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    return rows[::n]
