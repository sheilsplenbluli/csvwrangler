"""Bin numeric values into labeled buckets."""
from __future__ import annotations
from typing import Any


def _try_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def bin_column(
    rows: list[dict[str, Any]],
    column: str,
    edges: list[float],
    labels: list[str] | None = None,
    dest: str | None = None,
    default: str = "",
) -> list[dict[str, Any]]:
    """Assign each row a bin label based on edges (left-exclusive, right-inclusive).

    edges: sorted list of boundary values, e.g. [0, 10, 20] creates bins
           (-inf, 0], (0, 10], (10, 20], (20, inf).
    labels: one label per bin (len(edges)+1). Defaults to range strings.
    """
    n_bins = len(edges) + 1
    if labels is None:
        labels = _default_labels(edges)
    if len(labels) != n_bins:
        raise ValueError(f"Expected {n_bins} labels for {len(edges)} edges, got {len(labels)}")

    out_col = dest or f"{column}_bin"
    result = []
    for row in rows:
        v = _try_float(row.get(column, ""))
        new_row = dict(row)
        if v is None:
            new_row[out_col] = default
        else:
            new_row[out_col] = _assign(v, edges, labels)
        result.append(new_row)
    return result


def _default_labels(edges: list[float]) -> list[str]:
    parts = []
    for i, edge in enumerate(edges):
        if i == 0:
            parts.append(f"<={edge}")
        else:
            parts.append(f"{edges[i-1]}-{edge}")
    if edges:
        parts.append(f">{edges[-1]}")
    return parts


def _assign(value: float, edges: list[float], labels: list[str]) -> str:
    for i, edge in enumerate(edges):
        if value <= edge:
            return labels[i]
    return labels[-1]


def bin_many(
    rows: list[dict[str, Any]],
    specs: list[dict],
) -> list[dict[str, Any]]:
    """Apply multiple bin specs sequentially. Each spec: {column, edges, labels?, dest?, default?}"""
    for spec in specs:
        rows = bin_column(
            rows,
            column=spec["column"],
            edges=spec["edges"],
            labels=spec.get("labels"),
            dest=spec.get("dest"),
            default=spec.get("default", ""),
        )
    return rows
