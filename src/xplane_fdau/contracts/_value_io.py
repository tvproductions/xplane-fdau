"""Strict private wire readers for delivered canonical value primitives."""

from __future__ import annotations

from typing import cast

from ._identity_validation import _text
from ._json_parse import _check_duplicates, _materialize_number, _NumberToken, _ObjectPairs, _pointer
from .errors import CanonicalJSONError, ContractShapeError, FDAUContractError
from .values import (
    InlineValue,
    PayloadReference,
    PayloadSpec,
    RepresentationSpec,
    RetentionStatus,
    ScalarRepresentation,
    ShapeSpec,
    UnitSpec,
    ValueRepresentation,
    _choice,
    _scalar_check,
    _tag,
)


def _object(value: object, *, path: str) -> dict[str, object]:
    if isinstance(value, _ObjectPairs):
        return dict(value.pairs)
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise ContractShapeError("property name must be text", path=path)
        return cast(dict[str, object], value)
    raise ContractShapeError("expected value object", path=path)


def _layout(stem: str, fields: dict[str, object]) -> tuple[tuple[str, str], ...]:
    if stem == "payload_reference":
        return (("media_type", "string"), ("byte_length", "integer"), ("sha256", "string"), ("storage_role", "string"), ("retention_status", "retention_tag"))
    if stem == "payload_spec":
        return (("allowed_media_types", "array:string"), ("allowed_storage_roles", "array:string"))
    key = "representation" if stem == "inline_value" else "kind"
    if key not in fields:
        raise ContractShapeError("missing variant tag", path="/" + key)
    raw = fields[key]
    if stem in ("inline_value", "representation_spec"):
        tag = str(_tag(raw, ValueRepresentation, path="/" + key))
    else:
        tag = _choice(raw, ("scalar", "fixed", "variable") if stem == "shape_spec" else ("unitless", "unit"), path="/kind")
    result: tuple[tuple[str, str], ...] = ((key, "string"),)
    if stem == "inline_value":
        if tag == "referenced_bytes":
            raise ContractShapeError("bytes require a payload reference", path="/representation")
        if tag in ("fixed_array", "variable_array"):
            if "element_representation" not in fields:
                raise ContractShapeError("missing element tag", path="/element_representation")
            element = str(_tag(fields["element_representation"], ScalarRepresentation, path="/element_representation"))
            return (*result, ("element_representation", "string"), ("value", "array:" + element))
        return (*result, ("value", "array:real" if tag == "vector" else tag))
    if stem == "representation_spec":
        if tag == "vector":
            return (*result, ("length", "integer"))
        if tag == "referenced_bytes":
            return (*result, ("payload", "payload_spec"))
        if tag in ("fixed_array", "variable_array"):
            result += (("element_representation", "scalar_tag"),)
    if tag in ("fixed", "fixed_array"):
        return (*result, ("length", "integer"))
    if tag in ("variable", "variable_array"):
        return (*result, ("minimum_length", "integer"), ("maximum_length", "integer"))
    if tag == "unit":
        return (*result, ("quantity_id", "string"), ("unit_id", "string"))
    return result


def _primitive_shape(value: object, domain: str, *, path: str) -> None:
    if domain in ("scalar_tag", "retention_tag"):
        _tag(value, ScalarRepresentation if domain == "scalar_tag" else RetentionStatus, path=path)
        return
    if value is None:
        return  # null belongs to the canonical-domain tier after all shapes
    if isinstance(value, _NumberToken):
        expected = "real" if value.is_real else "integer"
        if domain != expected:
            raise ContractShapeError("unexpected numeric token type", path=path)
        return
    _scalar_check(value, domain, 0, path=path)


def _shape(value: object, stem: str, *, path: str = "") -> None:
    fields = _object(value, path=path)
    try:
        layout = _layout(stem, fields)
    except FDAUContractError as error:
        raise type(error)(str(error), path=path + error.path) from None
    domains = dict(layout)
    inventory = _inventory(stem, layout)
    for name in inventory:
        child_path = _pointer(path, name)
        if name not in domains:
            if name in fields:
                raise ContractShapeError("irrelevant variant property", path=child_path)
            continue
        if name not in fields:
            raise ContractShapeError("missing value property", path=child_path)
        domain = domains[name]
        child = fields[name]
        if domain == "payload_spec":
            if child is not None:
                _shape(child, domain, path=child_path)
        elif domain.startswith("array:"):
            if child is None:
                continue
            if type(child) not in (list, tuple):
                raise ContractShapeError("expected ordered array", path=child_path)
            child = cast(list[object] | tuple[object, ...], child)
            for index, item in enumerate(child):
                _primitive_shape(item, domain[6:], path=f"{child_path}/{index}")
        else:
            _primitive_shape(child, domain, path=child_path)
    allowed = {name for name, _ in layout}
    for name in sorted(fields):
        if name not in allowed:
            raise ContractShapeError("unknown value property", path=_pointer(path, name))


