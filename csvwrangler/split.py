"""Split CSV rows into multiple files based on a column value."""
from __future__ import annotations
from collections import defaultdict
from typing import Iterator


def split_by_column(
    rows: list[dict],
    column: str,
) -> dict[str, list[dict]]:
    """Group rows by unique values in *column*.

    Returns a mapping of {value: [rows]} preserving insertion order.
    Rows missing the column are grouped under the empty-string key.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        key = row.get(column, "")
        groups[key].append(row)
    return dict(groups)


def split_by_row_count(
    rows: list[dict],
    chunk_size: int,
) -> list[list[dict]]:
    """Split *rows* into chunks of at most *chunk_size* rows."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    return [rows[i : i + chunk_size] for i in range(0, len(rows), chunk_size)]


def iter_chunks(rows: list[dict], chunk_size: int) -> Iterator[list[dict]]:
    """Yield successive chunks without building the full list."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    for i in range(0, len(rows), chunk_size):
        yield rows[i : i + chunk_size]
