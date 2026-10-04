"""Authority and provenance values for canonical contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ._identity_validation import _field_domains, _identifier, _nfc_text, _revision, _sha256, _uuid, _version_text
from .errors import ContractShapeError, ContractValidationError

__all__ = ["Authority", "ProvenanceSource", "ProducerIdentity", "ProviderIdentity", "AdapterIdentity"]


@dataclass(frozen=True, slots=True, kw_only=True)
class Authority:
    authority_id: str
    authority_revision: int

    def __post_init__(self) -> None:
        _field_domains(("/authority_id", self.authority_id, "text"), ("/authority_revision", self.authority_revision, "integer"))
        _identifier(self.authority_id, path="/authority_id")
        _revision(self.authority_revision, path="/authority_revision")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceSource:
    source_id: str
    scope: str
    source_revision: int | None = None
    source_version: str | None = None
    locator: str | None = None
    sha256: str | None = None

    def __post_init__(self) -> None:
        _field_domains(
            ("/source_id", self.source_id, "text"),
            ("/scope", self.scope, "text"),
            ("/source_revision", self.source_revision, "integer"),
            ("/source_version", self.source_version, "text"),
            ("/locator", self.locator, "text"),
            ("/sha256", self.sha256, "text"),
            optional=("/source_revision", "/source_version", "/locator", "/sha256"),
        )
        _identifier(self.source_id, path="/source_id")
        _nfc_text(self.scope, path="/scope", maximum=1024)
        if self.source_revision is None and self.source_version is None:
            raise ContractValidationError("provenance source requires revision or version", path="/source_revision")
        if self.source_revision is not None:
            _revision(self.source_revision, path="/source_revision")
        if self.source_version is not None:
            _version_text(self.source_version, path="/source_version")
        if self.source_revision is not None and self.source_version is not None:
            raise ContractValidationError("provenance source cannot have both revision and version", path="/source_version")
        if self.locator is not None:
            _nfc_text(self.locator, path="/locator", maximum=2048)
        if self.sha256 is not None:
            _sha256(self.sha256, path="/sha256")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProducerIdentity:
    implementation_id: str
    implementation_version: str
    producer_instance_id: str
    source_revision: str | None = None

    def __post_init__(self) -> None:
        _field_domains(
            ("/implementation_id", self.implementation_id, "text"),
            ("/implementation_version", self.implementation_version, "text"),
            ("/producer_instance_id", self.producer_instance_id, "text"),
            ("/source_revision", self.source_revision, "text"),
            optional=("/source_revision",),
        )
        _identifier(self.implementation_id, path="/implementation_id")
        _version_text(self.implementation_version, path="/implementation_version")
        _uuid(self.producer_instance_id, path="/producer_instance_id")
        if self.source_revision is not None:
            _version_text(self.source_revision, path="/source_revision")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderIdentity:
    provider_family_id: str
    provider_version: str

    def __post_init__(self) -> None:
        _field_domains(("/provider_family_id", self.provider_family_id, "text"), ("/provider_version", self.provider_version, "text"))
        _identifier(self.provider_family_id, path="/provider_family_id")
        _version_text(self.provider_version, path="/provider_version")


@dataclass(frozen=True, slots=True, kw_only=True)
class AdapterIdentity:
    adapter_family_id: str
    adapter_version: str

    def __post_init__(self) -> None:
        _field_domains(("/adapter_family_id", self.adapter_family_id, "text"), ("/adapter_version", self.adapter_version, "text"))
        _identifier(self.adapter_family_id, path="/adapter_family_id")
        _version_text(self.adapter_version, path="/adapter_version")


def _authority_wire(value: Authority) -> dict[str, object]:
    return {"authority_id": value.authority_id, "authority_revision": value.authority_revision}


def _provenance_source_wire(value: ProvenanceSource) -> dict[str, object]:
    result: dict[str, object] = {"source_id": value.source_id, "scope": value.scope}
    if value.source_revision is not None:
        result["source_revision"] = value.source_revision
    if value.source_version is not None:
        result["source_version"] = value.source_version
    if value.locator is not None:
        result["locator"] = value.locator
    if value.sha256 is not None:
        result["sha256"] = value.sha256
    return result


def _producer_wire(value: ProducerIdentity) -> dict[str, object]:
    result: dict[str, object] = {
        "implementation_id": value.implementation_id,
        "implementation_version": value.implementation_version,
        "producer_instance_id": value.producer_instance_id,
    }
    if value.source_revision is not None:
        result["source_revision"] = value.source_revision
    return result


def _provider_wire(value: ProviderIdentity) -> dict[str, object]:
    return {"provider_family_id": value.provider_family_id, "provider_version": value.provider_version}


def _adapter_wire(value: AdapterIdentity) -> dict[str, object]:
    return {"adapter_family_id": value.adapter_family_id, "adapter_version": value.adapter_version}


def _catalog_provenance(value: Sequence[ProvenanceSource], *, path: str) -> tuple[ProvenanceSource, ...]:
    if not 1 <= len(value) <= 256:
        raise ContractValidationError("provenance count outside range", path=path)
    result = tuple(value)
    seen: set[tuple[str, str, int | str]] = set()
    for index, source in enumerate(result):
        item_path = f"{path}/{index}"
        if type(source) is not ProvenanceSource:
            raise ContractShapeError("expected provenance source", path=item_path)
        if source.source_revision is not None:
            key = (source.source_id, "revision", source.source_revision)
        else:
            assert source.source_version is not None
            key = (source.source_id, "version", source.source_version)
        if key in seen:
            raise ContractValidationError("duplicate provenance identity", path=item_path)
        seen.add(key)
    return result
