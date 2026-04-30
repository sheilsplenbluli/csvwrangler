"""Scorecard: assign a numeric score to each row based on weighted column rules."""
from typing import List, Dict, Any


def _try_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _eval_rule(row: Dict[str, str], col: str, op: str, threshold: str, points: float) -> float:
    """Return points if the rule matches, else 0."""
    raw = row.get(col, "")
    if op in ("gt", "gte", "lt", "lte"):
        val = _try_float(raw)
        thr = _try_float(threshold)
        if val is None or thr is None:
            return 0.0
        if op == "gt" and val > thr:
            return points
        if op == "gte" and val >= thr:
            return points
        if op == "lt" and val < thr:
            return points
        if op == "lte" and val <= thr:
            return points
    elif op == "eq":
        if raw.strip() == threshold.strip():
            return points
    elif op == "contains":
        if threshold.lower() in raw.lower():
            return points
    elif op == "notempty":
        if raw.strip():
            return points
    return 0.0


def score_rows(
    rows: List[Dict[str, str]],
    rules: List[Dict[str, Any]],
    dest: str = "score",
    default: float = 0.0,
) -> List[Dict[str, str]]:
    """Add a score column to each row based on rules.

    Each rule is a dict with keys: col, op, threshold, points.
    op may be: gt, gte, lt, lte, eq, contains, notempty.
    """
    result = []
    for row in rows:
        total = default
        for rule in rules:
            total += _eval_rule(
                row,
                rule.get("col", ""),
                rule.get("op", "eq"),
                str(rule.get("threshold", "")),
                float(rule.get("points", 0)),
            )
        out = dict(row)
        out[dest] = str(round(total, 10)).rstrip("0").rstrip(".")
        result.append(out)
    return result


def scorecard_summary(rows: List[Dict[str, str]], dest: str = "score") -> Dict[str, Any]:
    """Return basic stats about the score column."""
    vals = []
    for row in rows:
        v = _try_float(row.get(dest, ""))
        if v is not None:
            vals.append(v)
    if not vals:
        return {"count": 0, "min": None, "max": None, "mean": None}
    return {
        "count": len(vals),
        "min": min(vals),
        "max": max(vals),
        "mean": round(sum(vals) / len(vals), 6),
    }
