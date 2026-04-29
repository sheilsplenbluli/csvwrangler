import pytest
from csvwrangler.pivot_crosstab import crosstab, crosstab_summary


def _rows():
    return [
        {"region": "North", "product": "A", "sales": "10"},
        {"region": "North", "product": "B", "sales": "20"},
        {"region": "South", "product": "A", "sales": "30"},
        {"region": "South", "product": "A", "sales": "5"},
        {"region": "South", "product": "B", "sales": "15"},
        {"region": "East",  "product": "C", "sales": "8"},
    ]


def test_count_basic():
    result = crosstab(_rows(), row_col="region", col_col="product")
    north = next(r for r in result if r["region"] == "North")
    assert north["A"] == "1"
    assert north["B"] == "1"


def test_count_multiple_matches():
    result = crosstab(_rows(), row_col="region", col_col="product")
    south = next(r for r in result if r["region"] == "South")
    assert south["A"] == "2"


def test_fill_value_used_for_missing_cell():
    result = crosstab(_rows(), row_col="region", col_col="product", fill="0")
    east = next(r for r in result if r["region"] == "East")
    assert east.get("A") == "0"
    assert east.get("B") == "0"
    assert east.get("C") == "1"


def test_custom_fill():
    result = crosstab(_rows(), row_col="region", col_col="product", fill="-")
    east = next(r for r in result if r["region"] == "East")
    assert east["A"] == "-"


def test_sum_aggregation():
    result = crosstab(_rows(), row_col="region", col_col="product",
                      value_col="sales", agg="sum")
    south = next(r for r in result if r["region"] == "South")
    assert float(south["A"]) == pytest.approx(35.0)


def test_mean_aggregation():
    result = crosstab(_rows(), row_col="region", col_col="product",
                      value_col="sales", agg="mean")
    south = next(r for r in result if r["region"] == "South")
    assert float(south["A"]) == pytest.approx(17.5)


def test_row_order_preserved():
    result = crosstab(_rows(), row_col="region", col_col="product")
    regions = [r["region"] for r in result]
    assert regions == ["North", "South", "East"]


def test_col_order_preserved():
    result = crosstab(_rows(), row_col="region", col_col="product")
    cols = [k for k in result[0] if k != "region"]
    assert cols == ["A", "B", "C"]


def test_bad_agg_raises():
    with pytest.raises(ValueError, match="Unknown aggregation"):
        crosstab(_rows(), row_col="region", col_col="product", agg="median")


def test_sum_without_value_col_raises():
    with pytest.raises(ValueError, match="requires value_col"):
        crosstab(_rows(), row_col="region", col_col="product", agg="sum")


def test_non_numeric_value_col_skipped():
    rows = [
        {"r": "X", "c": "A", "v": "abc"},
        {"r": "X", "c": "A", "v": "5"},
    ]
    result = crosstab(rows, row_col="r", col_col="c", value_col="v", agg="sum")
    assert float(result[0]["A"]) == pytest.approx(5.0)


def test_empty_rows_returns_empty():
    assert crosstab([], row_col="region", col_col="product") == []


def test_summary():
    s = crosstab_summary(_rows(), row_col="region", col_col="product")
    assert s["row_values"] == 3
    assert s["col_values"] == 3
