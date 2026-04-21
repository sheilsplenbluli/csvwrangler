"""Tests for csvwrangler.cli_lag."""

import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_lag import run


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


SAMPLE_ROWS = [
    {"day": "1", "value": "10"},
    {"day": "2", "value": "20"},
    {"day": "3", "value": "30"},
]


def test_lag_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS, ["day", "value"])
        fname = f.name
    try:
        run([fname, "value"])
        captured = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(captured))
        rows = list(reader)
        assert "value_lag1" in rows[0]
        assert rows[0]["value_lag1"] == ""
        assert rows[1]["value_lag1"] == "10"
    finally:
        os.unlink(fname)


def test_lead_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS, ["day", "value"])
        fname = f.name
    try:
        run([fname, "value", "--direction", "lead"])
        captured = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(captured))
        rows = list(reader)
        assert "value_lead1" in rows[0]
        assert rows[0]["value_lead1"] == "20"
        assert rows[2]["value_lead1"] == ""
    finally:
        os.unlink(fname)


def test_output_file(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS, ["day", "value"])
        infile = f.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as g:
        outfile = g.name
    try:
        run([infile, "value", "-o", outfile])
        with open(outfile, newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert "value_lag1" in rows[0]
    finally:
        os.unlink(infile)
        os.unlink(outfile)


def test_custom_dest(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS, ["day", "value"])
        fname = f.name
    try:
        run([fname, "value", "--dest", "prev"])
        captured = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(captured))
        rows = list(reader)
        assert "prev" in rows[0]
        assert "value_lag1" not in rows[0]
    finally:
        os.unlink(fname)


def test_invalid_periods_exits():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE_ROWS, ["day", "value"])
        fname = f.name
    try:
        with pytest.raises(SystemExit):
            run([fname, "value", "--periods", "0"])
    finally:
        os.unlink(fname)
