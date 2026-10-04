"""Pinned canonical definition and record references."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, override

from ._identity_validation import _field_domains, _identifier, _revision, _sha256, _uuid
from .canonical_json import canonical_bytes
from .errors import CanonicalJSONError, ContractShapeError, ContractValidationError

__all__ = ["DefinitionRef", "RecordRef", "AlgorithmRef"]

_FAMILY_PREFIX = "https://tvproductions.github.io/xplane-fdau/contracts/"
_FAMILIES = frozenset(
    _FAMILY_PREFIX + stem
    for stem in (
        "measurement-catalog",
        "source-binding-catalog",
        "raw-observation",
        "measurement-sample",
        "measurement-frame",
    )
)


def _immutable(value: object) -> object:
    if type(value) is dict:
        return MappingProxyType({key: _immutable(child) for key, child in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_immutable(child) for child in value)
    return value


def _plain(value: object, *, depth: int = 1) -> object:
    """Copy containers without descending beyond the parameter domain.

    Keep a container at depth 33 so the canonical encoder reports that overflow
    in canonical property order, before it could inspect any children there.
    """
    if isinstance(value, Mapping):
        return {} if depth > 32 else {key: _plain(child, depth=depth + 1) for key, child in value.items()}
    if isinstance(value, (list, tuple)) and type(value) in (list, tuple):
        return [] if depth > 32 else [_plain(child, depth=depth + 1) for child in value]
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class DefinitionRef:
    """Pin a definition's semantic identity, revision, and canonical hash."""

    definition_id: str
    definition_revision: int
    definition_hash: str

    def __post_init__(self) -> None:
        _field_domains(
            ("/definition_id", self.definition_id, "text"),
            ("/definition_revision", self.definition_revision, "integer"),
            ("/definition_hash", self.definition_hash, "text"),
        )
        _identifier(self.definition_id, path="/definition_id")
        _revision(self.definition_revision, path="/definition_revision")
        _sha256(self.definition_hash, path="/definition_hash")


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordRef:
    """Pin a record's UUID, family, schema version, and canonical hash."""

    record_id: str
    contract_family: str
    schema_version: int
    content_hash: str

    def __post_init__(self) -> None:
        _field_domains(
            ("/record_id", self.record_id, "text"),
            ("/contract_family", self.contract_family, "text"),
            ("/schema_version", self.schema_version, "integer"),
            ("/content_hash", self.content_hash, "text"),
        )
        _uuid(self.record_id, path="/record_id")
        if type(self.contract_family) is not str:
            raise ContractShapeError("expected family URI", path="/contract_family")
        if self.contract_family not in _FAMILIES:
            raise ContractValidationError("unsupported family URI", path="/contract_family")
        if type(self.schema_version) is not int:
            raise ContractShapeError("expected integer schema version", path="/schema_version")
        if self.schema_version != 1:
            raise ContractValidationError("unsupported schema version", path="/schema_version")
        _sha256(self.content_hash, path="/content_hash")


@dataclass(frozen=True, slots=True, kw_only=True)
class AlgorithmRef:
    """Pin an algorithm definition together with immutable data-only parameters."""

    definition_id: str
    definition_revision: int
    definition_hash: str
    parameters: Mapping[str, object]

    def __post_init__(self) -> None:
        _field_domains(
            ("/definition_id", self.definition_id, "text"),
            ("/definition_revision", self.definition_revision, "integer"),
            ("/definition_hash", self.definition_hash, "text"),
            ("/parameters", self.parameters, "object"),
        )
        plain = _plain(self.parameters)
        try:
            canonical_bytes(plain)
        except CanonicalJSONError as error:
            raise CanonicalJSONError(str(error), path="/parameters" + error.path) from error
        _identifier(self.definition_id, path="/definition_id")
        _revision(self.definition_revision, path="/definition_revision")
        _sha256(self.definition_hash, path="/definition_hash")
        object.__setattr__(self, "parameters", _immutable(plain))

    @override
    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return _definition_ref_wire(self) == _definition_ref_wire(other) and canonical_bytes(_plain(self.parameters)) == canonical_bytes(
            _plain(other.parameters)
        )


def _definition_ref_wire(value: DefinitionRef | AlgorithmRef) -> dict[str, object]:
    return {
        "definition_id": value.definition_id,
        "definition_revision": value.definition_revision,
        "definition_hash": value.definition_hash,
    }


def _record_ref_wire(value: RecordRef) -> dict[str, object]:
    return {
        "record_id": value.record_id,
        "contract_family": value.contract_family,
        "schema_version": value.schema_version,
        "content_hash": value.content_hash,
    }


def _algorithm_ref_wire(value: AlgorithmRef) -> dict[str, object]:
    return _definition_ref_wire(value) | {"parameters": _plain(value.parameters)}
