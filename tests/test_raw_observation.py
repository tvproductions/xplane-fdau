"""Contract tests for immutable raw records and evidence."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace
from typing import Any, cast

from xplane_fdau.acquisition import ObservationStatus, RawAbsentReason, RawObservation, RawValueEvidence
from xplane_fdau.contracts import (
    AdapterIdentity,
    ClockAnchor,
    ClockDomain,
    ClockReading,
    ContractShapeError,
    ContractValidationError,
    InlineValue,
    ObservationTiming,
    PayloadReference,
    ProducerIdentity,
    ProviderIdentity,
    SourceTiming,
    UtcInstant,
    canonical_bytes,
)
from xplane_fdau.measurements import ApplicabilitySelector

from .raw_observation_support import CONTENT_HASH, FAMILY, uid


def minimum_timing() -> ObservationTiming:
    clock = ClockDomain(
        clock_domain_id=uid(6), kind="host_monotonic", unit="nanosecond", resolution=1, origin="test", scope="test", producer_instance_id=uid(2)
    )
    return ObservationTiming(
        receipt_clock=clock,
        receipt_reading=ClockReading(clock_domain_id=uid(6), value=0),
        receipt_utc=UtcInstant(value="2026-11-22T00:00:00.123456789Z"),
    )


def raw_record(**changes: Any) -> RawObservation:
    params: dict[str, Any] = {
        "contract_family": FAMILY,
        "schema_version": 1,
        "observation_id": uid(1),
        "producer": ProducerIdentity(implementation_id="test.producer", implementation_version="1", producer_instance_id=uid(2)),
        "provider": ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
        "adapter": AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
        "session_id": uid(3),
        "stream_id": uid(4),
        "epoch_id": uid(5),
        "sequence": 0,
        "connection_generation": 0,
        "source_generation": 0,
        "resource_kind": "test.resource",
        "resource_id": "test/source",
        "observed_shape": (),
        "observed_representation": "boolean",
        "value_evidence": RawValueEvidence(kind="inline", value=InlineValue(representation="boolean", value=False)),
        "timing": minimum_timing(),
        "applicability_context": (),
        "status": ObservationStatus.OK,
        "limitations": (),
    }
    params.update(changes)
    return RawObservation(**params)


def payload_reference(retention_status: str = "unverified") -> PayloadReference:
    return PayloadReference(media_type="application/octet-stream", byte_length=0, sha256="f" * 64, storage_role="test.raw", retention_status=retention_status)


class RawObservationTests(unittest.TestCase):
    def test_raw_observation_freezes_inputs_and_preserves_identity(self) -> None:
        self.assertEqual(CONTENT_HASH, raw_record().content_hash)
        shape: list[int] = []
        limitations = ["z", "a"]
        context = [ApplicabilitySelector(class_id="test.aircraft", value="example")]
        selection: dict[str, object] = {"kind": "index", "index": 2}
        value = raw_record(observed_shape=shape, limitations=limitations, applicability_context=context, resource_selection=selection)
        digest = value.content_hash
        shape.append(1)
        limitations.reverse()
        context.clear()
        selection["index"] = 0
        self.assertEqual((), value.observed_shape)
        self.assertEqual(("z", "a"), value.limitations)
        self.assertEqual("test.aircraft", value.applicability_context[0].class_id)
        self.assertEqual({"kind": "index", "index": 2}, value.resource_selection)
        self.assertEqual(digest, value.content_hash)
        with self.assertRaises(FrozenInstanceError):
            object_set = cast(Any, value)
            object_set.observation_id = uid(12)
        with self.assertRaises(TypeError):
            raw_record(content_hash="0" * 64)
        with self.assertRaises(TypeError):
            cast(Any, RawObservation)(uid(1))
        with self.assertRaises(ContractShapeError) as bad:
            raw_record(provider={"provider_family_id": "test.provider", "provider_version": "1"})
        self.assertEqual("/provider", bad.exception.path)

    def test_observed_type_and_shape_match_inline_value(self) -> None:
        scalars = {"boolean": False, "integer": -1, "real": 0.25, "string": "source", "enumeration": "test.unmapped"}
        vectors: list[tuple[str, list[object], dict[str, Any]]] = [("vector", [0.25], {})]
        for tag in ("fixed_array", "variable_array"):
            vectors.extend((tag, [value], {"element_representation": scalar}) for scalar, value in scalars.items())
            vectors.append((tag, [], {"element_representation": "integer"}))
        cases: list[tuple[str, object, dict[str, Any], tuple[int, ...]]] = [(tag, value, {}, ()) for tag, value in scalars.items()]
        cases.extend((tag, value, options, (len(value),)) for tag, value, options in vectors)
        for representation, value, options, shape in cases:
            with self.subTest(representation=representation, shape=shape, options=options):
                evidence = RawValueEvidence(kind="inline", value=InlineValue(representation=representation, value=value, **options))
                fields: dict[str, Any] = dict(observed_representation=representation, observed_shape=shape, value_evidence=evidence)
                if options:
                    fields["observed_element_representation"] = options["element_representation"]
                record = raw_record(**fields, resource_selection={"kind": "slice", "start": 5, "length": 30})
                self.assertEqual(shape, record.observed_shape)
                self.assertEqual(evidence, record.value_evidence)
                with self.assertRaises(ContractValidationError) as caught:
                    raw_record(**dict(fields, observed_shape=(9,)))
                self.assertEqual("/value_evidence/value/value", caught.exception.path)
        with self.assertRaises(ContractValidationError) as wrong_type:
            raw_record(observed_representation="integer")
        self.assertEqual("/value_evidence/value/representation", wrong_type.exception.path)
        ints = RawValueEvidence(kind="inline", value=InlineValue(representation="fixed_array", element_representation="integer", value=[1]))
        with self.assertRaises(ContractValidationError) as wrong_element:
            raw_record(observed_representation="fixed_array", observed_element_representation="string", observed_shape=(1,), value_evidence=ints)
        self.assertEqual("/value_evidence/value/element_representation", wrong_element.exception.path)

    def test_payload_and_absence_keep_claimed_metadata(self) -> None:
        for retention in ("retained", "intentionally_omitted", "missing", "unverified"):
            payload = payload_reference(retention)
            evidence = RawValueEvidence(kind="payload", payload=payload)
            record = raw_record(observed_representation="referenced_bytes", value_evidence=evidence)
            self.assertIs(payload, record.value_evidence.payload)
            with self.assertRaises(ContractValidationError) as caught:
                raw_record(value_evidence=evidence)
            self.assertEqual("/value_evidence/kind", caught.exception.path)
        for options, pointer in (
            ({"kind": "inline"}, "/value"),
            ({"kind": "payload", "payload": payload_reference(), "reason": RawAbsentReason.UNAVAILABLE}, "/reason"),
            ({"kind": "absent", "reason": RawAbsentReason.READ_ERROR, "value": InlineValue(representation="integer", value=0)}, "/value"),
        ):
            with self.subTest(options=options):
                with self.assertRaises(ContractShapeError) as caught:
                    RawValueEvidence(**cast(dict[str, Any], options))
                self.assertEqual(pointer, caught.exception.path)

    def test_status_evidence_and_diagnostic_matrix(self) -> None:
        inline = RawValueEvidence(kind="inline", value=InlineValue(representation="boolean", value=False))
        payload = RawValueEvidence(kind="payload", payload=payload_reference())
        evidence_cases = {
            "inline": ("boolean", inline),
            "payload": ("referenced_bytes", payload),
            **{reason.value: ("boolean", RawValueEvidence(kind="absent", reason=reason)) for reason in RawAbsentReason},
        }
        allow = {
            "ok": {"inline", "payload"},
            "unavailable": {"unavailable"},
            "orphaned": {"orphaned"},
            "read_error": {"read_error"},
            "type_mismatch": {"inline", "payload"},
            "provider_degraded": set(evidence_cases),
        }
        for status in ObservationStatus:
            for tag, (representation, evidence) in evidence_cases.items():
                for diagnostic in ({}, {"diagnostic": "provider diagnostic"}, {"diagnostic": ""}):
                    with self.subTest(status=status, evidence=tag, diagnostic=diagnostic):
                        error = None
                        if tag not in allow[status]:
                            error = (
                                "/value_evidence/reason"
                                if status in {"unavailable", "orphaned", "read_error"} and evidence.kind == "absent"
                                else "/value_evidence/kind"
                            )
                        elif (
                            (status == "ok" and diagnostic)
                            or (not diagnostic and status in {"read_error", "type_mismatch", "provider_degraded"})
                            or diagnostic == {"diagnostic": ""}
                        ):
                            error = "/diagnostic"
                        if error is None:
                            self.assertEqual(
                                evidence,
                                raw_record(status=status, value_evidence=evidence, observed_representation=representation, **diagnostic).value_evidence,
                            )
                        else:
                            with self.assertRaises(ContractValidationError) as caught:
                                raw_record(status=status, value_evidence=evidence, observed_representation=representation, **diagnostic)
                            self.assertEqual(error, caught.exception.path)

    def test_diagnostic_error_precedes_later_limitation_error(self) -> None:
        with self.assertRaises(ContractValidationError) as caught:
            raw_record(status="type_mismatch", limitations=("same", "same"))
        self.assertEqual("/diagnostic", caught.exception.path)

    def test_timing_retains_only_supplied_evidence(self) -> None:
        receipt = minimum_timing()
        self.assertNotIn(b'"source_timing"', canonical_bytes(raw_record(timing=receipt).timing))
        clock = replace(receipt.receipt_clock, clock_domain_id=uid(7), kind="source", producer_instance_id=uid(8))
        source = SourceTiming(clock=clock, reading=ClockReading(clock_domain_id=uid(7), value=-11))
        self.assertNotIn(b'"source_sequence"', canonical_bytes(source))
        anchor = ClockAnchor(monotonic_reading=receipt.receipt_reading, utc=receipt.receipt_utc, uncertainty_ns=7)
        for speed in (-1.25, 0.0, 1.25):
            timing = replace(
                receipt,
                source_timing=source,
                receipt_anchor=anchor,
                xplane_cycle=0,
                simulator_flight_time_ns=-1,
                acquisition_phase="after_flight_model",
                paused=False,
                replay_state="seeking",
                time_speed=speed,
            )
            self.assertEqual(timing, raw_record(timing=timing).timing)
        mismatched = replace(receipt, receipt_clock=replace(receipt.receipt_clock, producer_instance_id=uid(10)))
        with self.assertRaises(ContractValidationError) as caught:
            raw_record(timing=mismatched)
        self.assertEqual("/timing/receipt_clock/producer_instance_id", caught.exception.path)

    def test_limits_and_ordering(self) -> None:
        first = ApplicabilitySelector(class_id="test.a", value="one")
        second = ApplicabilitySelector(class_id="test.z", value="two")
        self.assertEqual((first, second), raw_record(applicability_context=[first, second]).applicability_context)
        self.assertEqual(256, len(raw_record(limitations=[str(i) for i in range(256)]).limitations))
        for field, value in (
            ("sequence", -1),
            ("source_generation", True),
            ("observation_id", "not-a-uuid"),
            ("observed_shape", [1, 2]),
            ("observed_shape", [65536]),
            ("applicability_context", (second, first)),
            ("applicability_context", (first, first)),
            ("limitations", ("a", "a")),
            ("limitations", tuple(str(i) for i in range(257))),
        ):
            with self.subTest(field=field):
                with self.assertRaises((ContractShapeError, ContractValidationError)) as caught:
                    raw_record(**{field: value})
                self.assertTrue(caught.exception.path.startswith(f"/{field}"), caught.exception.path)
