"""CLI tests for csvwrangler/cli_resample.py"""

import csv
import io
import os
import tempfile
from unittest.mock import patch

import pytest

from csvwrangler.cli_resample import run


def _write_csv(path: str, rows, fieldnames=None) -> None:
    if not rows:
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


SAMPLE_ROWS = [
    {"date": "2024-01-05", "sales": "100"},
    {"date": "2024-01-20", "sales": "200"},
    {"date": "2024-02-10", "sales": "50"},
    {"date": "2024-03-01", "sales": "400"},
]


def test_monthly_sum_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS)
        fname = f.name
    try:
        run([fname, "--date-col", "date", "--freq", "M", "--agg-col", "sales"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        assert len(rows) == 3
        jan = next(r for r in rows if r["date"] == "2024-01")
        assert float(jan["sales_sum"]) == 300.0
    finally:
        os.unlink(fname)


def test_monthly_count_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS)
        fname = f.name
    try:
        run([fname, "--date-col", "date", "--freq", "M", "--agg-col", "sales", "--agg", "count"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        jan = next(r for r in rows if r["date"] == "2024-01")
        assert float(jan["sales_count"]) == 2.0
    finally:
        os.unlink(fname)


def test_output_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fin:
        _write_csv(fin.name, SAMPLE_ROWS)
        in_name = fin.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as fout:
        out_name = fout.name
    try:
        run([in_name, "--date-col", "date", "--freq", "M", "--agg-col", "sales", "-o", out_name])
        with open(out_name, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 3
    finally:
        os.unlink(in_name)
        os.unlink(out_name)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["nonexistent.csv", "--date-col", "date", "--freq", "M", "--agg-col", "sales"])


def test_custom_dest_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS)
        fname = f.name
    try:
        run([fname, "--date-col", "date", "--freq", "M", "--agg-col", "sales", "--dest", "revenue"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        assert "revenue" in rows[0]
    finally:
        os.unlink(fname)
