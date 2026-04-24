import pytest
from csvwrangler.pivot_agg import pivot_agg, _aggregate


def _rows():
    return [
        {"region": "north", "product": "apple", "sales": "10"},
        {"region": "north", "product": "banana", "sales": "5"},
        {"region": "south", "product": "apple", "sales": "20"},
        {"region": "south", "product": "banana", "sales": "15"},
        {"region": "north", "product": "apple", "sales": "8"},
    ]


def test_pivot_agg_sum_row_count():
    result = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="sum")
    assert len(result) == 2


def test_pivot_agg_sum_values():
    result = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="sum")
    north = next(r for r in result if r["region"] == "north")
    assert north["apple"] == "18.0"
    assert north["banana"] == "5.0"


def test_pivot_agg_mean():
    result = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="mean")
    north = next(r for r in result if r["region"] == "north")
    assert float(north["apple"]) == pytest.approx(9.0)


def test_pivot_agg_count():
    result = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="count")
    north = next(r for r in result if r["region"] == "north")
    assert north["apple"] == "2"
    assert north["banana"] == "1"


def test_pivot_agg_min_max():
    result_min = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="min")
    result_max = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="max")
    north_min = next(r for r in result_min if r["region"] == "north")
    north_max = next(r for r in result_max if r["region"] == "north")
    assert float(north_min["apple"]) == 8.0
    assert float(north_max["apple"]) == 10.0


def test_pivot_agg_fill_value_for_missing_cell():
    rows = [
        {"region": "north", "product": "apple", "sales": "10"},
        {"region": "south", "product": "banana", "sales": "5"},
    ]
    result = pivot_agg(rows, index="region", columns="product", values="sales", fill_value="0")
    north = next(r for r in result if r["region"] == "north")
    assert north["banana"] == "0"


def test_pivot_agg_empty_rows():
    assert pivot_agg([], index="region", columns="product", values="sales") == []


def test_pivot_agg_first_last():
    result_first = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="first")
    result_last = pivot_agg(_rows(), index="region", columns="product", values="sales", aggfunc="last")
    north_first = next(r for r in result_first if r["region"] == "north")
    north_last = next(r for r in result_last if r["region"] == "north")
    assert north_first["apple"] == "10"
    assert north_last["apple"] == "8"


def test_aggregate_non_numeric_with_sum_returns_fill():
    assert _aggregate(["foo", "bar"], "sum", "") == ""


def test_aggregate_count_non_numeric():
    assert _aggregate(["foo", "bar"], "count", "") == "2"
