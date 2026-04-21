import pytest
from csvwrangler.compare import compare_columns, compare_many


def _rows():
    return [
        {"name": "alice", "a": "10", "b": "4"},
        {"name": "bob", "a": "3", "b": "3"},
        {"name": "carol", "a": "1", "b": "5"},
        {"name": "dave", "a": "hello", "b": "world"},
    ]


def test_diff_basic():
    result = compare_columns(_rows(), "a", "b", dest="delta", mode="diff")
    assert result[0]["delta"] == "6.0"
    assert result[1]["delta"] == "0.0"
    assert result[2]["delta"] == "-4.0"


def test_diff_non_numeric_empty():
    result = compare_columns(_rows(), "a", "b", dest="delta", mode="diff")
    assert result[3]["delta"] == ""


def test_ratio_basic():
    result = compare_columns(_rows(), "a", "b", dest="r", mode="ratio")
    assert float(result[0]["r"]) == pytest.approx(2.5)


def test_ratio_zero_divisor_empty():
    rows = [{"a": "5", "b": "0"}]
    result = compare_columns(rows, "a", "b", mode="ratio")
    assert result[0]["_cmp"] == ""


def test_eq_matching_strings():
    rows = [{"a": "Hello", "b": "hello"}, {"a": "yes", "b": "no"}]
    result = compare_columns(rows, "a", "b", mode="eq")
    assert result[0]["_cmp"] == "1"
    assert result[1]["_cmp"] == "0"


def test_gt_mode():
    result = compare_columns(_rows(), "a", "b", mode="gt")
    assert result[0]["_cmp"] == "1"   # 10 > 4
    assert result[1]["_cmp"] == "0"   # 3 == 3
    assert result[2]["_cmp"] == "0"   # 1 < 5


def test_lt_mode():
    result = compare_columns(_rows(), "a", "b", mode="lt")
    assert result[0]["_cmp"] == "0"
    assert result[2]["_cmp"] == "1"


def test_default_dest_column_name():
    result = compare_columns(_rows(), "a", "b", mode="diff")
    assert "_cmp" in result[0]


def test_does_not_mutate_original():
    rows = _rows()
    compare_columns(rows, "a", "b", mode="diff")
    assert "_cmp" not in rows[0]


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="Unknown mode"):
        compare_columns(_rows(), "a", "b", mode="badmode")


def test_compare_many_multiple_specs():
    specs = [
        {"col_a": "a", "col_b": "b", "dest": "diff", "mode": "diff"},
        {"col_a": "a", "col_b": "b", "dest": "eq", "mode": "eq"},
    ]
    result = compare_many(_rows(), specs)
    assert "diff" in result[0]
    assert "eq" in result[0]
    assert result[1]["eq"] == "1"  # bob: 3 == 3


def test_compare_many_empty_specs_returns_unchanged():
    rows = _rows()
    result = compare_many(rows, [])
    assert result == rows
