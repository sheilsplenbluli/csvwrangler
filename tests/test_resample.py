"""Tests for csvwrangler/resample.py"""

import pytest
from csvwrangler.resample import resample_rows, _parse_date, _bucket_key


def _rows():
    return [
        {"date": "2024-01-05", "sales": "100"},
        {"date": "2024-01-20", "sales": "200"},
        {"date": "2024-02-10", "sales": "50"},
        {"date": "2024-02-28", "sales": "75"},
        {"date": "2024-03-15", "sales": "300"},
    ]


def test_parse_date_iso():
    dt = _parse_date("2024-06-15")
    assert dt is not None
    assert dt.year == 2024 and dt.month == 6 and dt.day == 15


def test_parse_date_slash_format():
    dt = _parse_date("2024/06/15")
    assert dt is not None
    assert dt.year == 2024


def test_parse_date_invalid_returns_none():
    assert _parse_date("not-a-date") is None
    assert _parse_date("") is None


def test_bucket_key_monthly():
    from datetime import datetime
    dt = datetime(2024, 3, 15)
    assert _bucket_key(dt, "M") == "2024-03"


def test_bucket_key_yearly():
    from datetime import datetime
    dt = datetime(2024, 3, 15)
    assert _bucket_key(dt, "Y") == "2024"


def test_bucket_key_daily():
    from datetime import datetime
    dt = datetime(2024, 3, 15)
    assert _bucket_key(dt, "D") == "2024-03-15"


def test_bucket_key_invalid_freq_raises():
    from datetime import datetime
    with pytest.raises(ValueError, match="Unknown frequency"):
        _bucket_key(datetime(2024, 1, 1), "Q")


def test_resample_monthly_sum():
    result = resample_rows(_rows(), "date", "M", "sales", agg="sum")
    assert len(result) == 3
    jan = next(r for r in result if r["date"] == "2024-01")
    assert float(jan["sales_sum"]) == 300.0


def test_resample_monthly_mean():
    result = resample_rows(_rows(), "date", "M", "sales", agg="mean")
    feb = next(r for r in result if r["date"] == "2024-02")
    assert float(feb["sales_mean"]) == 62.5


def test_resample_monthly_count():
    result = resample_rows(_rows(), "date", "M", "sales", agg="count")
    jan = next(r for r in result if r["date"] == "2024-01")
    assert float(jan["sales_count"]) == 2.0


def test_resample_custom_dest():
    result = resample_rows(_rows(), "date", "M", "sales", agg="sum", dest="total")
    assert "total" in result[0]


def test_resample_skips_invalid_dates():
    rows = _rows() + [{"date": "bad", "sales": "999"}]
    result = resample_rows(rows, "date", "M", "sales", agg="sum")
    assert len(result) == 3


def test_resample_skips_non_numeric_values():
    rows = _rows() + [{"date": "2024-01-25", "sales": "n/a"}]
    result = resample_rows(rows, "date", "M", "sales", agg="sum")
    jan = next(r for r in result if r["date"] == "2024-01")
    assert float(jan["sales_sum"]) == 300.0


def test_resample_unknown_agg_raises():
    with pytest.raises(ValueError, match="Unknown aggregation"):
        resample_rows(_rows(), "date", "M", "sales", agg="median")


def test_resample_sorted_output():
    result = resample_rows(_rows(), "date", "M", "sales", agg="sum")
    dates = [r["date"] for r in result]
    assert dates == sorted(dates)
