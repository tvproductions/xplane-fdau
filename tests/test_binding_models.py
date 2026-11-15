"""Behavioral tests for owned source, transform and failure declarations."""

from __future__ import annotations

import importlib.util
import inspect
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass
from enum import StrEnum
from typing import Any, override

from tests.binding_support import algorithm, failure, model, payload, source, transform, transform_input, unit
from xplane_fdau.contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError
from xplane_fdau.contracts.values import ScalarRepresentation, ShapeSpec, UnitSpec, ValueRepresentation


class BindingModelTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertIsNotNone(importlib.util.find_spec("xplane_fdau.bindings"), "source binding declarations are not delivered")

    def assert_error(self, error_type: type[Exception], path: str, operation: Any) -> None:
        with self.assertRaises(error_type) as raised:
            operation()
        self.assertEqual(path, getattr(raised.exception, "path", None))

    def test_closed_binding_vocabularies(self) -> None:
        expected = {
            "CompanionRole": ["status", "validity", "status_and_validity"],
            "FailureCondition": ["unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded"],
            "FailureDisposition": ["reject", "accept_raw_only", "accept_flagged", "accept_without_value"],
            "AcquisitionPhase": ["before_flight_model", "after_flight_model", "either", "unknown"],
            "BindingReplayPolicy": ["preserve", "rederive", "prohibit"],
        }
        for name, values in expected.items():
            with self.subTest(name=name):
                vocabulary = model(name)
                self.assertTrue(issubclass(vocabulary, StrEnum))
                self.assertEqual(values, [item.value for item in vocabulary])

    def test_models_are_frozen_slotted_keyword_only(self) -> None:
        examples = [
            source(),
            model("BindingInputRef")(input_id="test.dependency", source=source(), required=True),
            model("CompanionSource")(input_id="test.status", role="status", source=source()),
            transform_input(),
            transform(),
            failure(),
        ]
        for value in examples:
            with self.subTest(model=type(value).__name__):
                self.assertTrue(is_dataclass(value))
                self.assertFalse(hasattr(value, "__dict__"))
                for parameter in inspect.signature(type(value)).parameters.values():
                    self.assertEqual(inspect.Parameter.KEYWORD_ONLY, parameter.kind)
                with self.assertRaises(FrozenInstanceError):
                    setattr(value, fields(value)[0].name, None)
        with self.assertRaises(TypeError):
            model("BindingInputRef")("test.dependency", source(), True)

    def test_source_representation_shape_payload_matrix(self) -> None:
        for representation in ValueRepresentation:
            elements = tuple(ScalarRepresentation) if representation in ("fixed_array", "variable_array") else (None,)
            for element in elements:
                with self.subTest(representation=representation, element=element):
                    shape = ShapeSpec(kind="scalar")
                    extra: dict[str, Any] = {}
                    if representation in ("fixed_array", "vector"):
                        shape = ShapeSpec(kind="fixed", length=2)
                    elif representation == "variable_array":
                        shape = ShapeSpec(kind="variable", minimum_length=0, maximum_length=3)
                    if element is not None:
                        extra["declared_element_representation"] = element
                    if representation == "referenced_bytes":
                        extra["declared_payload"] = payload()
                    numeric = representation in ("integer", "real", "vector") or element in ("integer", "real")
                    value = source(
                        declared_representation=representation, declared_shape=shape, native_unit=unit() if numeric else UnitSpec(kind="unitless"), **extra
                    )
                    self.assertEqual(representation, value.declared_representation)
                    self.assertEqual(shape, value.declared_shape)
                    self.assertIs(type(value.declared_representation), ValueRepresentation)

    def test_source_shape_bounds_follow_representation(self) -> None:
        for kind, accepted, rejected in (("vector", 1024, 1025), ("fixed_array", 65535, 65536)):
            extra = {"declared_element_representation": "real"} if kind == "fixed_array" else {}
            self.assertEqual(
                accepted, source(declared_representation=kind, declared_shape=ShapeSpec(kind="fixed", length=accepted), **extra).declared_shape.length
            )
            if rejected <= 65535:
                self.assert_error(
                    ContractValidationError,
                    "/declared_shape/length",
                    lambda kind=kind, rejected=rejected, extra=extra: source(
                        declared_representation=kind, declared_shape=ShapeSpec(kind="fixed", length=rejected), **extra
                    ),
                )
            else:
                raw_shape = object.__new__(ShapeSpec)
                object.__setattr__(raw_shape, "kind", "fixed")
                object.__setattr__(raw_shape, "length", rejected)
                from xplane_fdau.contracts.values import _OMITTED

                object.__setattr__(raw_shape, "minimum_length", _OMITTED)
                object.__setattr__(raw_shape, "maximum_length", _OMITTED)
                self.assert_error(
                    ContractValidationError,
                    "/declared_shape/length",
                    lambda kind=kind, raw_shape=raw_shape, extra=extra: source(declared_representation=kind, declared_shape=raw_shape, **extra),
                )

    def test_source_variants_reject_missing_and_irrelevant_fields(self) -> None:
        cases = [
            (dict(declared_representation="referenced_bytes", native_unit=UnitSpec(kind="unitless")), "/declared_payload"),
            (dict(declared_representation="fixed_array", declared_shape=ShapeSpec(kind="fixed", length=2)), "/declared_element_representation"),
            (dict(declared_element_representation="real"), "/declared_element_representation"),
            (dict(declared_payload=payload()), "/declared_payload"),
        ]
        for changes, path in cases:
            with self.subTest(changes=changes):
                self.assert_error(ContractShapeError, path, lambda changes=changes: source(**changes))
        self.assert_error(ContractValidationError, "/declared_shape/kind", lambda: source(declared_shape=ShapeSpec(kind="fixed", length=2)))
        self.assert_error(ContractShapeError, "/provider", lambda: source(provider={"provider_family_id": "test.provider", "provider_version": "1"}))
        self.assert_error(CanonicalJSONError, "/declared_shape", lambda: source(declared_shape=None))

    def test_non_numeric_sources_require_unitless(self) -> None:
        for kind in ("boolean", "string", "enumeration", "referenced_bytes", "fixed_array", "variable_array"):
            extra: dict[str, Any] = {}
            if kind == "referenced_bytes":
                extra["declared_payload"] = payload()
            if kind in ("fixed_array", "variable_array"):
                extra["declared_element_representation"] = "boolean"
                extra["declared_shape"] = (
                    ShapeSpec(kind="fixed", length=1) if kind == "fixed_array" else ShapeSpec(kind="variable", minimum_length=0, maximum_length=1)
                )
            with self.subTest(kind=kind):
                self.assert_error(ContractValidationError, "/native_unit/kind", lambda kind=kind, extra=extra: source(declared_representation=kind, **extra))

    def test_resource_selection_is_closed_and_frozen(self) -> None:
        for selection in ({"kind": "index", "index": 0}, {"kind": "slice", "start": 2, "length": 3}):
            original = dict(selection)
            value = source(resource_selection=selection)
            selection["kind"] = "changed"
            self.assertEqual(original, dict(value.resource_selection))
            with self.assertRaises(TypeError):
                value.resource_selection["kind"] = "changed"
        cases = [
            ({"kind": "index"}, ContractShapeError, "/resource_selection/index"),
            ({"kind": "index", "index": 0, "length": 1}, ContractShapeError, "/resource_selection/length"),
            ({"kind": "slice", "start": 0, "length": 0}, ContractValidationError, "/resource_selection/length"),
            ({"kind": "index", "index": True}, ContractShapeError, "/resource_selection/index"),
            ({"kind": "index", "index": -1}, ContractValidationError, "/resource_selection/index"),
            ({"kind": "index", "index": 2**63}, CanonicalJSONError, "/resource_selection/index"),
            ({"kind": "other"}, ContractShapeError, "/resource_selection/kind"),
        ]
        for selection, error, path in cases:
            with self.subTest(selection=selection):
                self.assert_error(error, path, lambda selection=selection: source(resource_selection=selection))
        self.assert_error(CanonicalJSONError, "/resource_selection", lambda: source(resource_selection=None))

    def test_source_text_and_boolean_domains(self) -> None:
        self.assertEqual(2048, len(source(resource_id="x" * 2048).resource_id))
        self.assertEqual(1024, len(source(owner_signature="x" * 1024).owner_signature))
        for name, count in (("resource_id", 2049), ("owner_signature", 1025)):
            self.assert_error(ContractValidationError, "/" + name, lambda name=name, count=count: source(**{name: "x" * count}))
        self.assert_error(CanonicalJSONError, "/resource_id", lambda: source(resource_id="e\u0301"))
        self.assert_error(ContractValidationError, "/resource_kind", lambda: source(resource_kind="unqualified"))
        self.assert_error(ContractShapeError, "/required", lambda: model("BindingInputRef")(input_id="test.input", source=source(), required=1))
        self.assert_error(CanonicalJSONError, "/required", lambda: model("BindingInputRef")(input_id="test.input", source=source(), required=None))

    def test_transform_inputs_and_parameters_are_deeply_owned(self) -> None:
        nested_flag = {"test.flag": True}
        parameters: dict[str, Any] = {"test.values": [1, nested_flag], "test.expression": "__import__('anything')"}
        reference = algorithm(parameters=parameters)
        inputs = [transform_input()]
        value = transform(algorithm=reference, inputs=inputs)
        inputs.clear()
        nested_flag["test.flag"] = False
        self.assertEqual(1, len(value.inputs))
        self.assertTrue(value.algorithm.parameters["test.values"][1]["test.flag"])
        self.assertEqual("__import__('anything')", value.algorithm.parameters["test.expression"])
        with self.assertRaises(TypeError):
            value.algorithm.parameters["test.new"] = 2
        with self.assertRaises(CanonicalJSONError):
            algorithm(parameters={"test.callable": lambda: None})
        self.assert_error(ContractShapeError, "/inputs", lambda: transform(inputs=set()))
        self.assert_error(ContractValidationError, "/inputs", lambda: transform(inputs=[]))
        self.assert_error(ContractShapeError, "/inputs/0", lambda: transform(inputs=[object()]))

    def test_transform_declarations_enforce_variant_rules(self) -> None:
        self.assert_error(ContractShapeError, "/element_representation", lambda: transform_input(element_representation="real"))
        self.assert_error(ContractShapeError, "/output_payload", lambda: transform(output_payload=payload()))
        self.assert_error(
            ContractShapeError,
            "/output_element_representation",
            lambda: transform(output_representation="fixed_array", output_shape=ShapeSpec(kind="fixed", length=2)),
        )
        self.assert_error(ContractValidationError, "/output_unit/kind", lambda: transform(output_representation="boolean"))
        bytes_input = transform_input(representation="referenced_bytes", payload=payload(), unit=UnitSpec(kind="unitless"))
        value = transform(inputs=[bytes_input], output_representation="referenced_bytes", output_payload=payload(), output_unit=UnitSpec(kind="unitless"))
        self.assertEqual(payload(), value.output_payload)

    def test_failure_policy_rejects_unusable_flagged_conditions(self) -> None:
        for condition in ("unavailable", "orphaned", "read_error"):
            with self.subTest(condition=condition):
                self.assert_error(ContractValidationError, "/" + condition, lambda condition=condition: failure(**{condition: "accept_flagged"}))
                for permitted in ("reject", "accept_raw_only", "accept_without_value"):
                    self.assertEqual(permitted, getattr(failure(**{condition: permitted}), condition))
        for condition in ("stale", "type_mismatch", "provider_degraded"):
            self.assertEqual("accept_flagged", getattr(failure(**{condition: "accept_flagged"}), condition))
        self.assert_error(ContractShapeError, "/stale", lambda: failure(stale="ignore"))
        with self.assertRaises(TypeError):
            model("FailurePolicy")()

    def test_declaration_mapping_validators_preserve_tiers_and_paths(self) -> None:
        from xplane_fdau.bindings._model_io import _source_spec_wire
        from xplane_fdau.bindings._source_validation import _validate_source_fields

        raw = _source_spec_wire(source())
        raw["resource_kind"] = "invalid"
        raw["declared_payload"] = {}
        self.assert_error(ContractShapeError, "/declared_payload", lambda: _validate_source_fields(raw, 0))
        raw = _source_spec_wire(source())
        raw["observed_shape"] = []
        self.assert_error(ContractShapeError, "/observed_shape", lambda: _validate_source_fields(raw, 0))

    def test_transform_input_collection_bound_is_65535(self) -> None:
        from xplane_fdau.bindings._model_io import _transform_step_wire
        from xplane_fdau.bindings._transform_validation import _validate_transform_step_fields

        raw = _transform_step_wire(transform())
        inputs: list[object] = [None] * 65535
        raw["inputs"] = inputs
        _validate_transform_step_fields(raw, 0)
        inputs.append(None)
        self.assert_error(ContractShapeError, "/inputs", lambda: _validate_transform_step_fields(raw, 0))

    def test_parameter_depth_bounds_and_canonical_domains_are_reused(self) -> None:
        value: dict[str, Any] = {}
        for _ in range(31):
            value = {"test.child": value}
        self.assertIsNotNone(transform(algorithm=algorithm(parameters=value)))
        value = {"test.child": value}
        with self.assertRaises(CanonicalJSONError):
            algorithm(parameters=value)
        for invalid in (None, float("inf"), 2**63, b"payload"):
            with self.subTest(value=invalid), self.assertRaises(CanonicalJSONError):
                algorithm(parameters={"test.value": invalid})
