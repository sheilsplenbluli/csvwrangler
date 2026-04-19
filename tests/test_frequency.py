import pytest
from csvwrangler.frequency import frequency_table, frequency_all

ROWS = [
    {"city": "London", "country": "UK"},
    {"city": "Paris", "country": "FR"},
    {"city": "London", "country": "UK"},
    {"city": "Berlin", "country": "DE"},
    {"city": "London", "country": "UK"},
    {"city": "Paris", "country": "FR"},
]


def test_basic_counts():
    result = frequency_table(ROWS, "city")
    by_val = {r["value"]: r["count"] for r in result}
    assert by_val["London"] == 3
    assert by_val["Paris"] == 2
    assert by_val["Berlin"] == 1


def test_percent_sums_to_100():
    result = frequency_table(ROWS, "city")
    total = sum(r["percent"] for r in result)
    assert abs(total - 100.0) < 0.01


def test_sort_by_count_default():
    result = frequency_table(ROWS, "city")
    counts = [r["count"] for r in result]
    assert counts == sorted(counts, reverse=True)


def test_sort_by_value():
    result = frequency_table(ROWS, "city", sort_by="value")
    values = [r["value"] for r in result]
    assert values == sorted(values)


def test_top_n():
    result = frequency_table(ROWS, "city", top_n=2)
    assert len(result) == 2
    assert result[0]["value"] == "London"


def test_empty_rows():
    assert frequency_table([], "city") == []


def test_frequency_all_keys():
    result = frequency_all(ROWS)
    assert set(result.keys()) == {"city", "country"}


def test_frequency_all_empty():
    assert frequency_all([]) == {}


def test_frequency_all_top_n():
    result = frequency_all(ROWS, top_n=1)
    assert len(result["city"]) == 1
    assert len(result["country"]) == 1
