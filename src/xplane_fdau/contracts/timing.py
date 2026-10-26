"""Immutable timing contracts for canonical FDAU evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from ._timing_validation import _OMITTED, _enum, _validate

__all__ = ["ClockKind", "ClockUnit", "ClockDomain", "ClockReading"]  # noqa: RUF022 -- specification ownership order


class ClockKind(StrEnum):
    """The source of a clock, independent of its integer unit."""

    HOST_MONOTONIC = "host_monotonic"
    SOURCE = "source"
    SIMULATOR = "simulator"


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
    tick_period: object = _OMITTED

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
    if value.tick_period is not _OMITTED:
        result["tick_period"] = value.tick_period
    if isinstance(value.tick_period, Mapping):
        result["tick_period"] = dict(value.tick_period)
    return result


def _clock_reading_wire(value: ClockReading) -> dict[str, object]:
    return {"clock_domain_id": value.clock_domain_id, "value": value.value}
