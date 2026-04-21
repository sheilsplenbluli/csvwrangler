"""Compute percentile ranks and quantile buckets for numeric columns."""

from __future__ import annotations

from typing import Any


def _numeric_values(rows: list[dict], col: str) -> list[float]:
    vals = []
    for r in rows:
        try:
            vals.append(float(r[col]))
        except (ValueError, TypeError, KeyError):
            pass
    return vals


def percentile_rank(
    rows: list[dict],
    col: str,
    dest: str | None = None,
    decimals: int = 2,
) -> list[dict]:
    """Add a column with each row's percentile rank (0-100) within *col*."""
    dest = dest or f"{col}_pct_rank"
    numeric = _numeric_values(rows, col)
    n = len(numeric)
    result = []
    for row in rows:
        out = dict(row)
        try:
            v = float(row[col])
            rank = sum(1 for x in numeric if x <= v) / n * 100
            out[dest] = str(round(rank, decimals))
        except (ValueError, TypeError, KeyError):
            out[dest] = ""
        result.append(out)
    return result


def quantile_bucket(
    rows: list[dict],
    col: str,
    q: int = 4,
    dest: str | None = None,
) -> list[dict]:
    """Add a column with quantile bucket (1..q) for each row in *col*."""
    if q < 1:
        raise ValueError("q must be >= 1")
    dest = dest or f"{col}_q{q}"
    numeric = sorted(_numeric_values(rows, col))
    n = len(numeric)
    result = []
    for row in rows:
        out = dict(row)
        try:
            v = float(row[col])
            if n == 0:
                out[dest] = ""
            else:
                rank = sum(1 for x in numeric if x <= v) / n
                bucket = min(q, max(1, int(rank * q) + (1 if rank < 1 else 0)))
                out[dest] = str(bucket)
        except (ValueError, TypeError, KeyError):
            out[dest] = ""
        result.append(out)
    return result


def percentile_many(
    rows: list[dict],
    specs: list[dict[str, Any]],
) -> list[dict]:
    """Apply multiple percentile/quantile operations in sequence.

    Each spec is a dict with keys:
      mode   : 'rank' | 'quantile'
      col    : source column name
      dest   : (optional) destination column name
      decimals: (optional, rank only) int
      q      : (optional, quantile only) int
    """
    for spec in specs:
        mode = spec.get("mode", "rank")
        if mode == "rank":
            rows = percentile_rank(
                rows,
                col=spec["col"],
                dest=spec.get("dest"),
                decimals=spec.get("decimals", 2),
            )
        elif mode == "quantile":
            rows = quantile_bucket(
                rows,
                col=spec["col"],
                q=spec.get("q", 4),
                dest=spec.get("dest"),
            )
        else:
            raise ValueError(f"Unknown mode: {mode!r}")
    return rows
