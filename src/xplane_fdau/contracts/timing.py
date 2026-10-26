"""Immutable timing contracts for canonical FDAU evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import cast

from ._timing_validation import _OMITTED, _enum, _Missing, _scalar, _utc_parts, _validate
from .errors import ContractShapeError, ContractValidationError

__all__ = ["ClockKind", "ClockUnit", "ClockDomain", "ClockReading"]  # noqa: RUF022 -- specification ownership order


class ClockKind(StrEnum):
    """The source of a clock, independent of its integer unit."""

    HOST_MONOTONIC = "host_monotonic"
    SOURCE = "source"
    SIMULATOR = "simulator"


class ReplayState(StrEnum):
    """Observed replay state; absence carries no implied state."""

    LIVE = "live"
    REPLAY = "replay"
    SEEKING = "seeking"
    UNKNOWN = "unknown"


class ClockUnit(StrEnum):
    """Integer reading units; tick periods are exact rational nanoseconds."""

    NANOSECOND = "nanosecond"
    MICROSECOND = "microsecond"
    MILLISECOND = "millisecond"
    TICK = "tick"


@dataclass(frozen=True, slots=True, kw_only=True)
class ClockDomain:
    """Describe a clock's identity, unit, resolution and producer scope."""

    clock_domain_id: str
    kind: ClockKind | str
    unit: ClockUnit | str
    resolution: int
    origin: str
    scope: str
    producer_instance_id: str
    tick_period: Mapping[str, int] | _Missing = _OMITTED

    def __post_init__(self) -> None:
        if isinstance(self.tick_period, Mapping):
            object.__setattr__(self, "tick_period", MappingProxyType(dict(self.tick_period)))
        _validate(_clock_domain_wire(self), "clock_domain")
        object.__setattr__(self, "kind", _enum(self.kind, "clock_kind", path="/kind"))
        object.__setattr__(self, "unit", _enum(self.unit, "clock_unit", path="/unit"))


@dataclass(frozen=True, slots=True, kw_only=True)
class ClockReading:
    """Retain a signed integer reading and the domain in which it is meaningful."""

    clock_domain_id: str
    value: int

    def __post_init__(self) -> None:
        _validate(_clock_reading_wire(self), "clock_reading")


def _clock_domain_wire(value: ClockDomain) -> dict[str, object]:
    result: dict[str, object] = {
        "clock_domain_id": value.clock_domain_id,
        "kind": value.kind,
        "unit": value.unit,
        "resolution": value.resolution,
        "origin": value.origin,
        "scope": value.scope,
        "producer_instance_id": value.producer_instance_id,
    }
    if type(value.kind) is ClockKind:
        result["kind"] = value.kind.value
    if type(value.unit) is ClockUnit:
        result["unit"] = value.unit.value
    if value.tick_period is not _OMITTED:
        result["tick_period"] = value.tick_period
    if isinstance(value.tick_period, Mapping):
        result["tick_period"] = dict(value.tick_period)
    return result


def _clock_reading_wire(value: ClockReading) -> dict[str, object]:
    return {"clock_domain_id": value.clock_domain_id, "value": value.value}


def compare_clock_readings(left: ClockReading, right: ClockReading) -> int:
    """Compare readings only within one explicit clock domain."""
    _arguments((left, ClockReading, "/left"), (right, ClockReading, "/right"))
    if left.clock_domain_id != right.clock_domain_id:
        raise ContractValidationError("unrelated clock domains", path="/right/clock_domain_id")
    return (left.value > right.value) - (left.value < right.value)


def difference_clock_readings_ns(later: ClockReading, earlier: ClockReading, domain: ClockDomain) -> int:
    """Return an exact signed nanosecond difference, with checked final bounds."""
    _arguments((later, ClockReading, "/later"), (earlier, ClockReading, "/earlier"), (domain, ClockDomain, "/domain"))
    for value, path in ((earlier, "/earlier"), (domain, "/domain")):
        if value.clock_domain_id != later.clock_domain_id:
            raise ContractValidationError("unrelated clock domains", path=path + "/clock_domain_id")
    difference = later.value - earlier.value
    if domain.unit == ClockUnit.TICK:
        period = cast(Mapping[str, int], domain.tick_period)
        result, remainder = divmod(difference * period["numerator_ns"], period["denominator"])
        if remainder:
            raise ContractValidationError("difference is a fractional nanosecond")
    else:
        result = difference * {ClockUnit.NANOSECOND: 1, ClockUnit.MICROSECOND: 1000, ClockUnit.MILLISECOND: 1000000}[ClockUnit(domain.unit)]
    if not -(2**63) <= result <= 2**63 - 1:
        raise ContractValidationError("nanosecond difference outside Int64 range")
    return result


def _arguments(*arguments: tuple[object, type, str]) -> None:
    for value, expected, path in arguments:
        if type(value) is not expected:
            raise ContractShapeError("unexpected timing model", path=path)


