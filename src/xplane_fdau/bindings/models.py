"""Immutable source and transform declarations owned by bindings."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from ..contracts.identity import AlgorithmRef
from ..contracts.provenance import AdapterIdentity, ProviderIdentity
from ..contracts.values import _OMITTED, ShapeSpec, UnitSpec, ValueRepresentation

__all__ = [  # noqa: RUF022 -- specification ownership order
    "CompanionRole",
    "FailureCondition",
    "FailureDisposition",
    "AcquisitionPhase",
    "BindingReplayPolicy",
    "BindingInputRef",
    "CompanionSource",
    "TransformInput",
    "TransformStep",
    "FailurePolicy",
    "SourceSpec",
]


class CompanionRole(StrEnum):
    """Evidence interpretation role for a companion source."""

    STATUS = "status"
    VALIDITY = "validity"
    STATUS_AND_VALIDITY = "status_and_validity"


class FailureCondition(StrEnum):
    """Conditions requiring an explicitly declared disposition."""

    UNAVAILABLE = "unavailable"
    ORPHANED = "orphaned"
    STALE = "stale"
    READ_ERROR = "read_error"
    TYPE_MISMATCH = "type_mismatch"
    PROVIDER_DEGRADED = "provider_degraded"


class FailureDisposition(StrEnum):
    """Closed outcomes declared for unusable or degraded evidence."""

    REJECT = "reject"
    ACCEPT_RAW_ONLY = "accept_raw_only"
    ACCEPT_FLAGGED = "accept_flagged"
    ACCEPT_WITHOUT_VALUE = "accept_without_value"


class AcquisitionPhase(StrEnum):
    """Declared phase relative to the X-Plane flight model."""

    BEFORE_FLIGHT_MODEL = "before_flight_model"
    AFTER_FLIGHT_MODEL = "after_flight_model"
    EITHER = "either"
    UNKNOWN = "unknown"


class BindingReplayPolicy(StrEnum):
    """Declared treatment of the binding during replay."""

    PRESERVE = "preserve"
    REDERIVE = "rederive"
    PROHIBIT = "prohibit"


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceSpec:
    """Exact source identity and its declared representation, shape and unit."""

    provider: ProviderIdentity
    adapter: AdapterIdentity
    resource_kind: str
    resource_id: str
    declared_representation: ValueRepresentation
    declared_shape: ShapeSpec
    native_unit: UnitSpec
    owner_signature: object = _OMITTED
    resource_selection: object = _OMITTED
    declared_element_representation: object = _OMITTED
    declared_payload: object = _OMITTED

    def __post_init__(self) -> None:
        from ._model_io import _source_spec_wire
        from ._source_validation import _validate_source_fields

        if isinstance(self.resource_selection, Mapping):
            object.__setattr__(self, "resource_selection", MappingProxyType(dict(self.resource_selection)))
        fields = _source_spec_wire(self)
        for phase in range(3):
            _validate_source_fields(fields, phase)
        object.__setattr__(self, "declared_representation", ValueRepresentation(self.declared_representation))
        if self.declared_element_representation is not _OMITTED:
            from ..contracts.values import ScalarRepresentation

            object.__setattr__(self, "declared_element_representation", ScalarRepresentation(self.declared_element_representation))


@dataclass(frozen=True, slots=True, kw_only=True)
class BindingInputRef:
    """A named dependency with an explicit required/optional declaration."""

    input_id: str
    source: SourceSpec
    required: bool

    def __post_init__(self) -> None:
        from ._model_io import _binding_input_ref_wire
        from ._source_validation import _validate_binding_input_fields

        fields = _binding_input_ref_wire(self)
        for phase in range(3):
            _validate_binding_input_fields(fields, phase)


@dataclass(frozen=True, slots=True, kw_only=True)
class CompanionSource:
    """A separately identified source of status or validity evidence."""

    input_id: str
    role: CompanionRole
    source: SourceSpec

    def __post_init__(self) -> None:
        from ._model_io import _companion_source_wire
        from ._source_validation import _validate_companion_fields

        fields = _companion_source_wire(self)
        for phase in range(3):
            _validate_companion_fields(fields, phase)
        object.__setattr__(self, "role", CompanionRole(self.role))


@dataclass(frozen=True, slots=True, kw_only=True)
class TransformInput:
    """One named value input with exact declared metadata."""

    input_id: str
    representation: ValueRepresentation
    shape: ShapeSpec
    unit: UnitSpec
    element_representation: object = _OMITTED
    payload: object = _OMITTED

    def __post_init__(self) -> None:
        from ._model_io import _transform_input_wire
        from ._transform_validation import _validate_transform_input_fields

        fields = _transform_input_wire(self)
        for phase in range(3):
            _validate_transform_input_fields(fields, phase)
        object.__setattr__(self, "representation", ValueRepresentation(self.representation))
        if self.element_representation is not _OMITTED:
            from ..contracts.values import ScalarRepresentation

            object.__setattr__(self, "element_representation", ScalarRepresentation(self.element_representation))


@dataclass(frozen=True, slots=True, kw_only=True)
class TransformStep:
    """An inert algorithm reference and ordered input/output declarations."""

    step_id: str
    algorithm: AlgorithmRef
    inputs: Sequence[TransformInput]
    output_representation: ValueRepresentation
    output_shape: ShapeSpec
    output_unit: UnitSpec
    output_element_representation: object = _OMITTED
    output_payload: object = _OMITTED

    def __post_init__(self) -> None:
        from ._model_io import _transform_step_wire
        from ._transform_validation import _validate_transform_step_fields

        if type(self.inputs) in (list, tuple):
            object.__setattr__(self, "inputs", tuple(self.inputs))
        fields = _transform_step_wire(self)
        for phase in range(3):
            _validate_transform_step_fields(fields, phase)
        object.__setattr__(self, "output_representation", ValueRepresentation(self.output_representation))
        if self.output_element_representation is not _OMITTED:
            from ..contracts.values import ScalarRepresentation

            object.__setattr__(self, "output_element_representation", ScalarRepresentation(self.output_element_representation))


@dataclass(frozen=True, slots=True, kw_only=True)
class FailurePolicy:
    """An explicit disposition for every required input-failure condition."""

    unavailable: FailureDisposition
    orphaned: FailureDisposition
    stale: FailureDisposition
    read_error: FailureDisposition
    type_mismatch: FailureDisposition
    provider_degraded: FailureDisposition

    def __post_init__(self) -> None:
        from ._model_io import _failure_policy_wire
        from ._source_validation import _validate_failure_policy_fields

        fields = _failure_policy_wire(self)
        for phase in range(3):
            _validate_failure_policy_fields(fields, phase)
        for name, value in fields.items():
            object.__setattr__(self, name, FailureDisposition(value))
