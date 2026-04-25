"""Tests for csvwrangler/cli_dateparse.py."""
import csv
import io
import os
from unittest.mock import patch

import pytest

from csvwrangler.cli_dateparse import run


def _write_csv(tmp_path, name, rows):
    path = tmp_path / name
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


@pytest.fixture()
def sample_csv(tmp_path):
    rows = [
        {"id": "1", "date": "2023-06-15"},
        {"id": "2", "date": "2024-01-01"},
        {"id": "3", "date": "bad-date"},
    ]
    return _write_csv(tmp_path, "sample.csv", rows)


def test_extract_year_stdout(sample_csv, capsys):
    run([sample_csv, "extract", "--column", "date", "--parts", "year"])
    out = capsys.readouterr().out
    assert "date_year" in out
    assert "2023" in out
    assert "2024" in out


def test_extract_multiple_parts(sample_csv, capsys):
    run([sample_csv, "extract", "--column", "date", "--parts", "year,month,day"])
    out = capsys.readouterr().out
    assert "date_year" in out
    assert "date_month" in out
    assert "date_day" in out


def test_extract_invalid_part_exits(sample_csv):
    with pytest.raises(SystemExit):
        run([sample_csv, "extract", "--column", "date", "--parts", "century"])


def test_format_stdout(sample_csv, capsys):
    run([sample_csv, "format", "--column", "date", "--fmt", "%d/%m/%Y"])
    out = capsys.readouterr().out
    assert "15/06/2023" in out


def test_format_output_file(sample_csv, tmp_path):
    out_path = str(tmp_path / "out.csv")
    run([sample_csv, "format", "--column", "date", "--fmt", "%Y", "--output", out_path])
    assert os.path.exists(out_path)
    with open(out_path) as fh:
        content = fh.read()
    assert "2023" in content


def test_diff_stdout(tmp_path, capsys):
    rows = [
        {"a": "2023-06-20", "b": "2023-06-15"},
        {"a": "2023-01-01", "b": "2023-01-01"},
    ]
    path = _write_csv(tmp_path, "diff.csv", rows)
    run([path, "diff", "--col-a", "a", "--col-b", "b"])
    out = capsys.readouterr().out
    assert "a_minus_b" in out
    assert "5" in out
    assert "0" in out


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["nonexistent.csv", "extract", "--column", "date", "--parts", "year"])


def test_extract_prefix(sample_csv, capsys):
    run([sample_csv, "extract", "--column", "date", "--parts", "year", "--prefix", "dt_"])
    out = capsys.readouterr().out
    assert "dt_year" in out
