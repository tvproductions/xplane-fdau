"""Strict private readers for nested timing evidence, with phased validation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ._json_parse import _check_duplicates, _materialize_number, _NumberToken
from ._timing_validation import _LAYOUT, _check, _mapping, _scalar
from .errors import FDAUContractError
from .timing import ClockAnchor, ClockDomain, ClockReading, ObservationTiming, SourceTiming, UtcInstant


def _materialize(fields: Mapping[str, object], stem: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, kind, _ in _LAYOUT[stem]:
        if name not in fields:
            continue
        value = fields[name]
        if kind in _LAYOUT:
            value = _materialize(_mapping(value, path=""), kind)
        elif isinstance(value, _NumberToken):
            value = _materialize_number(value, path="")
        result[name] = value
    return result


def _construct(fields: dict[str, object], stem: str) -> object:
    for name, kind, _ in _LAYOUT[stem]:
        if name in fields:
            if kind in _LAYOUT and kind != "tick_period":
                fields[name] = _construct(cast(dict[str, object], fields[name]), kind)
            elif kind == "utc":
                fields[name] = UtcInstant(value=cast(str, fields[name]))
    if stem == "clock_domain":
        return ClockDomain(**fields)  # ty: ignore[invalid-argument-type]
    if stem == "clock_reading":
        return ClockReading(**fields)  # ty: ignore[invalid-argument-type]
    if stem == "clock_anchor":
        return ClockAnchor(**fields)  # ty: ignore[invalid-argument-type]
    if stem == "source_timing":
        return SourceTiming(**fields)  # ty: ignore[invalid-argument-type]
    return ObservationTiming(**fields)  # ty: ignore[invalid-argument-type]


def _read(value: object, stem: str, *, path: str, source: str) -> object:
    try:
        _check_duplicates(value, source=source)
        if stem == "utc":
            for phase in range(3):
                _scalar(value, "utc", phase, path="")
            return UtcInstant(value=cast(str, value))
        fields = _mapping(value, path="")
        _check(fields, stem, 0)
        _check(fields, stem, 1)
        materialized = _materialize(fields, stem)
        _check(materialized, stem, 2)
        return _construct(materialized, stem)
    except FDAUContractError as error:
        raise type(error)(str(error), path=path + error.path, source=source, line=error.line, column=error.column) from None


def _clock_domain_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> ClockDomain:
    """Read clock metadata without sampling or registering a clock."""
    return cast(ClockDomain, _read(value, "clock_domain", path=path, source=source))


def _clock_reading_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> ClockReading:
    """Read a signed domain-scoped integer reading."""
    return cast(ClockReading, _read(value, "clock_reading", path=path, source=source))


def _utc_instant_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> UtcInstant:
    """Read an exact nine-digit UTC scalar."""
    return cast(UtcInstant, _read(value, "utc", path=path, source=source))


def _clock_anchor_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> ClockAnchor:
    """Read an explicit anchor without assuming external domain context."""
    return cast(ClockAnchor, _read(value, "clock_anchor", path=path, source=source))


def _source_timing_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> SourceTiming:
    """Read genuinely supplied source timing."""
    return cast(SourceTiming, _read(value, "source_timing", path=path, source=source))


def _observation_timing_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> ObservationTiming:
    """Read receipt and optional timing without synthesizing evidence."""
    return cast(ObservationTiming, _read(value, "observation_timing", path=path, source=source))
