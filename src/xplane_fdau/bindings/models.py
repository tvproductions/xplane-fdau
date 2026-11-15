"""Immutable source and transform declarations owned by bindings."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from ..contracts._content_hash import _definition_content_hash
from ..contracts.identity import AlgorithmRef, DefinitionRef
from ..contracts.provenance import AdapterIdentity, Authority, ProvenanceSource, ProviderIdentity
from ..contracts.values import _OMITTED, ShapeSpec, UnitSpec, ValueRepresentation
from ..measurements.models import ApplicabilitySelector

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
    "SourceBindingDefinition",
    "SourceBindingCatalog",
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


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceBindingDefinition:
    """An immutable exact source-to-measurement declaration and local graph."""

    definition_id: str
    definition_revision: int
    authority: Authority
    provenance: Sequence[ProvenanceSource]
    measurement_ref: DefinitionRef
    source: SourceSpec
    applicability: Sequence[ApplicabilitySelector]
    dependencies: Sequence[BindingInputRef]
    companions: Sequence[CompanionSource]
    transforms: Sequence[TransformStep]
    failure_policy: FailurePolicy
    acquisition_phase: AcquisitionPhase
    replay_policy: BindingReplayPolicy
    limitations: Sequence[str]
    _content_hash: str = field(init=False, repr=False, compare=False)

    @property
    def content_hash(self) -> str:
        """Cached source-binding-family definition identity."""
        return self._content_hash

    def __post_init__(self) -> None:
        from ._definition_validation import _FAMILY, _validate_binding_definition_fields
        from ._model_io import _source_binding_definition_wire

        for name in ("provenance", "applicability", "dependencies", "companions", "transforms", "limitations"):
            value = getattr(self, name)
            if type(value) in (list, tuple):
                object.__setattr__(self, name, tuple(value))
        fields = _source_binding_definition_wire(self, include_hash=False)
        for phase in range(3):
            _validate_binding_definition_fields(fields, phase)
        object.__setattr__(self, "acquisition_phase", AcquisitionPhase(self.acquisition_phase))
        object.__setattr__(self, "replay_policy", BindingReplayPolicy(self.replay_policy))
        object.__setattr__(self, "_content_hash", _definition_content_hash(_FAMILY, fields))


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceBindingCatalog:
    """An immutable, ordered collection of exact source-binding declarations."""

    contract_family: str
    schema_version: int
    catalog_id: str
    catalog_revision: int
    authority: Authority
    provenance: Sequence[ProvenanceSource]
    definitions: Sequence[SourceBindingDefinition]
    title: object = _OMITTED
    scope: object = _OMITTED
    _content_hash: str = field(init=False, repr=False, compare=False)

    @property
    def content_hash(self) -> str:
        """Cached identity covering catalog metadata and complete hashed entries."""
        return self._content_hash

    def __post_init__(self) -> None:
        from ..contracts._content_hash import _record_content_hash
        from ._catalog_validation import _validate_catalog_fields

        for name in ("provenance", "definitions"):
            value = getattr(self, name)
            if type(value) in (list, tuple):
                object.__setattr__(self, name, tuple(value))
        fields = _catalog_fields(self)
        for phase in range(3):
            _validate_catalog_fields(fields, phase)
        object.__setattr__(self, "_content_hash", _record_content_hash(fields))


def _catalog_fields(value: SourceBindingCatalog) -> dict[str, object]:
    """Project exact owned children; null remains available to its domain tier."""
    from ..contracts.provenance import _authority_wire, _provenance_source_wire
    from ._model_io import _source_binding_definition_wire, _unowned

    sources: object = value.provenance
    if type(sources) is tuple:
        sources = tuple(_provenance_source_wire(item) if type(item) is ProvenanceSource else _unowned(item) for item in sources)
    entries: object = value.definitions
    if type(entries) is tuple:
        entries = tuple(_source_binding_definition_wire(item) if type(item) is SourceBindingDefinition else _unowned(item) for item in entries)
    fields: dict[str, object] = dict(
        contract_family=value.contract_family,
        schema_version=value.schema_version,
        catalog_id=value.catalog_id,
        catalog_revision=value.catalog_revision,
        authority=_authority_wire(value.authority) if type(value.authority) is Authority else _unowned(value.authority),
        provenance=sources,
    )
    for name in ("title", "scope"):
        child = getattr(value, name)
        if child is not _OMITTED:
            fields[name] = child
    fields["definitions"] = entries
    return fields
