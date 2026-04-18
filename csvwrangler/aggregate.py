"""Group-by aggregation for CSV rows."""
from collections import defaultdict
from typing import Any


def _numeric(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _group_rows(rows: list[dict], group_by: list[str]) -> dict:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = tuple(row.get(col, "") for col in group_by)
        groups[key].append(row)
    return groups


def aggregate_rows(
    rows: list[dict],
    group_by: list[str],
    aggregations: dict[str, str],
) -> list[dict]:
    """Aggregate rows grouped by columns.

    aggregations maps output_col -> "func:source_col"
    supported funcs: sum, mean, min, max, count, first, last
    """
    groups = _group_rows(rows, group_by)
    result = []
    for key, group in groups.items():
        out = dict(zip(group_by, key))
        for out_col, spec in aggregations.items():
            func, src = spec.split(":", 1)
            values = [row.get(src, "") for row in group]
            nums = [_numeric(v) for v in values if _numeric(v) is not None]
            if func == "sum":
                out[out_col] = str(sum(nums)) if nums else ""
            elif func == "mean":
                out[out_col] = str(sum(nums) / len(nums)) if nums else ""
            elif func == "min":
                out[out_col] = str(min(nums)) if nums else ""
            elif func == "max":
                out[out_col] = str(max(nums)) if nums else ""
            elif func == "count":
                out[out_col] = str(len(group))
            elif func == "first":
                out[out_col] = values[0] if values else ""
            elif func == "last":
                out[out_col] = values[-1] if values else ""
            else:
                raise ValueError(f"Unknown aggregation function: {func}")
        result.append(out)
    return result
