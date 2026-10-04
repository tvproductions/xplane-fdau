"""Shared identity-domain validators for canonical contracts."""

from __future__ import annotations

import re
import unicodedata

from .errors import CanonicalJSONError, ContractShapeError, ContractValidationError

_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+\Z")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_MAX_U63 = 2**63 - 1


def _text(value: object, *, path: str) -> str:
    if type(value) is not str:
        raise ContractShapeError("expected text", path=path)
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise CanonicalJSONError("unpaired surrogate", path=path)
    if unicodedata.normalize("NFC", value) != value:
        raise CanonicalJSONError("text is not NFC", path=path)
    return value


def _identifier(value: object, *, path: str) -> str:
    checked = _text(value, path=path)
    if len(checked) > 255 or _IDENTIFIER.fullmatch(checked) is None:
        raise ContractValidationError("invalid identifier", path=path)
    return checked


def _revision(value: object, *, path: str) -> int:
    if type(value) is not int:
        raise ContractShapeError("expected integer revision", path=path)
    if not 1 <= value <= _MAX_U63:
        raise ContractValidationError("revision outside range", path=path)
    return value


def _counter(value: object, *, path: str) -> int:
    if type(value) is not int:
        raise ContractShapeError("expected integer counter", path=path)
    if not 0 <= value <= _MAX_U63:
        raise ContractValidationError("counter outside range", path=path)
    return value


def _uuid(value: object, *, path: str) -> str:
    checked = _text(value, path=path)
    if _UUID.fullmatch(checked) is None:
        raise ContractValidationError("invalid UUID", path=path)
    return checked


def _sha256(value: object, *, path: str) -> str:
    checked = _text(value, path=path)
    if _SHA256.fullmatch(checked) is None:
        raise ContractValidationError("invalid SHA-256", path=path)
    return checked


def _version_text(value: object, *, path: str) -> str:
    checked = _nfc_text(value, path=path, maximum=128)
    if any(unicodedata.category(char) in {"Cc", "Cf"} for char in checked):
        raise ContractValidationError("control or format character in version", path=path)
    return checked


def _nfc_text(value: object, *, path: str, maximum: int) -> str:
    checked = _text(value, path=path)
    if not 1 <= len(checked) <= maximum:
        raise ContractValidationError("text length outside range", path=path)
    return checked
