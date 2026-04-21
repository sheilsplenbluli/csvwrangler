"""Tests for csvwrangler.lag."""

import pytest
from csvwrangler.lag import lag_column, lead_column, lag_many


def _rows():
    return [
        {"day": "1", "value": "10"},
        {"day": "2", "value": "20"},
        {"day": "3", "value": "30"},
        {"day": "4", "value": "40"},
    ]


def test_lag_default_dest_name():
    result = lag_column(_rows(), "value")
    assert "value_lag1" in result[0]


def test_lag_first_row_is_fill():
    result = lag_column(_rows(), "value")
    assert result[0]["value_lag1"] == ""


def test_lag_second_row_has_first_value():
    result = lag_column(_rows(), "value")
    assert result[1]["value_lag1"] == "10"


def test_lag_last_row():
    result = lag_column(_rows(), "value")
    assert result[3]["value_lag1"] == "30"


def test_lag_periods_2():
    result = lag_column(_rows(), "value", periods=2)
    assert result[0]["value_lag2"] == ""
    assert result[1]["value_lag2"] == ""
    assert result[2]["value_lag2"] == "10"


def test_lag_custom_fill():
    result = lag_column(_rows(), "value", fill="N/A")
    assert result[0]["value_lag1"] == "N/A"


def test_lag_custom_dest():
    result = lag_column(_rows(), "value", dest="prev_value")
    assert "prev_value" in result[0]
    assert "value_lag1" not in result[0]


def test_lag_does_not_mutate_original():
    rows = _rows()
    lag_column(rows, "value")
    assert "value_lag1" not in rows[0]


def test_lag_invalid_periods_raises():
    with pytest.raises(ValueError):
        lag_column(_rows(), "value", periods=0)


def test_lead_default_dest_name():
    result = lead_column(_rows(), "value")
    assert "value_lead1" in result[0]


def test_lead_first_row_has_second_value():
    result = lead_column(_rows(), "value")
    assert result[0]["value_lead1"] == "20"


def test_lead_last_row_is_fill():
    result = lead_column(_rows(), "value")
    assert result[3]["value_lead1"] == ""


def test_lead_periods_2():
    result = lead_column(_rows(), "value", periods=2)
    assert result[0]["value_lead2"] == "30"
    assert result[2]["value_lead2"] == ""
    assert result[3]["value_lead2"] == ""


def test_lead_invalid_periods_raises():
    with pytest.raises(ValueError):
        lead_column(_rows(), "value", periods=0)


def test_lag_many_applies_multiple_specs():
    specs = [
        {"column": "value", "direction": "lag", "periods": 1},
        {"column": "value", "direction": "lead", "periods": 1},
    ]
    result = lag_many(_rows(), specs)
    assert "value_lag1" in result[0]
    assert "value_lead1" in result[0]


def test_lag_many_empty_specs_returns_original():
    rows = _rows()
    result = lag_many(rows, [])
    assert result == rows
