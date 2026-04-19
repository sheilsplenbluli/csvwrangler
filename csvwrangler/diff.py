"""Row-level diff between two CSV datasets."""
from typing import List, Dict, Tuple

Row = Dict[str, str]


def _row_key(row: Row, key_cols: List[str]) -> Tuple[str, ...]:
    return tuple(row.get(c, "") for c in key_cols)


def diff_rows(
    left: List[Row],
    right: List[Row],
    key_cols: List[str],
) -> List[Row]:
    """Return rows showing what changed between left and right.

    Each output row has a '_diff' field: 'added', 'removed', or 'modified'.
    Unchanged rows are omitted.
    """
    left_index = {_row_key(r, key_cols): r for r in left}
    right_index = {_row_key(r, key_cols): r for r in right}

    results: List[Row] = []

    for key, lrow in left_index.items():
        if key not in right_index:
            results.append({**lrow, "_diff": "removed"})
        else:
            rrow = right_index[key]
            if lrow != rrow:
                results.append({**rrow, "_diff": "modified"})

    for key, rrow in right_index.items():
        if key not in left_index:
            results.append({**rrow, "_diff": "added"})

    return results


def diff_summary(diff: List[Row]) -> Dict[str, int]:
    """Count added/removed/modified rows in a diff result."""
    counts: Dict[str, int] = {"added": 0, "removed": 0, "modified": 0}
    for row in diff:
        tag = row.get("_diff", "")
        if tag in counts:
            counts[tag] += 1
    return counts
