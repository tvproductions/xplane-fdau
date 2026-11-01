"""Normative schema resource and representable structural contract."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from typing import Any, cast, override

from jsonschema import Draft202012Validator

from tests.measurement_catalog_support import GOLDEN_CATALOG
from tests.test_measurement_catalog_io import raw_pair, signed_catalog
from tests.test_measurement_definition_io import signed
from xplane_fdau.contracts import FDAUContractError
from xplane_fdau.contracts.canonical_json import _encode_document
from xplane_fdau.measurements import loads_measurement_catalog_v1

ROOT = Path(__file__).resolve().parents[1]


def matrix() -> list[dict[str, Any]]:
    result = []
    representations: list[dict[str, Any]] = [{"kind": kind} for kind in ("boolean", "integer", "real", "string", "enumeration")]
    representations.extend(
        [
            {"kind": "vector", "length": 2},
            {"kind": "referenced_bytes", "payload": {"allowed_media_types": ["application/octet-stream"], "allowed_storage_roles": ["test.raw"]}},
        ]
    )
    for kind in ("fixed_array", "variable_array"):
        for scalar in ("boolean", "integer", "real", "string", "enumeration"):
            rep: dict[str, Any] = {"kind": kind, "element_representation": scalar}
            rep.update({"length": 2} if kind == "fixed_array" else {"minimum_length": 0, "maximum_length": 2})
            representations.append(rep)
    for rep in representations:
        raw = json.loads(GOLDEN_CATALOG)
        entry = raw["definitions"][0]
        entry["representation"] = rep
        scalar = rep.get("element_representation", rep["kind"])
        if scalar in ("integer", "real", "vector"):
            integer = scalar == "integer"
            entry["numeric"] = {
                "storage_precision_bits": 32,
                "resolution": 1 if integer else 1.0,
                "minimum": -1 if integer else -1.0,
                "maximum": 2 if integer else 2.0,
            }
        if scalar == "enumeration":
            entry["enumeration"] = {
                "members": [
                    {"code": "test.a", "label": "Known", "kind": "known"},
                    {"code": "test.b", "label": "Other", "kind": "unknown"},
                    {"code": "test.c", "label": "Reserved", "kind": "reserved"},
                ]
            }
        raw["definitions"][0] = signed(entry)
        result.append(signed_catalog(raw))
    return result


class MeasurementCatalogSchemaTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.path = ROOT / "src/xplane_fdau/schemas/measurement-catalog-v1.schema.json"
        self.assertTrue(self.path.is_file(), "normative catalog schema is missing")
        self.data = files("xplane_fdau.schemas").joinpath("measurement-catalog-v1.schema.json").read_bytes()
        self.schema = json.loads(self.data)
        self.validator = Draft202012Validator(self.schema)

    def test_schema_envelope_and_mirror(self) -> None:
        self.assertEqual({"$schema", "$id", "title", "type", "$defs", "properties", "required", "unevaluatedProperties"}, set(self.schema))
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", self.schema["$schema"])
        self.assertEqual("https://tvproductions.github.io/xplane-fdau/schemas/measurement-catalog-v1.schema.json", self.schema["$id"])
        self.assertEqual(
            {"contract_family", "schema_version", "catalog_id", "catalog_revision", "authority", "provenance", "definitions", "title", "scope", "content_hash"},
            set(self.schema["properties"]),
        )
        self.assertEqual(set(self.schema["properties"]) - {"title", "scope"}, set(self.schema["required"]))
        self.assertEqual(self.data, (ROOT / "docs/schemas/measurement-catalog-v1.schema.json").read_bytes())
        self.assertEqual(self.data, _encode_document(self.schema))
        self.assertFalse(self.data.startswith(b"\xef\xbb\xbf"))
        self.assertTrue(self.data.endswith(b"\n") and not self.data.endswith(b"\n\n"))
        Draft202012Validator.check_schema(self.schema)
        pending = [self.schema]
        while pending:
            value = pending.pop()
            if type(value) is dict:
                self.assertEqual(sorted(cast(dict[str, Any], value)), list(value))
                self.assertNotIn("default", value)
                if "$ref" in value:
                    self.assertTrue(value["$ref"].startswith("#/$defs/"))
                if value.get("type") == "object":
                    self.assertIs(False, value.get("unevaluatedProperties", value.get("additionalProperties")))
                pending.extend(value.values())
            elif type(value) is list:
                pending.extend(value)

    def test_every_representation_shape_accepts_and_rejects_variants(self) -> None:
        for raw in matrix():
            rep = raw["definitions"][0]["representation"]
            with self.subTest(rep=rep):
                self.validator.validate(raw)
                loads_measurement_catalog_v1(json.dumps(raw))
                for path, field in (
                    ([], "catalog_id"),
                    (["definitions", 0], "title"),
                    (["authority"], "authority_id"),
                    (["provenance", 0], "scope"),
                    (["definitions", 0, "representation"], "kind"),
                ):
                    invalid = deepcopy(raw)
                    target: Any = invalid
                    for token in path:
                        target = target[token]
                    del target[field]
                    self.assertFalse(self.validator.is_valid(invalid))
                    with self.assertRaises(FDAUContractError):
                        loads_measurement_catalog_v1(json.dumps(invalid))
                for location in ([], ["definitions", 0], ["definitions", 0, "representation"]):
                    invalid = deepcopy(raw)
                    target: Any = invalid
                    for token in location:
                        target = target[token]
                    target["provider"] = {}
                    self.assertFalse(self.validator.is_valid(invalid))
                    with self.assertRaises(FDAUContractError):
                        loads_measurement_catalog_v1(json.dumps(invalid))

    def test_optional_coordinate_unit_freshness_and_provenance_variants(self) -> None:
        for field, value in (
            (
                "coordinates",
                {
                    "kind": "applicable",
                    "reference_frame_id": "test.frame",
                    "datum_id": "test.datum",
                    "handedness": "left",
                    "axes": [{"axis_id": "test.x", "direction": "forward", "sign_convention": "positive"}],
                },
            ),
            ("freshness", {"stale_after_ns": 3}),
            ("freshness", {"fresh_for_ns": 0, "stale_after_ns": 3}),
            ("applicability", [{"class_id": "test.aircraft", "value": "Synthetic"}]),
            ("provenance", [{"source_id": "test.source", "scope": "Synthetic", "source_version": "1.0", "locator": "manual", "sha256": "a" * 64}]),
        ):
            raw = json.loads(GOLDEN_CATALOG)
            raw["definitions"][0][field] = value
            raw["definitions"][0] = signed(raw["definitions"][0])
            raw = signed_catalog(raw)
            self.validator.validate(raw)
            loads_measurement_catalog_v1(json.dumps(raw))
        raw = matrix()[1]
        raw["definitions"][0]["unit"] = {"kind": "unit", "quantity_id": "test.state", "unit_id": "test.unit"}
        raw["definitions"][0] = signed(raw["definitions"][0])
        raw = signed_catalog(raw)
        self.validator.validate(raw)
        loads_measurement_catalog_v1(json.dumps(raw))

    def test_irrelevant_fields_invalid_tags_types_and_null_fail(self) -> None:
        for field, value in (
            ("numeric", {"storage_precision_bits": 32, "resolution": 1}),
            ("enumeration", {"members": []}),
            ("title", None),
            ("title", True),
            ("allowed_validity", ["future"]),
            ("representation", {"kind": "boolean", "length": 1}),
            ("unit", {"kind": "unitless", "unit_id": "test.unit"}),
            ("coordinates", {"kind": "not_applicable", "axes": []}),
            ("freshness", {}),
        ):
            raw = json.loads(GOLDEN_CATALOG)
            raw["definitions"][0][field] = value
            self.assertFalse(self.validator.is_valid(raw), (field, value))
            with self.assertRaises(FDAUContractError):
                loads_measurement_catalog_v1(json.dumps(raw))

    def test_schema_runtime_boundary_is_explicit(self) -> None:
        variants = []
        raw = raw_pair()
        raw["definitions"].reverse()
        variants.append(signed_catalog(raw))
        raw = json.loads(GOLDEN_CATALOG)
        raw["content_hash"] = "0" * 64
        variants.append(raw)
        raw = json.loads(GOLDEN_CATALOG)
        raw["title"] = "e\u0301"
        variants.append(raw)
        raw = matrix()[2]
        raw["definitions"][0]["numeric"]["resolution"] = 1
        variants.append(raw)
        for raw in variants:
            self.assertTrue(self.validator.is_valid(raw))
            with self.assertRaises(FDAUContractError):
                loads_measurement_catalog_v1(json.dumps(raw))
        duplicate = GOLDEN_CATALOG.replace(b'"catalog_revision":1', b'"catalog_revision":1,"catalog_revision":1')
        self.assertTrue(self.validator.is_valid(json.loads(duplicate)))
        with self.assertRaises(FDAUContractError):
            loads_measurement_catalog_v1(duplicate)

    def test_nested_shape_closure_and_required_fields(self) -> None:
        # Each expected set comes from the specification, independently of schema constants.
        inventories = {
            "authority": ({"authority_id", "authority_revision"}, set()),
            "provenance_source": ({"source_id", "scope"}, {"source_revision", "source_version", "locator", "sha256"}),
            "axis_spec": ({"axis_id", "direction", "sign_convention"}, set()),
            "enumeration_member": ({"code", "label", "kind"}, set()),
            "enumeration_spec": ({"members"}, set()),
            "applicability_selector": ({"class_id", "value"}, set()),
            "payload_spec": ({"allowed_media_types", "allowed_storage_roles"}, set()),
            "integer_numeric_spec": ({"storage_precision_bits", "resolution"}, {"minimum", "maximum"}),
            "real_numeric_spec": ({"storage_precision_bits", "resolution"}, {"minimum", "maximum"}),
        }
        for name, (required, optional) in inventories.items():
            shape = self.schema["$defs"][name]
            self.assertEqual(required, set(shape["required"]))
            self.assertEqual(required | optional, set(shape["properties"]))
        for raw in matrix():
            pending: list[tuple[Any, list[str | int]]] = [(raw, [])]
            while pending:
                current, path = pending.pop()
                if type(current) is list:
                    pending.extend((child, [*path, i]) for i, child in enumerate(current))
                    continue
                if type(current) is not dict:
                    continue
                invalid = deepcopy(raw)
                target: Any = invalid
                for token in path:
                    target = target[token]
                target["provider"] = {"provider_family_id": "test.provider"}
                self.assertFalse(self.validator.is_valid(invalid), path)
                with self.assertRaises(FDAUContractError):
                    loads_measurement_catalog_v1(json.dumps(invalid))
                pending.extend((child, [*path, name]) for name, child in current.items())
