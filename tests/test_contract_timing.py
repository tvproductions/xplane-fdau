"""Behavioral contracts for clock identity, exact units and timing evidence."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from enum import StrEnum
from typing import Any

from xplane_fdau.contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError
from xplane_fdau.contracts.timing import ClockDomain, ClockKind, ClockReading, ClockUnit

DOMAIN_ID = "11111111-1111-4111-8111-111111111111"
PRODUCER_ID = "22222222-2222-4222-8222-222222222222"
OTHER_ID = "33333333-3333-4333-8333-333333333333"
DOMAIN_KWARGS: dict[str, Any] = dict(
    clock_domain_id=DOMAIN_ID,
    kind="host_monotonic",
    unit="nanosecond",
    resolution=1,
    origin="test process origin",
    scope="test process",
    producer_instance_id=PRODUCER_ID,
)


def _domain(**overrides: Any) -> ClockDomain:
    fields: dict[str, Any] = DOMAIN_KWARGS.copy()
    fields.update(overrides)
    return ClockDomain(**fields)


class ClockModelTests(unittest.TestCase):
    def test_clock_domain_rejects_boolean_resolution(self) -> None:
        with self.assertRaises(ContractShapeError) as caught:
            _domain(**({"resolution": True}))
        self.assertEqual("/resolution", caught.exception.path)
        self.assertEqual(1, ClockDomain(**DOMAIN_KWARGS).resolution)

    def test_kinds_units_and_preserved_metadata(self) -> None:
        for kind in ("host_monotonic", "source", "simulator"):
            for unit in ("nanosecond", "microsecond", "millisecond", "tick"):
                with self.subTest(kind=kind, unit=unit):
                    extra = {"tick_period": {"numerator_ns": 1, "denominator": 3}} if unit == "tick" else {}
                    value = _domain(**(dict(kind=kind, unit=unit, resolution=2**63 - 1) | extra))
                    self.assertIs(type(value.kind), ClockKind)
                    self.assertIs(type(value.unit), ClockUnit)
                    self.assertEqual(
                        (kind, unit, 2**63 - 1, DOMAIN_ID, PRODUCER_ID),
                        (value.kind, value.unit, value.resolution, value.clock_domain_id, value.producer_instance_id),
                    )
                    self.assertEqual("test process origin", value.origin)
                    self.assertEqual("test process", value.scope)

    def test_domain_rejects_invalid_fields_with_precise_paths(self) -> None:
        cases = [
            ("resolution", 0, ContractValidationError),
            ("resolution", -1, ContractValidationError),
            ("resolution", 1.0, ContractShapeError),
            ("resolution", 2**63, CanonicalJSONError),
            ("clock_domain_id", "not-a-uuid", ContractValidationError),
            ("producer_instance_id", "not-a-uuid", ContractValidationError),
            ("kind", "wall_clock", ContractShapeError),
            ("unit", "second", ContractShapeError),
        ]
        for name in ("origin", "scope"):
            cases.extend(
                (name, value, error)
                for value, error in (
                    ("", ContractValidationError),
                    ("x" * 513, ContractValidationError),
                    ("e\u0301", CanonicalJSONError),
                    ("\ud800", CanonicalJSONError),
                    (None, CanonicalJSONError),
                )
            )
        for name, value, error in cases:
            with self.subTest(name=name, value=repr(value)), self.assertRaises(error) as caught:
                _domain(**({name: value}))
            self.assertEqual("/" + name, caught.exception.path)
        for count in (1, 512):
            self.assertEqual("é" * count, _domain(**({"origin": "é" * count})).origin)

    def test_unrelated_enum_is_not_coerced(self) -> None:
        class Unrelated(StrEnum):
            HOST = "host_monotonic"

        with self.assertRaises(ContractShapeError):
            _domain(**({"kind": Unrelated.HOST}))

    def test_tick_period_is_copied_and_immutable(self) -> None:
        original = {"numerator_ns": 1, "denominator": 3}
        value = _domain(**({"unit": "tick", "tick_period": original}))
        original["denominator"] = 9
        self.assertEqual({"numerator_ns": 1, "denominator": 3}, value.tick_period)
        with self.assertRaises(TypeError):
            value.tick_period["denominator"] = 7  # ty: ignore[invalid-assignment]

    def test_tick_period_exact_shape_and_positive_reduced_domain(self) -> None:
        cases = [
            ({"numerator_ns": 1}, ContractShapeError, "/tick_period/denominator"),
            ({"numerator_ns": 1, "denominator": 3, "extra": 1}, ContractShapeError, "/tick_period/extra"),
            ({"numerator_ns": True, "denominator": 3}, ContractShapeError, "/tick_period/numerator_ns"),
            ({"numerator_ns": 0, "denominator": 3}, ContractValidationError, "/tick_period/numerator_ns"),
            ({"numerator_ns": 1, "denominator": -1}, ContractValidationError, "/tick_period/denominator"),
            ({"numerator_ns": 1, "denominator": 2**63}, CanonicalJSONError, "/tick_period/denominator"),
            ({"numerator_ns": 2, "denominator": 6}, ContractValidationError, "/tick_period"),
            (None, CanonicalJSONError, "/tick_period"),
        ]
        for period, error, path in cases:
            with self.subTest(period=period), self.assertRaises(error) as caught:
                _domain(**({"unit": "tick", "tick_period": period}))
            self.assertEqual(path, caught.exception.path)
        for extra in ({"unit": "tick"}, {"tick_period": {"numerator_ns": 1, "denominator": 3}}):
            with self.assertRaises(ContractValidationError) as caught:
                _domain(**(extra))
            self.assertEqual("/tick_period", caught.exception.path)

    def test_readings_preserve_signed_endpoints_without_coercion(self) -> None:
        for number in (-(2**63), -1, 0, 2**63 - 1):
            self.assertEqual(number, ClockReading(clock_domain_id=DOMAIN_ID, value=number).value)
        for value, error in (
            (True, ContractShapeError),
            (1.0, ContractShapeError),
            ("1", ContractShapeError),
            (2**63, CanonicalJSONError),
            (-(2**63) - 1, CanonicalJSONError),
        ):
            with self.subTest(value=value), self.assertRaises(error) as caught:
                ClockReading(clock_domain_id=DOMAIN_ID, value=value)  # ty: ignore[invalid-argument-type]
            self.assertEqual("/value", caught.exception.path)

    def test_shape_precedes_domain_and_semantics(self) -> None:
        with self.assertRaises(ContractShapeError) as caught:
            _domain(**({"clock_domain_id": "bad", "resolution": True}))
        self.assertEqual("/resolution", caught.exception.path)
        with self.assertRaises(CanonicalJSONError) as caught:
            _domain(**({"resolution": 0, "scope": "e\u0301"}))
        self.assertEqual("/scope", caught.exception.path)

    def test_models_are_keyword_only_frozen_and_slotted(self) -> None:
        value = ClockDomain(**DOMAIN_KWARGS)
        self.assertFalse(hasattr(value, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            value.resolution = 2  # ty: ignore[invalid-assignment]
        with self.assertRaises((AttributeError, TypeError)):
            value.extra = 1  # ty: ignore[invalid-assignment]
        with self.assertRaises(TypeError):
            ClockReading(DOMAIN_ID, 1)  # ty: ignore[too-many-positional-arguments, missing-argument]
