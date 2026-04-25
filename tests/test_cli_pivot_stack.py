import csv
import io
import os
import sys
import tempfile
import pytest

from csvwrangler.cli_pivot_stack import run


def _write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


_WIDE_ROWS = [
    {"region": "North", "year": "2022", "sales": "100", "cost": "80"},
    {"region": "South", "year": "2022", "sales": "200", "cost": "150"},
]

_LONG_ROWS = [
    {"region": "North", "year": "2022", "variable": "sales", "value": "100"},
    {"region": "North", "year": "2022", "variable": "cost", "value": "80"},
    {"region": "South", "year": "2022", "variable": "sales", "value": "200"},
    {"region": "South", "year": "2022", "variable": "cost", "value": "150"},
]


def test_stack_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(_WIDE_ROWS, f.name)
        fname = f.name
    try:
        run(["stack", fname, "--id-cols", "region,year", "--value-cols", "sales,cost"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 4
        assert reader[0]["variable"] == "sales"
        assert reader[0]["value"] == "100"
    finally:
        os.unlink(fname)


def test_unstack_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(_LONG_ROWS, f.name)
        fname = f.name
    try:
        run(["unstack", fname, "--id-cols", "region,year"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 2
        assert "sales" in reader[0]
        assert "cost" in reader[0]
    finally:
        os.unlink(fname)


def test_stack_output_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(_WIDE_ROWS, f.name)
        in_fname = f.name
    out_fname = in_fname + "_out.csv"
    try:
        run(["stack", in_fname, "--id-cols", "region,year", "--value-cols", "sales,cost", "-o", out_fname])
        with open(out_fname, newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 4
    finally:
        os.unlink(in_fname)
        if os.path.exists(out_fname):
            os.unlink(out_fname)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["stack", "no_such_file.csv", "--id-cols", "region", "--value-cols", "sales"])


def test_stack_custom_col_names(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(_WIDE_ROWS, f.name)
        fname = f.name
    try:
        run(["stack", fname, "--id-cols", "region", "--value-cols", "sales",
             "--var-col", "metric", "--val-col", "amount"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert "metric" in reader[0]
        assert "amount" in reader[0]
    finally:
        os.unlink(fname)
