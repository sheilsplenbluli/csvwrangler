"""Cross-join and conditional join utilities for CSV rows."""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Callable

Row = Dict[str, Any]


def cross_join(left: List[Row], right: List[Row]) -> List[Row]:
    """Return the cartesian product of left and right rows."""
    result = []
    for l in left:
        for r in right:
            merged = {**l}
            for k, v in r.items():
                if k in merged:
                    merged[f"right_{k}"] = v
                else:
                    merged[k] = v
            result.append(merged)
    return result


def conditional_join(
    left: List[Row],
    right: List[Row],
    predicate: Callable[[Row, Row], bool],
    prefix: str = "right_",
) -> List[Row]:
    """Join rows where predicate(left_row, right_row) is True."""
    result = []
    for l in left:
        for r in right:
            if predicate(l, r):
                merged = {**l}
                for k, v in r.items():
                    key = f"{prefix}{k}" if k in merged else k
                    merged[key] = v
                result.append(merged)
    return result


def anti_join(
    left: List[Row],
    right: List[Row],
    keys: List[str],
) -> List[Row]:
    """Return left rows that have NO matching key in right."""
    right_keys = set(
        tuple(r.get(k, "") for k in keys) for r in right
    )
    return [
        l for l in left
        if tuple(l.get(k, "") for k in keys) not in right_keys
    ]


def semi_join(
    left: List[Row],
    right: List[Row],
    keys: List[str],
) -> List[Row]:
    """Return left rows that have at least one matching key in right."""
    right_keys = set(
        tuple(r.get(k, "") for k in keys) for r in right
    )
    return [
        l for l in left
        if tuple(l.get(k, "") for k in keys) in right_keys
    ]
