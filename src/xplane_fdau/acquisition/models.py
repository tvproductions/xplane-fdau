"""Immutable version-1 raw acquisition evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from ..contracts._content_hash import _record_content_hash
from ..contracts.provenance import AdapterIdentity, ProducerIdentity, ProviderIdentity
from ..contracts.timing import ObservationTiming
from ..contracts.values import _OMITTED, InlineValue, PayloadReference, ScalarRepresentation, ValueRepresentation, _Missing
from ..measurements.models import ApplicabilitySelector

__all__ = [  # noqa: RUF022 -- canonical specification ownership order
    "RawAbsentReason",
    "ObservationStatus",
    "RawValueEvidence",
    "RawObservation",
]


class RawAbsentReason(StrEnum):
    """The underlying condition that prevented a raw value."""

    UNAVAILABLE = "unavailable"
    ORPHANED = "orphaned"
    READ_ERROR = "read_error"


class ObservationStatus(StrEnum):
    """The adapter status on one raw observation."""

    OK = "ok"
    UNAVAILABLE = "unavailable"
    ORPHANED = "orphaned"
    TYPE_MISMATCH = "type_mismatch"
    READ_ERROR = "read_error"
    PROVIDER_DEGRADED = "provider_degraded"


@dataclass(frozen=True, slots=True, kw_only=True)
class RawValueEvidence:
    """An inline observation, byte reference, or explicit absence."""

    kind: str
    value: InlineValue | _Missing = _OMITTED
    payload: PayloadReference | _Missing = _OMITTED
    reason: RawAbsentReason | str | _Missing = _OMITTED

    def __post_init__(self) -> None:
        from ._raw_validation import _validate_evidence_fields
        from ._raw_wire import _raw_evidence_wire

        fields = _raw_evidence_wire(self)
        for phase in range(3):
            _validate_evidence_fields(fields, phase, path="")
        if isinstance(self.reason, str):
            object.__setattr__(self, "reason", RawAbsentReason(self.reason))


@dataclass(frozen=True, slots=True, kw_only=True)
class RawObservation:
    """The raw evidence and context supplied by an external adapter."""

    contract_family: str
    schema_version: int
    observation_id: str
    producer: ProducerIdentity
    provider: ProviderIdentity
    adapter: AdapterIdentity
    session_id: str
    stream_id: str
    epoch_id: str
    sequence: int
    connection_generation: int
    source_generation: int
    resource_kind: str
    resource_id: str
    observed_shape: Sequence[int]
    observed_representation: ValueRepresentation | str
    value_evidence: RawValueEvidence
    timing: ObservationTiming
    applicability_context: Sequence[ApplicabilitySelector]
    status: ObservationStatus | str
    limitations: Sequence[str]
    resource_selection: Mapping[str, object] | _Missing = _OMITTED
    observed_element_representation: ScalarRepresentation | str | _Missing = _OMITTED
    diagnostic: str | _Missing = _OMITTED
    _content_hash: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        from ._raw_validation import _validate_raw_fields
        from ._raw_wire import _raw_observation_wire

        for name in ("observed_shape", "applicability_context", "limitations"):
            value = getattr(self, name)
            if type(value) in (list, tuple):
                object.__setattr__(self, name, tuple(value))
        selection = self.resource_selection
        if isinstance(selection, Mapping):
            object.__setattr__(self, "resource_selection", MappingProxyType(dict(selection)))
        fields = _raw_observation_wire(self, include_hash=False)
        for phase in range(3):
            _validate_raw_fields(fields, phase)
        object.__setattr__(self, "observed_representation", ValueRepresentation(self.observed_representation))
        if isinstance(self.observed_element_representation, str):
            object.__setattr__(self, "observed_element_representation", ScalarRepresentation(self.observed_element_representation))
        object.__setattr__(self, "status", ObservationStatus(self.status))
        object.__setattr__(self, "_content_hash", _record_content_hash(fields))

    @property
    def content_hash(self) -> str:
        """Return the record's canonical SHA-256 identity."""
        return self._content_hash
