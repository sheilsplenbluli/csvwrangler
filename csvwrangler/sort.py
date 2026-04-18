"""Sorting utilities for CSV rows."""

from typing import Any, Callable, Iterable


def _coerce_for_sort(value: str) -> Any:
    """Try to coerce a string to float for numeric sorting, else lowercase str."""
    try:
        return (0, float(value))
    except (ValueError, TypeError):
        return (1, value.lower())


def _make_sorter(
    key: str,
    reverse: bool = False,
    numeric: bool = False,
) -> Callable[[Iterable[dict]], list[dict]]:
    """Return a function that sorts rows by *key*."""

    def _sort(rows: Iterable[dict]) -> list[dict]:
        row_list = list(rows)
        if numeric:
            return sorted(
                row_list,
                key=lambda r: float(r.get(key, 0) or 0),
                reverse=reverse,
            )
        return sorted(
            row_list,
            key=lambda r: _coerce_for_sort(r.get(key, "")),
            reverse=reverse,
        )

    return _sort


def sort_rows(
    rows: Iterable[dict],
    key: str,
    reverse: bool = False,
    numeric: bool = False,
) -> list[dict]:
    """Sort *rows* (list of dicts) by *key*.

    Parameters
    ----------
    rows:    iterable of row dicts
    key:     column name to sort by
    reverse: descending order when True
    numeric: force numeric (float) comparison
    """
    sorter = _make_sorter(key, reverse=reverse, numeric=numeric)
    return sorter(rows)
