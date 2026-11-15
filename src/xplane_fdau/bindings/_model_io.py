"""Explicit owned-model projections; no reflective serializer dispatch."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import cast

from ..contracts.identity import AlgorithmRef, DefinitionRef, _algorithm_ref_wire, _definition_ref_wire
from ..contracts.provenance import (
    AdapterIdentity,
    Authority,
    ProvenanceSource,
    ProviderIdentity,
    _adapter_wire,
    _authority_wire,
    _provenance_source_wire,
    _provider_wire,
)
from ..contracts.values import (
    _OMITTED,
    PayloadSpec,
    ScalarRepresentation,
    ShapeSpec,
    UnitSpec,
    ValueRepresentation,
    _payload_spec_wire,
    _shape_spec_wire,
    _unit_spec_wire,
)
from ..measurements.models import ApplicabilitySelector
from .models import (
    AcquisitionPhase,
    BindingInputRef,
    BindingReplayPolicy,
    CompanionRole,
    CompanionSource,
    FailureDisposition,
    FailurePolicy,
    SourceBindingDefinition,
    SourceSpec,
    TransformInput,
    TransformStep,
)


def _unowned(value: object) -> object:
    return None if value is None else object()


def _tag_wire(value: object, vocabulary: type[StrEnum]) -> object:
    return str(value) if isinstance(value, vocabulary) else value


def _source_spec_wire(value: SourceSpec) -> dict[str, object]:
    result: dict[str, object] = {
        "provider": _provider_wire(value.provider) if type(value.provider) is ProviderIdentity else _unowned(value.provider),
        "adapter": _adapter_wire(value.adapter) if type(value.adapter) is AdapterIdentity else _unowned(value.adapter),
        "resource_kind": value.resource_kind,
        "resource_id": value.resource_id,
    }
    if value.owner_signature is not _OMITTED:
        result["owner_signature"] = value.owner_signature
    if value.resource_selection is not _OMITTED:
        result["resource_selection"] = dict(value.resource_selection) if isinstance(value.resource_selection, Mapping) else value.resource_selection
    result["declared_representation"] = _tag_wire(value.declared_representation, ValueRepresentation)
    if value.declared_element_representation is not _OMITTED:
        result["declared_element_representation"] = _tag_wire(value.declared_element_representation, ScalarRepresentation)
    if value.declared_payload is not _OMITTED:
        result["declared_payload"] = (
            _payload_spec_wire(value.declared_payload) if type(value.declared_payload) is PayloadSpec else _unowned(value.declared_payload)
        )
    result["declared_shape"] = _shape_spec_wire(value.declared_shape) if type(value.declared_shape) is ShapeSpec else _unowned(value.declared_shape)
    result["native_unit"] = _unit_spec_wire(value.native_unit) if type(value.native_unit) is UnitSpec else _unowned(value.native_unit)
    return result


def _binding_input_ref_wire(value: BindingInputRef) -> dict[str, object]:
    return dict(
        input_id=value.input_id, source=_source_spec_wire(value.source) if type(value.source) is SourceSpec else _unowned(value.source), required=value.required
    )


def _companion_source_wire(value: CompanionSource) -> dict[str, object]:
    return dict(
        input_id=value.input_id,
        role=_tag_wire(value.role, CompanionRole),
        source=_source_spec_wire(value.source) if type(value.source) is SourceSpec else _unowned(value.source),
    )


def _transform_input_wire(value: TransformInput) -> dict[str, object]:
    result: dict[str, object] = dict(input_id=value.input_id, representation=_tag_wire(value.representation, ValueRepresentation))
    if value.element_representation is not _OMITTED:
        result["element_representation"] = _tag_wire(value.element_representation, ScalarRepresentation)
    if value.payload is not _OMITTED:
        result["payload"] = _payload_spec_wire(value.payload) if type(value.payload) is PayloadSpec else _unowned(value.payload)
    result["shape"] = _shape_spec_wire(value.shape) if type(value.shape) is ShapeSpec else _unowned(value.shape)
    result["unit"] = _unit_spec_wire(value.unit) if type(value.unit) is UnitSpec else _unowned(value.unit)
    return result


def _transform_step_wire(value: TransformStep) -> dict[str, object]:
    inputs: object = value.inputs
    if type(inputs) is tuple:
        inputs = tuple(_transform_input_wire(item) if type(item) is TransformInput else _unowned(item) for item in cast(tuple[object, ...], inputs))
    result: dict[str, object] = dict(
        step_id=value.step_id,
        algorithm=_algorithm_ref_wire(value.algorithm) if type(value.algorithm) is AlgorithmRef else _unowned(value.algorithm),
        inputs=inputs,
        output_representation=_tag_wire(value.output_representation, ValueRepresentation),
    )
    if value.output_element_representation is not _OMITTED:
        result["output_element_representation"] = _tag_wire(value.output_element_representation, ScalarRepresentation)
    if value.output_payload is not _OMITTED:
        result["output_payload"] = _payload_spec_wire(value.output_payload) if type(value.output_payload) is PayloadSpec else _unowned(value.output_payload)
    result["output_shape"] = _shape_spec_wire(value.output_shape) if type(value.output_shape) is ShapeSpec else _unowned(value.output_shape)
    result["output_unit"] = _unit_spec_wire(value.output_unit) if type(value.output_unit) is UnitSpec else _unowned(value.output_unit)
    return result


def _failure_policy_wire(value: FailurePolicy) -> dict[str, object]:
    return {
        name: _tag_wire(getattr(value, name), FailureDisposition)
        for name in ("unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded")
    }


def _source_binding_definition_wire(value: SourceBindingDefinition, *, include_hash: bool = True) -> dict[str, object]:
    """Project exact owned children without consulting any external catalog."""
    provenance: object = value.provenance
    if type(provenance) is tuple:
        provenance = tuple(_provenance_source_wire(item) if type(item) is ProvenanceSource else _unowned(item) for item in provenance)
    applicability: object = value.applicability
    if type(applicability) is tuple:
        applicability = tuple(
            dict(class_id=item.class_id, value=item.value) if type(item) is ApplicabilitySelector else _unowned(item) for item in applicability
        )
    dependencies: object = value.dependencies
    if type(dependencies) is tuple:
        dependencies = tuple(_binding_input_ref_wire(item) if type(item) is BindingInputRef else _unowned(item) for item in dependencies)
    companions: object = value.companions
    if type(companions) is tuple:
        companions = tuple(_companion_source_wire(item) if type(item) is CompanionSource else _unowned(item) for item in companions)
    transforms: object = value.transforms
    if type(transforms) is tuple:
        transforms = tuple(_transform_step_wire(item) if type(item) is TransformStep else _unowned(item) for item in transforms)
    result: dict[str, object] = dict(
        definition_id=value.definition_id,
        definition_revision=value.definition_revision,
        authority=_authority_wire(value.authority) if type(value.authority) is Authority else _unowned(value.authority),
        provenance=provenance,
        measurement_ref=_definition_ref_wire(value.measurement_ref) if type(value.measurement_ref) is DefinitionRef else _unowned(value.measurement_ref),
        source=_source_spec_wire(value.source) if type(value.source) is SourceSpec else _unowned(value.source),
        applicability=applicability,
        dependencies=dependencies,
        companions=companions,
        transforms=transforms,
        failure_policy=_failure_policy_wire(value.failure_policy) if type(value.failure_policy) is FailurePolicy else _unowned(value.failure_policy),
        acquisition_phase=_tag_wire(value.acquisition_phase, AcquisitionPhase),
        replay_policy=_tag_wire(value.replay_policy, BindingReplayPolicy),
        limitations=value.limitations,
    )
    if include_hash:
        result["content_hash"] = value.content_hash
    return result
