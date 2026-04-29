import csv
import io
import os
import tempfile
from unittest.mock import patch

import pytest

from csvwrangler.cli_pivot_long import run


def _write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


WIDE_ROWS = [
    {"id": "1", "name": "Alice", "jan": "100", "feb": "200"},
    {"id": "2", "name": "Bob",   "jan": "80",  "feb": "90"},
]

LONG_ROWS = [
    {"id": "1", "month": "jan", "sales": "100"},
    {"id": "1", "month": "feb", "sales": "200"},
    {"id": "2", "month": "jan", "sales": "80"},
    {"id": "2", "month": "feb", "sales": "90"},
]


def test_wide_to_long_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(WIDE_ROWS, f.name)
        fname = f.name
    try:
        run(["wide-to-long", fname, "--id-cols", "id,name", "--value-cols", "jan,feb"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 4
        assert "variable" in reader[0]
        assert "value" in reader[0]
    finally:
        os.unlink(fname)


def test_wide_to_long_custom_names(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(WIDE_ROWS, f.name)
        fname = f.name
    try:
        run(["wide-to-long", fname, "--id-cols", "id",
             "--value-cols", "jan,feb", "--var-name", "month", "--val-name", "sales"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert "month" in reader[0]
        assert "sales" in reader[0]
    finally:
        os.unlink(fname)


def test_long_to_wide_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(LONG_ROWS, f.name)
        fname = f.name
    try:
        run(["long-to-wide", fname, "--id-cols", "id",
             "--var-col", "month", "--val-col", "sales"])
        out = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(out)))
        assert len(reader) == 2
        assert "jan" in reader[0]
        assert "feb" in reader[0]
    finally:
        os.unlink(fname)


def test_output_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(WIDE_ROWS, f.name)
        in_file = f.name
    out_file = in_file + "_out.csv"
    try:
        run(["wide-to-long", in_file, "--id-cols", "id,name",
             "--value-cols", "jan,feb", "--output", out_file])
        with open(out_file, newline="") as fh:
            reader = list(csv.DictReader(fh))
        assert len(reader) == 4
    finally:
        os.unlink(in_file)
        if os.path.exists(out_file):
            os.unlink(out_file)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["wide-to-long", "nonexistent.csv", "--id-cols", "id"])
