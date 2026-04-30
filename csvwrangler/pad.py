"""Pad string values in CSV columns to a fixed width."""

from typing import List, Dict, Optional


def _pad_value(
    value: str,
    width: int,
    align: str = "left",
    fillchar: str = " ",
) -> str:
    """Pad a single string value to the given width."""
    if len(value) >= width:
        return value
    if align == "right":
        return value.rjust(width, fillchar)
    if align == "center":
        return value.center(width, fillchar)
    return value.ljust(width, fillchar)


def pad_column(
    rows: List[Dict[str, str]],
    column: str,
    width: int,
    align: str = "left",
    fillchar: str = " ",
    dest: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Pad all values in *column* to *width* characters.

    Args:
        rows: Input rows.
        column: Column to pad.
        width: Target width in characters.
        align: 'left', 'right', or 'center'.
        fillchar: Character used for padding (default space).
        dest: Destination column name; defaults to *column* (in-place).

    Returns:
        New list of rows with padded values.
    """
    if width < 1:
        raise ValueError("width must be >= 1")
    if len(fillchar) != 1:
        raise ValueError("fillchar must be exactly one character")
    if align not in ("left", "right", "center"):
        raise ValueError("align must be 'left', 'right', or 'center'")

    dest = dest or column
    result = []
    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        new_row[dest] = _pad_value(raw, width, align, fillchar)
        result.append(new_row)
    return result


def pad_many(
    rows: List[Dict[str, str]],
    specs: List[Dict],
) -> List[Dict[str, str]]:
    """Apply multiple pad operations sequentially.

    Each spec is a dict with keys: column, width, and optionally
    align, fillchar, dest.
    """
    for spec in specs:
        rows = pad_column(
            rows,
            column=spec["column"],
            width=spec["width"],
            align=spec.get("align", "left"),
            fillchar=spec.get("fillchar", " "),
            dest=spec.get("dest"),
        )
    return rows
