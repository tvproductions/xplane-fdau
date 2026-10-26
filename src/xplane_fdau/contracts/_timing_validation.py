"""Private shape, canonical-domain and semantic validation for timing."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from datetime import date
from enum import Enum, StrEnum
from math import gcd
from typing import TYPE_CHECKING, cast

from ._identity_validation import _counter, _integer_domain, _nfc_text, _text, _uuid
from ._json_parse import _materialize_number, _NumberToken, _ObjectPairs
from .errors import CanonicalJSONError, ContractShapeError, ContractValidationError

if TYPE_CHECKING:
    from .timing import ClockAnchor, ClockDomain, ObservationTiming


class _Missing(Enum):
    OMITTED = "omitted"


_OMITTED = _Missing.OMITTED

_LAYOUT: dict[str, tuple[tuple[str, str, bool], ...]] = {
    "clock_domain": (
        ("clock_domain_id", "uuid", False),
        ("kind", "clock_kind", False),
        ("unit", "clock_unit", False),
        ("resolution", "positive", False),
        ("origin", "description", False),
        ("scope", "description", False),
        ("producer_instance_id", "uuid", False),
        ("tick_period", "tick_period", True),
    ),
    "clock_reading": (("clock_domain_id", "uuid", False), ("value", "integer", False)),
    "tick_period": (("numerator_ns", "positive", False), ("denominator", "positive", False)),
    "clock_anchor": (("monotonic_reading", "clock_reading", False), ("utc", "utc", False), ("uncertainty_ns", "counter", False)),
    "source_timing": (("clock", "clock_domain", False), ("reading", "clock_reading", False), ("source_sequence", "counter", True)),
    "observation_timing": (
        ("receipt_clock", "clock_domain", False),
        ("receipt_reading", "clock_reading", False),
        ("receipt_utc", "utc", False),
        ("source_timing", "source_timing", True),
        ("receipt_anchor", "clock_anchor", True),
        ("xplane_cycle", "counter", True),
        ("simulator_flight_time_ns", "integer", True),
        ("acquisition_phase", "phase", True),
        ("paused", "boolean", True),
        ("replay_state", "replay_state", True),
        ("time_speed", "real", True),
    ),
}

_UTC = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})\.([0-9]{9})Z")


def _utc_parts(value: str, *, path: str = "") -> tuple[int, ...]:
    match = _UTC.fullmatch(value)
    if match is None:
        raise ContractValidationError("expected exact nanosecond UTC text", path=path)
    parts = tuple(int(item) for item in match.groups())
    try:
        date(*parts[:3])
        if parts[3] > 23 or parts[4] > 59 or parts[5] > 59:
            raise ValueError
    except ValueError:
        raise ContractValidationError("invalid Gregorian UTC instant", path=path) from None
    return parts


def _vocabulary(kind: str) -> type[StrEnum]:
    from .timing import ClockKind, ClockUnit, ReplayState

    return {"clock_kind": ClockKind, "clock_unit": ClockUnit, "replay_state": ReplayState}[kind]


def _enum(value: object, kind: str, *, path: str) -> StrEnum:
    vocabulary = _vocabulary(kind)
    if type(value) not in (str, vocabulary):
        raise ContractShapeError("expected timing vocabulary", path=path)
    try:
        return vocabulary(value)
    except ValueError:
        raise ContractShapeError("unknown timing vocabulary", path=path) from None


def _scalar(value: object, kind: str, phase: int, *, path: str) -> None:
    if value is None:
        if phase:
            raise CanonicalJSONError("null is prohibited", path=path)
        return
    if kind in ("clock_kind", "clock_unit", "replay_state"):
        _enum(value, kind, path=path)
        return
    if kind == "phase":
        if type(value) is not str or value not in ("before_flight_model", "after_flight_model", "unknown"):
            raise ContractShapeError("unknown acquisition phase", path=path)
        return
    if phase == 0:
        _scalar_shape(value, kind, path=path)
    elif phase == 1:
        _scalar_domain(value, kind, path=path)
    else:
        _scalar_semantics(value, kind, path=path)


def _scalar_shape(value: object, kind: str, *, path: str) -> None:
    integer = kind in ("integer", "positive", "counter")
    expected = int if integer else {"boolean": bool, "real": float}.get(kind, str)
    if isinstance(value, _NumberToken):
        if expected is not (float if value.is_real else int):
            raise ContractShapeError("unexpected numeric token type", path=path)
    elif type(value) is not expected:
        raise ContractShapeError("unexpected timing field type", path=path)


def _scalar_domain(value: object, kind: str, *, path: str) -> None:
    if isinstance(value, _NumberToken):
        value = _materialize_number(value, path=path)
    if kind in ("integer", "positive", "counter"):
        _integer_domain(value, path=path)
    elif kind == "real":
        if not isinstance(value, float) or not math.isfinite(value):
            raise CanonicalJSONError("nonfinite binary64", path=path)
    elif kind != "boolean":
        _text(value, path=path)


def _scalar_semantics(value: object, kind: str, *, path: str) -> None:
    if kind == "uuid":
        _uuid(value, path=path)
    elif kind == "description":
        _nfc_text(value, path=path, maximum=512)
    elif kind == "utc":
        _utc_parts(cast(str, value), path=path)
    elif kind in ("positive", "counter"):
        number = _counter(value, path=path)
        if kind == "positive" and number == 0:
            raise ContractValidationError("expected positive integer", path=path)


def _mapping(value: object, *, path: str) -> Mapping[str, object]:
    if isinstance(value, _ObjectPairs):
        return dict(value.pairs)
    if not isinstance(value, Mapping):
        raise ContractShapeError("expected timing object", path=path)
    if any(type(key) is not str for key in value):
        raise ContractShapeError("property name must be text", path=path)
    return cast(Mapping[str, object], value)


def _check(
    fields: Mapping[str, object],
    stem: str,
    phase: int,
    *,
    path: str = "",
    expectations: dict[str, tuple[object, ...]] | None = None,
) -> None:
    if phase == 2 and expectations is None:
        expectations = _context_expectations(fields, stem, path=path)
    layout = _LAYOUT[stem]
    for name, kind, optional in layout:
        value = fields.get(name, _OMITTED)
        child_path = path + "/" + name
        if value is _OMITTED:
            if not optional:
                raise ContractShapeError("missing timing property", path=child_path)
            continue
        if kind in _LAYOUT and value is not None:
            _check(_mapping(value, path=child_path), kind, phase, path=child_path, expectations=expectations)
        else:
            _scalar(value, kind, phase, path=child_path)
        if phase == 2 and expectations is not None and child_path in expectations and value not in expectations[child_path]:
            raise ContractValidationError("timing evidence does not match its context", path=child_path)
    if phase == 0:
        allowed = {name for name, _, _ in layout}
        for name in sorted(fields):
            if name not in allowed:
                raise ContractShapeError("unknown timing property", path=path + "/" + name.replace("~", "~0").replace("/", "~1"))
    if phase == 2:
        _semantics(fields, stem, path=path)


def _semantics(fields: Mapping[str, object], stem: str, *, path: str) -> None:
    if stem == "clock_domain":
        present = fields.get("tick_period", _OMITTED) is not _OMITTED
        if present != (fields["unit"] == "tick"):
            raise ContractValidationError("tick period required exactly for tick units", path=path + "/tick_period")
    elif stem == "tick_period":
        if gcd(cast(int, fields["numerator_ns"]), cast(int, fields["denominator"])) != 1:
            raise ContractValidationError("tick period must be in lowest terms", path=path)


def _context_expectations(fields: Mapping[str, object], stem: str, *, path: str) -> dict[str, tuple[object, ...]]:
    """Place contextual constraints on their exact semantic leaf positions."""
    result: dict[str, tuple[object, ...]] = {}
    for name, kind, _ in _LAYOUT[stem]:
        if kind in _LAYOUT and name in fields:
            result.update(_context_expectations(_mapping(fields[name], path=path + "/" + name), kind, path=path + "/" + name))
    if stem == "source_timing":
        clock = _mapping(fields["clock"], path=path + "/clock")
        result[path + "/clock/kind"] = ("source", "simulator")
        result[path + "/reading/clock_domain_id"] = (clock["clock_domain_id"],)
    elif stem == "observation_timing":
        result.update(_observation_expectations(fields, path=path))
    return result


def _match(expected: object, actual: object, *, path: str) -> None:
    if expected != actual:
        raise ContractValidationError("timing evidence does not match its context", path=path)


def _observation_expectations(fields: Mapping[str, object], *, path: str) -> dict[str, tuple[object, ...]]:
    clock = _mapping(fields["receipt_clock"], path=path + "/receipt_clock")
    reading = _mapping(fields["receipt_reading"], path=path + "/receipt_reading")
    result = {path + "/receipt_clock/kind": ("host_monotonic",), path + "/receipt_reading/clock_domain_id": (clock["clock_domain_id"],)}
    if "receipt_anchor" in fields:
        for name in ("clock_domain_id", "value"):
            result[path + "/receipt_anchor/monotonic_reading/" + name] = (reading[name],)
        result[path + "/receipt_anchor/utc"] = (fields["receipt_utc"],)
    return result


def _validate(fields: Mapping[str, object], stem: str) -> None:
    for phase in range(3):
        _check(fields, stem, phase)


def _validate_clock_anchor(value: ClockAnchor, *, domain: ClockDomain | None = None, path: str = "") -> None:
    """Check anchor context only when an external domain is supplied."""
    from .timing import ClockAnchor, ClockDomain, _arguments

    _arguments((value, ClockAnchor, path))
    if domain is not None:
        _arguments((domain, ClockDomain, path + "/domain"))
        if domain.kind != "host_monotonic" or value.monotonic_reading.clock_domain_id != domain.clock_domain_id:
            raise ContractValidationError("anchor requires its host monotonic domain", path=path + "/monotonic_reading/clock_domain_id")


def _validate_observation_producer(value: ObservationTiming, producer_instance_id: str, *, path: str = "") -> None:
    """Check producer context supplied by an enclosing observation record."""
    from .timing import ObservationTiming, _arguments

    _arguments((value, ObservationTiming, path))
    _uuid(producer_instance_id, path=path + "/producer_instance_id")
    _match(producer_instance_id, value.receipt_clock.producer_instance_id, path=path + "/receipt_clock/producer_instance_id")
