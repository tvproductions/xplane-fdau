"""Strict staged binding-entry interchange and constructor barriers."""

from __future__ import annotations

import copy
import hashlib
import importlib
import json
import unittest
from contextlib import ExitStack
from pathlib import Path
from typing import Any, override
from unittest.mock import patch

from tests.binding_support import algorithm, binding, model, payload, source, transform
from xplane_fdau.contracts import CanonicalJSONError, ContractHashError, ContractParseError, ContractShapeError, ContractValidationError, FDAUContractError
from xplane_fdau.contracts._json_parse import _NumberToken, _ObjectPairs, _parse_json_document
from xplane_fdau.contracts.provenance import Authority
from xplane_fdau.contracts.values import ShapeSpec, UnitSpec

FAMILY = "https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog"
# Independent literal entry body; no production projection or encoder as oracle.
BODY: dict[str, Any] = {
    "definition_id": "test.binding",
    "definition_revision": 1,
    "authority": {"authority_id": "test.authority", "authority_revision": 1},
    "provenance": [{"source_id": "test.source", "scope": "synthetic", "source_revision": 1}],
    "measurement_ref": {"definition_id": "test.measurement", "definition_revision": 1, "definition_hash": "b" * 64},
    "source": {
        "provider": {"provider_family_id": "test.provider", "provider_version": "1"},
        "adapter": {"adapter_family_id": "test.adapter", "adapter_version": "1"},
        "resource_kind": "test.resource",
        "resource_id": "test.primary",
        "declared_representation": "real",
        "declared_shape": {"kind": "scalar"},
        "native_unit": {"kind": "unit", "quantity_id": "test.length", "unit_id": "test.feet"},
    },
    "applicability": [],
    "dependencies": [],
    "companions": [],
    "transforms": [],
    "failure_policy": dict.fromkeys(("unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded"), "reject"),
    "acquisition_phase": "unknown",
    "replay_policy": "preserve",
    "limitations": [],
}


