"""Immutable timing contracts for canonical FDAU evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import cast

from ._timing_validation import _OMITTED, _enum, _validate
from .errors import ContractShapeError, ContractValidationError

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
