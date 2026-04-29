"""Convert column values to URL/filename-friendly slugs."""

import re
from typing import List, Dict, Any, Optional


def _slugify_value(
    value: str,
    separator: str = "-",
    lowercase: bool = True,
    max_length: Optional[int] = None,
) -> str:
    """Convert a single string value to a slug."""
    if not value or not value.strip():
        return value

    result = value.strip()

    if lowercase:
        result = result.lower()

    # Replace accented characters with ascii equivalents (basic)
    replacements = {
        "á": "a", "à": "a", "ä": "a", "â": "a", "ã": "a",
        "é": "e", "è": "e", "ë": "e", "ê": "e",
        "í": "i", "ì": "i", "ï": "i", "î": "i",
        "ó": "o", "ò": "o", "ö": "o", "ô": "o", "õ": "o",
        "ú": "u", "ù": "u", "ü": "u", "û": "u",
        "ñ": "n", "ç": "c",
    }
    for src, dst in replacements.items():
        result = result.replace(src, dst)
        result = result.replace(src.upper(), dst.upper() if not lowercase else dst)

    # Replace non-alphanumeric characters with separator
    result = re.sub(r"[^\w\s-]", "", result)
    result = re.sub(r"[\s_-]+", separator, result)
    result = result.strip(separator)

    if max_length and len(result) > max_length:
        result = result[:max_length].rstrip(separator)

    return result


def slugify_column(
    rows: List[Dict[str, Any]],
    column: str,
    dest: Optional[str] = None,
    separator: str = "-",
    lowercase: bool = True,
    max_length: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Slugify values in a single column, writing to dest (or overwriting column)."""
    target = dest if dest else column
    result = []
    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        new_row[target] = _slugify_value(str(raw), separator, lowercase, max_length)
        result.append(new_row)
    return result


def slugify_many(
    rows: List[Dict[str, Any]],
    columns: List[str],
    separator: str = "-",
    lowercase: bool = True,
    max_length: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Slugify multiple columns in-place."""
    result = rows
    for col in columns:
        result = slugify_column(result, col, separator=separator,
                                lowercase=lowercase, max_length=max_length)
    return result
