"""Tests for csvwrangler.sample."""

import pytest
from csvwrangler.sample import sample_rows, sample_fraction, head_rows, tail_rows

ROWS = [{"id": str(i), "val": str(i * 10)} for i in range(1, 11)]  # 10 rows


def test_sample_exact_count():
    result = sample_rows(ROWS, 3, seed=42)
    assert len(result) == 3


def test_sample_all_rows_when_n_exceeds_length():
    result = sample_rows(ROWS, 50, seed=0)
    assert len(result) == len(ROWS)


def test_sample_zero_rows():
    result = sample_rows(ROWS, 0, seed=0)
    assert result == []


def test_sample_negative_n_raises():
    with pytest.raises(ValueError):
        sample_rows(ROWS, -1)


def test_sample_reproducible_with_seed():
    a = sample_rows(ROWS, 5, seed=7)
    b = sample_rows(ROWS, 5, seed=7)
    assert a == b


def test_sample_different_seeds_differ():
    a = sample_rows(ROWS, 5, seed=1)
    b = sample_rows(ROWS, 5, seed=2)
    assert a != b


def test_sample_fraction_half():
    result = sample_fraction(ROWS, 0.5, seed=0)
    assert len(result) == 5


def test_sample_fraction_full():
    result = sample_fraction(ROWS, 1.0, seed=0)
    assert len(result) == len(ROWS)


def test_sample_fraction_zero():
    result = sample_fraction(ROWS, 0.0, seed=0)
    assert result == []


def test_sample_fraction_out_of_range_raises():
    with pytest.raises(ValueError):
        sample_fraction(ROWS, 1.5)


def test_head_rows():
    result = head_rows(ROWS, 3)
    assert result == ROWS[:3]


def test_head_rows_zero():
    assert head_rows(ROWS, 0) == []


def test_head_rows_negative_raises():
    with pytest.raises(ValueError):
        head_rows(ROWS, -1)


def test_tail_rows():
    result = tail_rows(ROWS, 4)
    assert result == ROWS[-4:]


def test_tail_rows_zero():
    assert tail_rows(ROWS, 0) == []


def test_tail_rows_exceeds_length():
    result = tail_rows(ROWS, 100)
    assert result == ROWS