def signed(fields: dict[str, Any]) -> dict[str, Any]:
    body = {key: value for key, value in fields.items() if key != "content_hash"}
    preimage = (
        json.dumps(dict(contract_family=FAMILY, schema_version=1, definition=body), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode() + b"\n"
    )
    return fields | {"content_hash": hashlib.sha256(preimage).hexdigest()}


def entry() -> dict[str, Any]:
    return signed(copy.deepcopy(BODY))


def nested(depth: int) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for _ in range(depth - 1):
        result = {"test.child": result}
    return result


class SourceBindingDefinitionIOTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        module = importlib.import_module("xplane_fdau.bindings.models")
        self.assertTrue(Path(module.__file__).with_name("_definition_io.py").is_file(), "private staged binding reader is absent")
        self.io = importlib.import_module("xplane_fdau.bindings._definition_io")

    def assert_failure(self, value: object, error: type[FDAUContractError], pointer: str, *, identity: str | None = "test.binding") -> FDAUContractError:
        with self.assertRaises(error) as caught:
            self.io._source_binding_definition_from_wire(value, path="/definitions/2", source="binding.json")
        failure = caught.exception
        self.assertEqual("/definitions/2" + pointer, failure.path)
        self.assertEqual("binding.json", failure.source)
        self.assertEqual(FAMILY, failure.contract_family)
        self.assertEqual(identity, failure.identity)
        self.assertIsNone(failure.line)
        self.assertIsNone(failure.column)
        return failure

    def test_binding_entry_round_trip_preserves_exact_references(self) -> None:
        expected = json.dumps(entry(), sort_keys=True, separators=(",", ":")).encode() + b"\n"
        self.assertEqual(expected, self.io._source_binding_definition_bytes(binding()))
        self.assertEqual(binding(), self.io._source_binding_definition_from_wire(_parse_json_document(expected)))
        reordered = json.dumps(dict(reversed(tuple(entry().items()))), indent=2)
        self.assertEqual(binding(), self.io._source_binding_definition_from_wire(_parse_json_document(reordered)))
        value = binding(transforms=[transform(algorithm=algorithm(parameters={"test.factor": [1, 1.0]}))])
        wire = self.io._source_binding_definition_bytes(value)
        loaded = self.io._source_binding_definition_from_wire(_parse_json_document(wire))
        self.assertEqual(value, loaded)
        self.assertEqual("a" * 64, loaded.transforms[0].algorithm.definition_hash)
        self.assertEqual("b" * 64, loaded.measurement_ref.definition_hash)
        self.assertNotIn(b"owner_signature", wire)
        self.assertNotIn(b"declared_payload", wire)
        self.assertIn(b'"test.factor":[1,1.0]', wire)

    def test_round_trip_all_representation_variants_and_selection(self) -> None:
        cases: list[dict[str, Any]] = [dict(declared_representation=k, native_unit=UnitSpec(kind="unitless")) for k in ("boolean", "string", "enumeration")]
        cases += [dict(declared_representation=k) for k in ("integer", "real")]
        cases += [dict(declared_representation="vector", declared_shape=ShapeSpec(kind="fixed", length=2))]
        for kind in ("fixed_array", "variable_array"):
            for element in ("boolean", "integer", "real", "string", "enumeration"):
                shape = ShapeSpec(kind="fixed", length=2) if kind == "fixed_array" else ShapeSpec(kind="variable", minimum_length=0, maximum_length=2)
                cases.append(
                    dict(declared_representation=kind, declared_element_representation=element, declared_shape=shape, native_unit=UnitSpec(kind="unitless"))
                )
        cases.append(dict(declared_representation="referenced_bytes", declared_payload=payload(), native_unit=UnitSpec(kind="unitless")))
        for fields in cases:
            with self.subTest(fields=fields):
                src = source(**fields, owner_signature="synthetic", resource_selection={"kind": "slice", "start": 0, "length": 2})
                value = binding(source=src)
                self.assertEqual(value, self.io._source_binding_definition_from_wire(_parse_json_document(self.io._source_binding_definition_bytes(value))))
        dependency = model("BindingInputRef")(input_id="test.dep", source=source(resource_id="dep"), required=False)
        companion = model("CompanionSource")(input_id="test.health", role="status", source=source(resource_id="health"))
        from xplane_fdau.measurements import ApplicabilitySelector

        value = binding(
            dependencies=[dependency],
            companions=[companion],
            transforms=[transform()],
            applicability=[ApplicabilitySelector(class_id="test.aircraft", value="Synthetic")],
            limitations=["Synthetic only"],
        )
        self.assertEqual(value, self.io._source_binding_definition_from_wire(_parse_json_document(self.io._source_binding_definition_bytes(value))))

    def test_binding_entry_rejects_observed_fields(self) -> None:
        for name in ("observed_representation", "observed_shape"):
            fields = entry()
            fields["source"][name] = "real"
            self.assert_failure(fields, ContractShapeError, "/source/" + name)
        for name in ("provider", "resource_id", "observed_representation", "observed_shape"):
            self.assert_failure(entry() | {name: "invented"}, ContractShapeError, "/" + name)

    def test_complete_binding_entry_precedence(self) -> None:
        value = entry()
        value["definition_id"] = "bad"
        value["transforms"] = [{"step_id": "bad"}]
        self.assert_failure(value, ContractShapeError, "/transforms/0/algorithm", identity="bad")
        value["definition_id"] = "e\u0301"
        self.assert_failure(value, ContractShapeError, "/transforms/0/algorithm", identity="e\u0301")
        value = entry() | {"definition_id": "bad", "content_hash": "0" * 64}
        self.assert_failure(value, ContractHashError, "/content_hash", identity="bad")
        self.assert_failure(value | {"content_hash": "MALFORMED"}, ContractValidationError, "/definition_id", identity="bad")
        self.assert_failure(entry() | {"content_hash": "MALFORMED"}, ContractValidationError, "/content_hash")
        value = entry()
        value["limitations"] = [None]
        self.assert_failure(value, CanonicalJSONError, "/limitations/0")
        value = entry()
        value["limitations"] = ["e\u0301"]
        self.assert_failure(value, CanonicalJSONError, "/limitations/0")
        value = entry()
        value["definition_revision"] = _NumberToken("9223372036854775808", False)
        value["replay_policy"] = 3
        self.assert_failure(value, ContractShapeError, "/replay_policy")
        for raw in (value, dict(reversed(tuple(value.items())))):
            raw["replay_policy"] = "preserve"
            self.assert_failure(raw, CanonicalJSONError, "/definition_revision")

    def test_parameter_domains_precede_hash_and_use_lexical_keys(self) -> None:
        value = binding(transforms=[transform()])
        fields = json.loads(self.io._source_binding_definition_bytes(value))
        for bad in (None, "e\u0301", _NumberToken("1e1000", True), _NumberToken("1e-1000", True), 1 << 63):
            fields["transforms"][0]["algorithm"]["parameters"] = {"z": bad, "a/b~c": bad}
            error = self.assert_failure(fields, CanonicalJSONError, "/transforms/0/algorithm/parameters/a~1b~0c")
            self.assertNotIn("1e1000", str(error))
        fields["transforms"][0]["algorithm"]["parameters"] = {"secret": "SENSITIVE-" + "x" * 250, "a": None}
        self.assertNotIn("SENSITIVE", str(self.assert_failure(fields, CanonicalJSONError, "/transforms/0/algorithm/parameters/a")))

    def test_duplicates_precede_overflow_and_shape(self) -> None:
        raw = _ObjectPairs((("definition_revision", _NumberToken("9" * 100, False)), ("x", 1), ("x", 2)))
        self.assert_failure(raw, ContractParseError, "/x", identity=None)
        with self.assertRaises(ContractParseError):
            _parse_json_document('{"definition_revision":99999999999999999999,"x":1,"x":2}')

    def test_stale_hash_precedes_graph_but_reference_hashes_are_opaque(self) -> None:
        fields = entry()
        fields["measurement_ref"]["definition_hash"] = "c" * 64
        self.assert_failure(fields, ContractHashError, "/content_hash")
        loaded = self.io._source_binding_definition_from_wire(signed(fields))
        self.assertEqual("c" * 64, loaded.measurement_ref.definition_hash)
        fields = json.loads(self.io._source_binding_definition_bytes(binding(transforms=[transform()])))
        fields["transforms"][0]["inputs"][0]["input_id"] = "test.future"
        self.assert_failure(fields, ContractHashError, "/content_hash")
        self.assert_failure(signed(fields), ContractValidationError, "/transforms/0/inputs/0/input_id")

    def test_constructor_barrier_instruments_actual_initializers(self) -> None:
        from xplane_fdau.contracts.identity import AlgorithmRef, DefinitionRef
        from xplane_fdau.contracts.provenance import AdapterIdentity, ProvenanceSource, ProviderIdentity
        from xplane_fdau.contracts.values import PayloadSpec
        from xplane_fdau.measurements import ApplicabilitySelector

        classes = [
            Authority,
            ProvenanceSource,
            DefinitionRef,
            AlgorithmRef,
            ProviderIdentity,
            AdapterIdentity,
            ShapeSpec,
            UnitSpec,
            PayloadSpec,
            ApplicabilitySelector,
        ]
        classes += [
            model(name)
            for name in ("SourceSpec", "BindingInputRef", "CompanionSource", "TransformInput", "TransformStep", "FailurePolicy", "SourceBindingDefinition")
        ]
        value = entry()
        value["limitations"] = [None]
        with ExitStack() as stack:
            guards = [stack.enter_context(patch.object(cls, "__init__", side_effect=AssertionError("premature structural construction"))) for cls in classes]
            builder = stack.enter_context(patch.object(self.io, "_binding_entry_build", side_effect=AssertionError("premature builder")))
            self.assert_failure(value, CanonicalJSONError, "/limitations/0")
            builder.assert_not_called()
            for guard in guards:
                guard.assert_not_called()
            original = self.io._binding_entry_shape

            def early_authority(*args: Any, **kwargs: Any) -> Any:
                Authority(authority_id="test.authority", authority_revision=1)
                return original(*args, **kwargs)

            with patch.object(self.io, "_binding_entry_shape", side_effect=early_authority), self.assertRaisesRegex(AssertionError, "premature structural"):
                self.io._source_binding_definition_from_wire(value)
        calls: list[str] = []

        def forwarding(cls: Any) -> Any:
            original = cls.__init__

            def initialize(self: Any, *args: Any, **kwargs: Any) -> None:
                calls.append(cls.__name__)
                original(self, *args, **kwargs)

            return initialize

        with ExitStack() as stack:
            for cls in classes:
                stack.enter_context(patch.object(cls, "__init__", forwarding(cls)))
            loaded = self.io._source_binding_definition_from_wire(entry())
        self.assertEqual(binding(), loaded)
        self.assertIn("Authority", calls)
        self.assertIn("SourceBindingDefinition", calls)

    def test_parameter_and_document_depth_and_collection_limits(self) -> None:
        fields = json.loads(self.io._source_binding_definition_bytes(binding(transforms=[transform()])))
        fields["transforms"][0]["algorithm"]["parameters"] = nested(32)
        self.io._source_binding_definition_from_wire(signed(fields))
        fields["transforms"][0]["algorithm"]["parameters"] = nested(33)
        with self.assertRaises(CanonicalJSONError):
            self.io._source_binding_definition_from_wire(signed(fields))
        for depth in (64, 65):
            value = nested(depth)
            if depth == 64:
                self.io._domain_tree(value, path="")
            else:
                with self.assertRaises(CanonicalJSONError):
                    self.io._domain_tree(value, path="")
        self.assert_failure(entry() | {"companions": [{}] * 257}, ContractShapeError, "/companions")
        fields = json.loads(self.io._source_binding_definition_bytes(binding(transforms=[transform()])))
        fields["transforms"][0]["inputs"] *= 65536
        self.assert_failure(fields, ContractShapeError, "/transforms/0/inputs")
        cyclic: dict[str, Any] = {}
        cyclic["child"] = cyclic
        for invalid in (cyclic, nested(1100)):
            fields = entry()
            fields["source"] = invalid
            self.assert_failure(fields, ContractShapeError, "/source/" + next(iter(invalid)))
        fields = entry() | {"definition_id": "x" * 300, "limitations": [None]}
        self.assert_failure(fields, CanonicalJSONError, "/limitations/0", identity="x" * 160)
