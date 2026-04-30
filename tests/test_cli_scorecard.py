"""Integration tests for cli_scorecard."""
import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_scorecard import run


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


SAMPLE = [
    {"name": "Alice", "age": "30", "city": "London"},
    {"name": "Bob", "age": "17", "city": "Paris"},
    {"name": "Carol", "age": "45", "city": "London"},
]


def test_score_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE)
        fname = f.name
    try:
        run([fname, "-r", "age:gt:18:10"])
        out = capsys.readouterr().out
        assert "score" in out
        assert "10" in out
    finally:
        os.unlink(fname)


def test_score_zero_for_unmatched(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE)
        fname = f.name
    try:
        run([fname, "-r", "age:gt:18:10"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        bob = next(r for r in rows if r["name"] == "Bob")
        assert bob["score"] == "0"
    finally:
        os.unlink(fname)


def test_output_file(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE)
        fname = f.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as out_f:
        out_name = out_f.name
    try:
        run([fname, "-r", "city:eq:London:5", "-o", out_name])
        with open(out_name, newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert rows[0]["score"] == "5"
        assert rows[1]["score"] == "0"
    finally:
        os.unlink(fname)
        os.unlink(out_name)


def test_custom_dest(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE)
        fname = f.name
    try:
        run([fname, "--dest", "points"])
        out = capsys.readouterr().out
        assert "points" in out
        assert "score" not in out
    finally:
        os.unlink(fname)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["nonexistent_file.csv"])


def test_bad_rule_spec_exits():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(f.name, SAMPLE)
        fname = f.name
    try:
        with pytest.raises(SystemExit):
            run([fname, "-r", "bad_rule"])
    finally:
        os.unlink(fname)
