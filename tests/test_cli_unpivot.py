import csv
import io
import os
import tempfile
from unittest.mock import patch

import pytest

from csvwrangler.cli_unpivot import run


def _write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


SAMPLE_ROWS = [
    {"name": "Alice", "math": "90", "english": "85"},
    {"name": "Bob", "math": "78", "english": "88"},
]


def test_basic_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        _write_csv(SAMPLE_ROWS, path)
        run([path, "--id-cols", "name"])
        captured = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(captured)))
        assert len(reader) == 4
        variables = {r["variable"] for r in reader}
        assert variables == {"math", "english"}
    finally:
        os.unlink(path)


def test_custom_var_val_names(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        _write_csv(SAMPLE_ROWS, path)
        run([path, "--id-cols", "name", "--var-name", "subject", "--val-name", "score"])
        captured = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(captured)))
        assert "subject" in reader[0]
        assert "score" in reader[0]
    finally:
        os.unlink(path)


def test_explicit_value_cols(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = f.name
    try:
        _write_csv(SAMPLE_ROWS, path)
        run([path, "--id-cols", "name", "--value-cols", "math"])
        captured = capsys.readouterr().out
        reader = list(csv.DictReader(io.StringIO(captured)))
        assert len(reader) == 2
        assert all(r["variable"] == "math" for r in reader)
    finally:
        os.unlink(path)


def test_output_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fin:
        in_path = fin.name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fout:
        out_path = fout.name
    try:
        _write_csv(SAMPLE_ROWS, in_path)
        run([in_path, "--id-cols", "name", "-o", out_path])
        with open(out_path, newline="", encoding="utf-8") as fh:
            reader = list(csv.DictReader(fh))
        assert len(reader) == 4
    finally:
        os.unlink(in_path)
        os.unlink(out_path)
