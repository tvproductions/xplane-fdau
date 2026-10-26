"""Strict nested timing readers and omission/error-precedence controls."""

from __future__ import annotations

import json
import unittest
from typing import Any

from tests.test_contract_timing import DOMAIN_ID, DOMAIN_KWARGS, OTHER_ID, PRODUCER_ID, _domain
from xplane_fdau.contracts import _timing_io as readers
from xplane_fdau.contracts import canonical_bytes, timing
from xplane_fdau.contracts._json_parse import _parse_json_document
from xplane_fdau.contracts._timing_validation import _validate_observation_producer
from xplane_fdau.contracts.errors import CanonicalJSONError, ContractParseError, ContractShapeError, ContractValidationError

UTC_TEXT = "2026-10-26T12:34:56.123456789Z"


def _wire() -> dict[str, Any]:
    return {"receipt_clock": DOMAIN_KWARGS.copy(), "receipt_reading": {"clock_domain_id": DOMAIN_ID, "value": 7}, "receipt_utc": UTC_TEXT}


def _observation(**extra: Any) -> timing.ObservationTiming:
    fields: dict[str, Any] = {
        "receipt_clock": _domain(),
        "receipt_reading": timing.ClockReading(clock_domain_id=DOMAIN_ID, value=7),
        "receipt_utc": timing.UtcInstant(value=UTC_TEXT),
    }
    fields.update(extra)
    return timing.ObservationTiming(**fields)


def _read(fields: dict[str, Any]) -> timing.ObservationTiming:
    return readers._observation_timing_from_wire(_parse_json_document(json.dumps(fields)), source="timing.json")


