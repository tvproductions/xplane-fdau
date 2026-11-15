"""Normative binding schema, structural variants and semantic boundaries."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from dataclasses import replace
from importlib.resources import files
from pathlib import Path
from typing import Any, cast, override

from jsonschema import Draft202012Validator

from tests.binding_catalog_support import GOLDEN_CATALOG, catalog
from tests.binding_support import algorithm, binding, model, source, transform, unit
from tests.test_binding_catalog_validation import compatible, measurement, variants
from tests.test_source_binding_catalog_io import raw_pair, signed_catalog
from tests.test_source_binding_definition_io import nested, signed
from xplane_fdau.bindings import dumps_source_binding_catalog_v1, loads_source_binding_catalog_v1
from xplane_fdau.contracts import FDAUContractError
from xplane_fdau.contracts.canonical_json import _encode_document

ROOT = Path(__file__).resolve().parents[1]


def resign(raw: dict[str, Any]) -> dict[str, Any]:
    raw = deepcopy(raw)
    raw["definitions"] = [signed(e) for e in raw["definitions"]]
    return signed_catalog(raw)


def matrix() -> list[dict[str, Any]]:
    result = []
    for kind, element in variants():
        for transformed in (False, True):
            b = compatible(measurement(kind, element), transformed=transformed)
            result.append(json.loads(dumps_source_binding_catalog_v1(catalog(definitions=[b]))))
    from xplane_fdau.bindings import TransformInput, TransformStep

    for kind, element in variants():
        m = measurement(kind, element)
        b = compatible(m)
        input_fields: dict[str, Any] = dict(input_id="binding.primary", representation=kind, shape=b.source.declared_shape, unit=b.source.native_unit)
        output_fields: dict[str, Any] = dict(output_representation=kind, output_shape=b.source.declared_shape, output_unit=b.source.native_unit)
        if element is not None:
            input_fields["element_representation"] = element
            output_fields["output_element_representation"] = element
        if kind == "referenced_bytes":
            input_fields["payload"] = m.representation.payload
            output_fields["output_payload"] = m.representation.payload
        step = TransformStep(step_id="test.convert", algorithm=algorithm(), inputs=[TransformInput(**input_fields)], **output_fields)
        result.append(json.loads(dumps_source_binding_catalog_v1(catalog(definitions=[replace(b, transforms=[step])]))))
    for transformed in (False, True):
        result.append(json.loads(dumps_source_binding_catalog_v1(catalog(definitions=[compatible(measurement(unit=unit()), transformed=transformed)]))))
    dependency = model("BindingInputRef")(input_id="test.dep", source=source(resource_id="dep"), required=False)
    for role in ("status", "validity", "status_and_validity"):
        companion = model("CompanionSource")(input_id="test.health", role=role, source=source(resource_id="health"))
        b = binding(dependencies=[dependency], companions=[companion], transforms=[transform()])
        result.append(json.loads(dumps_source_binding_catalog_v1(catalog(definitions=[b]))))
    return result


class BindingCatalogSchemaTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        path = ROOT / "src/xplane_fdau/schemas/source-binding-catalog-v1.schema.json"
        self.assertTrue(path.is_file(), "normative source binding schema missing")
        self.data = files("xplane_fdau.schemas").joinpath(path.name).read_bytes()
        self.schema = json.loads(self.data)
        self.validator = Draft202012Validator(self.schema)

    def test_schema_envelope_mirror_and_shared_defs(self) -> None:
        self.assertEqual({"$schema", "$id", "title", "type", "$defs", "properties", "required", "unevaluatedProperties"}, set(self.schema))
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", self.schema["$schema"])
        self.assertEqual("https://tvproductions.github.io/xplane-fdau/schemas/source-binding-catalog-v1.schema.json", self.schema["$id"])
        expected = {
            "contract_family",
            "schema_version",
            "catalog_id",
            "catalog_revision",
            "authority",
            "provenance",
            "title",
            "scope",
            "definitions",
            "content_hash",
        }
        self.assertEqual(expected, set(self.schema["properties"]))
        self.assertEqual(expected - {"title", "scope"}, set(self.schema["required"]))
        self.assertEqual(self.data, (ROOT / "docs/schemas/source-binding-catalog-v1.schema.json").read_bytes())
        self.assertEqual(self.data, _encode_document(self.schema))
        self.assertFalse(self.data.startswith(b"\xef\xbb\xbf"))
        Draft202012Validator.check_schema(self.schema)
        shared = json.loads(files("xplane_fdau.schemas").joinpath("measurement-catalog-v1.schema.json").read_bytes())["$defs"]
        for name in shared.keys() & self.schema["$defs"].keys():
            self.assertEqual(_encode_document(shared[name]), _encode_document(self.schema["$defs"][name]), name)
        pending = [self.schema]
        while pending:
            value = pending.pop()
            if type(value) is dict:
                self.assertEqual(sorted(cast(dict[str, Any], value)), list(value))
                self.assertNotIn("default", value)
                if "$ref" in value:
                    self.assertTrue(value["$ref"].startswith("#/$defs/"))
                pending.extend(value.values())
            elif type(value) is list:
                pending.extend(value)

    def test_every_binding_variant_and_nested_shape_is_closed(self) -> None:
        optional = {"title", "scope", "owner_signature", "resource_selection", "locator", "sha256"}
        for raw in matrix():
            self.validator.validate(raw)
            loads_source_binding_catalog_v1(json.dumps(raw))
            pending = [(raw, [])]
            while pending:
                current, path = pending.pop()
                if type(current) is list:
                    pending.extend((child, [*path, i]) for i, child in enumerate(current))
                if type(current) is not dict or "parameters" in path:
                    continue
                for name in [None, *[k for k in current if k not in optional or (k == "scope" and path)]]:
                    invalid = deepcopy(raw)
                    target = invalid
                    for key in path:
                        target = target[key]
                    if name is None:
                        target["observed_representation"] = "real"
                    else:
                        del target[name]
                    with self.subTest(path=path, field=name):
                        self.assertFalse(self.validator.is_valid(invalid))
                        with self.assertRaises(FDAUContractError):
                            loads_source_binding_catalog_v1(json.dumps(invalid))
                pending.extend((child, [*path, key]) for key, child in current.items())

    def test_optional_fields_parameters_enums_and_bounds(self) -> None:
        raw = matrix()[1]
        raw["definitions"][0]["source"].update(owner_signature="synthetic", resource_selection={"kind": "slice", "start": 0, "length": 2})
        raw["provenance"] = [{"source_id": "test.source", "scope": "Synthetic", "source_version": "1.0", "locator": "manual", "sha256": "a" * 64}]
        raw["definitions"][0]["transforms"][0]["algorithm"]["parameters"] = {"test.data": [True, 1, 1.0, "value", {"test.child": []}]}
        raw = resign(raw)
        self.validator.validate(raw)
        loads_source_binding_catalog_v1(json.dumps(raw))
        for field, values in (
            ("acquisition_phase", ("before_flight_model", "after_flight_model", "either", "unknown")),
            ("replay_policy", ("preserve", "rederive", "prohibit")),
        ):
            for value in values:
                changed = deepcopy(raw)
                changed["definitions"][0][field] = value
                changed = resign(changed)
                self.validator.validate(changed)
                loads_source_binding_catalog_v1(json.dumps(changed))
        for disposition in ("reject", "accept_raw_only", "accept_without_value", "accept_flagged"):
            changed = deepcopy(raw)
            changed["definitions"][0]["failure_policy"]["stale"] = disposition
            changed = resign(changed)
            self.validator.validate(changed)
            loads_source_binding_catalog_v1(json.dumps(changed))
        for bad in ({"test.value": None}, {"test.value": ""}, {"bad": 1}):
            changed = deepcopy(raw)
            changed["definitions"][0]["transforms"][0]["algorithm"]["parameters"] = bad
            self.assertFalse(self.validator.is_valid(changed))
        for selection in ({"kind": "index", "index": 0}, {"kind": "slice", "start": 0, "length": 1}):
            changed = deepcopy(raw)
            changed["definitions"][0]["source"]["resource_selection"] = selection
            self.validator.validate(changed)
            loads_source_binding_catalog_v1(json.dumps(resign(changed)))
        for field, value in (
            ("title", "x" * 257),
            ("scope", "x" * 2049),
            ("catalog_revision", 0),
            ("schema_version", True),
            ("definitions", []),
            ("provenance", []),
        ):
            changed = deepcopy(raw)
            changed[field] = value
            self.assertFalse(self.validator.is_valid(changed))

    def test_schema_does_not_claim_semantic_closure(self) -> None:
        cases = []
        raw = raw_pair()
        raw["definitions"].reverse()
        cases.append(resign(raw))
        raw = raw_pair()
        raw["definitions"][1] = deepcopy(raw["definitions"][0])
        cases.append(resign(raw))
        raw = json.loads(GOLDEN_CATALOG)
        raw["content_hash"] = "0" * 64
        cases.append(raw)
        raw = json.loads(GOLDEN_CATALOG)
        raw["title"] = "e\u0301"
        cases.append(raw)
        raw = matrix()[1]
        raw["definitions"][0]["transforms"][0]["inputs"][0]["input_id"] = "test.future"
        cases.append(resign(raw))
        raw = json.loads(GOLDEN_CATALOG)
        raw["definitions"][0]["failure_policy"]["unavailable"] = "accept_flagged"
        cases.append(resign(raw))
        raw = matrix()[1]
        raw["definitions"][0]["transforms"][0]["algorithm"]["parameters"] = nested(33)
        cases.append(resign(raw))
        raw = matrix()[1]
        raw["definitions"][0]["transforms"][0]["algorithm"]["parameters"] = {"test.factor": 1.0}
        raw = resign(raw)
        raw["definitions"][0]["transforms"][0]["algorithm"]["parameters"]["test.factor"] = 1
        cases.append(raw)
        for raw in cases:
            self.assertTrue(self.validator.is_valid(raw))
            with self.assertRaises(FDAUContractError):
                loads_source_binding_catalog_v1(json.dumps(raw))
        # Unknown algorithm declarations and cross-catalog mismatches are locally valid.
        raw = matrix()[1]
        raw["definitions"][0]["transforms"][0]["algorithm"]["definition_id"] = "test.unknown"
        raw = resign(raw)
        self.validator.validate(raw)
        loads_source_binding_catalog_v1(json.dumps(raw))

    def test_binding_owned_inventories_and_bounds(self) -> None:
        inventories = {
            "definition_ref": {"definition_id", "definition_revision", "definition_hash"},
            "algorithm_ref": {"definition_id", "definition_revision", "definition_hash", "parameters"},
            "provider_identity": {"provider_family_id", "provider_version"},
            "adapter_identity": {"adapter_family_id", "adapter_version"},
            "binding_input_ref": {"input_id", "source", "required"},
            "companion_source": {"input_id", "role", "source"},
            "failure_policy": {"unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded"},
            "source_binding_definition": {
                "definition_id",
                "definition_revision",
                "content_hash",
                "authority",
                "provenance",
                "measurement_ref",
                "source",
                "applicability",
                "dependencies",
                "companions",
                "transforms",
                "failure_policy",
                "acquisition_phase",
                "replay_policy",
                "limitations",
            },
        }
        for name, expected in inventories.items():
            shape = self.schema["$defs"][name]
            self.assertEqual(expected, set(shape["properties"]))
            self.assertEqual(expected, set(shape["required"]))
            self.assertIs(False, shape["unevaluatedProperties"])
        for kind, maximum in (("vector", 1024), ("fixed_array", 65535)):
            raw = json.loads(
                dumps_source_binding_catalog_v1(catalog(definitions=[compatible(measurement(kind, "integer" if kind == "fixed_array" else None))]))
            )
            for length in (1, maximum):
                raw["definitions"][0]["source"]["declared_shape"]["length"] = length
                self.validator.validate(raw)
                loads_source_binding_catalog_v1(json.dumps(resign(raw)))
            for length in (0, maximum + 1):
                raw["definitions"][0]["source"]["declared_shape"]["length"] = length
                self.assertFalse(self.validator.is_valid(raw))
        raw = json.loads(dumps_source_binding_catalog_v1(catalog(definitions=[compatible(measurement("variable_array", "integer"))])))
        for minimum, maximum in ((0, 0), (65535, 65535)):
            raw["definitions"][0]["source"]["declared_shape"].update(minimum_length=minimum, maximum_length=maximum)
            self.validator.validate(raw)
            loads_source_binding_catalog_v1(json.dumps(resign(raw)))
        for minimum, maximum in ((-1, 1), (0, 65536)):
            raw["definitions"][0]["source"]["declared_shape"].update(minimum_length=minimum, maximum_length=maximum)
            self.assertFalse(self.validator.is_valid(raw))
        raw = json.loads(GOLDEN_CATALOG)
        for field, limit in (("resource_id", 2048), ("owner_signature", 1024)):
            raw["definitions"][0]["source"][field] = "x" * limit
            self.validator.validate(raw)
            loads_source_binding_catalog_v1(json.dumps(resign(raw)))
            raw["definitions"][0]["source"][field] += "x"
            self.assertFalse(self.validator.is_valid(raw))
            raw = json.loads(GOLDEN_CATALOG)
        for required in (False, True):
            raw = deepcopy(matrix()[-3])
            raw["definitions"][0]["dependencies"][0]["required"] = required
            self.validator.validate(raw)
            loads_source_binding_catalog_v1(json.dumps(resign(raw)))

    def test_every_failure_condition_has_each_structural_disposition(self) -> None:
        for condition in ("unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded"):
            for disposition in ("reject", "accept_raw_only", "accept_flagged", "accept_without_value"):
                raw = json.loads(GOLDEN_CATALOG)
                raw["definitions"][0]["failure_policy"][condition] = disposition
                raw = resign(raw)
                self.validator.validate(raw)
                if disposition == "accept_flagged" and condition in ("unavailable", "orphaned", "read_error"):
                    with self.assertRaises(FDAUContractError):
                        loads_source_binding_catalog_v1(json.dumps(raw))
                else:
                    loads_source_binding_catalog_v1(json.dumps(raw))
