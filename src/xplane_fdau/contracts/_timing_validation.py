"""Private shape, canonical-domain and semantic validation for timing."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from enum import Enum, StrEnum
from math import gcd
from typing import TYPE_CHECKING, cast

from ._identity_validation import _counter, _integer_domain, _nfc_text, _text, _uuid
from .errors import CanonicalJSONError, ContractShapeError, ContractValidationError

if TYPE_CHECKING:
    from .timing import ClockAnchor, ClockDomain


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
    from .timing import ClockKind, ClockUnit

    return {"clock_kind": ClockKind, "clock_unit": ClockUnit}[kind]


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
    if kind in ("clock_kind", "clock_unit"):
        _enum(value, kind, path=path)
        return
    integer = kind in ("integer", "positive", "counter")
    if phase == 0:
        if type(value) is not (int if integer else str):
            raise ContractShapeError("unexpected timing field type", path=path)
    elif phase == 1:
        if integer:
            _integer_domain(value, path=path)
        else:
            _text(value, path=path)
    elif kind == "uuid":
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
    if not isinstance(value, Mapping):
        raise ContractShapeError("expected timing object", path=path)
    if any(type(key) is not str for key in value):
        raise ContractShapeError("property name must be text", path=path)
    return cast(Mapping[str, object], value)


def _check(fields: Mapping[str, object], stem: str, phase: int, *, path: str = "") -> None:
    layout = _LAYOUT[stem]
    for name, kind, optional in layout:
        value = fields.get(name, _OMITTED)
        child_path = path + "/" + name
        if value is _OMITTED:
            if not optional:
                raise ContractShapeError("missing timing property", path=child_path)
            continue
        if kind in _LAYOUT and value is not None:
            _check(_mapping(value, path=child_path), kind, phase, path=child_path)
        else:
            _scalar(value, kind, phase, path=child_path)
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
