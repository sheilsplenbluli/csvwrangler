"""Integration tests for cli_zscore.run."""
import csv
import io
import os
import tempfile

import pytest

from csvwrangler.cli_zscore import run


def _write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


SAMPLE = [
    {"name": "alice", "score": "10"},
    {"name": "bob", "score": "20"},
    {"name": "carol", "score": "30"},
]


def test_zscore_stdout(capsys):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        fname = f.name
    try:
        _write_csv(fname, SAMPLE)
        run([fname, "--col", "score"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        assert "score_zscore" in rows[0]
        assert float(rows[1]["score_zscore"]) == pytest.approx(0.0, abs=1e-4)
    finally:
        os.unlink(fname)


def test_zscore_custom_dest(capsys):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        fname = f.name
    try:
        _write_csv(fname, SAMPLE)
        run([fname, "--col", "score", "--dest", "z"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        assert "z" in rows[0]
        assert "score_zscore" not in rows[0]
    finally:
        os.unlink(fname)


def test_zscore_output_file():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        infile = f.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        outfile = f.name
    try:
        _write_csv(infile, SAMPLE)
        run([infile, "--col", "score", "-o", outfile])
        with open(outfile, newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert "score_zscore" in rows[0]
    finally:
        os.unlink(infile)
        os.unlink(outfile)


def test_bad_column_exits():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        fname = f.name
    try:
        _write_csv(fname, SAMPLE)
        with pytest.raises(SystemExit):
            run([fname, "--col", "nonexistent"])
    finally:
        os.unlink(fname)


def test_dest_with_multiple_cols_exits():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        fname = f.name
    try:
        _write_csv(fname, SAMPLE)
        with pytest.raises(SystemExit):
            run([fname, "--col", "score", "--col", "score", "--dest", "z"])
    finally:
        os.unlink(fname)
