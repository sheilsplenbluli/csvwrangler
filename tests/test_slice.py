import pytest
from csvwrangler.slice import slice_rows, slice_between, every_nth

ROWS = [{"id": str(i), "val": str(i * 10)} for i in range(10)]


def test_slice_rows_basic():
    result = slice_rows(ROWS, 2, 5)
    assert [r["id"] for r in result] == ["2", "3", "4"]


def test_slice_rows_no_args_returns_all():
    assert slice_rows(ROWS) == ROWS


def test_slice_rows_with_step():
    result = slice_rows(ROWS, 0, 10, 2)
    assert [r["id"] for r in result] == ["0", "2", "4", "6", "8"]


def test_slice_rows_negative_start():
    result = slice_rows(ROWS, -3)
    assert [r["id"] for r in result] == ["7", "8", "9"]


def test_slice_between_basic():
    result = slice_between(ROWS, 1, 4)
    assert [r["id"] for r in result] == ["1", "2", "3"]


def test_slice_between_no_stop():
    result = slice_between(ROWS, 8)
    assert [r["id"] for r in result] == ["8", "9"]


def test_slice_between_empty_range():
    result = slice_between(ROWS, 5, 5)
    assert result == []


def test_every_nth_all():
    result = every_nth(ROWS, 1)
    assert result == ROWS


def test_every_nth_two():
    result = every_nth(ROWS, 2)
    assert [r["id"] for r in result] == ["0", "2", "4", "6", "8"]


def test_every_nth_three():
    result = every_nth(ROWS, 3)
    assert [r["id"] for r in result] == ["0", "3", "6", "9"]


def test_every_nth_invalid_raises():
    with pytest.raises(ValueError):
        every_nth(ROWS, 0)


def test_slice_empty_input():
    assert slice_rows([], 0, 5) == []
    assert slice_between([], 0, 5) == []
    assert every_nth([], 2) == []
