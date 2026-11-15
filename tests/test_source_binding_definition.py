"""Binding identity, local source uniqueness and transform graph tests."""

from __future__ import annotations

import hashlib
import importlib
import unittest
from dataclasses import replace
from functools import partial
from typing import Any, override
from unittest.mock import patch

from tests.binding_support import algorithm, binding, failure, model, payload, source, transform, transform_input, unit
from xplane_fdau.contracts.canonical_json import _encode_document
from xplane_fdau.contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError
from xplane_fdau.contracts.identity import DefinitionRef
from xplane_fdau.contracts.provenance import ProvenanceSource, ProviderIdentity
from xplane_fdau.contracts.values import RepresentationSpec, ShapeSpec, UnitSpec
from xplane_fdau.measurements import ApplicabilitySelector, NumericSpec


class SourceBindingDefinitionTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertTrue(
            hasattr(importlib.import_module("xplane_fdau.bindings.models"), "SourceBindingDefinition"), "complete binding definition is not delivered"
        )

    def assert_error(self, error_type: type[Exception], path: str, operation: Any) -> None:
        with self.assertRaises(error_type) as raised:
            operation()
        self.assertEqual(path, getattr(raised.exception, "path", None))

    def test_binding_pins_exact_measurement_triple(self) -> None:
        ref = DefinitionRef(definition_id="test.measurement", definition_revision=3, definition_hash="c" * 64)
        value = binding(measurement_ref=ref)
        self.assertEqual(ref, value.measurement_ref)
        self.assertEqual("test.measurement", value.measurement_ref.definition_id)
        self.assertEqual(3, value.measurement_ref.definition_revision)
        self.assertEqual("c" * 64, value.measurement_ref.definition_hash)
        self.assert_error(ContractShapeError, "/measurement_ref", partial(binding, measurement_ref={}))
        self.assert_error(CanonicalJSONError, "/measurement_ref", partial(binding, measurement_ref=None))
        self.assert_error(ContractShapeError, "/definition_revision", partial(binding, definition_revision=True))

    def test_binding_identity_has_independent_family_preimage(self) -> None:
        entry = {
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
            "failure_policy": {
                "unavailable": "reject",
                "orphaned": "reject",
                "stale": "reject",
                "read_error": "reject",
                "type_mismatch": "reject",
                "provider_degraded": "reject",
            },
            "acquisition_phase": "unknown",
            "replay_policy": "preserve",
            "limitations": [],
        }
        preimage = _encode_document(
            {"contract_family": "https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog", "schema_version": 1, "definition": entry}
        )
        value = binding()
        self.assertEqual(hashlib.sha256(preimage).hexdigest(), value.content_hash)
        self.assertEqual(64, len(value.content_hash))
        expected = value.content_hash
        with patch("xplane_fdau.bindings.models._definition_content_hash", side_effect=AssertionError("hash recomputed")):
            self.assertEqual(expected, value.content_hash)
            self.assertEqual(expected, value.content_hash)
        with self.assertRaises(TypeError):
            binding(content_hash="0" * 64)
        with self.assertRaises((AttributeError, TypeError)):
            value.content_hash = "0" * 64
        self.assertFalse(hasattr(value, "__dict__"))

    def test_semantic_edits_change_identity_without_mutating_original(self) -> None:
        value = binding()
        changed = [
            replace(value, measurement_ref=replace(value.measurement_ref, definition_hash="c" * 64)),
            replace(value, source=source(resource_selection={"kind": "index", "index": 0})),
            replace(value, failure_policy=failure(stale="accept_without_value")),
            replace(value, acquisition_phase="before_flight_model"),
            replace(value, replay_policy="prohibit"),
        ]
        for item in changed:
            self.assertNotEqual(value.content_hash, item.content_hash)
        a = transform(step_id="test.a", algorithm=algorithm(parameters={"test.factor": 1}))
        b = transform(step_id="test.b", algorithm=algorithm(parameters={"test.factor": 2}))
        self.assertNotEqual(binding(transforms=[a, b]).content_hash, binding(transforms=[b, a]).content_hash)
        self.assertNotEqual(
            binding(transforms=[a]).content_hash, binding(transforms=[replace(a, algorithm=algorithm(parameters={"test.factor": 1.0}))]).content_hash
        )

    def test_every_sequence_is_defensively_copied(self) -> None:
        dependency = model("BindingInputRef")(input_id="test.dependency", source=source(resource_id="test.second"), required=True)
        companion = model("CompanionSource")(input_id="test.health", role="status_and_validity", source=source(resource_id="test.health"))
        originals = {
            "provenance": [ProvenanceSource(source_id="test.source", scope="synthetic", source_revision=1)],
            "applicability": [ApplicabilitySelector(class_id="test.aircraft", value="synthetic")],
            "dependencies": [dependency],
            "companions": [companion],
            "transforms": [transform()],
            "limitations": ["Synthetic example"],
        }
        value = binding(**originals)
        identity = value.content_hash
        for items in originals.values():
            items.clear()
        for name in originals:
            self.assertIs(type(getattr(value, name)), tuple)
            self.assertEqual(1, len(getattr(value, name)))
        self.assertEqual(identity, value.content_hash)
        self.assert_error(ContractShapeError, "/dependencies", partial(binding, dependencies=set()))

    def test_provenance_applicability_and_limitations_invariants(self) -> None:
        source_ref = ProvenanceSource(source_id="test.source", scope="synthetic", source_revision=1)
        self.assert_error(ContractValidationError, "/provenance", partial(binding, provenance=[]))
        self.assert_error(ContractValidationError, "/provenance/1", partial(binding, provenance=[source_ref, source_ref]))
        self.assert_error(ContractShapeError, "/provenance", partial(binding, provenance=[source_ref] * 257))
        self.assert_error(ContractValidationError, "/limitations/1", partial(binding, limitations=["same", "same"]))
        self.assert_error(ContractValidationError, "/limitations/0", partial(binding, limitations=["x" * 1025]))
        self.assertEqual(1024, len(binding(limitations=["x" * 1024]).limitations[0]))
        self.assert_error(ContractShapeError, "/limitations", partial(binding, limitations=["x"] * 257))
        selectors = [ApplicabilitySelector(class_id="test.z", value="z"), ApplicabilitySelector(class_id="test.a", value="a")]
        self.assert_error(ContractValidationError, "/applicability/1/class_id", partial(binding, applicability=selectors))
        self.assert_error(ContractValidationError, "/applicability/1/class_id", partial(binding, applicability=[selectors[0], selectors[0]]))
        self.assert_error(ContractShapeError, "/applicability", partial(binding, applicability=[selectors[0]] * 257))
        self.assertEqual((), binding(applicability=[], limitations=[]).limitations)

    def test_source_ids_and_resource_keys_are_jointly_unique(self) -> None:
        dependency = model("BindingInputRef")(input_id="test.dependency", source=source(resource_id="test.second"), required=False)
        self.assert_error(
            ContractValidationError,
            "/dependencies/0/input_id",
            partial(binding, dependencies=[replace(dependency, input_id="binding.primary")], transforms=[transform()]),
        )
        self.assert_error(
            ContractValidationError, "/dependencies/1/input_id", partial(binding, dependencies=[dependency, dependency], transforms=[transform()])
        )
        companion = model("CompanionSource")(input_id="test.dependency", role="status", source=source(resource_id="test.health"))
        self.assert_error(
            ContractValidationError, "/companions/0/input_id", partial(binding, dependencies=[dependency], companions=[companion], transforms=[transform()])
        )
        alias = source(provider=ProviderIdentity(provider_family_id="test.provider", provider_version="2"), owner_signature="different owner")
        self.assert_error(
            ContractValidationError, "/dependencies/0/source", partial(binding, dependencies=[replace(dependency, source=alias)], transforms=[transform()])
        )
        self.assert_error(
            ContractValidationError, "/companions/0/source", partial(binding, companions=[replace(companion, input_id="test.health", source=source())])
        )
        self.assert_error(
            ContractValidationError,
            "/companions/0/source",
            partial(
                binding, dependencies=[dependency], companions=[replace(companion, input_id="test.health", source=dependency.source)], transforms=[transform()]
            ),
        )
        selected = replace(dependency, source=source(resource_selection={"kind": "index", "index": 0}))
        self.assertEqual(1, len(binding(dependencies=[selected], transforms=[transform()]).dependencies))
        self.assert_error(ContractValidationError, "/transforms", partial(binding, dependencies=[dependency]))
        self.assertEqual(1, len(binding(companions=[replace(companion, input_id="test.health")]).companions))

    def test_source_uniqueness_is_per_binding(self) -> None:
        primary = source()
        first, second = binding(source=primary), binding(definition_id="test.other", source=primary)
        self.assertEqual(first.source, second.source)
        self.assertNotEqual(first.content_hash, second.content_hash)

    def test_transform_edges_resolve_only_prior_value_inputs(self) -> None:
        first = transform(step_id="test.first")
        second = transform(step_id="test.second", inputs=[transform_input(input_id="test.first")])
        self.assertEqual(2, len(binding(transforms=[first, second]).transforms))
        dependency = model("BindingInputRef")(input_id="test.dep", source=source(resource_id="test.dep"), required=True)
        uses_dependency = transform(inputs=[transform_input(input_id="test.dep")])
        self.assertEqual(1, len(binding(dependencies=[dependency], transforms=[uses_dependency]).transforms))
        for invalid in ("test.unknown", "test.first", "test.second"):
            bad = replace(first, inputs=[transform_input(input_id=invalid)])
            self.assert_error(ContractValidationError, "/transforms/0/inputs/0/input_id", partial(binding, transforms=[bad, second]))
        companion = model("CompanionSource")(input_id="test.health", role="status", source=source(resource_id="test.health"))
        bad = replace(first, inputs=[transform_input(input_id="test.health")])
        self.assert_error(ContractValidationError, "/transforms/0/inputs/0/input_id", partial(binding, companions=[companion], transforms=[bad]))
        self.assert_error(ContractValidationError, "/transforms/1/step_id", partial(binding, transforms=[first, first]))
        for reserved in ("binding.primary", "test.dep", "test.health"):
            bad = transform(step_id=reserved)
            self.assert_error(
                ContractValidationError, "/transforms/0/step_id", partial(binding, dependencies=[dependency], companions=[companion], transforms=[bad])
            )

    def test_transform_input_matches_resolved_declaration(self) -> None:
        pointer = "/transforms/0/inputs/0/"
        self.assert_error(
            ContractValidationError, pointer + "representation", partial(binding, transforms=[transform(inputs=[transform_input(representation="integer")])])
        )
        metres = UnitSpec(kind="unit", quantity_id="test.length", unit_id="test.metres")
        self.assert_error(ContractValidationError, pointer + "unit", partial(binding, transforms=[transform(inputs=[transform_input(unit=metres)])]))
        vector_source = source(declared_representation="vector", declared_shape=ShapeSpec(kind="fixed", length=2))
        vector_input = transform_input(representation="vector", shape=ShapeSpec(kind="fixed", length=3))
        self.assert_error(ContractValidationError, pointer + "shape", partial(binding, source=vector_source, transforms=[transform(inputs=[vector_input])]))
        array_source = source(declared_representation="fixed_array", declared_element_representation="real", declared_shape=ShapeSpec(kind="fixed", length=2))
        array_input = transform_input(representation="fixed_array", element_representation="integer", shape=ShapeSpec(kind="fixed", length=2))
        self.assert_error(
            ContractValidationError, pointer + "element_representation", partial(binding, source=array_source, transforms=[transform(inputs=[array_input])])
        )
        bytes_source = source(declared_representation="referenced_bytes", declared_payload=payload(), native_unit=UnitSpec(kind="unitless"))
        from xplane_fdau.contracts.values import PayloadSpec

        different_payload = PayloadSpec(allowed_media_types=["text/plain"], allowed_storage_roles=["test.raw"])
        bytes_input = transform_input(representation="referenced_bytes", payload=different_payload, unit=UnitSpec(kind="unitless"))
        self.assert_error(ContractValidationError, pointer + "payload", partial(binding, source=bytes_source, transforms=[transform(inputs=[bytes_input])]))

    def test_bytes_to_bytes_and_scalar_chains(self) -> None:
        primary = source(declared_representation="referenced_bytes", declared_payload=payload(), native_unit=UnitSpec(kind="unitless"))
        raw_input = transform_input(representation="referenced_bytes", payload=payload(), unit=UnitSpec(kind="unitless"))
        first = transform(
            step_id="test.bytes", inputs=[raw_input], output_representation="referenced_bytes", output_payload=payload(), output_unit=UnitSpec(kind="unitless")
        )
        second = transform(step_id="test.scalar", inputs=[replace(raw_input, input_id="test.bytes")])
        self.assertEqual(2, len(binding(source=primary, transforms=[first, second]).transforms))
        self.assertEqual(first.algorithm, second.algorithm)

    def test_final_measurement_compatibility_waits_for_catalog_validation(self) -> None:
        from tests.measurement_catalog_support import definition

        measurement = definition(
            definition_id="test.real",
            quantity_id="test.length",
            representation=RepresentationSpec(kind="real"),
            numeric=NumericSpec(storage_precision_bits=64, resolution=0.1),
            unit=UnitSpec(kind="unit", quantity_id="test.length", unit_id="test.metres"),
        )
        ref = DefinitionRef(
            definition_id=measurement.definition_id, definition_revision=measurement.definition_revision, definition_hash=measurement.content_hash
        )
        output_unit = unit()
        value = binding(measurement_ref=ref, transforms=[transform(output_unit=output_unit)])
        self.assertEqual(output_unit, value.transforms[-1].output_unit)
        self.assertEqual(ref, value.measurement_ref)
        self.assertNotEqual(measurement.unit, output_unit)

    def test_semantic_error_order_precedes_later_graph_errors(self) -> None:
        wrong = transform(algorithm=algorithm(definition_id="test.good"), inputs=[transform_input(input_id="test.unknown")])
        self.assert_error(ContractValidationError, "/definition_id", partial(binding, definition_id="unqualified", transforms=[wrong]))
        self.assert_error(ContractShapeError, "/replay_policy", partial(binding, definition_id="unqualified", replay_policy="future"))

    def test_repeated_algorithm_and_input_references_preserve_order(self) -> None:
        first = transform(step_id="test.first", inputs=[transform_input(), transform_input()])
        second = transform(step_id="test.second")
        value = binding(transforms=[first, second])
        self.assertEqual(("test.first", "test.second"), tuple(step.step_id for step in value.transforms))
        self.assertEqual(2, len(value.transforms[0].inputs))
        self.assertEqual(value.transforms[0].algorithm, value.transforms[1].algorithm)
