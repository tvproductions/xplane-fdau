"""Canonical preimages for self-hashed FDAU contracts."""

from __future__ import annotations

from hashlib import sha256

from ._identity_validation import _sha256
from .canonical_json import _encode_document
from .errors import ContractShapeError, ContractValidationError

_DEFINITION_FAMILIES = frozenset(
    {
        "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",
        "https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog",
    }
)


def _without_self_hash(value: dict[str, object], *, path: str) -> dict[str, object]:
    result = value.copy()
    if "content_hash" in result:
        _sha256(result.pop("content_hash"), path=path)
    return result


def _record_preimage(document: dict[str, object]) -> bytes:
    return _encode_document(_without_self_hash(document, path="/content_hash"))


def _record_content_hash(document: dict[str, object]) -> str:
    return sha256(_record_preimage(document)).hexdigest()


def _definition_preimage(contract_family: str, definition: dict[str, object]) -> bytes:
    if type(contract_family) is not str:
        raise ContractShapeError("expected definition family URI", path="/contract_family")
    if contract_family not in _DEFINITION_FAMILIES:
        raise ContractValidationError("unsupported definition family", path="/contract_family")
    envelope = {
        "contract_family": contract_family,
        "schema_version": 1,
        "definition": _without_self_hash(definition, path="/definition/content_hash"),
    }
    return _encode_document(envelope)


def _definition_content_hash(contract_family: str, definition: dict[str, object]) -> str:
    return sha256(_definition_preimage(contract_family, definition)).hexdigest()
