import pytest
from csvwrangler.transform import build_transforms, apply_transforms


ROWS = [
    {"name": "Alice", "age": "30", "city": "NYC"},
    {"name": "Bob",   "age": "25", "city": "LA"},
]


def test_rename():
    transforms = build_transforms([{"op": "rename", "mapping": {"name": "full_name"}}])
    result = apply_transforms(ROWS, transforms)
    assert "full_name" in result[0]
    assert "name" not in result[0]
    assert result[0]["full_name"] == "Alice"


def test_select():
    transforms = build_transforms([{"op": "select", "columns": ["name", "age"]}])
    result = apply_transforms(ROWS, transforms)
    assert list(result[0].keys()) == ["name", "age"]
    assert "city" not in result[0]


def test_drop():
    transforms = build_transforms([{"op": "drop", "columns": ["city"]}])
    result = apply_transforms(ROWS, transforms)
    assert "city" not in result[0]
    assert "name" in result[0]
    assert "age" in result[0]


def test_replace():
    transforms = build_transforms([{"op": "replace", "column": "city", "old": "NYC", "new": "New York"}])
    result = apply_transforms(ROWS, transforms)
    assert result[0]["city"] == "New York"
    assert result[1]["city"] == "LA"  # unchanged


def test_chained_transforms():
    specs = [
        {"op": "drop", "columns": ["city"]},
        {"op": "rename", "mapping": {"name": "full_name"}},
    ]
    transforms = build_transforms(specs)
    result = apply_transforms(ROWS, transforms)
    assert "city" not in result[0]
    assert "full_name" in result[0]
    assert result[0]["age"] == "30"


def test_unknown_op_raises():
    with pytest.raises(ValueError, match="Unknown transform op"):
        build_transforms([{"op": "explode", "column": "x"}])


def test_empty_rows():
    transforms = build_transforms([{"op": "select", "columns": ["name"]}])
    assert apply_transforms([], transforms) == []
