"""Column transformation utilities for csvwrangler."""

from typing import List, Dict, Callable


def _make_renamer(mapping: Dict[str, str]) -> Callable:
    def rename(row: Dict) -> Dict:
        return {mapping.get(k, k): v for k, v in row.items()}
    return rename


def _make_column_selector(columns: List[str]) -> Callable:
    def select(row: Dict) -> Dict:
        return {k: v for k, v in row.items() if k in columns}
    return select


def _make_column_dropper(columns: List[str]) -> Callable:
    def drop(row: Dict) -> Dict:
        return {k: v for k, v in row.items() if k not in columns}
    return drop


def _make_value_replacer(column: str, old: str, new: str) -> Callable:
    def replace(row: Dict) -> Dict:
        row = dict(row)
        if column in row and row[column] == old:
            row[column] = new
        return row
    return replace


def build_transforms(specs: List[Dict]) -> List[Callable]:
    """Build a list of transform functions from spec dicts.

    Supported specs:
      {"op": "rename", "mapping": {"old": "new", ...}}
      {"op": "select", "columns": [...]}
      {"op": "drop",   "columns": [...]}
      {"op": "replace", "column": "col", "old": "x", "new": "y"}
    """
    transforms = []
    for spec in specs:
        op = spec.get("op")
        if op == "rename":
            transforms.append(_make_renamer(spec["mapping"]))
        elif op == "select":
            transforms.append(_make_column_selector(spec["columns"]))
        elif op == "drop":
            transforms.append(_make_column_dropper(spec["columns"]))
        elif op == "replace":
            transforms.append(_make_value_replacer(spec["column"], spec["old"], spec["new"]))
        else:
            raise ValueError(f"Unknown transform op: {op!r}")
    return transforms


def apply_transforms(rows: List[Dict], transforms: List[Callable]) -> List[Dict]:
    """Apply a list of transforms to each row."""
    result = []
    for row in rows:
        for t in transforms:
            row = t(row)
        result.append(row)
    return result
