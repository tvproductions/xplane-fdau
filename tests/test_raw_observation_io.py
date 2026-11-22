"""Test the four public raw-observation interchange functions and failure tiers."""

from __future__ import annotations

import json
import unittest
from contextlib import ExitStack
from dataclasses import replace
from hashlib import sha256
from io import BytesIO, StringIO
from typing import Any, BinaryIO, cast
from unittest.mock import Mock, patch

from xplane_fdau.acquisition import (
    RawObservation,
    RawValueEvidence,
    dump_raw_observation_v1,
    dumps_raw_observation_v1,
    load_raw_observation_v1,
    loads_raw_observation_v1,
)
from xplane_fdau.contracts import (
    AdapterIdentity,
    CanonicalJSONError,
    ClockAnchor,
    ClockDomain,
    ClockReading,
    ContractHashError,
    ContractParseError,
    ContractShapeError,
    ContractValidationError,
    FDAUContractError,
    InlineValue,
    ObservationTiming,
    PayloadReference,
    ProducerIdentity,
    ProviderIdentity,
    SourceTiming,
    UnsupportedContractVersionError,
    UtcInstant,
)
from xplane_fdau.measurements import ApplicabilitySelector

from .raw_observation_support import CONTENT_HASH, DOCUMENT_HASH, FAMILY, independent_bytes, raw_observation_wire, uid
from .test_raw_observation import minimum_timing, payload_reference, raw_record


def signed(document: dict[str, object]) -> bytes:
    body = {k: v for k, v in document.items() if k != "content_hash"}
    body["content_hash"] = sha256(independent_bytes(body)).hexdigest()
    return independent_bytes(body)


class _Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.closed = False

    def read(self) -> bytes:
        return self.data

    def close(self) -> None:
        self.closed = True


class _ShortWriter:
    def __init__(self) -> None:
        self.received = bytearray()
        self.closed = False

    def write(self, data: memoryview) -> int:
        self.received.extend(data[:1])
        return 1

    def close(self) -> None:
        self.closed = True


class _BadWriter:
    def __init__(self, result: object) -> None:
        self.result = result

    def write(self, data: memoryview) -> object:
        if isinstance(self.result, OSError):
            raise self.result
        return self.result


