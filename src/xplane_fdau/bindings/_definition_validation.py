"""Whole-definition field phases and local source/transform closure."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ..contracts._identity_validation import _identifier, _revision
from ..contracts.errors import ContractShapeError, ContractValidationError
from ..contracts.values import _ordered_array, _scalar_check, _tag
from ..measurements._definition_validation import _definition_collection, _fields, _null, _required, _text_field, _validate_authority_fields
from ._source_validation import (
    _validate_binding_input_fields,
    _validate_companion_fields,
    _validate_failure_policy_fields,
    _validate_ref_fields,
    _validate_source_fields,
)
from ._transform_validation import _source_value_metadata, _validate_step_graph, _validate_transform_step_fields
from .models import AcquisitionPhase, BindingReplayPolicy

_FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog"
_DEFINITION_ORDER = (
    "definition_id",
    "definition_revision",
    "authority",
    "provenance",
    "measurement_ref",
    "source",
    "applicability",
    "dependencies",
    "companions",
    "transforms",
    "failure_policy",
    "acquisition_phase",
    "replay_policy",
    "limitations",
)


def _source_key(fields: Mapping[str, object]) -> tuple[object, ...]:
    provider = cast(Mapping[str, object], fields["provider"])
    adapter = cast(Mapping[str, object], fields["adapter"])
    selection = cast(Mapping[str, object], fields.get("resource_selection", {}))
    return (
        provider["provider_family_id"],
        adapter["adapter_family_id"],
        fields["resource_kind"],
        fields["resource_id"],
        tuple((name, selection[name]) for name in ("kind", "index", "start", "length") if name in selection),
    )


def _source_inputs(
    value: object,
    name: str,
    phase: int,
    *,
    path: str,
    reserved: set[str],
    sources: set[tuple[object, ...]],
    values: dict[str, Mapping[str, object]],
) -> None:
    if _null(value, phase, path=path):
        return
    entries = _ordered_array(value, path=path)
    if len(entries) > 256:
        raise ContractShapeError("collection exceeds shape limit", path=path)
    validator = _validate_binding_input_fields if name == "dependencies" else _validate_companion_fields
    for index, item in enumerate(entries):
        child_path = path + f"/{index}"
        if _null(item, phase, path=child_path):
            continue
        fields = cast(Mapping[str, object], item)
        if phase == 2:
            identifier = _identifier(fields["input_id"], path=child_path + "/input_id")
            if identifier in reserved:
                raise ContractValidationError("source input identity is reserved or duplicate", path=child_path + "/input_id")
            reserved.add(identifier)
        validator(fields, phase, path=child_path)
        if phase == 2:
            source = cast(Mapping[str, object], fields["source"])
            key = _source_key(source)
            if key in sources:
                raise ContractValidationError("source selection is duplicate", path=child_path + "/source")
            sources.add(key)
            if name == "dependencies":
                values[cast(str, fields["input_id"])] = _source_value_metadata(source)


def _transform_collection(
    value: object,
    phase: int,
    *,
    path: str,
    dependencies: object,
    reserved: set[str],
    values: dict[str, Mapping[str, object]],
) -> None:
    if _null(value, phase, path=path):
        return
    steps = _ordered_array(value, path=path)
    if len(steps) > 256:
        raise ContractShapeError("collection exceeds shape limit", path=path)
    if phase == 2 and dependencies and not steps:
        raise ContractValidationError("dependencies require at least one transform", path=path)
    for index, item in enumerate(steps):
        child_path = path + f"/{index}"
        if _null(item, phase, path=child_path):
            continue
        fields = cast(Mapping[str, object], item)
        if phase == 2:
            _validate_step_graph(fields, values, reserved, path=child_path)
        else:
            _validate_transform_step_fields(fields, phase, path=child_path)


def _validate_binding_definition_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None:
    """Validate one whole-entry tier without constructing any models."""
    _fields(fields, _DEFINITION_ORDER, (), path=path)
    reserved = {"binding.primary"}
    sources: set[tuple[object, ...]] = set()
    values: dict[str, Mapping[str, object]] = {}
    for name in _DEFINITION_ORDER:
        value = _required(fields, name, path=path)
        child_path = path + "/" + name
        if _null(value, phase, path=child_path):
            continue
        if name == "definition_id":
            _text_field(value, phase, path=child_path)
        elif name == "definition_revision":
            _scalar_check(value, "integer", min(phase, 1), path=child_path)
            if phase == 2:
                _revision(value, path=child_path)
        elif name == "authority":
            _validate_authority_fields(cast(Mapping[str, object], value), phase, path=child_path)
        elif name in ("provenance", "applicability", "limitations"):
            _definition_collection(value, name, phase, path=child_path)
        elif name == "measurement_ref":
            _validate_ref_fields(value, phase, path=child_path)
        elif name == "source":
            source = cast(Mapping[str, object], value)
            _validate_source_fields(source, phase, path=child_path)
            if phase == 2:
                sources.add(_source_key(source))
                values["binding.primary"] = _source_value_metadata(source)
        elif name in ("dependencies", "companions"):
            _source_inputs(value, name, phase, path=child_path, reserved=reserved, sources=sources, values=values)
        elif name == "transforms":
            _transform_collection(value, phase, path=child_path, dependencies=fields["dependencies"], reserved=reserved, values=values)
        elif name == "failure_policy":
            _validate_failure_policy_fields(cast(Mapping[str, object], value), phase, path=child_path)
        elif name == "acquisition_phase":
            _tag(value, AcquisitionPhase, path=child_path)
        else:
            _tag(value, BindingReplayPolicy, path=child_path)
