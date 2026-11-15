"""Private staged binding-entry I/O, ready for later catalog composition."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, cast

from ..contracts._content_hash import _definition_content_hash
from ..contracts._identity_validation import _identifier, _revision, _sha256
from ..contracts._json_parse import _NumberToken, _ObjectPairs
from ..contracts.canonical_json import _encode_document
from ..contracts.errors import ContractHashError, ContractShapeError, FDAUContractError
from ..contracts.identity import AlgorithmRef, DefinitionRef
from ..contracts.provenance import AdapterIdentity, Authority, ProvenanceSource, ProviderIdentity
from ..contracts.values import PayloadSpec, ShapeSpec, UnitSpec, _scalar_check
from ..measurements._definition_io import _domain_tree, _duplicates
from ..measurements._definition_validation import _fields, _required
from ..measurements.models import ApplicabilitySelector
from ._definition_validation import _DEFINITION_ORDER, _FAMILY, _validate_binding_definition_fields
from ._model_io import _source_binding_definition_wire
from ._source_validation import _FAILURE_ORDER, _SOURCE_ORDER
from .models import BindingInputRef, CompanionSource, FailurePolicy, SourceBindingDefinition, SourceSpec, TransformInput, TransformStep

_ORDERS = {
    "definition": (*_DEFINITION_ORDER[:2], "content_hash", *_DEFINITION_ORDER[2:]),
    "authority": ("authority_id", "authority_revision"),
    "provenance": ("source_id", "scope", "source_revision", "source_version", "locator", "sha256"),
    "measurement_ref": ("definition_id", "definition_revision", "definition_hash"),
    "source": _SOURCE_ORDER,
    "provider": ("provider_family_id", "provider_version"),
    "adapter": ("adapter_family_id", "adapter_version"),
    "resource_selection": ("kind", "index", "start", "length"),
    "declared_payload": ("allowed_media_types", "allowed_storage_roles"),
    "payload": ("allowed_media_types", "allowed_storage_roles"),
    "output_payload": ("allowed_media_types", "allowed_storage_roles"),
    "declared_shape": ("kind", "length", "minimum_length", "maximum_length"),
    "shape": ("kind", "length", "minimum_length", "maximum_length"),
    "output_shape": ("kind", "length", "minimum_length", "maximum_length"),
    "native_unit": ("kind", "quantity_id", "unit_id"),
    "unit": ("kind", "quantity_id", "unit_id"),
    "output_unit": ("kind", "quantity_id", "unit_id"),
    "applicability": ("class_id", "value"),
    "dependencies": ("input_id", "source", "required"),
    "companions": ("input_id", "role", "source"),
    "transforms": ("step_id", "algorithm", "inputs", "output_representation", "output_element_representation", "output_payload", "output_shape", "output_unit"),
    "algorithm": ("definition_id", "definition_revision", "definition_hash", "parameters"),
    "inputs": ("input_id", "representation", "element_representation", "payload", "shape", "unit"),
    "failure_policy": _FAILURE_ORDER,
}


def _plain(value: object, *, tokens: bool = True) -> object:
    """Iterative semantic projection; parameter subtrees use lexical key order."""
    pending = [(value, "definition", False, False)]
    projected: list[object] = []
    ancestors: set[int] = set()
    while pending:
        current, stem, parameter, expanded = pending.pop()
        if isinstance(current, _NumberToken):
            projected.append(current if tokens else 0.0 if current.is_real else 0)
            continue
        original = current
        if isinstance(current, _ObjectPairs) or type(current) in (dict, list, tuple):
            if expanded:
                ancestors.remove(id(current))
            else:
                if id(current) in ancestors:
                    projected.append(object())
                    continue
                ancestors.add(id(current))
        if isinstance(current, _ObjectPairs):
            current = dict(current.pairs)
        if type(current) is dict:
            fields = cast(dict[str, object], current)
            order = _ORDERS.get(stem, ())
            # Non-string keys are rejected by the shape/domain tiers, not sorted.
            names = (
                tuple(sorted(fields))
                if parameter and all(type(k) is str for k in fields)
                else (*[n for n in order if n in fields], *[n for n in fields if n not in order])
            )
            if not expanded:
                pending.append((original, stem, parameter, True))
                pending.extend((fields[n], n, parameter or n == "parameters", False) for n in reversed(names))
                continue
            children = projected[-len(names) :] if names else []
            if names:
                del projected[-len(names) :]
            projected.append(dict(zip(names, children, strict=True)))
        elif type(current) in (list, tuple):
            items = cast(list[object] | tuple[object, ...], current)
            if not expanded:
                pending.append((original, stem, parameter, True))
                pending.extend((item, stem, parameter, False) for item in reversed(items))
                continue
            children = projected[-len(items) :] if items else []
            if items:
                del projected[-len(items) :]
            projected.append(tuple(children))
        elif not tokens and current is not None and type(current) not in (str, int, float, bool):
            projected.append(object())
        else:
            projected.append(current)
    return projected[0]


def _without_hash(fields: Mapping[str, object]) -> dict[str, object]:
    return {name: value for name, value in fields.items() if name != "content_hash"}


def _source_binding_definition_bytes(value: SourceBindingDefinition) -> bytes:
    return _encode_document(_source_binding_definition_wire(value))


def _binding_entry_shape(value: object, *, path: str = "") -> dict[str, object]:
    if not isinstance(value, _ObjectPairs) and type(value) is not dict:
        raise ContractShapeError("expected source binding entry object", path=path)
    fields = cast(dict[str, object], _plain(value))
    shadow = cast(dict[str, object], _plain(fields, tokens=False))
    _fields(shadow, (*_DEFINITION_ORDER, "content_hash"), (), path=path)
    for name, domain in (("definition_id", "string"), ("definition_revision", "integer"), ("content_hash", "string")):
        _scalar_check(_required(shadow, name, path=path), domain, 0, path=path + "/" + name)
    _validate_binding_definition_fields(_without_hash(shadow), 0, path=path)
    return fields


def _binding_entry_domains(fields: Mapping[str, object], *, path: str = "") -> dict[str, object]:
    result = cast(dict[str, object], _domain_tree(_plain(dict(fields)), path=path))
    _validate_binding_definition_fields(_without_hash(result), 1, path=path)
    return result


def _binding_entry_hash(fields: Mapping[str, object], *, path: str = "") -> None:
    declared = fields["content_hash"]
    if type(declared) is str and re.fullmatch(r"[0-9a-f]{64}", declared) is not None and _definition_content_hash(_FAMILY, _without_hash(fields)) != declared:
        raise ContractHashError("declared definition hash differs from computed hash", path=path + "/content_hash")


def _binding_entry_semantics(fields: Mapping[str, object], *, path: str = "") -> None:
    _identifier(fields["definition_id"], path=path + "/definition_id")
    _revision(fields["definition_revision"], path=path + "/definition_revision")
    _sha256(fields["content_hash"], path=path + "/content_hash")
    _validate_binding_definition_fields(_without_hash(fields), 2, path=path)


def _value_build(fields: Mapping[str, Any], names: tuple[str, str, str]) -> dict[str, Any]:
    payload, shape, unit = names
    result: dict[str, Any] = {shape: ShapeSpec(**fields[shape]), unit: UnitSpec(**fields[unit])}
    if payload in fields:
        result[payload] = PayloadSpec(**fields[payload])
    return result


def _source_build(fields: Mapping[str, Any]) -> SourceSpec:
    built: dict[str, Any] = dict(fields)
    built["provider"] = ProviderIdentity(**fields["provider"])
    built["adapter"] = AdapterIdentity(**fields["adapter"])
    built.update(_value_build(fields, ("declared_payload", "declared_shape", "native_unit")))
    return SourceSpec(**built)


def _binding_entry_build(fields: Mapping[str, object]) -> SourceBindingDefinition:
    """The only stage that instantiates structural models."""
    f = cast(Mapping[str, Any], fields)
    transforms = []
    for step in f["transforms"]:
        inputs = tuple(TransformInput(**(dict(item) | _value_build(item, ("payload", "shape", "unit")))) for item in step["inputs"])
        built: dict[str, Any] = dict(step)
        built["algorithm"] = AlgorithmRef(**step["algorithm"])
        built["inputs"] = inputs
        built.update(_value_build(step, ("output_payload", "output_shape", "output_unit")))
        transforms.append(TransformStep(**built))

    return SourceBindingDefinition(
        definition_id=f["definition_id"],
        definition_revision=f["definition_revision"],
        authority=Authority(**f["authority"]),
        provenance=tuple(ProvenanceSource(**p) for p in f["provenance"]),
        measurement_ref=DefinitionRef(**f["measurement_ref"]),
        source=_source_build(f["source"]),
        applicability=tuple(ApplicabilitySelector(**p) for p in f["applicability"]),
        dependencies=tuple(BindingInputRef(input_id=p["input_id"], source=_source_build(p["source"]), required=p["required"]) for p in f["dependencies"]),
        companions=tuple(CompanionSource(input_id=p["input_id"], role=p["role"], source=_source_build(p["source"])) for p in f["companions"]),
        transforms=tuple(transforms),
        failure_policy=FailurePolicy(**f["failure_policy"]),
        acquisition_phase=f["acquisition_phase"],
        replay_policy=f["replay_policy"],
        limitations=f["limitations"],
    )


def _source_binding_definition_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> SourceBindingDefinition:
    identity: str | None = None
    try:
        raw = dict(value.pairs) if isinstance(value, _ObjectPairs) else value
        if type(raw) is dict:
            candidate = cast(dict[str, object], raw).get("definition_id")
            if type(candidate) is str:
                identity = candidate[:160]
        _duplicates(value)
        fields = _binding_entry_shape(value)
        fields = _binding_entry_domains(fields)
        _binding_entry_hash(fields)
        _binding_entry_semantics(fields)
        return _binding_entry_build(fields)
    except FDAUContractError as error:
        raise type(error)(
            str(error), source=source, path=path + error.path, line=error.line, column=error.column, contract_family=_FAMILY, identity=identity
        ) from None
