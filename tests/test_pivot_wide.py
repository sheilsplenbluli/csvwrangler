import pytest
from csvwrangler.pivot_wide import spread_rows, spread_summary, _collect_keys


def _long_rows():
    return [
        {"id": "A", "metric": "x", "value": "10"},
        {"id": "A", "metric": "y", "value": "20"},
        {"id": "B", "metric": "x", "value": "30"},
        {"id": "B", "metric": "y", "value": "40"},
        {"id": "C", "metric": "x", "value": "50"},
    ]


def test_spread_row_count():
    result = spread_rows(_long_rows(), "id", "metric", "value")
    assert len(result) == 3


def test_spread_column_names():
    result = spread_rows(_long_rows(), "id", "metric", "value")
    assert "x" in result[0]
    assert "y" in result[0]
    assert "id" in result[0]


def test_spread_values_correct():
    result = spread_rows(_long_rows(), "id", "metric", "value")
    row_a = next(r for r in result if r["id"] == "A")
    assert row_a["x"] == "10"
    assert row_a["y"] == "20"


def test_spread_missing_cell_uses_fill():
    result = spread_rows(_long_rows(), "id", "metric", "value", fill="0")
    row_c = next(r for r in result if r["id"] == "C")
    assert row_c["y"] == "0"


def test_spread_missing_cell_default_empty():
    result = spread_rows(_long_rows(), "id", "metric", "value")
    row_c = next(r for r in result if r["id"] == "C")
    assert row_c["y"] == ""


def test_spread_agg_first():
    rows = [
        {"id": "A", "metric": "x", "value": "1"},
        {"id": "A", "metric": "x", "value": "99"},
    ]
    result = spread_rows(rows, "id", "metric", "value", agg="first")
    assert result[0]["x"] == "1"


def test_spread_agg_last():
    rows = [
        {"id": "A", "metric": "x", "value": "1"},
        {"id": "A", "metric": "x", "value": "99"},
    ]
    result = spread_rows(rows, "id", "metric", "value", agg="last")
    assert result[0]["x"] == "99"


def test_spread_agg_sum():
    rows = [
        {"id": "A", "metric": "x", "value": "10"},
        {"id": "A", "metric": "x", "value": "5"},
    ]
    result = spread_rows(rows, "id", "metric", "value", agg="sum")
    assert float(result[0]["x"]) == pytest.approx(15.0)


def test_spread_preserves_index_order():
    result = spread_rows(_long_rows(), "id", "metric", "value")
    assert [r["id"] for r in result] == ["A", "B", "C"]


def test_spread_preserves_key_order():
    result = spread_rows(_long_rows(), "id", "metric", "value")
    cols = list(result[0].keys())
    assert cols.index("x") < cols.index("y")


def test_spread_empty_rows():
    result = spread_rows([], "id", "metric", "value")
    assert result == []


def test_collect_keys_order():
    rows = [
        {"k": "b"},
        {"k": "a"},
        {"k": "b"},
        {"k": "c"},
    ]
    assert _collect_keys(rows, "k") == ["b", "a", "c"]


def test_spread_summary_column_count():
    summary = spread_summary(_long_rows(), "metric")
    assert summary["column_count"] == 2
    assert set(summary["new_columns"]) == {"x", "y"}
