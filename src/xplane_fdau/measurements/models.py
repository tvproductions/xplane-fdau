"""Immutable measurement semantics and owned closed vocabularies."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import cast

from ..contracts.errors import ContractShapeError
from ..contracts.values import _OMITTED, _ordered_array
from ._definition_validation import (
    _coordinate_header,
    _validate_applicability_fields,
    _validate_axis_fields,
    _validate_coordinates_fields,
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
