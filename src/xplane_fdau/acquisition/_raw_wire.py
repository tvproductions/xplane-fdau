"""Explicit canonical wire projection for owned raw records."""

from __future__ import annotations

from collections.abc import Callable
from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from ..contracts.provenance import AdapterIdentity, ProducerIdentity, ProviderIdentity, _adapter_wire, _producer_wire, _provider_wire
from ..contracts.timing import ObservationTiming, _observation_timing_wire
from ..contracts.values import _OMITTED, InlineValue, PayloadReference, ScalarRepresentation, ValueRepresentation, _inline_value_wire, _payload_reference_wire
from ..measurements.models import ApplicabilitySelector
from .models import ObservationStatus, RawAbsentReason, RawValueEvidence

if TYPE_CHECKING:
    from .models import RawObservation

_NOT_OWNED = object()


def _owned[T](value: object, expected: type[T], serialize: Callable[[T], dict[str, object]]) -> object:
    if value is None:
        return None
    return serialize(cast(T, value)) if type(value) is expected else _NOT_OWNED


def _selector_wire(value: ApplicabilitySelector) -> dict[str, object]:
    return {"class_id": value.class_id, "value": value.value}


def _raw_evidence_wire(value: RawValueEvidence) -> dict[str, object]:
    fields: dict[str, object] = {"kind": value.kind}
    if value.value is not _OMITTED:
        fields["value"] = _owned(value.value, InlineValue, _inline_value_wire)
    if value.payload is not _OMITTED:
        fields["payload"] = _owned(value.payload, PayloadReference, _payload_reference_wire)
    if value.reason is not _OMITTED:
        fields["reason"] = str(value.reason) if type(value.reason) is RawAbsentReason else value.reason
    return fields


def _raw_observation_wire(value: RawObservation, *, include_hash: bool = True) -> dict[str, object]:
    fields: dict[str, object] = {
        "contract_family": value.contract_family,
        "schema_version": value.schema_version,
        "observation_id": value.observation_id,
        "producer": _owned(value.producer, ProducerIdentity, _producer_wire),
        "provider": _owned(value.provider, ProviderIdentity, _provider_wire),
        "adapter": _owned(value.adapter, AdapterIdentity, _adapter_wire),
        "session_id": value.session_id,
        "stream_id": value.stream_id,
        "epoch_id": value.epoch_id,
        "sequence": value.sequence,
        "connection_generation": value.connection_generation,
        "source_generation": value.source_generation,
        "resource_kind": value.resource_kind,
        "resource_id": value.resource_id,
        "observed_shape": value.observed_shape,
        "observed_representation": str(value.observed_representation)
        if type(value.observed_representation) is ValueRepresentation
        else value.observed_representation,
        "value_evidence": _owned(value.value_evidence, RawValueEvidence, _raw_evidence_wire),
        "timing": _owned(value.timing, ObservationTiming, _observation_timing_wire),
        "applicability_context": value.applicability_context,
        "status": str(value.status) if type(value.status) is ObservationStatus else value.status,
        "limitations": value.limitations,
    }
    if type(value.applicability_context) in (tuple, list):
        fields["applicability_context"] = tuple(_owned(item, ApplicabilitySelector, _selector_wire) for item in value.applicability_context)
    if value.resource_selection is not _OMITTED:
        fields["resource_selection"] = dict(value.resource_selection) if type(value.resource_selection) is MappingProxyType else value.resource_selection
    if value.observed_element_representation is not _OMITTED:
        element = value.observed_element_representation
        fields["observed_element_representation"] = str(element) if type(element) is ScalarRepresentation else element
    if value.diagnostic is not _OMITTED:
        fields["diagnostic"] = value.diagnostic
    if include_hash:
        fields["content_hash"] = value.content_hash
    return fields
