"""Exact resolution, declaration compatibility and policy authorization."""

from __future__ import annotations

import unittest
from dataclasses import replace
from typing import Any, cast, override
from unittest.mock import patch

from tests.binding_catalog_support import FAMILY, catalog
from tests.binding_support import binding, failure, payload, source, transform, transform_input, unit
from tests.measurement_catalog_support import catalog as measurement_catalog
from tests.measurement_catalog_support import definition
from xplane_fdau import bindings
from xplane_fdau.contracts import ContractShapeError, ContractValidationError, DefinitionRef, RepresentationSpec, ShapeSpec, UnitSpec
from xplane_fdau.measurements import ApplicabilitySelector, EnumerationMember, EnumerationSpec, NumericSpec


def reference(m: Any) -> DefinitionRef:
    return DefinitionRef(definition_id=m.definition_id, definition_revision=m.definition_revision, definition_hash=m.content_hash)


def variants() -> list[tuple[str, str | None]]:
    return [(k, None) for k in ("boolean", "integer", "real", "string", "enumeration", "vector", "referenced_bytes")] + [
        (k, e) for k in ("fixed_array", "variable_array") for e in ("boolean", "integer", "real", "string", "enumeration")
    ]


def measurement(kind: str = "real", element: str | None = None, **changes: Any) -> Any:
    rep: dict[str, Any] = {"kind": kind}
    if kind in ("vector", "fixed_array"):
        rep["length"] = 2
    if kind == "variable_array":
        rep.update(minimum_length=0, maximum_length=2)
    if element is not None:
        rep["element_representation"] = element
    if kind == "referenced_bytes":
        rep["payload"] = payload()
    fields: dict[str, Any] = dict(definition_id="test.measurement", quantity_id="test.length", representation=RepresentationSpec(**rep))
    scalar = element or kind
    if scalar in ("integer", "real", "vector"):
        fields["numeric"] = NumericSpec(storage_precision_bits=64, resolution=1 if scalar == "integer" else 1.0)
    if scalar == "enumeration":
        fields["enumeration"] = EnumerationSpec(members=[EnumerationMember(code="test.member", label="Member", kind="known")])
    return definition(**(fields | changes))


def compatible(m: Any, *, transformed: bool = False, **changes: Any) -> Any:
    kind = str(m.representation.kind)
    shape = (
        ShapeSpec(kind="fixed", length=m.representation.length)
        if kind in ("vector", "fixed_array")
        else ShapeSpec(kind="variable", minimum_length=m.representation.minimum_length, maximum_length=m.representation.maximum_length)
        if kind == "variable_array"
        else ShapeSpec(kind="scalar")
    )
    extra: dict[str, Any] = {}
    if kind in ("fixed_array", "variable_array"):
        extra["declared_element_representation"] = m.representation.element_representation
    if kind == "referenced_bytes":
        extra["declared_payload"] = m.representation.payload
    src = source(declared_representation=kind, declared_shape=shape, native_unit=m.unit, **extra)
    steps = []
    if transformed:
        opts = {n.replace("declared_", "output_"): v for n, v in extra.items()}
        steps = [transform(output_representation=kind, output_shape=shape, output_unit=m.unit, **opts)]
        src = source()
    return binding(measurement_ref=reference(m), source=src, transforms=steps, **changes)


class BindingCatalogValidationTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertTrue(hasattr(bindings, "validate_binding_catalog"), "pure cross-catalog validator missing")
        self.validate = bindings.validate_binding_catalog

    def check(self, b: Any, m: Any) -> None:
        self.assertIsNone(self.validate(catalog(definitions=[b]), measurement_catalog(definitions=[m])))

    def rejected(self, b: Any, m: Any, path: str) -> None:
        with self.assertRaises(ContractValidationError) as caught:
            self.check(b, m)
        self.assertEqual("/definitions/0" + path, caught.exception.path)
        self.assertEqual(FAMILY, caught.exception.contract_family)
        self.assertEqual(b.definition_id, caught.exception.identity)

    def test_reference_resolution_requires_pair_then_hash(self) -> None:
        m = measurement()
        b = compatible(m)
        self.check(b, m)
        for ref in (replace(b.measurement_ref, definition_id="test.missing"), replace(b.measurement_ref, definition_revision=2)):
            self.rejected(replace(b, measurement_ref=ref), m, "/measurement_ref")
        self.rejected(replace(b, measurement_ref=replace(b.measurement_ref, definition_hash="0" * 64)), m, "/measurement_ref/definition_hash")
        m2 = replace(m, definition_revision=2)
        self.assertIsNone(
            self.validate(
                catalog(definitions=[b, replace(b, definition_revision=2, measurement_ref=reference(m2)), replace(b, definition_id="test.other")]),
                measurement_catalog(definitions=[m, m2]),
            )
        )
        self.rejected(b, replace(m, title="Changed"), "/measurement_ref/definition_hash")
        self.check(b, m)
        for first, second in (({}, {}), (catalog(), {})):
            with self.assertRaises(ContractShapeError):
                self.validate(cast(Any, first), cast(Any, second))

    def test_direct_and_final_metadata_match_all_representations(self) -> None:
        for kind, element in variants():
            m = measurement(kind, element)
            for transformed in (False, True):
                with self.subTest(kind=kind, element=element, transformed=transformed):
                    self.check(compatible(m, transformed=transformed), m)

    def test_representation_element_shape_payload_and_unit_mismatches(self) -> None:
        scalar = measurement()
        array = measurement("fixed_array", "real")
        variable = measurement("variable_array", "integer")
        byte = measurement("referenced_bytes")
        changes = [
            (scalar, "representation", "integer"),
            (array, "element_representation", "integer"),
            (array, "shape", ShapeSpec(kind="fixed", length=3)),
            (variable, "shape", ShapeSpec(kind="variable", minimum_length=1, maximum_length=2)),
            (variable, "shape", ShapeSpec(kind="variable", minimum_length=0, maximum_length=3)),
            (byte, "payload", replace(payload(), allowed_media_types=["application/octet-stream", "text/plain"])),
            (byte, "payload", replace(payload(), allowed_storage_roles=["test.other"])),
            (scalar, "unit", unit()),
        ]
        for m, field, bad in changes:
            for transformed in (False, True):
                b = compatible(m, transformed=transformed)
                names = {
                    "representation": "declared_representation",
                    "element_representation": "declared_element_representation",
                    "shape": "declared_shape",
                    "payload": "declared_payload",
                    "unit": "native_unit",
                }
                name = "output_" + field if transformed else names[field]
                if transformed:
                    b = replace(b, transforms=[replace(b.transforms[0], **{name: bad})])
                    path = "/transforms/0/" + name
                else:
                    b = replace(b, source=replace(b.source, **{name: bad}))
                    path = "/source/" + name
                with self.subTest(field=field, transformed=transformed):
                    self.rejected(b, m, path)
        m = measurement(unit=unit())
        b = compatible(m)
        self.check(b, m)
        for changed in (replace(unit(), unit_id="test.metres"), replace(unit(), quantity_id="test.other"), UnitSpec(kind="unitless")):
            self.rejected(replace(b, source=replace(b.source, native_unit=changed)), m, "/source/native_unit")

    def test_binding_applicability_preserves_and_may_narrow(self) -> None:
        a = ApplicabilitySelector(class_id="test.aircraft", value="A")
        extra = ApplicabilitySelector(class_id="test.plugin", value="P")
        for transformed in (False, True):
            m = measurement(applicability=[a])
            b = compatible(m, transformed=transformed, applicability=[a, extra])
            self.check(b, m)
            self.rejected(replace(b, applicability=[extra]), m, "/applicability")
            self.rejected(replace(b, applicability=[replace(a, value="B"), extra]), m, "/applicability/0/value")
            m = measurement()
            self.check(compatible(m, transformed=transformed, applicability=[a]), m)

    def test_algorithm_is_opaque_and_validation_is_pure(self) -> None:
        m = measurement()
        b = compatible(m, transformed=True)
        first = transform(step_id="test.first")
        last = replace(b.transforms[0], inputs=[transform_input(input_id="test.first")])
        b = replace(b, transforms=[first, last])
        bc = catalog(definitions=[b])
        mc = measurement_catalog(definitions=[m])
        before = (bindings.dumps_source_binding_catalog_v1(bc), bc.content_hash, mc.content_hash)
        with patch("importlib.import_module", side_effect=AssertionError("algorithm discovery forbidden")):
            self.validate(bc, mc)
        self.assertEqual(before, (bindings.dumps_source_binding_catalog_v1(bc), bc.content_hash, mc.content_hash))
        # Earlier outputs can differ; only the final one must match the measurement.
        wrong = replace(last, output_representation="integer")
        self.rejected(replace(b, transforms=[first, wrong]), m, "/transforms/1/output_representation")
        self.assertEqual(before, (bindings.dumps_source_binding_catalog_v1(bc), bc.content_hash, mc.content_hash))

    def test_failure_authorization_matrix(self) -> None:
        conditions = ("unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded")
        validities = (("valid",), ("invalid",), ("unknown",), ("not_applicable",), ("not_applicable", "valid"), ("invalid", "valid"))
        for condition in conditions:
            for disposition in ("reject", "accept_raw_only", "accept_without_value", "accept_flagged"):
                if disposition == "accept_flagged" and condition in ("unavailable", "orphaned", "read_error"):
                    continue
                for states in validities:
                    for authorized in (False, True):
                        m = measurement(allowed_validity=states, allowed_quality=[condition] if authorized else [])
                        b = compatible(m, failure_policy=failure(**{condition: disposition}))
                        row = {"invalid", "unknown", "valid"} if condition == "provider_degraded" else {"invalid", "unknown"}
                        allowed = disposition == "reject" or (
                            authorized and bool(set(states) & row) and (disposition == "accept_flagged" or bool(set(states) & {"invalid", "unknown"}))
                        )
                        with self.subTest(condition=condition, disposition=disposition, states=states, authorized=authorized):
                            if allowed:
                                self.check(b, m)
                            else:
                                self.rejected(b, m, "/failure_policy/" + condition)

    def test_first_cross_catalog_failure_follows_semantic_order(self) -> None:
        a = ApplicabilitySelector(class_id="test.aircraft", value="A")
        m = measurement(applicability=[a])
        good = compatible(m, applicability=[a])
        badsource = replace(good.source, declared_representation="integer")
        wrong = replace(good, source=badsource, applicability=[], failure_policy=failure(stale="accept_flagged"))
        self.rejected(wrong, m, "/source/declared_representation")
        self.rejected(replace(wrong, measurement_ref=replace(good.measurement_ref, definition_revision=2)), m, "/measurement_ref")
        self.rejected(replace(wrong, source=good.source), m, "/applicability")
        self.rejected(replace(wrong, source=good.source, applicability=[a]), m, "/failure_policy/stale")
        transformed = compatible(m, transformed=True)
        wrong = replace(transformed, transforms=[replace(transformed.transforms[0], output_representation="integer")])
        self.rejected(wrong, m, "/applicability")
        self.rejected(replace(wrong, applicability=[a]), m, "/transforms/0/output_representation")

    def test_every_representation_and_array_element_mismatch_fails(self) -> None:
        for kind, element in variants():
            m = measurement(kind, element)
            other = measurement("integer" if kind != "integer" else "real")
            for transformed in (False, True):
                bad = replace(compatible(other, transformed=transformed), measurement_ref=reference(m))
                path = "/transforms/0/output_representation" if transformed else "/source/declared_representation"
                self.rejected(bad, m, path)
                if element is not None:
                    other = measurement(kind, "integer" if element != "integer" else "real")
                    bad = replace(compatible(other, transformed=transformed), measurement_ref=reference(m))
                    path = "/transforms/0/output_element_representation" if transformed else "/source/declared_element_representation"
                    self.rejected(bad, m, path)
                    other = measurement("integer")

    def test_failure_policy_field_order_and_canonical_binding_order(self) -> None:
        from itertools import combinations

        m = measurement()
        for first, second in combinations(("unavailable", "orphaned", "stale", "read_error", "type_mismatch", "provider_degraded"), 2):
            for changes, want in (
                ({first: "accept_raw_only", second: "accept_raw_only"}, first),
                ({first: "accept_raw_only"}, first),
                ({second: "accept_raw_only"}, second),
            ):
                self.rejected(compatible(m, failure_policy=failure(**changes)), m, "/failure_policy/" + want)
        first = replace(compatible(m), definition_id="test.a", measurement_ref=replace(reference(m), definition_revision=2))
        second = replace(compatible(measurement("integer")), definition_id="test.b", measurement_ref=reference(m))
        mc = measurement_catalog(definitions=[m])
        for entries, want in (
            ([first, second], "/definitions/0/measurement_ref"),
            ([replace(first, measurement_ref=reference(m)), second], "/definitions/1/source/declared_representation"),
        ):
            with self.assertRaises(ContractValidationError) as caught:
                self.validate(catalog(definitions=entries), mc)
            self.assertEqual(want, caught.exception.path)

    def test_only_final_output_matters_and_failure_keeps_inputs_unchanged(self) -> None:
        m = measurement()
        first = transform(step_id="test.first", output_representation="integer")
        final = transform(inputs=[transform_input(input_id="test.first", representation="integer")], output_unit=m.unit)
        b = binding(measurement_ref=reference(m), transforms=[first, final])
        self.check(b, m)
        first = replace(first, output_representation="real", output_unit=m.unit)
        final = replace(final, inputs=[transform_input(input_id="test.first", unit=m.unit)], output_representation="integer")
        dependency = bindings.BindingInputRef(input_id="test.dep", source=source(resource_id="test.dependency", native_unit=m.unit), required=True)
        bad = replace(b, dependencies=[dependency], transforms=[first, final])
        bc = catalog(definitions=[bad])
        mc = measurement_catalog(definitions=[m])
        before = (bindings.dumps_source_binding_catalog_v1(bc), bc.content_hash, mc.content_hash)
        with self.assertRaises(ContractValidationError) as caught:
            self.validate(bc, mc)
        self.assertEqual("/definitions/0/transforms/1/output_representation", caught.exception.path)
        self.assertEqual(before, (bindings.dumps_source_binding_catalog_v1(bc), bc.content_hash, mc.content_hash))
