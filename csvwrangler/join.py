"""Simple CSV join operations (inner, left, right)."""
from typing import List, Dict, Optional

Row = Dict[str, str]


def _index_rows(rows: List[Row], key: str) -> Dict[str, List[Row]]:
    index: Dict[str, List[Row]] = {}
    for row in rows:
        val = row.get(key, "")
        index.setdefault(val, []).append(row)
    return index


def _merge(left: Row, right: Optional[Row], right_cols: List[str]) -> Row:
    merged = dict(left)
    for col in right_cols:
        merged[col] = right[col] if right else ""
    return merged


def join_rows(
    left: List[Row],
    right: List[Row],
    on: str,
    how: str = "inner",
    suffixes: tuple = ("_x", "_y"),
) -> List[Row]:
    if not left or not right:
        return []

    left_cols = list(left[0].keys())
    right_cols = [c for c in right[0].keys() if c != on]

    # handle column name collisions
    renamed_right: List[Row] = []
    col_map: Dict[str, str] = {}
    for col in right_cols:
        new_name = col + suffixes[1] if col in left_cols else col
        col_map[col] = new_name
    for row in right:
        renamed_right.append({col_map.get(k, k): v for k, v in row.items() if k != on} | {on: row[on]})

    final_right_cols = [col_map[c] for c in right_cols]
    right_index = _index_rows(renamed_right, on)
    left_index = _index_rows(left, on)

    result: List[Row] = []

    if how in ("inner", "left"):
        for row in left:
            key_val = row[on]
            matches = right_index.get(key_val)
            if matches:
                for r in matches:
                    result.append(_merge(row, r, final_right_cols))
            elif how == "left":
                result.append(_merge(row, None, final_right_cols))

    elif how == "right":
        for row in renamed_right:
            key_val = row[on]
            matches = left_index.get(key_val)
            if matches:
                for l in matches:
                    result.append(_merge(l, row, final_right_cols))
            else:
                empty_left = {c: "" for c in left_cols}
                empty_left[on] = key_val
                result.append(_merge(empty_left, row, final_right_cols))
    else:
        raise ValueError(f"Unknown join type: {how!r}. Use 'inner', 'left', or 'right'.")

    return result
