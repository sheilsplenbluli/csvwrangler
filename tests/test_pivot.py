import pytest
from csvwrangler.pivot import pivot_rows, melt_rows

SALES = [
    {"region": "East", "product": "A", "sales": "10"},
    {"region": "East", "product": "B", "sales": "20"},
    {"region": "West", "product": "A", "sales": "30"},
    {"region": "West", "product": "B", "sales": "40"},
]


def test_pivot_first():
    result = pivot_rows(SALES, index="region", columns="product", values="sales")
    east = next(r for r in result if r["region"] == "East")
    assert east["A"] == "10"
    assert east["B"] == "20"


def test_pivot_sum():
    rows = [
        {"region": "East", "product": "A", "sales": "10"},
        {"region": "East", "product": "A", "sales": "5"},
    ]
    result = pivot_rows(rows, index="region", columns="product", values="sales", aggfunc="sum")
    assert result[0]["A"] == 15.0


def test_pivot_count():
    rows = SALES + [{"region": "East", "product": "A", "sales": "99"}]
    result = pivot_rows(rows, index="region", columns="product", values="sales", aggfunc="count")
    east = next(r for r in result if r["region"] == "East")
    assert east["A"] == 2


def test_pivot_last():
    rows = [
        {"region": "East", "product": "A", "sales": "10"},
        {"region": "East", "product": "A", "sales": "99"},
    ]
    result = pivot_rows(rows, index="region", columns="product", values="sales", aggfunc="last")
    assert result[0]["A"] == "99"


def test_pivot_missing_cell():
    rows = [
        {"region": "East", "product": "A", "sales": "10"},
        {"region": "West", "product": "B", "sales": "20"},
    ]
    result = pivot_rows(rows, index="region", columns="product", values="sales")
    east = next(r for r in result if r["region"] == "East")
    assert east.get("B", "") == ""


def test_pivot_invalid_aggfunc():
    with pytest.raises(ValueError):
        pivot_rows(SALES, index="region", columns="product", values="sales", aggfunc="mean")


def test_melt_basic():
    rows = [{"id": "1", "A": "10", "B": "20"}]
    result = melt_rows(rows, id_vars=["id"], value_vars=["A", "B"])
    assert len(result) == 2
    assert result[0] == {"id": "1", "variable": "A", "value": "10"}
    assert result[1] == {"id": "1", "variable": "B", "value": "20"}


def test_melt_infer_value_vars():
    rows = [{"id": "1", "x": "a", "y": "b"}]
    result = melt_rows(rows, id_vars=["id"])
    vars_found = {r["variable"] for r in result}
    assert vars_found == {"x", "y"}


def test_melt_custom_names():
    rows = [{"id": "1", "col": "v"}]
    result = melt_rows(rows, id_vars=["id"], var_name="metric", value_name="amount")
    assert result[0]["metric"] == "col"
    assert result[0]["amount"] == "v"


def test_melt_empty():
    assert melt_rows([], id_vars=["id"]) == []