@dataclass(frozen=True, slots=True, kw_only=True)
class UtcInstant:
    """Preserve explicit UTC text at nanosecond precision."""

    value: str

    def __post_init__(self) -> None:
        for phase in range(3):
            _scalar(self.value, "utc", phase, path="")

    def to_datetime(self) -> datetime:
        """Convert only when microseconds can preserve the instant exactly."""
        parts = _utc_parts(self.value)
        if parts[6] % 1000:
            raise ContractValidationError("datetime conversion would lose nanosecond precision")
        return datetime(*parts[:6], microsecond=parts[6] // 1000, tzinfo=UTC)


@dataclass(frozen=True, slots=True, kw_only=True)
class ClockAnchor:
    """Record correlation at one exact monotonic reading with uncertainty."""

    monotonic_reading: ClockReading
    utc: UtcInstant
    uncertainty_ns: int

    def __post_init__(self) -> None:
        _nested_arguments((self.monotonic_reading, ClockReading, "/monotonic_reading"), (self.utc, UtcInstant, "/utc"))
        _validate(_clock_anchor_wire(self), "clock_anchor")


def _utc_instant_wire(value: UtcInstant) -> str:
    return value.value


def _clock_anchor_wire(value: ClockAnchor) -> dict[str, object]:
    return {
        "monotonic_reading": _clock_reading_wire(value.monotonic_reading) if type(value.monotonic_reading) is ClockReading else value.monotonic_reading,
        "utc": value.utc.value if type(value.utc) is UtcInstant else value.utc,
        "uncertainty_ns": value.uncertainty_ns,
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceTiming:
    """Timing genuinely supplied by a source or simulator."""

    clock: ClockDomain
    reading: ClockReading
    source_sequence: int | _Missing = _OMITTED

    def __post_init__(self) -> None:
        _nested_arguments((self.clock, ClockDomain, "/clock"), (self.reading, ClockReading, "/reading"))
        _validate(_source_timing_wire(self), "source_timing")


@dataclass(frozen=True, slots=True, kw_only=True)
class ObservationTiming:
    """Receipt timing plus independently supplied source and simulator evidence."""

    receipt_clock: ClockDomain
    receipt_reading: ClockReading
    receipt_utc: UtcInstant
    source_timing: SourceTiming | _Missing = _OMITTED
    receipt_anchor: ClockAnchor | _Missing = _OMITTED
    xplane_cycle: int | _Missing = _OMITTED
    simulator_flight_time_ns: int | _Missing = _OMITTED
    acquisition_phase: str | _Missing = _OMITTED
    paused: bool | _Missing = _OMITTED
    replay_state: ReplayState | str | _Missing = _OMITTED
    time_speed: float | _Missing = _OMITTED

    def __post_init__(self) -> None:
        _nested_arguments(
            (self.receipt_clock, ClockDomain, "/receipt_clock"),
            (self.receipt_reading, ClockReading, "/receipt_reading"),
            (self.receipt_utc, UtcInstant, "/receipt_utc"),
            (self.source_timing, SourceTiming, "/source_timing"),
            (self.receipt_anchor, ClockAnchor, "/receipt_anchor"),
        )
        _validate(_observation_timing_wire(self), "observation_timing")
        if self.replay_state is not _OMITTED:
            object.__setattr__(self, "replay_state", _enum(self.replay_state, "replay_state", path="/replay_state"))


def _nested_arguments(*arguments: tuple[object, type, str]) -> None:
    for value, expected, path in arguments:
        if value is not None and value is not _OMITTED:
            _arguments((value, expected, path))


def _source_timing_wire(value: SourceTiming) -> dict[str, object]:
    result: dict[str, object] = {
        "clock": _clock_domain_wire(value.clock) if type(value.clock) is ClockDomain else value.clock,
        "reading": _clock_reading_wire(value.reading) if type(value.reading) is ClockReading else value.reading,
    }
    if value.source_sequence is not _OMITTED:
        result["source_sequence"] = value.source_sequence
    return result


def _observation_timing_wire(value: ObservationTiming) -> dict[str, object]:
    result: dict[str, object] = {
        "receipt_clock": _clock_domain_wire(value.receipt_clock) if type(value.receipt_clock) is ClockDomain else value.receipt_clock,
        "receipt_reading": _clock_reading_wire(value.receipt_reading) if type(value.receipt_reading) is ClockReading else value.receipt_reading,
        "receipt_utc": value.receipt_utc.value if type(value.receipt_utc) is UtcInstant else value.receipt_utc,
    }
    for name, child in (
        ("source_timing", _source_timing_wire(value.source_timing) if type(value.source_timing) is SourceTiming else value.source_timing),
        ("receipt_anchor", _clock_anchor_wire(value.receipt_anchor) if type(value.receipt_anchor) is ClockAnchor else value.receipt_anchor),
        ("xplane_cycle", value.xplane_cycle),
        ("simulator_flight_time_ns", value.simulator_flight_time_ns),
        ("acquisition_phase", value.acquisition_phase),
        ("paused", value.paused),
        ("replay_state", value.replay_state.value if type(value.replay_state) is ReplayState else value.replay_state),
        ("time_speed", value.time_speed),
    ):
        if child is not _OMITTED:
            result[name] = child
    return result
