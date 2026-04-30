"""Fuzzy string matching and nearest-neighbor lookup using Levenshtein distance."""

from __future__ import annotations
from typing import List, Dict, Optional


def _levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein edit distance between two strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[len(b)]


def distance_column(
    rows: List[Dict[str, str]],
    col_a: str,
    col_b: str,
    dest: Optional[str] = None,
    ignore_case: bool = False,
) -> List[Dict[str, str]]:
    """Add a column with the Levenshtein distance between two columns."""
    out_col = dest or f"{col_a}_dist_{col_b}"
    result = []
    for row in rows:
        a = row.get(col_a, "")
        b = row.get(col_b, "")
        if ignore_case:
            a, b = a.lower(), b.lower()
        dist = _levenshtein(a, b)
        result.append({**row, out_col: str(dist)})
    return result


def nearest_match(
    rows: List[Dict[str, str]],
    col: str,
    candidates: List[str],
    dest: Optional[str] = None,
    ignore_case: bool = False,
) -> List[Dict[str, str]]:
    """For each row, find the closest string in *candidates* and add it."""
    out_col = dest or f"{col}_nearest"
    result = []
    for row in rows:
        val = row.get(col, "")
        cmp_val = val.lower() if ignore_case else val
        best: Optional[str] = None
        best_dist = float("inf")
        for cand in candidates:
            cmp_cand = cand.lower() if ignore_case else cand
            d = _levenshtein(cmp_val, cmp_cand)
            if d < best_dist:
                best_dist = d
                best = cand
        result.append({**row, out_col: best or ""})
    return result


def similarity_score(
    rows: List[Dict[str, str]],
    col_a: str,
    col_b: str,
    dest: Optional[str] = None,
    ignore_case: bool = False,
) -> List[Dict[str, str]]:
    """Add a 0-1 similarity score (1 = identical) between two string columns."""
    out_col = dest or f"{col_a}_sim_{col_b}"
    result = []
    for row in rows:
        a = row.get(col_a, "")
        b = row.get(col_b, "")
        if ignore_case:
            a, b = a.lower(), b.lower()
        dist = _levenshtein(a, b)
        max_len = max(len(a), len(b), 1)
        score = round(1.0 - dist / max_len, 4)
        result.append({**row, out_col: str(score)})
    return result
