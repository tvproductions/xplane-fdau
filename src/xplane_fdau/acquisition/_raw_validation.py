"""Phased raw-observation field checks shared by construction and interchange."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

from ..bindings._source_validation import _validate_selection_fields
from ..contracts._identity_validation import _counter, _identifier, _nfc_text, _sha256, _uuid, _version_text
from ..contracts._json_parse import _pointer
from ..contracts._timing_validation import _check as _check_timing
from ..contracts._timing_validation import _context_expectations
from ..contracts._value_io import _domains as _value_domains
from ..contracts._value_io import _shape as _value_shape
from ..contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError, FDAUContractError, UnsupportedContractVersionError
from ..contracts.values import _OMITTED, ScalarRepresentation, ValueRepresentation, _inline_check, _media_type, _ordered_array, _scalar_check
from ..measurements._definition_validation import _validate_applicability_fields
from .models import ObservationStatus, RawAbsentReason

_FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/raw-observation"
_ORDER = (
    "contract_family",
    "schema_version",
    "observation_id",
    "producer",
    "provider",
    "adapter",
    "session_id",
    "stream_id",
    "epoch_id",
    "sequence",
    "connection_generation",
    "source_generation",
    "resource_kind",
    "resource_id",
    "resource_selection",
    "observed_shape",
    "observed_representation",
    "observed_element_representation",
    "value_evidence",
    "timing",
    "applicability_context",
    "status",
    "diagnostic",
    "limitations",
    "content_hash",
)
_OPTIONAL = frozenset({"resource_selection", "observed_element_representation", "diagnostic"})
_COUNTERS = frozenset({"sequence", "connection_generation", "source_generation"})
_UUID_FIELDS = frozenset({"observation_id", "session_id", "stream_id", "epoch_id"})
_ARRAY_REPRESENTATIONS = frozenset({"fixed_array", "variable_array"})
_IDENTITIES = {
    "producer": (("implementation_id", "identifier"), ("implementation_version", "version"), ("producer_instance_id", "uuid"), ("source_revision", "version")),
    "provider": (("provider_family_id", "identifier"), ("provider_version", "version")),
    "adapter": (("adapter_family_id", "identifier"), ("adapter_version", "version")),
}
_EVIDENCE_FIELDS = {"inline": "value", "payload": "payload", "absent": "reason"}
_REQUIRED_DIAGNOSTIC = frozenset({"read_error", "type_mismatch", "provider_degraded"})
_ALLOWED_MISSING = frozenset(reason.value for reason in RawAbsentReason)
_STATUSES = frozenset(status.value for status in ObservationStatus)
_REPRESENTATIONS = frozenset(representation.value for representation in ValueRepresentation)
_SCALARS = frozenset(representation.value for representation in ScalarRepresentation)


def _mapping(value: object, *, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ContractShapeError("expected a raw observation object", path=path)
    if any(type(name) is not str for name in value):
        raise ContractShapeError("expected text property name", path=path)
    return cast(Mapping[str, object], value)


def _reject_unknown(fields: Mapping[str, object], names: tuple[str, ...], *, path: str) -> None:
    unknown = sorted(fields.keys() - set(names))
    if unknown:
        raise ContractShapeError("unknown raw observation property", path=_pointer(path, unknown[0]))


def _required(fields: Mapping[str, object], name: str, *, path: str) -> object:
    if name not in fields:
        raise ContractShapeError("missing raw observation property", path=_pointer(path, name))
    return fields[name]


def _null(value: object, phase: int, *, path: str) -> bool:
    if value is None and phase != 0:
        raise CanonicalJSONError("null is prohibited", path=path)
    return value is None


def _closed(value: object, allowed: frozenset[str], phase: int, *, path: str) -> None:
    if _null(value, phase, path=path):
        return
    _scalar_check(value, "string", min(phase, 1), path=path)
    if value not in allowed:
        raise ContractShapeError("unknown raw observation vocabulary member", path=path)


def _identity(value: object, name: str, phase: int, *, path: str) -> None:
    fields = _mapping(value, path=path)
    layout = _IDENTITIES[name]
    for property_name, domain in layout:
        if property_name == "source_revision" and property_name not in fields:
            continue
        leaf = path + "/" + property_name
        entry = _required(fields, property_name, path=path)
        if _null(entry, phase, path=leaf):
            continue
        _scalar_check(entry, "string", min(phase, 1), path=leaf)
        if phase == 2:
            {"identifier": _identifier, "version": _version_text, "uuid": _uuid}[domain](entry, path=leaf)
    if phase == 0:
        _reject_unknown(fields, tuple(property_name for property_name, _ in layout), path=path)


def _observed_shape(value: object, phase: int, *, path: str) -> None:
    dimensions = _ordered_array(value, path=path)
    if len(dimensions) > 1:
        raise ContractShapeError("expected zero or one observed dimension", path=path)
    for dimension in dimensions:
        _scalar_check(dimension, "integer", min(phase, 1), path=path + "/0")
        if phase == 2 and _counter(dimension, path=path + "/0") > 65535:
            raise ContractValidationError("observed dimension exceeds its limit", path=path + "/0")


def _applicability(value: object, phase: int, *, path: str) -> None:
    selectors = _ordered_array(value, path=path)
    if len(selectors) > 256:
        raise ContractShapeError("applicability context exceeds its limit", path=path)
    previous = ""
    for index, selector in enumerate(selectors):
        location = f"{path}/{index}"
        if _null(selector, phase, path=location):
            continue
        fields = _mapping(selector, path=location)
        _validate_applicability_fields(fields, phase, path=location)
        if phase == 2:
            class_id = cast(str, fields["class_id"])
            if class_id <= previous:
                raise ContractValidationError("applicability keys must be unique and ordered", path=location + "/class_id")
            previous = class_id


def _limitations(value: object, phase: int, *, path: str) -> None:
    limitations = _ordered_array(value, path=path)
    if len(limitations) > 256:
        raise ContractShapeError("limitations exceed their limit", path=path)
    seen: set[str] = set()
    for index, entry in enumerate(limitations):
        location = f"{path}/{index}"
        _scalar_check(entry, "string", min(phase, 1), path=location)
        if phase == 2:
            checked = _nfc_text(entry, path=location, maximum=1024)
            if checked in seen:
                raise ContractValidationError("limitations must be unique", path=location)
            seen.add(checked)


def _local_evidence_metadata(fields: Mapping[str, object], *, path: str) -> None:
    evidence = _mapping(fields["value_evidence"], path=path)
    kind = evidence["kind"]
    representation = fields["observed_representation"]
    if kind == "payload" and representation != "referenced_bytes":
        raise ContractValidationError("payload requires observed byte representation", path=path + "/kind")
    if kind != "inline":
        return
    inline = _mapping(evidence["value"], path=path + "/value")
    if inline["representation"] != representation:
        raise ContractValidationError("inline representation differs from observation", path=path + "/value/representation")
    if inline.get("element_representation", _OMITTED) != fields.get("observed_element_representation", _OMITTED):
        raise ContractValidationError("inline element representation differs from observation", path=path + "/value/element_representation")
    value = inline["value"]
    shape = (len(cast(Sequence[object], value)),) if type(value) in (tuple, list) else ()
    if tuple(cast(Sequence[int], fields["observed_shape"])) != shape:
        raise ContractValidationError("inline shape differs from observation", path=path + "/value/value")


def _status_evidence(fields: Mapping[str, object], status: object, *, path: str) -> None:
    evidence_path = path + "/value_evidence"
    evidence = _mapping(fields["value_evidence"], path=evidence_path)
    kind = evidence["kind"]
    if status in _ALLOWED_MISSING:
        if kind != "absent":
            raise ContractValidationError("adapter status requires absent evidence", path=evidence_path + "/kind")
        if evidence["reason"] != status:
            raise ContractValidationError("absence reason must match adapter status", path=evidence_path + "/reason")
    elif status in ("ok", "type_mismatch") and kind == "absent":
        raise ContractValidationError("adapter status requires received evidence", path=evidence_path + "/kind")


def _nested_value(value: object, variant: str, phase: int, *, path: str) -> None:
    fields = _mapping(value, path=path)
    stem = "inline_value" if variant == "value" else "payload_reference"
    if phase == 0:
        _nested_value_shape(fields, stem, path=path)
    elif phase == 1:
        _value_domains(dict(fields), stem, path=path)
    elif variant == "value":
        try:
            _inline_check(fields["representation"], fields.get("element_representation", _OMITTED), fields["value"], 2)
        except FDAUContractError as error:
            raise type(error)(str(error), path=path + error.path) from None
    else:
        _media_type(fields["media_type"], path=path + "/media_type")
        _counter(fields["byte_length"], path=path + "/byte_length")
        _sha256(fields["sha256"], path=path + "/sha256")
        _identifier(fields["storage_role"], path=path + "/storage_role")


def _nested_value_shape(fields: Mapping[str, object], stem: str, *, path: str) -> None:
    # A null discriminant belongs to the canonical-domain tier. Inspect the
    # remaining shape wherever it is known without that discriminant.
    shadow = dict(fields)
    if stem == "payload_reference" and shadow.get("retention_status", _OMITTED) is None:
        shadow["retention_status"] = "unverified"
    if stem == "inline_value":
        tag = shadow.get("representation", _OMITTED)
        if tag is None:
            _required(shadow, "value", path=path)
            _reject_unknown(shadow, ("representation", "element_representation", "value"), path=path)
            return
        if isinstance(tag, str) and tag in _ARRAY_REPRESENTATIONS and shadow.get("element_representation", _OMITTED) is None:
            array = _required(shadow, "value", path=path)
            if array is not None:
                _ordered_array(array, path=path + "/value")
            _reject_unknown(shadow, ("representation", "element_representation", "value"), path=path)
            return
    _value_shape(shadow, stem, path=path)


def _validate_evidence_fields(fields: Mapping[str, object], phase: int, *, path: str) -> None:
    kind = _required(fields, "kind", path=path)
    _closed(kind, frozenset(_EVIDENCE_FIELDS), phase, path=path + "/kind")
    selected = _EVIDENCE_FIELDS.get(cast(str, kind))
    for name in _EVIDENCE_FIELDS.values():
        location = path + "/" + name
        if selected is not None and name != selected:
            if name in fields:
                raise ContractShapeError("irrelevant raw evidence property", path=location)
            continue
        if selected is None and name not in fields:
            continue
        value = _required(fields, name, path=path)
        if _null(value, phase, path=location):
            continue
        if name == "reason":
            _closed(value, _ALLOWED_MISSING, phase, path=location)
        else:
            _nested_value(value, name, phase, path=location)
    if phase == 0:
        _reject_unknown(fields, ("kind", *_EVIDENCE_FIELDS.values()), path=path)


def _envelope(value: object, name: str, phase: int, *, path: str) -> None:
    integer = name == "schema_version"
    _scalar_check(value, "integer" if integer else "string", min(phase, 1), path=path)
    if phase == 0 and value != (1 if integer else _FAMILY):
        raise UnsupportedContractVersionError("unsupported contract family or version", path=path)


def _text_field(value: object, name: str, phase: int, *, path: str) -> None:
    _scalar_check(value, "string", min(phase, 1), path=path)
    if phase != 2:
        return
    if name in _UUID_FIELDS:
        _uuid(value, path=path)
    elif name == "resource_kind":
        _identifier(value, path=path)
    elif name == "content_hash":
        _sha256(value, path=path)
    else:
        _nfc_text(value, path=path, maximum=1024 if name == "diagnostic" else 2048)


def _timing(value: object, fields: Mapping[str, object], phase: int, *, path: str) -> None:
    timing = _mapping(value, path=path)
    expectations = None
    if phase == 2:
        expectations = _context_expectations(timing, "observation_timing", path=path)
        producer = _mapping(fields["producer"], path="/producer")
        expectations[path + "/receipt_clock/producer_instance_id"] = (producer["producer_instance_id"],)
    _check_timing(timing, "observation_timing", phase, path=path, expectations=expectations)


def _validate_field(fields: Mapping[str, object], name: str, value: object, phase: int, *, path: str) -> None:
    location = path + "/" + name
    if _null(value, phase, path=location):
        return
    if name in ("contract_family", "schema_version"):
        _envelope(value, name, phase, path=location)
    elif name in _COUNTERS:
        _scalar_check(value, "integer", min(phase, 1), path=location)
        if phase == 2:
            _counter(value, path=location)
    elif name in _IDENTITIES:
        _identity(value, name, phase, path=location)
    elif name == "resource_selection":
        _validate_selection_fields(_mapping(value, path=location), phase, path=location)
    elif name == "observed_shape":
        _observed_shape(value, phase, path=location)
    elif name == "observed_representation":
        _closed(value, _REPRESENTATIONS, phase, path=location)
    elif name == "observed_element_representation":
        _closed(value, _SCALARS, phase, path=location)
    elif name == "value_evidence":
        _validate_evidence_fields(_mapping(value, path=location), phase, path=location)
        if phase == 2:
            _local_evidence_metadata(fields, path=location)
    elif name == "timing":
        _timing(value, fields, phase, path=location)
    elif name == "applicability_context":
        _applicability(value, phase, path=location)
    elif name == "status":
        _closed(value, _STATUSES, phase, path=location)
        if phase == 2:
            _status_evidence(fields, value, path=path)
    elif name == "limitations":
        _limitations(value, phase, path=location)
    else:
        _text_field(value, name, phase, path=location)


def _element_is_required(fields: Mapping[str, object], *, path: str) -> bool:
    representation = fields["observed_representation"]
    array = representation in _ARRAY_REPRESENTATIONS
    if representation is not None and not array and "observed_element_representation" in fields:
        raise ContractShapeError("irrelevant observed element representation", path=path + "/observed_element_representation")
    return array


def _validate_raw_fields(fields: Mapping[str, object], phase: int, *, path: str = "", wire: bool = False) -> None:
    for name in _ORDER:
        if name == "content_hash" and not wire:
            continue
        optional = name in _OPTIONAL
        if name == "observed_element_representation" and phase == 0:
            optional = not _element_is_required(fields, path=path)
        if name == "diagnostic" and phase == 2:
            status = fields["status"]
            has_diagnostic = name in fields
            if (status == "ok" and has_diagnostic) or (status in _REQUIRED_DIAGNOSTIC and not has_diagnostic):
                raise ContractValidationError("diagnostic presence conflicts with adapter status", path=path + "/diagnostic")
        if optional and name not in fields:
            continue
        _validate_field(fields, name, _required(fields, name, path=path), phase, path=path)
    if phase == 0:
        _reject_unknown(fields, _ORDER if wire else _ORDER[:-1], path=path)
