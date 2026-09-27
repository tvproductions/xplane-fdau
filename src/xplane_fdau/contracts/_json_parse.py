"""Strict lexical JSON decoding for canonical contracts."""

from __future__ import annotations

import json
import math
from typing import NamedTuple

from .errors import CanonicalJSONError, ContractParseError


class _NumberToken(NamedTuple):
    text: str
    is_real: bool


class _ObjectPairs(NamedTuple):
    pairs: tuple[tuple[str, object], ...]


def _pointer(path: str, token: str) -> str:
    return f"{path}/{token.replace('~', '~0').replace('/', '~1')}"


def _reject_constant(value: str) -> object:
    raise ValueError(f"non-JSON constant: {value[:16]}")


def _check_duplicates(value: object, *, source: str, path: str = "") -> None:
    if isinstance(value, _ObjectPairs):
        seen: set[str] = set()
        for key, child in value.pairs:
            child_path = _pointer(path, key)
            if key in seen:
                raise ContractParseError("duplicate JSON property", source=source, path=child_path)
            seen.add(key)
            _check_duplicates(child, source=source, path=child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_duplicates(child, source=source, path=f"{path}/{index}")


def _parse_json_document(data: str | bytes, *, source: str = "<memory>") -> object:
    """Parse a JSON document while preserving number tokens."""
    if isinstance(data, bytes):
        try:
            document = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ContractParseError("invalid UTF-8", source=source) from error
    else:
        document = data
    if document.startswith("\ufeff"):
        raise ContractParseError("UTF-8 BOM is prohibited", source=source)
    try:
        value = json.loads(
            document,
            parse_int=lambda text: _NumberToken(text, False),
            parse_float=lambda text: _NumberToken(text, True),
            parse_constant=_reject_constant,
            object_pairs_hook=lambda pairs: _ObjectPairs(tuple(pairs)),
        )
    except json.JSONDecodeError as error:
        raise ContractParseError("invalid JSON syntax", source=source, line=error.lineno, column=error.colno) from error
    except (RecursionError, MemoryError) as error:
        raise ContractParseError("JSON document exceeds parser limits", source=source) from error
    except ValueError as error:
        raise ContractParseError("invalid JSON constant", source=source) from error
    try:
        _check_duplicates(value, source=source)
    except (RecursionError, MemoryError) as error:
        raise ContractParseError("JSON document exceeds parser limits", source=source) from error
    return value


def _materialize_number(token: _NumberToken, *, source: str = "<memory>", path: str = "") -> int | float:
    """Convert a checked lexical JSON number to its canonical domain."""
    if not token.is_real:
        digits = token.text.removeprefix("-")
        limit = "9223372036854775808" if token.text.startswith("-") else "9223372036854775807"
        if len(digits) > len(limit) or len(digits) == len(limit) and digits > limit:
            raise CanonicalJSONError("integer outside Int64 range", source=source, path=path)
        return int(token.text)
    try:
        value = float(token.text)
    except (ValueError, OverflowError) as error:
        raise CanonicalJSONError("invalid binary64 number", source=source, path=path) from error
    if not math.isfinite(value):
        raise CanonicalJSONError("binary64 overflow", source=source, path=path)
    mantissa = token.text.lower().split("e", 1)[0]
    if value == 0.0 and any(character in "123456789" for character in mantissa):
        raise CanonicalJSONError("nonzero binary64 underflow", source=source, path=path)
    return value
