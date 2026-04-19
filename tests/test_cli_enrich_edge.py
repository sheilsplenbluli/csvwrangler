"""Edge-case tests for cli_enrich."""
import csv
import io
from pathlib import Path

import pytest

from csvwrangler.cli_enrich import run


def _write_csv(tmp_path: Path, rows: list[dict], name: str = "in.csv") -> str:
    p = tmp_path / name
    fields = list(rows[0].keys())
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return str(p)


def test_template_missing_field_empty_string(tmp_path, capsys):
    rows = [{"a": "hello"}]
    src = _write_csv(tmp_path, rows)
    run([src, "add-column", "x", "{a}_{missing}"])
    out = capsys.readouterr().out
    result = list(csv.DictReader(io.StringIO(out)))
    assert result[0]["x"] == "hello_"


def test_math_invalid_expr_empty(tmp_path, capsys):
    rows = [{"n": "5"}]
    src = _write_csv(tmp_path, rows)
    run([src, "add-column", "bad", "{n} *** 2", "--mode", "math"])
    out = capsys.readouterr().out
    result = list(csv.DictReader(io.StringIO(out)))
    assert result[0]["bad"] == ""


def test_rownum_preserves_original_fields(tmp_path, capsys):
    rows = [{"name": "X", "val": "1"}]
    src = _write_csv(tmp_path, rows)
    run([src, "add-rownum"])
    out = capsys.readouterr().out
    result = list(csv.DictReader(io.StringIO(out)))
    assert result[0]["name"] == "X"
    assert result[0]["val"] == "1"


def test_no_subcommand_exits(tmp_path):
    rows = [{"a": "1"}]
    src = _write_csv(tmp_path, rows)
    with pytest.raises(SystemExit):
        run([src])


def test_rownum_starts_at_one_and_increments(tmp_path, capsys):
    """Row numbers should start at 1 and increment for each row."""
    rows = [{"x": "a"}, {"x": "b"}, {"x": "c"}]
    src = _write_csv(tmp_path, rows)
    run([src, "add-rownum"])
    out = capsys.readouterr().out
    result = list(csv.DictReader(io.StringIO(out)))
    assert result[0]["rownum"] == "1"
    assert result[1]["rownum"] == "2"
    assert result[2]["rownum"] == "3"
