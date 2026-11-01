"""Plain-field catalog validation, with no structural model construction."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ..contracts._identity_validation import _identifier, _revision, _sha256
from ..contracts.errors import ContractShapeError, ContractValidationError
from ..contracts.values import _ordered_array, _scalar_check
from ._definition_validation import _definition_collection, _fields, _null, _required, _text_field, _validate_authority_fields, _validate_definition_fields

_FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog"
_ORDER = ("contract_family", "schema_version", "catalog_id", "catalog_revision", "authority", "provenance", "title", "scope", "definitions", "content_hash")
_REQUIRED = tuple(name for name in _ORDER if name not in ("title", "scope", "content_hash"))


def _definitions(value: object, phase: int, *, path: str) -> None:
    from ._definition_io import _definition_entry_semantics

    if _null(value, phase, path=path):
        return
    entries = _ordered_array(value, path=path)
    if phase == 2 and not entries:
        raise ContractValidationError("definitions must be nonempty", path=path)
    previous: tuple[str, int] | None = None
    for index, entry in enumerate(entries):
        child_path = f"{path}/{index}"
        if _null(entry, phase, path=child_path):
            continue
        if not isinstance(entry, Mapping):
            raise ContractShapeError("expected definition entry object", path=child_path)
        fields = cast(Mapping[str, object], entry)
        if phase == 2:
            identifier = _identifier(fields["definition_id"], path=f"{child_path}/definition_id")
            if previous is not None and identifier < previous[0]:
                raise ContractValidationError("definition IDs must be ordered", path=f"{child_path}/definition_id")
            revision = _revision(fields["definition_revision"], path=f"{child_path}/definition_revision")
            if previous is not None and identifier == previous[0] and revision <= previous[1]:
                raise ContractValidationError("definition pairs must be unique and ordered", path=f"{child_path}/definition_revision")
            previous = (identifier, revision)
            _definition_entry_semantics(fields, path=child_path)
        else:
            _scalar_check(_required(fields, "content_hash", path=child_path), "string", phase, path=f"{child_path}/content_hash")
            _validate_definition_fields({name: child for name, child in fields.items() if name != "content_hash"}, phase, path=child_path)


def _validate_catalog_fields(fields: Mapping[str, object], phase: int, *, path: str = "", wire: bool = False) -> None:
    """Complete one shape/domain/semantic tier over the entire catalog."""
    _fields(fields, (*_REQUIRED, "content_hash") if wire else _REQUIRED, ("title", "scope"), path=path)
    for name in _ORDER:
        if name not in fields and (name in ("title", "scope") or (name == "content_hash" and not wire)):
            continue
        value = _required(fields, name, path=path)
        child_path = f"{path}/{name}"
        if _null(value, phase, path=child_path):
            continue
        if name in ("contract_family", "catalog_id", "title", "scope", "content_hash"):
            _scalar_check(value, "string", min(phase, 1), path=child_path)
            if phase == 2:
                if name == "contract_family" and value != _FAMILY:
                    raise ContractValidationError("wrong catalog family", path=child_path)
                if name == "catalog_id":
                    _identifier(value, path=child_path)
                elif name in ("title", "scope"):
                    _text_field(value, phase, path=child_path, maximum=256 if name == "title" else 2048)
                elif name == "content_hash":
                    _sha256(value, path=child_path)
        elif name in ("schema_version", "catalog_revision"):
            _scalar_check(value, "integer", min(phase, 1), path=child_path)
            if phase == 2:
                if name == "schema_version" and value != 1:
                    raise ContractValidationError("wrong catalog version", path=child_path)
                if name == "catalog_revision":
                    _revision(value, path=child_path)
        elif name == "authority":
            _validate_authority_fields(cast(Mapping[str, object], value), phase, path=child_path)
        elif name == "provenance":
            _definition_collection(value, name, phase, path=child_path)
        else:
            _definitions(value, phase, path=child_path)
