"""Rank rows by a numeric column."""
from __future__ import annotations
from typing import List, Dict, Any, Optional


def _try_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def rank_column(
    rows: List[Dict[str, Any]],
    column: str,
    dest: str = "rank",
    method: str = "average",
    ascending: bool = True,
) -> List[Dict[str, Any]]:
    """Add a rank column based on values in *column*.

    method: 'average' | 'min' | 'max' | 'dense' | 'rownum'
    """
    if not rows:
        return []

    indexed = [(i, _try_float(r.get(column, ""))) for i, r in enumerate(rows)]
    numeric = [(i, v) for i, v in indexed if v is not None]
    non_numeric = {i for i, v in indexed if v is None}

    numeric.sort(key=lambda x: x[1], reverse=not ascending)

    rank_map: Dict[int, str] = {}

    if method == "rownum":
        for rank, (i, _) in enumerate(numeric, 1):
            rank_map[i] = str(rank)
    elif method == "dense":
        current_rank = 1
        prev_val = None
        for i, v in numeric:
            if prev_val is not None and v != prev_val:
                current_rank += 1
            rank_map[i] = str(current_rank)
            prev_val = v
    else:
        pos = 0
        while pos < len(numeric):
            val = numeric[pos][1]
            group = [numeric[j][0] for j in range(pos, len(numeric)) if numeric[j][1] == val]
            if method == "min":
                r = pos + 1
            elif method == "max":
                r = pos + len(group)
            else:  # average
                r = (pos + 1 + pos + len(group)) / 2
            for idx in group:
                rank_map[idx] = str(int(r)) if r == int(r) else str(r)
            pos += len(group)

    result = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        new_row[dest] = rank_map.get(i, "")
        result.append(new_row)
    return result


def rank_many(
    rows: List[Dict[str, Any]],
    specs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply multiple rank operations sequentially.

    Each spec: {column, dest?, method?, ascending?}
    """
    for spec in specs:
        rows = rank_column(
            rows,
            column=spec["column"],
            dest=spec.get("dest", "rank"),
            method=spec.get("method", "average"),
            ascending=spec.get("ascending", True),
        )
    return rows
