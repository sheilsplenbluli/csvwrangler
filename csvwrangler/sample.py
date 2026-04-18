"""Sampling utilities for CSV rows."""

from __future__ import annotations

import random
from typing import List, Dict, Optional

Row = Dict[str, str]


def sample_rows(
    rows: List[Row],
    n: int,
    seed: Optional[int] = None,
) -> List[Row]:
    """Return up to *n* randomly sampled rows (without replacement)."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    rng = random.Random(seed)
    if n >= len(rows):
        result = list(rows)
        rng.shuffle(result)
        return result
    return rng.sample(rows, n)


def sample_fraction(
    rows: List[Row],
    fraction: float,
    seed: Optional[int] = None,
) -> List[Row]:
    """Return a random fraction of rows (0.0 – 1.0)."""
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction must be between 0.0 and 1.0, got {fraction}")
    n = round(len(rows) * fraction)
    return sample_rows(rows, n, seed=seed)


def head_rows(rows: List[Row], n: int) -> List[Row]:
    """Return the first *n* rows."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return rows[:n]


def tail_rows(rows: List[Row], n: int) -> List[Row]:
    """Return the last *n* rows."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return rows[-n:] if n else []
