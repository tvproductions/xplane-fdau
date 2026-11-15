"""Plain-field phases for source declarations and failure policy."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ..contracts._identity_validation import _counter, _identifier, _revision, _sha256, _version_text
from ..contracts.canonical_json import canonical_bytes
from ..contracts.errors import ContractShapeError, ContractValidationError, FDAUContractError
from ..contracts.values import ScalarRepresentation, ValueRepresentation, _array_set_check, _choice, _scalar_check, _tag
from ..measurements._definition_validation import _fields, _null, _required, _text_field
from .models import CompanionRole, FailureDisposition

_SOURCE_ORDER = (
    "provider",
    "adapter",
    "resource_kind",
    "resource_id",
    "owner_signature",
    "resource_selection",
    "declared_representation",
    "declared_element_representation",
    "declared_payload",
    "declared_shape",
    "native_unit",
)
_SOURCE_OPTIONAL = ("owner_signature", "resource_selection", "declared_element_representation", "declared_payload")
_FAILURE_ORDER = ("unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded")


def _validate_provider_fields(value: object, phase: int, *, path: str, adapter: bool = False) -> None:
    if _null(value, phase, path=path):
        return
    fields = cast(Mapping[str, object], value)
    prefix = "adapter" if adapter else "provider"
    identity, version = prefix + "_family_id", prefix + "_version"
    _fields(fields, (identity, version), (), path=path)
    _text_field(_required(fields, identity, path=path), phase, path=path + "/" + identity)
    raw = _required(fields, version, path=path)
    _text_field(raw, phase, path=path + "/" + version, maximum=128)
    if phase == 2:
        _version_text(raw, path=path + "/" + version)


def _validate_selection_fields(value: object, phase: int, *, path: str) -> None:
    if _null(value, phase, path=path):
        return
    fields = cast(Mapping[str, object], value)
    _fields(fields, ("kind",), ("index", "start", "length"), path=path)
    kind = _required(fields, "kind", path=path)
    if not _null(kind, phase, path=path + "/kind"):
        kind = _choice(kind, ("index", "slice"), path=path + "/kind")
    selected = ("index",) if kind == "index" else ("start", "length") if kind == "slice" else ()
    for name in ("index", "start", "length"):
        child_path = path + "/" + name
        if kind is not None and name not in selected:
            if name in fields:
                raise ContractShapeError("irrelevant selection property", path=child_path)
            continue
        if kind is None and name not in fields:
            continue
        raw = _required(fields, name, path=path)
        _scalar_check(raw, "integer", min(phase, 1), path=child_path)
        if phase == 2:
            number = _counter(raw, path=child_path)
            if name == "length" and number == 0:
                raise ContractValidationError("slice length must be positive", path=child_path)


def _validate_payload_fields(value: object, phase: int, *, path: str) -> None:
    if _null(value, phase, path=path):
        return
    fields = cast(Mapping[str, object], value)
    names = ("allowed_media_types", "allowed_storage_roles")
    _fields(fields, names, (), path=path)
    for name in names:
        _array_set_check(_required(fields, name, path=path), phase, path=path + "/" + name, media=name == "allowed_media_types")


def _validate_shape_fields(value: object, phase: int, *, path: str, representation: object) -> None:
    if _null(value, phase, path=path):
        return
    fields = cast(Mapping[str, object], value)
    _fields(fields, ("kind",), ("length", "minimum_length", "maximum_length"), path=path)
    kind = _required(fields, "kind", path=path)
    if not _null(kind, phase, path=path + "/kind"):
        kind = _choice(kind, ("scalar", "fixed", "variable"), path=path + "/kind")
    expected = "fixed" if representation in ("vector", "fixed_array") else "variable" if representation == "variable_array" else "scalar"
    if phase == 2 and kind != expected:
        raise ContractValidationError("shape differs from representation", path=path + "/kind")
    selected = ("length",) if kind == "fixed" else ("minimum_length", "maximum_length") if kind == "variable" else ()
    for name in ("length", "minimum_length", "maximum_length"):
        child_path = path + "/" + name
        if kind is not None and name not in selected:
            if name in fields:
                raise ContractShapeError("irrelevant shape property", path=child_path)
            continue
        if kind is None and name not in fields:
            continue
        raw = _required(fields, name, path=path)
        _scalar_check(raw, "integer", min(phase, 1), path=child_path)
        if phase == 2:
            number = _counter(raw, path=child_path)
            maximum = 1024 if representation == "vector" else 65535
            if not (1 if name == "length" else 0) <= number <= maximum:
                raise ContractValidationError("declared length outside range", path=child_path)
            if name == "minimum_length" and number > cast(int, fields["maximum_length"]):
                raise ContractValidationError("minimum exceeds maximum length", path=child_path)


def _validate_unit_fields(value: object, phase: int, *, path: str, numeric: bool) -> None:
    if _null(value, phase, path=path):
        return
    fields = cast(Mapping[str, object], value)
    _fields(fields, ("kind",), ("quantity_id", "unit_id"), path=path)
    kind = _required(fields, "kind", path=path)
    if not _null(kind, phase, path=path + "/kind"):
        kind = _choice(kind, ("unitless", "unit"), path=path + "/kind")
    if phase == 2 and not numeric and kind != "unitless":
        raise ContractValidationError("non-numeric representation requires unitless", path=path + "/kind")
    for name in ("quantity_id", "unit_id"):
        if kind == "unitless" and name in fields:
            raise ContractShapeError("irrelevant unit property", path=path + "/" + name)
        if kind == "unit" or name in fields:
            _text_field(_required(fields, name, path=path), phase, path=path + "/" + name)


def _validate_value_fields(
    fields: Mapping[str, object],
    phase: int,
    names: tuple[str, str, str, str, str],
    *,
    path: str,
    expected: Mapping[str, object] | None = None,
) -> None:
    rep_name, element_name, payload_name, shape_name, unit_name = names
    representation = _required(fields, rep_name, path=path)
    if not _null(representation, phase, path=path + "/" + rep_name):
        representation = _tag(representation, ValueRepresentation, path=path + "/" + rep_name)
    if phase == 2 and expected is not None and representation != expected["representation"]:
        raise ContractValidationError("input representation differs from resolved declaration", path=path + "/" + rep_name)
    array = representation in ("fixed_array", "variable_array")
    element: object = None
    for name, needed, expected_name in ((element_name, array, "element_representation"), (payload_name, representation == "referenced_bytes", "payload")):
        if representation is not None:
            if not needed:
                if name in fields:
                    raise ContractShapeError("irrelevant representation property", path=path + "/" + name)
                continue
            value = _required(fields, name, path=path)
        elif name in fields:
            value = fields[name]
        else:
            continue
        if _null(value, phase, path=path + "/" + name):
            continue
        if name == element_name:
            element = _tag(value, ScalarRepresentation, path=path + "/" + name)
        else:
            _validate_payload_fields(value, phase, path=path + "/" + name)
        if phase == 2 and expected is not None and value != expected[expected_name]:
            raise ContractValidationError("input declaration differs from resolved value", path=path + "/" + name)
    shape = _required(fields, shape_name, path=path)
    _validate_shape_fields(shape, phase, path=path + "/" + shape_name, representation=representation)
    if phase == 2 and expected is not None and shape != expected["shape"]:
        raise ContractValidationError("input shape differs from resolved declaration", path=path + "/" + shape_name)
    numeric = representation in ("integer", "real", "vector") or (array and element in ("integer", "real"))
    unit = _required(fields, unit_name, path=path)
    _validate_unit_fields(unit, phase, path=path + "/" + unit_name, numeric=numeric)
    if phase == 2 and expected is not None and unit != expected["unit"]:
        raise ContractValidationError("input unit differs from resolved declaration", path=path + "/" + unit_name)


def _validate_source_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, tuple(name for name in _SOURCE_ORDER if name not in _SOURCE_OPTIONAL), _SOURCE_OPTIONAL, path=path)
    for name in ("provider", "adapter"):
        _validate_provider_fields(_required(fields, name, path=path), phase, path=path + "/" + name, adapter=name == "adapter")
    _text_field(_required(fields, "resource_kind", path=path), phase, path=path + "/resource_kind")
    _text_field(_required(fields, "resource_id", path=path), phase, path=path + "/resource_id", maximum=2048)
    if "owner_signature" in fields:
        _text_field(fields["owner_signature"], phase, path=path + "/owner_signature", maximum=1024)
    if "resource_selection" in fields:
        _validate_selection_fields(fields["resource_selection"], phase, path=path + "/resource_selection")
    _validate_value_fields(
        fields, phase, ("declared_representation", "declared_element_representation", "declared_payload", "declared_shape", "native_unit"), path=path
    )


def _validate_binding_input_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, ("input_id", "source", "required"), (), path=path)
    _text_field(_required(fields, "input_id", path=path), phase, path=path + "/input_id")
    _validate_source_fields_or_null(_required(fields, "source", path=path), phase, path=path + "/source")
    _scalar_check(_required(fields, "required", path=path), "boolean", min(phase, 1), path=path + "/required")


def _validate_source_fields_or_null(value: object, phase: int, *, path: str) -> None:
    if not _null(value, phase, path=path):
        _validate_source_fields(cast(Mapping[str, object], value), phase, path=path)


def _validate_companion_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, ("input_id", "role", "source"), (), path=path)
    _text_field(_required(fields, "input_id", path=path), phase, path=path + "/input_id")
    value = _required(fields, "role", path=path)
    if not _null(value, phase, path=path + "/role"):
        _tag(value, CompanionRole, path=path + "/role")
    _validate_source_fields_or_null(_required(fields, "source", path=path), phase, path=path + "/source")


def _validate_failure_policy_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    _fields(fields, _FAILURE_ORDER, (), path=path)
    for name in _FAILURE_ORDER:
        value = _required(fields, name, path=path)
        child_path = path + "/" + name
        if _null(value, phase, path=child_path):
            continue
        disposition = _tag(value, FailureDisposition, path=child_path)
        if phase == 2 and name in ("unavailable", "orphaned", "read_error") and disposition == "accept_flagged":
            raise ContractValidationError("condition cannot supply usable flagged evidence", path=child_path)


def _validate_ref_fields(value: object, phase: int, *, path: str, algorithm: bool = False) -> None:
    if _null(value, phase, path=path):
        return
    fields = cast(Mapping[str, object], value)
    names = ("definition_id", "definition_revision", "definition_hash")
    _fields(fields, (*names, "parameters") if algorithm else names, (), path=path)
    for name in names:
        raw = _required(fields, name, path=path)
        child_path = path + "/" + name
        _scalar_check(raw, "integer" if name == "definition_revision" else "string", min(phase, 1), path=child_path)
        if phase == 2:
            validator = _identifier if name == "definition_id" else _revision if name == "definition_revision" else _sha256
            validator(raw, path=child_path)
    if algorithm:
        parameters = _required(fields, "parameters", path=path)
        parameter_path = path + "/parameters"
        if _null(parameters, phase, path=parameter_path):
            return
        if not isinstance(parameters, Mapping):
            raise ContractShapeError("expected parameter object", path=parameter_path)
        if phase == 1:
            try:
                canonical_bytes(parameters)
            except FDAUContractError as error:
                raise type(error)(str(error), path=parameter_path + error.path) from None
