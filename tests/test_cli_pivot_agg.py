import csv
import io
import os
import sys
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_pivot_agg import run


def _write_csv(path, rows, fieldnames=None):
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


_SAMPLE = [
    {"region": "north", "product": "apple", "sales": "10"},
    {"region": "north", "product": "banana", "sales": "5"},
    {"region": "south", "product": "apple", "sales": "20"},
    {"region": "south", "product": "banana", "sales": "15"},
]


def test_sum_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, _SAMPLE)
        fname = f.name
    try:
        run([fname, "--index", "region", "--columns", "product", "--values", "sales"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        assert len(rows) == 2
        north = next(r for r in rows if r["region"] == "north")
        assert float(north["apple"]) == 10.0
    finally:
        os.unlink(fname)


def test_count_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, _SAMPLE)
        fname = f.name
    try:
        run([fname, "--index", "region", "--columns", "product", "--values", "sales", "--aggfunc", "count"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        north = next(r for r in rows if r["region"] == "north")
        assert north["apple"] == "1"
    finally:
        os.unlink(fname)


def test_output_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, _SAMPLE)
        fname = f.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as out_f:
        out_name = out_f.name
    try:
        run([fname, "--index", "region", "--columns", "product", "--values", "sales", "-o", out_name])
        with open(out_name, newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 2
    finally:
        os.unlink(fname)
        os.unlink(out_name)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["nonexistent.csv", "--index", "region", "--columns", "product", "--values", "sales"])
