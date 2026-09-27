"""Deterministic FDAU JSON byte encoding."""

from __future__ import annotations

import math
import re
import unicodedata

from ._json_parse import _NumberToken, _ObjectPairs, _materialize_number, _pointer
from ._binary64 import _ecmascript_number_token
from .errors import CanonicalJSONError

__all__ = ["canonical_bytes"]

_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+\Z")
_SHORT_ESCAPES = {"\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r"}


def _checked_text(value: str, *, path: str, parameter: bool) -> str:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise CanonicalJSONError("unpaired surrogate", path=path)
    if unicodedata.normalize("NFC", value) != value:
        raise CanonicalJSONError("text is not NFC", path=path)
    if parameter and not 1 <= len(value) <= 16384:
        raise CanonicalJSONError("parameter text length is invalid", path=path)
    return value


def _quoted(value: str) -> str:
    result = ['"']
    for character in value:
        if character == '"':
            result.append('\\"')
        elif character == "\\":
            result.append("\\\\")
        elif character in _SHORT_ESCAPES:
            result.append(_SHORT_ESCAPES[character])
        elif ord(character) < 32:
            result.append(f"\\u{ord(character):04x}")
        else:
            result.append(character)
    result.append('"')
    return "".join(result)


def _members(value: object) -> tuple[tuple[object, object], ...]:
    if isinstance(value, _ObjectPairs):
        return value.pairs
    if type(value) is dict:
        return tuple(value.items())
    raise TypeError("not an object")


def _encode(value: object, *, path: str, depth: int, parameter: bool, parts: list[str]) -> None:
    if isinstance(value, _NumberToken):
        value = _materialize_number(value, path=path)
    if isinstance(value, _ObjectPairs) or type(value) is dict:
        if depth > (32 if parameter else 64):
            raise CanonicalJSONError("JSON nesting depth exceeded", path=path)
        members = _members(value)
        if len(members) > 65535:
            raise CanonicalJSONError("object member limit exceeded", path=path)
        keyed: list[tuple[str, object]] = []
        for key, child in members:
            if type(key) is not str:
                raise CanonicalJSONError("object property must be text", path=path)
            keyed.append((key, child))
        parts.append("{")
        for index, (key, child) in enumerate(sorted(keyed, key=lambda item: item[0])):
            child_path = _pointer(path, key)
            _checked_text(key, path=child_path, parameter=False)
            if parameter and (len(key) > 255 or _IDENTIFIER.fullmatch(key) is None):
                raise CanonicalJSONError("invalid parameter identifier", path=child_path)
            if index:
                parts.append(",")
            parts.extend((_quoted(key), ":"))
            _encode(child, path=child_path, depth=depth + 1, parameter=parameter, parts=parts)
        parts.append("}")
        return
    if isinstance(value, (list, tuple)) and type(value) in (list, tuple):
        if depth > (32 if parameter else 64):
            raise CanonicalJSONError("JSON nesting depth exceeded", path=path)
        if len(value) > 65535:
            raise CanonicalJSONError("array member limit exceeded", path=path)
        parts.append("[")
        for index, child in enumerate(value):
            if index:
                parts.append(",")
            _encode(child, path=f"{path}/{index}", depth=depth + 1, parameter=parameter, parts=parts)
        parts.append("]")
        return
    if type(value) is str:
        parts.append(_quoted(_checked_text(value, path=path, parameter=parameter)))
        return
    if type(value) is bool:
        parts.append("true" if value else "false")
        return
    if type(value) is int:
        if not -(2**63) <= value <= 2**63 - 1:
            raise CanonicalJSONError("integer outside Int64 range", path=path)
        parts.append(str(value))
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise CanonicalJSONError("nonfinite binary64", path=path)
        token = _ecmascript_number_token(value)
        parts.append("0.0" if value == 0.0 else token if "." in token or "e" in token else token + ".0")
        return
    raise CanonicalJSONError("unsupported canonical value", path=path)


def _encode_bytes(value: object, *, parameter: bool) -> bytes:
    parts: list[str] = []
    _encode(value, path="", depth=1, parameter=parameter, parts=parts)
    return "".join(parts).encode("utf-8") + b"\n"


def canonical_bytes(value: object) -> bytes:
    """Encode a data-only parameter object."""
    if type(value) is not dict:
        raise CanonicalJSONError("parameter root must be an object")
    return _encode_bytes(value, parameter=True)


def _encode_document(value: object) -> bytes:
    """Encode a validated contract document."""
    return _encode_bytes(value, parameter=False)
