"""Staged reading of a complete raw-observation wire document."""

from __future__ import annotations

import re
from typing import Any, cast

from ..bindings._definition_io import _plain
from ..contracts._content_hash import _record_content_hash
from ..contracts._identity_validation import _uuid
from ..contracts._json_parse import _NumberToken, _ObjectPairs, _parse_json_document
from ..contracts._timing_io import _construct as _construct_timing
from ..contracts._timing_validation import _LAYOUT as _TIMING_LAYOUT
from ..contracts._value_io import _construct as _construct_value
from ..contracts.errors import CanonicalJSONError, ContractHashError, ContractShapeError, FDAUContractError, UnsupportedContractVersionError
from ..contracts.provenance import AdapterIdentity, ProducerIdentity, ProviderIdentity
from ..contracts.values import _scalar_check
from ..measurements._definition_io import _domain_tree
from ..measurements.models import ApplicabilitySelector
from ._raw_validation import _FAMILY, _IDENTITIES, _ORDER, _required, _validate_raw_fields
from .models import RawObservation, RawValueEvidence

_MEMBERS = {
    "": _ORDER,
    **{name: tuple(property_name for property_name, _ in layout) for name, layout in _IDENTITIES.items()},
    **{name: tuple(property_name for property_name, _, _ in layout) for name, layout in _TIMING_LAYOUT.items()},
    "resource_selection": ("kind", "index", "start", "length"),
    "applicability_context": ("class_id", "value"),
    "value_evidence": ("kind", "value", "payload", "reason"),
    "value": ("representation", "element_representation", "value"),
    "payload": ("media_type", "byte_length", "sha256", "storage_role", "retention_status"),
}
_TIMING_STEM = {
    "timing": "observation_timing",
    **{name: kind for layout in _TIMING_LAYOUT.values() for name, kind, _ in layout if kind in _TIMING_LAYOUT},
}


def _root_fields(raw: object) -> dict[str, object]:
    if raw is None:
        raise CanonicalJSONError("null is prohibited", path="")
    if not isinstance(raw, _ObjectPairs):
        raise ContractShapeError("expected raw observation object", path="")
    return dict(raw.pairs)


def _check_envelope(fields: dict[str, object]) -> None:
    for name, domain, expected in (("contract_family", "string", _FAMILY), ("schema_version", "integer", "1")):
        value = _required(fields, name, path="")
        if value is None:
            continue
        actual = value
        if domain == "integer" and isinstance(value, _NumberToken) and not value.is_real:
            actual = value.text
        else:
            _scalar_check(value, domain, 0, path="/" + name)
        if actual != expected:
            raise UnsupportedContractVersionError("unsupported contract family or version", path="/" + name)


def _ordered_fields(value: object, *, stem: str = "") -> object:
    if type(value) in (list, tuple):
        return tuple(_ordered_fields(item, stem=stem) for item in cast(list[object] | tuple[object, ...], value))
    if type(value) is dict:
        fields = cast(dict[str, object], value)
        return {name: _ordered_fields(fields[name], stem=_TIMING_STEM.get(name, name)) for name in _MEMBERS[stem] if name in fields}
    return value


def _build_observation(fields: dict[str, Any]) -> RawObservation:
    fields.pop("content_hash")
    fields["producer"] = ProducerIdentity(**fields["producer"])
    fields["provider"] = ProviderIdentity(**fields["provider"])
    fields["adapter"] = AdapterIdentity(**fields["adapter"])
    fields["timing"] = _construct_timing(fields["timing"], "observation_timing")
    fields["applicability_context"] = tuple(ApplicabilitySelector(**item) for item in fields["applicability_context"])
    evidence = fields["value_evidence"]
    if evidence["kind"] == "inline":
        evidence["value"] = _construct_value(evidence["value"], "inline_value")
    elif evidence["kind"] == "payload":
        evidence["payload"] = _construct_value(evidence["payload"], "payload_reference")
    fields["value_evidence"] = RawValueEvidence(**evidence)
    return RawObservation(**fields)


def _identity(raw: object) -> str | None:
    if not isinstance(raw, _ObjectPairs):
        return None
    try:
        return _uuid(dict(raw.pairs).get("observation_id"), path="/observation_id")
    except FDAUContractError:
        return None


def _read_raw_observation(data: str | bytes, *, source: str) -> RawObservation:
    raw: object = None
    try:
        raw = _parse_json_document(data, source=source)
        root = _root_fields(raw)
        _check_envelope(root)
        shadow = cast(dict[str, object], _plain(root, tokens=False))
        if isinstance(root["schema_version"], _NumberToken):
            shadow["schema_version"] = 1
        _validate_raw_fields(shadow, 0, wire=True)
        ordered = _ordered_fields(_plain(root))
        fields = cast(dict[str, Any], _domain_tree(ordered, path=""))
        declared = fields["content_hash"]
        if re.fullmatch(r"[0-9a-f]{64}", declared) and _record_content_hash(fields) != declared:
            raise ContractHashError("declared raw observation hash differs from computed hash", path="/content_hash")
        _validate_raw_fields(fields, 2, wire=True)
        return _build_observation(fields)
    except FDAUContractError as error:
        raise type(error)(
            str(error), source=source, line=error.line, column=error.column, path=error.path, contract_family=_FAMILY, identity=_identity(raw)
        ) from None