def _inventory(stem: str, layout: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    if stem == "inline_value":
        return ("representation", "element_representation", "value")
    if stem == "representation_spec":
        return ("kind", "element_representation", "length", "minimum_length", "maximum_length", "payload")
    if stem == "shape_spec":
        return ("kind", "length", "minimum_length", "maximum_length")
    if stem == "unit_spec":
        return ("kind", "quantity_id", "unit_id")
    return tuple(name for name, _ in layout)


def _primitive_domain(value: object, domain: str, *, path: str) -> object:
    if value is None:
        raise CanonicalJSONError("null is prohibited", path=path)
    if isinstance(value, _NumberToken):
        value = _materialize_number(value, path=path)
    if domain in ("scalar_tag", "retention_tag"):
        _text(str(value), path=path)
    else:
        _scalar_check(value, domain, 1, path=path)
    return value


def _domains(value: object, stem: str, *, path: str = "") -> dict[str, object]:
    fields = _object(value, path=path)
    result: dict[str, object] = {}
    for name, domain in _layout(stem, fields):
        child = fields[name]
        child_path = _pointer(path, name)
        if child is None:
            raise CanonicalJSONError("null is prohibited", path=child_path)
        if domain == "payload_spec":
            result[name] = _domains(child, domain, path=child_path)
        elif domain.startswith("array:"):
            child = cast(list[object] | tuple[object, ...], child)
            result[name] = tuple(_primitive_domain(item, domain[6:], path=f"{child_path}/{index}") for index, item in enumerate(child))
        else:
            result[name] = _primitive_domain(child, domain, path=child_path)
    return result


def _construct(fields: dict[str, object], stem: str) -> object:
    if stem == "inline_value":
        return InlineValue(**fields)  # ty: ignore[invalid-argument-type]
    if stem == "payload_reference":
        return PayloadReference(**fields)  # ty: ignore[invalid-argument-type]
    if stem == "payload_spec":
        return PayloadSpec(**fields)
    if stem == "shape_spec":
        return ShapeSpec(**fields)  # ty: ignore[invalid-argument-type]
    if stem == "unit_spec":
        return UnitSpec(**fields)  # ty: ignore[invalid-argument-type]
    if "payload" in fields:
        try:
            fields["payload"] = _construct(cast(dict[str, object], fields["payload"]), "payload_spec")
        except FDAUContractError as error:
            raise type(error)(str(error), path="/payload" + error.path) from None
    return RepresentationSpec(**fields)  # ty: ignore[invalid-argument-type]


def _read(value: object, stem: str, *, path: str, source: str) -> object:
    try:
        _check_duplicates(value, source=source)
        _shape(value, stem)
        return _construct(_domains(value, stem), stem)
    except FDAUContractError as error:
        raise type(error)(str(error), source=source, path=path + error.path, line=error.line, column=error.column) from None


def _inline_value_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> InlineValue:
    """Read an exact typed value with source and enclosing-pointer context."""
    return cast(InlineValue, _read(value, "inline_value", path=path, source=source))


def _payload_reference_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> PayloadReference:
    """Read an original payload claim without accessing its storage."""
    return cast(PayloadReference, _read(value, "payload_reference", path=path, source=source))


def _payload_spec_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> PayloadSpec:
    """Read ordered payload media and role allow-lists."""
    return cast(PayloadSpec, _read(value, "payload_spec", path=path, source=source))


def _representation_spec_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> RepresentationSpec:
    """Read a representation's exact selected variant and constraints."""
    return cast(RepresentationSpec, _read(value, "representation_spec", path=path, source=source))


def _shape_spec_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> ShapeSpec:
    """Read scalar, fixed, or variable shape without inferring dimensions."""
    return cast(ShapeSpec, _read(value, "shape_spec", path=path, source=source))


def _unit_spec_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> UnitSpec:
    """Read explicit unitless status or qualified quantity/unit identities."""
    return cast(UnitSpec, _read(value, "unit_spec", path=path, source=source))
