import pytest
from csvwrangler.fillna import fill_value, fill_forward, fill_backward, fill_many


ROWS = [
    {"name": "Alice", "dept": "Eng"},
    {"name": "", "dept": "HR"},
    {"name": "Bob", "dept": ""},
    {"name": "", "dept": ""},
]


def test_fill_value_replaces_empty():
    result = fill_value(ROWS, "name", "Unknown")
    assert result[1]["name"] == "Unknown"
    assert result[3]["name"] == "Unknown"


def test_fill_value_leaves_non_empty():
    result = fill_value(ROWS, "name", "Unknown")
    assert result[0]["name"] == "Alice"
    assert result[2]["name"] == "Bob"


def test_fill_value_does_not_mutate_original():
    original = [{"a": ""}]
    fill_value(original, "a", "x")
    assert original[0]["a"] == ""


def test_fill_forward_basic():
    rows = [{"v": "1"}, {"v": ""}, {"v": ""}, {"v": "2"}, {"v": ""}]
    result = fill_forward(rows, "v")
    assert result[1]["v"] == "1"
    assert result[2]["v"] == "1"
    assert result[4]["v"] == "2"


def test_fill_forward_no_prior_value_stays_empty():
    rows = [{"v": ""}, {"v": "x"}]
    result = fill_forward(rows, "v")
    assert result[0]["v"] == ""


def test_fill_backward_basic():
    rows = [{"v": ""}, {"v": ""}, {"v": "3"}]
    result = fill_backward(rows, "v")
    assert result[0]["v"] == "3"
    assert result[1]["v"] == "3"


def test_fill_backward_no_later_value_stays_empty():
    rows = [{"v": "x"}, {"v": ""}]
    result = fill_backward(rows, "v")
    assert result[1]["v"] == ""


def test_fill_many_value():
    rows = [{"a": "", "b": ""}]
    result = fill_many(rows, [{"column": "a", "method": "value", "value": "Z"}])
    assert result[0]["a"] == "Z"
    assert result[0]["b"] == ""


def test_fill_many_forward_and_value():
    rows = [{"a": "1"}, {"a": ""}, {"a": ""}]
    result = fill_many(rows, [{"column": "a", "method": "forward"}])
    assert all(r["a"] == "1" for r in result)


def test_fill_many_unknown_method_raises():
    with pytest.raises(ValueError, match="Unknown fill method"):
        fill_many([{"a": ""}], [{"column": "a", "method": "interpolate"}])