class RawObservationIOTests(unittest.TestCase):
    def test_round_trip_exact_raw_and_timing_evidence(self) -> None:
        minimum = raw_record()
        expected = independent_bytes(raw_observation_wire())
        self.assertEqual(CONTENT_HASH, minimum.content_hash)
        self.assertEqual(DOCUMENT_HASH, sha256(expected).hexdigest())
        self.assertEqual(expected, dumps_raw_observation_v1(minimum))
        self.assertEqual(minimum, loads_raw_observation_v1(json.dumps(raw_observation_wire(), indent=2)))
        self.assertNotIn(b'"source_timing"', expected)

        clock = minimum_timing()
        source_clock = replace(clock.receipt_clock, kind="simulator", clock_domain_id=uid(7))
        timing = replace(
            clock,
            source_timing=SourceTiming(clock=source_clock, reading=ClockReading(clock_domain_id=uid(7), value=-321), source_sequence=0),
            receipt_anchor=ClockAnchor(monotonic_reading=clock.receipt_reading, utc=clock.receipt_utc, uncertainty_ns=14),
            xplane_cycle=0,
            simulator_flight_time_ns=-11,
            acquisition_phase="after_flight_model",
            paused=False,
            replay_state="seeking",
            time_speed=-1.25,
        )
        inline = RawValueEvidence(kind="inline", value=InlineValue(representation="integer", value=-22))
        payload = RawValueEvidence(kind="payload", payload=payload_reference("missing"))
        for status, representation, evidence in (
            ("ok", "integer", inline),
            ("ok", "referenced_bytes", payload),
            ("type_mismatch", "integer", inline),
            ("provider_degraded", "referenced_bytes", payload),
            *(
                (status, "integer", RawValueEvidence(kind="absent", reason=reason))
                for reason in ("unavailable", "orphaned", "read_error")
                for status in (reason, "provider_degraded")
            ),
        ):
            with self.subTest(status=status, evidence=evidence.kind):
                diagnostic = {"diagnostic": "adapter diagnostic"} if status in {"type_mismatch", "provider_degraded", "read_error"} else {}
                observation = raw_record(timing=timing, observed_representation=representation, value_evidence=evidence, status=status, **diagnostic)
                stream = BytesIO()
                dump_raw_observation_v1(observation, stream)
                self.assertFalse(stream.closed)
                self.assertEqual(stream.getvalue(), dumps_raw_observation_v1(observation))
                self.assertEqual(observation, loads_raw_observation_v1(stream.getvalue()))
                stream.seek(0)
                self.assertEqual(observation, load_raw_observation_v1(stream))
                self.assertFalse(stream.closed)
                self.assertEqual(observation, loads_raw_observation_v1(dumps_raw_observation_v1(observation)))

    def test_absent_value_preserves_known_type_and_shape(self) -> None:
        raw = dict(
            raw_observation_wire(),
            status="unavailable",
            observed_shape=[3],
            observed_representation="variable_array",
            observed_element_representation="integer",
            value_evidence={"kind": "absent", "reason": "unavailable"},
        )
        encoded = signed(raw)
        self.assertEqual((3,), loads_raw_observation_v1(encoded).observed_shape)
        self.assertEqual(encoded, dumps_raw_observation_v1(loads_raw_observation_v1(encoded)))
        for name in ("observed_shape", "observed_representation"):
            invalid = raw.copy()
            del invalid[name]
            self.error(ContractShapeError, "/" + name, independent_bytes(invalid))

    def test_binary_stream_ownership_and_write_progress(self) -> None:
        data = independent_bytes(raw_observation_wire())
        reader = _Reader(data)
        self.assertEqual(raw_record(), load_raw_observation_v1(cast(BinaryIO, reader)))
        self.assertFalse(reader.closed)
        writer = _ShortWriter()
        dump_raw_observation_v1(raw_record(), cast(BinaryIO, writer))
        self.assertFalse(writer.closed)
        self.assertEqual(data, bytes(writer.received))
        for result, error_class in ((None, BlockingIOError), (0, BlockingIOError), (-1, OSError), (len(data) + 1, OSError), (True, OSError), (False, OSError)):
            with self.subTest(result=result), self.assertRaises(error_class) as caught:
                dump_raw_observation_v1(raw_record(), cast(BinaryIO, _BadWriter(result)))
            self.assertIs(error_class, type(caught.exception))
        io_failure = OSError("device error")
        with self.assertRaises(OSError) as caught:
            dump_raw_observation_v1(raw_record(), cast(BinaryIO, _BadWriter(io_failure)))
        self.assertIs(io_failure, caught.exception)
        with self.assertRaises(OSError) as read_failure:
            load_raw_observation_v1(Mock(read=Mock(side_effect=io_failure)))
        self.assertIs(io_failure, read_failure.exception)
        with self.assertRaises(TypeError):
            dump_raw_observation_v1(raw_record(), cast(Any, StringIO()))
        with self.assertRaises(TypeError):
            load_raw_observation_v1(cast(Any, StringIO(data.decode("utf-8"))))
        for value in ("raw.json", data):
            with self.assertRaises(TypeError):
                load_raw_observation_v1(cast(BinaryIO, value))
        with self.assertRaises(ContractShapeError):
            dumps_raw_observation_v1(cast(Any, {}))
        with self.assertRaises(TypeError):
            loads_raw_observation_v1(cast(Any, bytearray(data)))

    def error(self, error_class: type[FDAUContractError], pointer: str, data: str | bytes) -> FDAUContractError:
        with self.assertRaises(error_class) as caught:
            loads_raw_observation_v1(data, source="synthetic capture")
        error = caught.exception
        self.assertIs(error_class, type(error))
        self.assertEqual(pointer, error.path)
        self.assertEqual("synthetic capture", error.source)
        self.assertEqual(FAMILY, error.contract_family)
        if error_class is not ContractParseError:
            self.assertEqual(uid(1), error.identity)
            self.assertIsNone(error.line)
            self.assertIsNone(error.column)
        return error

    def test_complete_document_precedence_and_constructor_barrier(self) -> None:
        raw = raw_observation_wire()
        overflow = dict(raw, sequence=1 << 63)
        duplicate = json.dumps(overflow).replace('"value": false', '"value": false, "value": true')
        with ExitStack() as stack:
            constructors = [
                stack.enter_context(patch.object(model, "__init__", autospec=True, side_effect=AssertionError("premature construction")))
                for model in (
                    RawObservation,
                    RawValueEvidence,
                    InlineValue,
                    PayloadReference,
                    ProducerIdentity,
                    ProviderIdentity,
                    AdapterIdentity,
                    ApplicabilitySelector,
                    ObservationTiming,
                    ClockDomain,
                    ClockReading,
                    SourceTiming,
                    ClockAnchor,
                    UtcInstant,
                )
            ]
            self.error(ContractParseError, "/value_evidence/value/value", duplicate)
            self.error(ContractParseError, "", b"\xff")
            self.error(ContractParseError, "", b"\xef\xbb\xbf" + independent_bytes(raw))
            for field, value in (("schema_version", 2), ("contract_family", "https://example.invalid/raw")):
                self.error(UnsupportedContractVersionError, "/" + field, json.dumps(dict(raw, status=2, **{field: value})))
            self.error(ContractShapeError, "/schema_version", json.dumps(dict(raw, schema_version=1.0)))
            self.error(ContractShapeError, "/status", json.dumps(dict(overflow, resource_id="e\u0301", status=3)))
            self.error(CanonicalJSONError, "/sequence", json.dumps(dict(overflow, content_hash="0" * 64)))
            self.error(ContractHashError, "/content_hash", json.dumps(dict(raw, resource_kind="not-qualified", content_hash="0" * 64)))
            self.error(ContractValidationError, "/resource_kind", json.dumps(dict(raw, resource_kind="not-qualified", content_hash="bad")))
            self.error(ContractShapeError, "/observed_element_representation", json.dumps(dict(raw, observed_representation="variable_array")))
            self.error(ContractShapeError, "/observed_element_representation", json.dumps(dict(raw, observed_element_representation="integer")))
            self.error(ContractShapeError, "/sequence", json.dumps(dict(raw, sequence=True)))
            self.error(ContractShapeError, "/bad~1key~0", json.dumps(dict(raw, **{"bad/key~": False})))

            timing: dict[str, Any] = cast(dict[str, Any], raw["timing"])
            bad_receipt = dict(timing, receipt_clock=dict(timing["receipt_clock"], resolution=True))
            for evidence, pointer, observation_representation in (
                ({"kind": "inline", "value": {"representation": None, "value": False}}, "/value_evidence/value/representation", "boolean"),
                (
                    {
                        "kind": "payload",
                        "payload": {
                            "media_type": "application/octet-stream",
                            "byte_length": 0,
                            "sha256": "f" * 64,
                            "storage_role": "test.raw",
                            "retention_status": None,
                        },
                    },
                    "/value_evidence/payload/retention_status",
                    "referenced_bytes",
                ),
            ):
                invalid = dict(raw, value_evidence=evidence, observed_representation=observation_representation)
                self.error(CanonicalJSONError, pointer, json.dumps(invalid))
                self.error(ContractShapeError, "/timing/receipt_clock/resolution", json.dumps(dict(invalid, timing=bad_receipt)))

            for constructor in constructors:
                constructor.assert_not_called()

    def test_semantic_error_context_and_inline_diagnostics(self) -> None:
        original = raw_observation_wire()
        forbidden = "private-inline-payload-marker"
        raw = dict(original, observed_representation="integer", value_evidence={"kind": "inline", "value": {"representation": "string", "value": forbidden}})
        error = self.error(ContractValidationError, "/value_evidence/value/representation", signed(raw))
        self.assertNotIn(forbidden, str(error))
        with self.assertRaises(ContractValidationError) as constructed:
            raw_record(
                observed_representation="integer", value_evidence=RawValueEvidence(kind="inline", value=InlineValue(representation="string", value=forbidden))
            )
        self.assertEqual(error.path, constructed.exception.path)
        timing = cast(dict[str, Any], original["timing"])
        wrong = dict(timing, receipt_clock=dict(timing["receipt_clock"], producer_instance_id=uid(8)), receipt_utc="not-a-timestamp")
        self.error(ContractValidationError, "/timing/receipt_clock/producer_instance_id", signed(dict(original, timing=wrong)))

    def test_null_inline_tags_still_require_possible_value_shapes(self) -> None:
        raw = raw_observation_wire()
        cases = (
            (None, {}, ContractShapeError, "/value"),
            (None, [False, {}], ContractShapeError, "/value/1"),
            (None, [False, []], ContractShapeError, "/value/1"),
            (None, False, CanonicalJSONError, "/representation"),
            ("variable_array", [{"representation": {}}], ContractShapeError, "/value/0"),
            ("variable_array", [1], CanonicalJSONError, "/element_representation"),
        )
        for representation, value, error, pointer in cases:
            with self.subTest(representation=representation, pointer=pointer):
                inline = {"representation": representation, "value": value}
                if representation is not None:
                    inline["element_representation"] = None
                invalid = dict(raw, value_evidence={"kind": "inline", "value": inline})
                self.error(error, "/value_evidence/value" + pointer, json.dumps(invalid))

    def test_competing_nested_semantics_follow_property_order(self) -> None:
        raw = raw_observation_wire()
        inline = {"kind": "inline", "value": {"representation": "enumeration", "value": "invalid-code"}}
        payload = {
            "kind": "payload",
            "payload": {
                "media_type": "invalid",
                "byte_length": 0,
                "sha256": "f" * 64,
                "storage_role": "test.raw",
                "retention_status": "retained",
            },
        }
        context = [{"class_id": "test.z", "value": "last"}, {"class_id": "test.a", "value": ""}]
        for pointer, invalid in (
            ("/value_evidence/value/representation", dict(raw, value_evidence=inline)),
            ("/value_evidence/kind", dict(raw, value_evidence=payload)),
            ("/applicability_context/1/class_id", dict(raw, applicability_context=context)),
        ):
            with self.subTest(pointer=pointer):
                self.error(ContractValidationError, pointer, signed(invalid))

    def test_source_domain_cannot_alias_receipt_domain(self) -> None:
        raw = raw_observation_wire()
        timing = cast(dict[str, Any], raw["timing"])
        source = {
            "clock": dict(timing["receipt_clock"], kind="source", unit="millisecond"),
            "reading": {"clock_domain_id": uid(6), "value": 100},
        }
        invalid = dict(raw, timing=dict(timing, source_timing=source))
        pointer = "/timing/source_timing/clock/clock_domain_id"
        with patch.object(RawObservation, "__init__", side_effect=AssertionError("premature construction")):
            self.error(ContractValidationError, pointer, signed(invalid))

        receipt = minimum_timing()
        source_clock = replace(receipt.receipt_clock, kind="source", unit="millisecond")
        source_timing = SourceTiming(clock=source_clock, reading=ClockReading(clock_domain_id=uid(6), value=100))
        with self.assertRaises(ContractValidationError) as caught:
            raw_record(timing=replace(receipt, source_timing=source_timing))
        self.assertEqual(pointer, caught.exception.path)

    def test_constructor_envelope_follows_shape_and_domain_checks(self) -> None:
        for field, value in (("contract_family", "unsupported"), ("schema_version", 2)):
            arguments = {field: value}
            with self.subTest(field=field):
                with self.assertRaises(ContractShapeError) as shape:
                    raw_record(sequence=True, **arguments)
                self.assertEqual("/sequence", shape.exception.path)
                with self.assertRaises(CanonicalJSONError) as domain:
                    raw_record(resource_id="e\u0301", **arguments)
                self.assertEqual("/resource_id", domain.exception.path)
                with self.assertRaises(ContractValidationError) as semantic:
                    raw_record(**arguments)
                self.assertEqual("/" + field, semantic.exception.path)

    def test_numeric_tokens_remain_distinct_from_decoded_numbers(self) -> None:
        raw = dict(
            raw_observation_wire(), observed_representation="real", value_evidence={"kind": "inline", "value": {"representation": "real", "value": 1.25}}
        )
        baseline = json.dumps(raw)
        for spelling, error_class in (("1", ContractShapeError), ("true", ContractShapeError), ("1e999", CanonicalJSONError), ("1e-999", CanonicalJSONError)):
            with self.subTest(spelling=spelling):
                self.error(error_class, "/value_evidence/value/value", baseline.replace("1.25", spelling))
