"""Immutable measurement semantics and owned closed vocabularies."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import cast

from ..contracts._content_hash import _definition_content_hash
from ..contracts.errors import ContractShapeError
from ..contracts.provenance import Authority, ProvenanceSource, _authority_wire, _provenance_source_wire
from ..contracts.values import _OMITTED, PayloadSpec, RepresentationSpec, UnitSpec, _ordered_array, _representation_spec_wire, _unit_spec_wire
from ._definition_validation import (
    _coordinate_header,
    _validate_applicability_fields,
    _validate_axis_fields,
    _validate_coordinates_fields,
    _validate_definition_fields,
    _validate_enumeration_fields,
    _validate_enumeration_member_fields,
    _validate_freshness_fields,
    _validate_numeric_fields,
)

__all__ = [  # noqa: RUF022 -- specification ownership order
    "ValidityState",
    "QualityFlag",
    "EnumerationMemberKind",
    "InterpolationPolicy",
    "DiscontinuityPolicy",
    "Sensitivity",
    "AxisSpec",
    "CoordinateSpec",
    "NumericSpec",
    "EnumerationMember",
    "EnumerationSpec",
    "FreshnessSpec",
    "ApplicabilitySelector",
    "MeasurementDefinition",
]


class ValidityState(StrEnum):
    """Producer assertion about evidence validity for its declared use."""

    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class QualityFlag(StrEnum):
    """Acquisition evidence conditions, independent of operational findings."""

    CONVERSION_FAILED = "conversion_failed"
    DISCONTINUOUS = "discontinuous"
    DROPPED = "dropped"
    DUPLICATE = "duplicate"
    ORPHANED = "orphaned"
    OUT_OF_DECLARED_RANGE = "out_of_declared_range"
    PRECISION_LOST = "precision_lost"
    PROVIDER_DEGRADED = "provider_degraded"
    READ_ERROR = "read_error"
    REORDERED = "reordered"
    ROUNDED = "rounded"
    SATURATED = "saturated"
    STALE = "stale"
    TYPE_MISMATCH = "type_mismatch"
    UNAVAILABLE = "unavailable"


class EnumerationMemberKind(StrEnum):
    """Meaning of a declared enumeration code."""

    KNOWN = "known"
    UNKNOWN = "unknown"
    RESERVED = "reserved"


class InterpolationPolicy(StrEnum):
    """Permitted treatment between observations."""

    PROHIBITED = "prohibited"
    HOLD = "hold"
    LINEAR = "linear"


class DiscontinuityPolicy(StrEnum):
    """Declared treatment of discontinuous evidence."""

    PRESERVE = "preserve"
    START_NEW_EPOCH = "start_new_epoch"
    REJECT = "reject"


class Sensitivity(StrEnum):
    """Semantic sensitivity classification."""

    PUBLIC = "public"
    OPERATIONAL = "operational"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True, kw_only=True)
class AxisSpec:
    """One named coordinate axis and its explicit sign meaning."""

    axis_id: str
    direction: str
    sign_convention: str

    def __post_init__(self) -> None:
        fields = {"axis_id": self.axis_id, "direction": self.direction, "sign_convention": self.sign_convention}
        for phase in range(3):
            _validate_axis_fields(fields, phase)


@dataclass(frozen=True, slots=True, kw_only=True)
class CoordinateSpec:
    """Explicit coordinate semantics, or their declared absence."""

    kind: str
    reference_frame_id: object = _OMITTED
    datum_id: object = _OMITTED
    handedness: object = _OMITTED
    axes: object = _OMITTED

    def __post_init__(self) -> None:
        axes = self.axes
        if type(axes) in (list, tuple):
            axes = tuple(cast(list[object] | tuple[object, ...], axes))
        fields: dict[str, object] = {"kind": self.kind}
        for name, value in (("reference_frame_id", self.reference_frame_id), ("datum_id", self.datum_id), ("handedness", self.handedness), ("axes", axes)):
            if value is not _OMITTED:
                fields[name] = value
        if _coordinate_header(fields, 0) and axes is not None:
            checked = _ordered_array(axes, path="/axes")
            if len(checked) > 32:
                raise ContractShapeError("axis count exceeds shape limit", path="/axes")
            for index, axis in enumerate(checked):
                if axis is not None and type(axis) is not AxisSpec:
                    raise ContractShapeError("expected owned axis model", path=f"/axes/{index}")
            fields["axes"] = tuple(
                {"axis_id": axis.axis_id, "direction": axis.direction, "sign_convention": axis.sign_convention} if type(axis) is AxisSpec else axis
                for axis in checked
            )
        for phase in range(3):
            _validate_coordinates_fields(fields, phase)
        object.__setattr__(self, "axes", axes)


@dataclass(frozen=True, slots=True, kw_only=True)
class NumericSpec:
    """Storage precision and one integer or binary64 numeric domain."""

    storage_precision_bits: int
    resolution: int | float
    minimum: object = _OMITTED
    maximum: object = _OMITTED

    def __post_init__(self) -> None:
        fields: dict[str, object] = {"storage_precision_bits": self.storage_precision_bits, "resolution": self.resolution}
        for name, value in (("minimum", self.minimum), ("maximum", self.maximum)):
            if value is not _OMITTED:
                fields[name] = value
        for phase in range(3):
            _validate_numeric_fields(fields, phase)


@dataclass(frozen=True, slots=True, kw_only=True)
class EnumerationMember:
    """One declared code, label and known/unknown/reserved meaning."""

    code: str
    label: str
    kind: EnumerationMemberKind | str

    def __post_init__(self) -> None:
        fields = {"code": self.code, "label": self.label, "kind": self.kind}
        for phase in range(3):
            _validate_enumeration_member_fields(fields, phase)
        object.__setattr__(self, "kind", EnumerationMemberKind(self.kind))


@dataclass(frozen=True, slots=True, kw_only=True)
class EnumerationSpec:
    """Ordered immutable enumeration metadata."""

    members: object

    def __post_init__(self) -> None:
        members = self.members
        if type(members) in (list, tuple):
            members = tuple(cast(list[object] | tuple[object, ...], members))
        projected = members
        if members is not None:
            checked = _ordered_array(members, path="/members")
            for index, member in enumerate(checked):
                if member is not None and type(member) is not EnumerationMember:
                    raise ContractShapeError("expected owned enumeration member", path=f"/members/{index}")
            projected = tuple(
                {"code": member.code, "label": member.label, "kind": member.kind} if type(member) is EnumerationMember else member for member in checked
            )
        fields = {"members": projected}
        for phase in range(3):
            _validate_enumeration_fields(fields, phase)
        object.__setattr__(self, "members", members)


@dataclass(frozen=True, slots=True, kw_only=True)
class FreshnessSpec:
    """Explicit fresh and stale age limits in nanoseconds."""

    fresh_for_ns: object = _OMITTED
    stale_after_ns: object = _OMITTED

    def __post_init__(self) -> None:
        fields = {name: value for name, value in (("fresh_for_ns", self.fresh_for_ns), ("stale_after_ns", self.stale_after_ns)) if value is not _OMITTED}
        for phase in range(3):
            _validate_freshness_fields(fields, phase)


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicabilitySelector:
    """One aircraft or simulator applicability class and value."""

    class_id: str
    value: str

    def __post_init__(self) -> None:
        fields = {"class_id": self.class_id, "value": self.value}
        for phase in range(3):
            _validate_applicability_fields(fields, phase)


@dataclass(frozen=True, slots=True, kw_only=True)
class MeasurementDefinition:
    """Complete immutable meaning of one revision of a measurement."""

    definition_id: str
    definition_revision: int
    authority: Authority
    provenance: Sequence[ProvenanceSource]
    title: str
    description: str
    limitations: Sequence[str]
    quantity_id: str
    representation: RepresentationSpec
    unit: UnitSpec
    coordinates: CoordinateSpec
    freshness: FreshnessSpec
    interpolation_policy: InterpolationPolicy | str
    discontinuity_policy: DiscontinuityPolicy | str
    allowed_validity: Sequence[ValidityState | str]
    allowed_quality: Sequence[QualityFlag | str]
    sensitivity: Sensitivity | str
    applicability: Sequence[ApplicabilitySelector]
    numeric: object = _OMITTED
    enumeration: object = _OMITTED
    _content_hash: str = field(init=False, repr=False, compare=False)

    @property
    def content_hash(self) -> str:
        """Cached family-bound identity computed after constructor validation."""
        return self._content_hash

    def __post_init__(self) -> None:
        # Copy only supported ordered containers; never consume arbitrary iterables.
        for name, value in (
            ("provenance", self.provenance),
            ("limitations", self.limitations),
            ("allowed_validity", self.allowed_validity),
            ("allowed_quality", self.allowed_quality),
            ("applicability", self.applicability),
        ):
            if type(value) in (list, tuple):
                object.__setattr__(self, name, tuple(value))
        fields = _definition_fields(self)
        for phase in range(3):
            _validate_definition_fields(fields, phase)
        object.__setattr__(self, "interpolation_policy", InterpolationPolicy(self.interpolation_policy))
        object.__setattr__(self, "discontinuity_policy", DiscontinuityPolicy(self.discontinuity_policy))
        object.__setattr__(self, "sensitivity", Sensitivity(self.sensitivity))
        object.__setattr__(self, "allowed_validity", tuple(ValidityState(item) for item in self.allowed_validity))
        object.__setattr__(self, "allowed_quality", tuple(QualityFlag(item) for item in self.allowed_quality))
        from ._definition_io import _measurement_definition_wire

        object.__setattr__(
            self,
            "_content_hash",
            _definition_content_hash(
                "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",
                _measurement_definition_wire(self, include_hash=False),
            ),
        )


def _unowned(value: object) -> object:
    """Retain null for its domain phase; reject raw model substitutes at shape."""
    return None if value is None else object()


def _definition_fields(value: MeasurementDefinition) -> dict[str, object]:
    """Project owned nested models explicitly without constructing replacements."""
    authority = _authority_wire(value.authority) if type(value.authority) is Authority else _unowned(value.authority)
    provenance: object = value.provenance
    if type(provenance) is tuple:
        provenance = tuple(_provenance_source_wire(item) if type(item) is ProvenanceSource else _unowned(item) for item in provenance)
    representation: object = _unowned(value.representation)
    if type(value.representation) is RepresentationSpec:
        representation = _representation_spec_wire(value.representation)
        if value.representation.payload is not _OMITTED and type(value.representation.payload) is not PayloadSpec:
            representation["payload"] = _unowned(value.representation.payload)
    unit = _unit_spec_wire(value.unit) if type(value.unit) is UnitSpec else _unowned(value.unit)
    coordinates: object = _unowned(value.coordinates)
    if type(value.coordinates) is CoordinateSpec:
        coordinates = cast(dict[str, object], {"kind": value.coordinates.kind})
        for name, child in (
            ("reference_frame_id", value.coordinates.reference_frame_id),
            ("datum_id", value.coordinates.datum_id),
            ("handedness", value.coordinates.handedness),
        ):
            if child is not _OMITTED:
                coordinates[name] = child
        if value.coordinates.axes is not _OMITTED:
            coordinates["axes"] = tuple(
                {"axis_id": axis.axis_id, "direction": axis.direction, "sign_convention": axis.sign_convention}
                for axis in cast(tuple[AxisSpec, ...], value.coordinates.axes)
            )
    freshness: object = _unowned(value.freshness)
    if type(value.freshness) is FreshnessSpec:
        freshness = {
            name: child
            for name, child in (("fresh_for_ns", value.freshness.fresh_for_ns), ("stale_after_ns", value.freshness.stale_after_ns))
            if child is not _OMITTED
        }
    applicability: object = value.applicability
    if type(applicability) is tuple:
        applicability = tuple(
            {"class_id": item.class_id, "value": item.value} if type(item) is ApplicabilitySelector else _unowned(item) for item in applicability
        )
    fields = dict(
        definition_id=value.definition_id,
        definition_revision=value.definition_revision,
        authority=authority,
        provenance=provenance,
        title=value.title,
        description=value.description,
        limitations=value.limitations,
        quantity_id=value.quantity_id,
        representation=representation,
        unit=unit,
        coordinates=coordinates,
        freshness=freshness,
        interpolation_policy=value.interpolation_policy,
        discontinuity_policy=value.discontinuity_policy,
        allowed_validity=value.allowed_validity,
        allowed_quality=value.allowed_quality,
        sensitivity=value.sensitivity,
        applicability=applicability,
    )
    if value.numeric is not _OMITTED:
        numeric: object = _unowned(value.numeric)
        if type(value.numeric) is NumericSpec:
            numeric = cast(dict[str, object], {"storage_precision_bits": value.numeric.storage_precision_bits, "resolution": value.numeric.resolution})
            for name, child in (("minimum", value.numeric.minimum), ("maximum", value.numeric.maximum)):
                if child is not _OMITTED:
                    numeric[name] = child
        fields["numeric"] = numeric
    if value.enumeration is not _OMITTED:
        enumeration: object = _unowned(value.enumeration)
        if type(value.enumeration) is EnumerationSpec:
            enumeration = {
                "members": tuple(
                    {"code": item.code, "label": item.label, "kind": item.kind} for item in cast(tuple[EnumerationMember, ...], value.enumeration.members)
                )
            }
        fields["enumeration"] = enumeration
    return fields
