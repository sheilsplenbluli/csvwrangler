"""Cross-tabulation (contingency table) of two categorical columns."""
from collections import defaultdict
from typing import Dict, List, Optional


def crosstab(
    rows: List[Dict[str, str]],
    row_col: str,
    col_col: str,
    value_col: Optional[str] = None,
    agg: str = "count",
    fill: str = "0",
) -> List[Dict[str, str]]:
    """Build a cross-tabulation table.

    Args:
        rows: input rows.
        row_col: column whose distinct values become output rows.
        col_col: column whose distinct values become output columns.
        value_col: optional numeric column to aggregate; required for sum/mean.
        agg: aggregation – 'count', 'sum', or 'mean'.
        fill: value to use when a cell has no data.

    Returns:
        List of dicts with row_col plus one key per distinct col_col value.
    """
    if agg not in ("count", "sum", "mean"):
        raise ValueError(f"Unknown aggregation '{agg}'. Use count, sum, or mean.")
    if agg in ("sum", "mean") and not value_col:
        raise ValueError(f"agg='{agg}' requires value_col to be specified.")

    # accumulators: {row_val: {col_val: [values]}}
    acc: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    col_order: List[str] = []
    row_order: List[str] = []
    seen_cols = set()
    seen_rows = set()

    for r in rows:
        rv = r.get(row_col, "")
        cv = r.get(col_col, "")
        if rv not in seen_rows:
            row_order.append(rv)
            seen_rows.add(rv)
        if cv not in seen_cols:
            col_order.append(cv)
            seen_cols.add(cv)
        if value_col:
            raw = r.get(value_col, "")
            try:
                acc[rv][cv].append(float(raw))
            except (ValueError, TypeError):
                pass
        else:
            acc[rv][cv].append(1.0)

    result = []
    for rv in row_order:
        out: Dict[str, str] = {row_col: rv}
        for cv in col_order:
            vals = acc[rv].get(cv, [])
            if not vals:
                out[cv] = fill
            elif agg == "count":
                out[cv] = str(len(vals))
            elif agg == "sum":
                out[cv] = str(sum(vals))
            elif agg == "mean":
                out[cv] = str(sum(vals) / len(vals))
        result.append(out)
    return result


def crosstab_summary(rows: List[Dict[str, str]], row_col: str, col_col: str) -> Dict[str, int]:
    """Return counts of distinct row and column values."""
    return {
        "row_values": len({r.get(row_col, "") for r in rows}),
        "col_values": len({r.get(col_col, "") for r in rows}),
    }
