"""Tests for csvwrangler/pad.py"""

import pytest
from csvwrangler.pad import _pad_value, pad_column, pad_many


def _rows():
    return [
        {"name": "Alice", "code": "7"},
        {"name": "Bob", "code": "42"},
        {"name": "Charlotte", "code": "100"},
    ]


# --- _pad_value unit tests ---

def test_pad_value_left_default():
    assert _pad_value("hi", 6) == "hi    "


def test_pad_value_right():
    assert _pad_value("hi", 6, align="right") == "    hi"


def test_pad_value_center_even():
    assert _pad_value("hi", 6, align="center") == "  hi  "


def test_pad_value_center_odd():
    assert _pad_value("hi", 5, align="center") == "  hi "


def test_pad_value_custom_fillchar():
    assert _pad_value("7", 4, fillchar="0", align="right") == "0007"


def test_pad_value_already_wide_enough():
    assert _pad_value("hello", 3) == "hello"


def test_pad_value_exact_width():
    assert _pad_value("abc", 3) == "abc"


# --- pad_column tests ---

def test_pad_column_left_default():
    rows = pad_column(_rows(), "code", width=5)
    assert rows[0]["code"] == "7    "
    assert rows[1]["code"] == "42   "
    assert rows[2]["code"] == "100  "


def test_pad_column_right_zero_fill():
    rows = pad_column(_rows(), "code", width=4, align="right", fillchar="0")
    assert rows[0]["code"] == "0007"
    assert rows[1]["code"] == "0042"
    assert rows[2]["code"] == "0100"


def test_pad_column_dest_separate():
    rows = pad_column(_rows(), "code", width=5, dest="code_padded")
    assert "code_padded" in rows[0]
    assert rows[0]["code"] == "7"  # original unchanged
    assert rows[0]["code_padded"] == "7    "


def test_pad_column_does_not_mutate_original():
    original = _rows()
    copies = [dict(r) for r in original]
    pad_column(original, "code", width=10)
    assert original == copies


def test_pad_column_missing_column_uses_empty():
    rows = [{"a": "x"}]
    result = pad_column(rows, "missing", width=4)
    assert result[0]["missing"] == "    "


def test_pad_column_invalid_width_raises():
    with pytest.raises(ValueError, match="width"):
        pad_column(_rows(), "code", width=0)


def test_pad_column_invalid_fillchar_raises():
    with pytest.raises(ValueError, match="fillchar"):
        pad_column(_rows(), "code", width=5, fillchar="--")


def test_pad_column_invalid_align_raises():
    with pytest.raises(ValueError, match="align"):
        pad_column(_rows(), "code", width=5, align="middle")


# --- pad_many tests ---

def test_pad_many_applies_multiple_specs():
    specs = [
        {"column": "code", "width": 5, "align": "right", "fillchar": "0"},
        {"column": "name", "width": 10},
    ]
    rows = pad_many(_rows(), specs)
    assert rows[0]["code"] == "00007"
    assert rows[0]["name"] == "Alice     "


def test_pad_many_empty_specs_unchanged():
    original = _rows()
    result = pad_many(original, [])
    assert result[0]["name"] == "Alice"
