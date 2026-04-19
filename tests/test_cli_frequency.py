import csv
import os
import pytest
from unittest.mock import patch
from io import StringIO
from csvwrangler.cli_frequency import run


def _write_csv(tmp_path, name, rows):
    path = tmp_path / name
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


DATA = [
    {"city": "London", "country": "UK"},
    {"city": "Paris", "country": "FR"},
    {"city": "London", "country": "UK"},
    {"city": "Berlin", "country": "DE"},
]


def test_single_column_stdout(tmp_path, capsys):
    path = _write_csv(tmp_path, "data.csv", DATA)
    run([path, "--column", "city"])
    out = capsys.readouterr().out
    assert "London" in out
    assert "2" in out


def test_all_columns_stdout(tmp_path, capsys):
    path = _write_csv(tmp_path, "data.csv", DATA)
    run([path])
    out = capsys.readouterr().out
    assert "Column: city" in out
    assert "Column: country" in out


def test_top_n(tmp_path, capsys):
    path = _write_csv(tmp_path, "data.csv", DATA)
    run([path, "--column", "city", "--top", "1"])
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l and not l.startswith("-") and "value" not in l and "Column" not in l]
    assert len(lines) == 1


def test_bad_column_exits(tmp_path):
    path = _write_csv(tmp_path, "data.csv", DATA)
    with pytest.raises(SystemExit):
        run([path, "--column", "nonexistent"])


def test_sort_by_value(tmp_path, capsys):
    path = _write_csv(tmp_path, "data.csv", DATA)
    run([path, "--column", "city", "--sort", "value"])
    out = capsys.readouterr().out
    assert "Berlin" in out
