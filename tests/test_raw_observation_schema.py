"""Independent checks for the raw-observation version-1 wire shape."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, override

from jsonschema import Draft202012Validator

from xplane_fdau.contracts.canonical_json import _encode_document

from .raw_observation_support import FAMILY, SCHEMA_ID, SCHEMA_NAME, raw_observation_wire, uid

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "src/xplane_fdau/schemas"
REQUIRED = {
    "contract_family",
    "schema_version",
    "observation_id",
    "producer",
    "provider",
    "adapter",
    "session_id",
    "stream_id",
    "epoch_id",
    "sequence",
    "connection_generation",
    "source_generation",
    "resource_kind",
    "resource_id",
    "observed_shape",
    "observed_representation",
    "value_evidence",
    "timing",
    "applicability_context",
    "status",
    "limitations",
    "content_hash",
}
OPTIONAL = {"resource_selection", "observed_element_representation", "diagnostic"}
SCALARS = {"boolean": False, "integer": 0, "real": 1.25, "string": "received", "enumeration": "test.unmapped"}


class RawObservationSchemaTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.path = SCHEMAS / SCHEMA_NAME
        self.assertTrue(self.path.is_file(), "missing shipped raw-observation schema")
        self.data = self.path.read_bytes()
        self.schema = json.loads(self.data)
        self.validator = Draft202012Validator(self.schema)

    def test_schema_identity_mirror_and_shared_defs(self) -> None:
        self.assertEqual({"$schema", "$id", "title", "type", "$defs", "properties", "required", "unevaluatedProperties"}, set(self.schema))
        self.assertEqual(SCHEMA_ID, self.schema["$id"])
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", self.schema["$schema"])
        self.assertEqual("object", self.schema["type"])
        self.assertIs(False, self.schema["unevaluatedProperties"])
        self.assertEqual(REQUIRED, set(self.schema["required"]))
        self.assertEqual(REQUIRED | OPTIONAL, set(self.schema["properties"]))
        self.assertEqual(FAMILY, self.schema["properties"]["contract_family"]["const"])
        self.assertEqual(self.data, (ROOT / "docs/schemas" / SCHEMA_NAME).read_bytes())
        self.assertEqual(_encode_document(self.schema), self.data)
        Draft202012Validator.check_schema(self.schema)

        pending: list[object] = [self.schema]
        while pending:
            node = pending.pop()
            if isinstance(node, dict):
                self.assertNotIn("default", node)
                if "$ref" in node:
                    self.assertTrue(node["$ref"].startswith("#/$defs/"))
                pending.extend(node.values())
            elif isinstance(node, list):
                pending.extend(node)

        raw_defs = self.schema["$defs"]
        for name in ("source-binding-catalog-v1.schema.json", "measurement-catalog-v1.schema.json"):
            existing = json.loads((SCHEMAS / name).read_bytes())["$defs"]
            with self.subTest(schema=name):
                self.assertTrue(existing.keys() & raw_defs.keys())
                for stem in existing.keys() & raw_defs.keys():
                    self.assertEqual(_encode_document(existing[stem]), _encode_document(raw_defs[stem]), stem)

    def test_closed_observation_variants(self) -> None:
        raw = raw_observation_wire()
        self.validator.validate(raw)
        inline: list[dict[str, object]] = [{"representation": tag, "value": value} for tag, value in SCALARS.items()]
        inline.append({"representation": "vector", "value": [1.25]})
        inline.extend(
            {"representation": tag, "element_representation": scalar, "value": [value]}
            for tag in ("fixed_array", "variable_array")
            for scalar, value in SCALARS.items()
        )
        for value in inline:
            evidence: dict[str, Any] = {"kind": "inline", "value": value}
            self.validator.validate(dict(raw, value_evidence=evidence))
            self.assertFalse(self.validator.is_valid(dict(raw, value_evidence=dict(evidence, reason="unavailable"))))
            self.assertFalse(self.validator.is_valid(dict(raw, value_evidence=dict(evidence, value=dict(value, unknown=1)))))

        payload = {
            "media_type": "application/octet-stream",
            "byte_length": 0,
            "sha256": "f" * 64,
            "storage_role": "test.raw",
            "retention_status": "intentionally_omitted",
        }
        for evidence in (
            {"kind": "payload", "payload": payload},
            *({"kind": "absent", "reason": reason} for reason in ("orphaned", "unavailable", "read_error")),
        ):
            self.validator.validate(dict(raw, value_evidence=evidence))
            self.assertFalse(self.validator.is_valid(dict(raw, value_evidence=dict(evidence, value=inline[0]))))
            self.assertFalse(self.validator.is_valid(dict(raw, value_evidence={"kind": evidence["kind"]})))
        for name in REQUIRED:
            invalid = raw.copy()
            del invalid[name]
            with self.subTest(missing=name):
                self.assertFalse(self.validator.is_valid(invalid))
        self.assertFalse(self.validator.is_valid(dict(raw, unknown=True)))
        self.assertFalse(self.validator.is_valid(dict(raw, diagnostic=None)))

    def test_timing_selection_and_structural_bounds(self) -> None:
        raw: dict[str, Any] = raw_observation_wire()
        raw["timing"].update(
            source_timing={
                "clock": dict(
                    raw["timing"]["receipt_clock"], clock_domain_id=uid(7), kind="source", unit="tick", tick_period={"numerator_ns": 3, "denominator": 2}
                ),
                "reading": {"clock_domain_id": uid(7), "value": -1},
                "source_sequence": 0,
            },
            receipt_anchor={"monotonic_reading": raw["timing"]["receipt_reading"], "utc": raw["timing"]["receipt_utc"], "uncertainty_ns": 0},
            xplane_cycle=0,
            simulator_flight_time_ns=-1,
            acquisition_phase="unknown",
            paused=False,
            replay_state="seeking",
            time_speed=-1.25,
        )
        for selection in ({"kind": "index", "index": 0}, {"kind": "slice", "start": 0, "length": 1}):
            self.validator.validate(dict(raw, resource_selection=selection))
        eligible = dict(raw, observed_shape=[65535], source_generation=(1 << 63) - 1, resource_id="x" * 2048)
        self.validator.validate(eligible)
        for field, value in (
            ("observed_shape", [65536]),
            ("observed_shape", [1, 2]),
            ("observed_shape", [-1]),
            ("source_generation", 1 << 63),
            ("connection_generation", True),
            ("resource_id", "x" * 2049),
            ("limitations", ["x"] * 257),
            ("resource_selection", {"kind": "index", "index": 0, "start": 0}),
            ("resource_selection", {"kind": "slice", "start": 0, "length": 0}),
        ):
            with self.subTest(field=field):
                self.assertFalse(self.validator.is_valid(dict(eligible, **{field: value})))
        for owner in ("receipt_clock", "receipt_reading", "source_timing", "receipt_anchor"):
            with self.subTest(owner=owner):
                timing = dict(raw["timing"], **{owner: dict(raw["timing"][owner], unknown=True)})
                self.assertFalse(self.validator.is_valid(dict(raw, timing=timing)))


if __name__ == "__main__":
    unittest.main()