class TimingReaderTests(unittest.TestCase):
    def test_earlier_cross_field_semantics_precede_later_counter_failure(self) -> None:
        with self.assertRaises(ContractValidationError) as caught:
            _read(_wire() | {"receipt_clock": DOMAIN_KWARGS | {"kind": "source"}, "xplane_cycle": -1})
        self.assertEqual("/receipt_clock/kind", caught.exception.path)
        source = {"clock": DOMAIN_KWARGS, "reading": {"clock_domain_id": DOMAIN_ID, "value": 1}, "source_sequence": -1}
        with self.assertRaises(ContractValidationError) as caught:
            readers._source_timing_from_wire(_parse_json_document(json.dumps(source)))
        self.assertEqual("/clock/kind", caught.exception.path)

    def test_minimal_receipt_round_trips_without_invention(self) -> None:
        value = _observation()
        wire = canonical_bytes(value)
        self.assertEqual({"receipt_clock", "receipt_reading", "receipt_utc"}, set(json.loads(wire)))
        loaded = readers._observation_timing_from_wire(_parse_json_document(wire), source="timing.json")
        self.assertEqual(value, loaded)
        self.assertEqual(wire, canonical_bytes(loaded))

    def test_full_timing_round_trip_preserves_all_evidence(self) -> None:
        receipt = timing.ClockReading(clock_domain_id=DOMAIN_ID, value=7)
        for kind in ("source", "simulator"):
            with self.subTest(kind=kind):
                source = timing.SourceTiming(
                    clock=_domain(clock_domain_id=OTHER_ID, kind=kind, unit="tick", tick_period={"numerator_ns": 1, "denominator": 3}),
                    reading=timing.ClockReading(clock_domain_id=OTHER_ID, value=-3),
                    source_sequence=2**63 - 1,
                )
                value = _observation(
                    source_timing=source,
                    receipt_anchor=timing.ClockAnchor(monotonic_reading=receipt, utc=timing.UtcInstant(value=UTC_TEXT), uncertainty_ns=9),
                    xplane_cycle=2**63 - 1,
                    simulator_flight_time_ns=-(2**63),
                    acquisition_phase="after_flight_model",
                    paused=True,
                    replay_state="seeking",
                    time_speed=-2.0,
                )
                loaded = readers._observation_timing_from_wire(_parse_json_document(canonical_bytes(value)))
                self.assertEqual(value, loaded)
                self.assertEqual("seeking", loaded.replay_state)
                self.assertIs(type(loaded.replay_state), timing.ReplayState)
                self.assertEqual(-2.0, loaded.time_speed)
                self.assertEqual(9, loaded.receipt_anchor.uncertainty_ns)  # ty: ignore[unresolved-attribute]
                self.assertEqual(canonical_bytes(value), canonical_bytes(loaded))

    def test_optional_fields_never_infer_each_other(self) -> None:
        cases = {"paused": True, "replay_state": "replay", "time_speed": -1.0, "xplane_cycle": 0, "simulator_flight_time_ns": 0, "acquisition_phase": "unknown"}
        for name, item in cases.items():
            with self.subTest(name=name):
                value = _observation(**{name: item})
                wire = json.loads(canonical_bytes(value))
                self.assertEqual({"receipt_clock", "receipt_reading", "receipt_utc", name}, set(wire))
                self.assertEqual(item, wire[name])
                self.assertEqual(value, _read(wire))
        for speed in (-1.0, -0.0, 0.0, 5e-324, 1.7976931348623157e308):
            value = _observation(time_speed=speed)
            self.assertEqual(speed, _read(json.loads(canonical_bytes(value))).time_speed)
        self.assertIn(b'"time_speed":0.0', canonical_bytes(_observation(time_speed=-0.0)))
        for phase in ("before_flight_model", "after_flight_model", "unknown"):
            self.assertEqual(phase, _observation(acquisition_phase=phase).acquisition_phase)
        for replay in ("live", "replay", "seeking", "unknown"):
            self.assertEqual(replay, _observation(replay_state=replay).replay_state)

    def test_invalid_optional_types_domains_and_semantics(self) -> None:
        cases = (
            ("xplane_cycle", True, ContractShapeError),
            ("xplane_cycle", -1, ContractValidationError),
            ("xplane_cycle", 2**63, CanonicalJSONError),
            ("simulator_flight_time_ns", 1.0, ContractShapeError),
            ("simulator_flight_time_ns", 2**63, CanonicalJSONError),
            ("paused", 1, ContractShapeError),
            ("replay_state", "future", ContractShapeError),
            ("acquisition_phase", "future", ContractShapeError),
            ("time_speed", 1, ContractShapeError),
            ("time_speed", True, ContractShapeError),
            ("time_speed", float("nan"), CanonicalJSONError),
            ("time_speed", float("inf"), CanonicalJSONError),
        )
        for name, item, error in cases:
            with self.subTest(name=name, item=item), self.assertRaises(error) as caught:
                _observation(**{name: item})
            self.assertEqual("/" + name, caught.exception.path)

    def test_null_is_prohibited_for_every_optional_field(self) -> None:
        for name in (
            "source_timing",
            "receipt_anchor",
            "xplane_cycle",
            "simulator_flight_time_ns",
            "acquisition_phase",
            "paused",
            "replay_state",
            "time_speed",
        ):
            for parsed in (True, False):
                with self.subTest(name=name, parsed=parsed), self.assertRaises(CanonicalJSONError) as caught:
                    _read(_wire() | {name: None}) if parsed else _observation(**{name: None})
                self.assertEqual("/" + name, caught.exception.path)
        source = {"clock": DOMAIN_KWARGS | {"kind": "source"}, "reading": {"clock_domain_id": DOMAIN_ID, "value": 0}, "source_sequence": None}
        with self.assertRaises(CanonicalJSONError) as caught:
            _read(_wire() | {"source_timing": source})
        self.assertEqual("/source_timing/source_sequence", caught.exception.path)

    def test_clock_kind_identity_anchor_and_producer_context(self) -> None:
        cases = [
            (_wire() | {"receipt_clock": DOMAIN_KWARGS | {"kind": "source"}}, "/receipt_clock/kind"),
            (_wire() | {"receipt_reading": {"clock_domain_id": OTHER_ID, "value": 7}}, "/receipt_reading/clock_domain_id"),
        ]
        anchor = {"monotonic_reading": {"clock_domain_id": DOMAIN_ID, "value": 8}, "utc": UTC_TEXT, "uncertainty_ns": 0}
        cases.append((_wire() | {"receipt_anchor": anchor}, "/receipt_anchor/monotonic_reading/value"))
        cases.append(
            (
                _wire()
                | {"receipt_anchor": anchor | {"monotonic_reading": {"clock_domain_id": DOMAIN_ID, "value": 7}, "utc": "2026-10-26T12:34:56.123456788Z"}},
                "/receipt_anchor/utc",
            )
        )
        for fields, path in cases:
            with self.subTest(path=path), self.assertRaises(ContractValidationError) as caught:
                _read(fields)
            self.assertEqual(path, caught.exception.path)
        _validate_observation_producer(_observation(), PRODUCER_ID)
        with self.assertRaises(ContractValidationError) as caught:
            _validate_observation_producer(_observation(), OTHER_ID, path="/timing")
        self.assertEqual("/timing/receipt_clock/producer_instance_id", caught.exception.path)
        for kind, reading_id, path in (("host_monotonic", DOMAIN_ID, "/clock/kind"), ("source", OTHER_ID, "/reading/clock_domain_id")):
            with self.subTest(kind=kind), self.assertRaises(ContractValidationError) as caught:
                timing.SourceTiming(clock=_domain(kind=kind), reading=timing.ClockReading(clock_domain_id=reading_id, value=1))
            self.assertEqual(path, caught.exception.path)

    def test_nested_shapes_outrank_domains_and_semantics(self) -> None:
        cases = [
            (_wire() | {"receipt_clock": DOMAIN_KWARGS | {"clock_domain_id": "bad"}, "paused": 1}, ContractShapeError, "/paused"),
            (
                _wire() | {"receipt_clock": DOMAIN_KWARGS | {"resolution": 0}, "simulator_flight_time_ns": 2**63},
                CanonicalJSONError,
                "/simulator_flight_time_ns",
            ),
            (
                _wire() | {"receipt_clock": DOMAIN_KWARGS | {"unit": "tick", "tick_period": {"numerator_ns": True, "denominator": 0}}},
                ContractShapeError,
                "/receipt_clock/tick_period/numerator_ns",
            ),
        ]
        for fields, error, path in cases:
            with self.subTest(path=path), self.assertRaises(error) as caught:
                _read(fields)
            self.assertEqual(path, caught.exception.path)
            self.assertEqual("timing.json", caught.exception.source)
            self.assertIsNone(caught.exception.line)
            self.assertIsNone(caught.exception.column)

    def test_all_private_readers_keep_enclosing_pointer_and_token_types(self) -> None:
        cases = [
            (readers._clock_domain_from_wire, DOMAIN_KWARGS, timing.ClockDomain),
            (readers._clock_reading_from_wire, {"clock_domain_id": DOMAIN_ID, "value": -1}, timing.ClockReading),
            (readers._utc_instant_from_wire, UTC_TEXT, timing.UtcInstant),
            (
                readers._clock_anchor_from_wire,
                {"monotonic_reading": {"clock_domain_id": DOMAIN_ID, "value": 1}, "utc": UTC_TEXT, "uncertainty_ns": 0},
                timing.ClockAnchor,
            ),
            (
                readers._source_timing_from_wire,
                {"clock": DOMAIN_KWARGS | {"kind": "source"}, "reading": {"clock_domain_id": DOMAIN_ID, "value": 1}},
                timing.SourceTiming,
            ),
            (readers._observation_timing_from_wire, _wire(), timing.ObservationTiming),
        ]
        for reader, fields, expected in cases:
            with self.subTest(reader=reader.__name__):
                self.assertIs(type(reader(_parse_json_document(json.dumps(fields)))), expected)
                with self.assertRaises(ContractShapeError) as caught:
                    reader([], path="/outer", source="context")
                self.assertEqual("/outer", caught.exception.path)
                self.assertEqual("context", caught.exception.source)
        for name, token in (("xplane_cycle", "1.0"), ("time_speed", "1"), ("time_speed", "1e999")):
            text = json.dumps(_wire())[:-1] + ',"' + name + '":' + token + "}"
            error = CanonicalJSONError if token == "1e999" else ContractShapeError
            with self.subTest(name=name, token=token), self.assertRaises(error) as caught:
                readers._observation_timing_from_wire(_parse_json_document(text))
            self.assertEqual("/" + name, caught.exception.path)

    def test_missing_unknown_and_duplicate_properties_fail_closed(self) -> None:
        fields = _wire()
        del fields["receipt_reading"]
        with self.assertRaises(ContractShapeError) as caught:
            _read(fields)
        self.assertEqual("/receipt_reading", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            _read(_wire() | {"bad/~": 1})
        self.assertEqual("/bad~1~0", caught.exception.path)
        text = json.dumps(_wire())[:-1] + ',"paused":true,"paused":false}'
        with self.assertRaises(ContractParseError):
            readers._observation_timing_from_wire(_parse_json_document(text, source="duplicate.json"))
        with self.assertRaises(ContractShapeError):
            _observation(receipt_clock=DOMAIN_KWARGS)
