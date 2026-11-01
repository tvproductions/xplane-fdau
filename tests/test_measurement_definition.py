"""Intrinsic supporting measurement semantic contracts."""

from __future__ import annotations

import dataclasses
import inspect
import unittest
from enum import StrEnum
from typing import Any, cast, override

from xplane_fdau.contracts import CanonicalJSONError, ContractShapeError, ContractValidationError, FDAUContractError
from xplane_fdau.contracts.values import _OMITTED
from xplane_fdau.measurements import models


class ForeignTag(StrEnum):
    KNOWN = "known"
    APPLICABLE = "applicable"


class MeasurementSemanticValueTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        # A missing public model is an explicit feature failure in the RED run.
        self.assertTrue(hasattr(models, "AxisSpec"), "supporting measurement models have not been delivered")
        self.axis = models.AxisSpec(axis_id="test.x", direction="forward", sign_convention="positive forward")
        self.member = models.EnumerationMember(code="test.a", label="Active", kind="known")

    def assertContract(self, error: type[FDAUContractError], path: str, cls: Any, **fields: Any) -> None:
        with self.assertRaises(error) as caught:
            cls(**fields)
        self.assertEqual(path, caught.exception.path)

    def test_vocabularies_have_exact_names_values_and_no_aliases(self) -> None:
        for name, expected in (
            ("EnumerationMemberKind", [("KNOWN", "known"), ("UNKNOWN", "unknown"), ("RESERVED", "reserved")]),
            ("InterpolationPolicy", [("PROHIBITED", "prohibited"), ("HOLD", "hold"), ("LINEAR", "linear")]),
            ("DiscontinuityPolicy", [("PRESERVE", "preserve"), ("START_NEW_EPOCH", "start_new_epoch"), ("REJECT", "reject")]),
            ("Sensitivity", [("PUBLIC", "public"), ("OPERATIONAL", "operational"), ("RESTRICTED", "restricted"), ("UNKNOWN", "unknown")]),
        ):
            with self.subTest(name=name):
                vocabulary = getattr(models, name)
                self.assertTrue(issubclass(vocabulary, StrEnum))
                self.assertFalse(dataclasses.is_dataclass(vocabulary))
                self.assertEqual(expected, [(key, item.value) for key, item in vocabulary.__members__.items()])
                self.assertEqual(len(expected), len(vocabulary))

    def test_model_signatures_immutability_and_omission(self) -> None:
        cases = (
            (models.AxisSpec, ["axis_id", "direction", "sign_convention"], self.axis),
            (models.CoordinateSpec, ["kind", "reference_frame_id", "datum_id", "handedness", "axes"], models.CoordinateSpec(kind="not_applicable")),
            (models.NumericSpec, ["storage_precision_bits", "resolution", "minimum", "maximum"], models.NumericSpec(storage_precision_bits=1, resolution=1)),
            (models.EnumerationMember, ["code", "label", "kind"], self.member),
            (models.EnumerationSpec, ["members"], models.EnumerationSpec(members=[self.member])),
            (models.FreshnessSpec, ["fresh_for_ns", "stale_after_ns"], models.FreshnessSpec(fresh_for_ns=0)),
            (models.ApplicabilitySelector, ["class_id", "value"], models.ApplicabilitySelector(class_id="test.aircraft", value="A")),
        )
        for cls, names, instance in cases:
            with self.subTest(cls=cls):
                self.assertTrue(dataclasses.is_dataclass(cls))
                signature = inspect.signature(cls)
                self.assertEqual(names, list(signature.parameters))
                self.assertTrue(all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in signature.parameters.values()))
                self.assertFalse(hasattr(instance, "__dict__"))
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    setattr(instance, names[0], "changed")
                with self.assertRaises(TypeError):
                    cast(Any, cls)("positional")
        self.assertIs(_OMITTED, cases[1][2].axes)
        self.assertIs(_OMITTED, cases[2][2].minimum)
        self.assertIs(_OMITTED, cases[5][2].stale_after_ns)

    def test_axis_identifier_and_text_boundaries(self) -> None:
        models.AxisSpec(axis_id="test.axis", direction="a" * 256, sign_convention="a" * 512)
        for field, bad, error in (
            ("axis_id", "invalid", ContractValidationError),
            ("direction", "", ContractValidationError),
            ("direction", "a" * 257, ContractValidationError),
            ("sign_convention", "", ContractValidationError),
            ("sign_convention", "a" * 513, ContractValidationError),
            ("direction", "e\u0301", CanonicalJSONError),
            ("direction", "\ud800", CanonicalJSONError),
            ("direction", None, CanonicalJSONError),
            ("direction", 1, ContractShapeError),
        ):
            fields: dict[str, Any] = dict(axis_id="test.x", direction="x", sign_convention="positive")
            fields[field] = bad
            with self.subTest(field=field, bad=repr(bad)):
                self.assertContract(error, "/" + field, models.AxisSpec, **fields)

    def test_coordinate_variants_axes_and_precise_errors(self) -> None:
        axes = [self.axis]
        coordinates = models.CoordinateSpec(kind="applicable", reference_frame_id="test.frame", handedness="right", axes=axes)
        axes.clear()
        self.assertEqual((self.axis,), coordinates.axes)
        models.CoordinateSpec(kind="applicable", reference_frame_id="test.frame", datum_id="test.datum", handedness="left", axes=(self.axis,))
        fields: dict[str, Any] = dict(kind="applicable", reference_frame_id="test.frame", handedness="right", axes=[self.axis])
        for field in ("reference_frame_id", "handedness", "axes"):
            missing = dict(fields)
            del missing[field]
            self.assertContract(ContractShapeError, "/" + field, models.CoordinateSpec, **missing)
        for field, value in (("reference_frame_id", "test.frame"), ("datum_id", "test.datum"), ("handedness", "left"), ("axes", [])):
            self.assertContract(ContractShapeError, "/" + field, models.CoordinateSpec, kind="not_applicable", **{field: value})
        for replacement, path, error in (
            ({"kind": "future"}, "/kind", ContractShapeError),
            ({"kind": ForeignTag.APPLICABLE}, "/kind", ContractShapeError),
            ({"handedness": "future"}, "/handedness", ContractShapeError),
            ({"axes": []}, "/axes", ContractValidationError),
            ({"axes": [self.axis, self.axis]}, "/axes/1/axis_id", ContractValidationError),
            ({"axes": [self.axis] * 33}, "/axes", ContractShapeError),
            ({"axes": [self.axis, {}]}, "/axes/1", ContractShapeError),
            ({"axes": {self.axis}}, "/axes", ContractShapeError),
            ({"axes": iter([self.axis])}, "/axes", ContractShapeError),
            ({"axes": None}, "/axes", CanonicalJSONError),
            ({"datum_id": None}, "/datum_id", CanonicalJSONError),
        ):
            with self.subTest(path=path, replacement=replacement):
                self.assertContract(error, path, models.CoordinateSpec, **(fields | replacement))
        many_axes = [models.AxisSpec(axis_id=f"test.axis_{index}", direction="x", sign_convention="positive") for index in range(32)]
        self.assertEqual(tuple(many_axes), models.CoordinateSpec(kind="applicable", reference_frame_id="test.frame", handedness="right", axes=many_axes).axes)

    def test_numeric_domains_and_inclusive_boundaries(self) -> None:
        for fields in (
            dict(storage_precision_bits=1, resolution=1),
            dict(storage_precision_bits=64, resolution=1, minimum=-(2**63), maximum=2**63 - 1),
            dict(storage_precision_bits=64, resolution=0.5, minimum=1.0, maximum=1.0),
            dict(storage_precision_bits=32, resolution=5e-324),
        ):
            with self.subTest(fields=fields):
                cast(Any, models.NumericSpec)(**fields)
        base = dict(storage_precision_bits=32, resolution=1)
        for replacement, path, error in (
            ({"storage_precision_bits": 0}, "/storage_precision_bits", ContractValidationError),
            ({"storage_precision_bits": 65}, "/storage_precision_bits", ContractValidationError),
            ({"storage_precision_bits": True}, "/storage_precision_bits", ContractShapeError),
            ({"resolution": 0}, "/resolution", ContractValidationError),
            ({"resolution": float("1e-9999")}, "/resolution", ContractValidationError),
            ({"resolution": -1.0}, "/resolution", ContractValidationError),
            ({"resolution": True}, "/resolution", ContractShapeError),
            ({"resolution": None}, "/resolution", CanonicalJSONError),
            ({"minimum": 0.0}, "/minimum", ContractShapeError),
            ({"resolution": 1.0, "maximum": 1}, "/maximum", ContractShapeError),
            ({"resolution": float("inf")}, "/resolution", CanonicalJSONError),
            ({"resolution": float("nan")}, "/resolution", CanonicalJSONError),
            ({"resolution": 2**63}, "/resolution", CanonicalJSONError),
            ({"minimum": -(2**63) - 1}, "/minimum", CanonicalJSONError),
            ({"minimum": None}, "/minimum", CanonicalJSONError),
            ({"minimum": True}, "/minimum", ContractShapeError),
            ({"minimum": 2, "maximum": 1}, "/maximum", ContractValidationError),
        ):
            with self.subTest(replacement=replacement):
                self.assertContract(error, path, models.NumericSpec, **(base | replacement))

    def test_null_numeric_resolution_preserves_real_bounds_and_shape_priority(self) -> None:
        for bound in ("minimum", "maximum"):
            with self.subTest(bound=bound):
                with self.assertRaises(FDAUContractError) as caught:
                    cast(Any, models.NumericSpec)(storage_precision_bits=64, resolution=None, **{bound: 1.0})
                self.assertIs(type(caught.exception), CanonicalJSONError)
                self.assertEqual("/resolution", caught.exception.path)
            for malformed in (True, "1", [], {}):
                with self.subTest(bound=bound, malformed=malformed):
                    self.assertContract(ContractShapeError, "/" + bound, models.NumericSpec, storage_precision_bits=64, resolution=None, **{bound: malformed})
        self.assertContract(ContractShapeError, "/maximum", models.NumericSpec, storage_precision_bits=64, resolution=None, minimum=1.0, maximum=True)

    def test_enumeration_metadata_and_frozen_order(self) -> None:
        unknown = models.EnumerationMember(code="test.b", label="Unknown", kind=models.EnumerationMemberKind.UNKNOWN)
        reserved = models.EnumerationMember(code="test.c", label="Reserved", kind="reserved")
        members = [self.member, unknown, reserved]
        enumeration = models.EnumerationSpec(members=members)
        members.clear()
        self.assertEqual((self.member, unknown, reserved), enumeration.members)
        self.assertIs(models.EnumerationMemberKind.KNOWN, self.member.kind)
        for members, path, error in (
            ([], "/members", ContractValidationError),
            ([unknown, self.member], "/members/1/code", ContractValidationError),
            ([self.member, self.member], "/members/1/code", ContractValidationError),
            ([unknown, models.EnumerationMember(code="test.c", label="?", kind="unknown")], "/members/1/kind", ContractValidationError),
            ([self.member] * 65536, "/members", ContractShapeError),
            ([{}], "/members/0", ContractShapeError),
            ({self.member}, "/members", ContractShapeError),
            (None, "/members", CanonicalJSONError),
        ):
            with self.subTest(path=path, error=error):
                self.assertContract(error, path, models.EnumerationSpec, members=members)
        for kind in (ForeignTag.KNOWN, "future", 1):
            self.assertContract(ContractShapeError, "/kind", models.EnumerationMember, code="test.a", label="A", kind=kind)
        self.assertContract(ContractValidationError, "/label", models.EnumerationMember, code="test.a", label="a" * 257, kind="known")
        self.assertContract(ContractValidationError, "/label", models.EnumerationMember, code="test.a", label="", kind="known")

    def test_freshness_and_applicability_boundaries(self) -> None:
        for fields in (dict(fresh_for_ns=0), dict(stale_after_ns=0), dict(fresh_for_ns=2**63 - 1, stale_after_ns=2**63 - 1)):
            models.FreshnessSpec(**fields)
        self.assertContract(ContractShapeError, "/fresh_for_ns", models.FreshnessSpec)
        self.assertContract(ContractValidationError, "/stale_after_ns", models.FreshnessSpec, fresh_for_ns=2, stale_after_ns=1)
        for bad, error in ((-1, ContractValidationError), (2**63, CanonicalJSONError), (True, ContractShapeError), (None, CanonicalJSONError)):
            self.assertContract(error, "/fresh_for_ns", models.FreshnessSpec, fresh_for_ns=bad)
        models.ApplicabilitySelector(class_id="test.aircraft", value="a" * 256)
        for field, bad, error in (
            ("class_id", "invalid", ContractValidationError),
            ("value", "", ContractValidationError),
            ("value", "a" * 257, ContractValidationError),
            ("value", "e\u0301", CanonicalJSONError),
        ):
            self.assertContract(error, "/" + field, models.ApplicabilitySelector, **(dict(class_id="test.aircraft", value="A") | {field: bad}))

    def test_shape_precedes_domains_and_semantics(self) -> None:
        self.assertContract(ContractShapeError, "/sign_convention", models.AxisSpec, axis_id="bad", direction="e\u0301", sign_convention=1)
        self.assertContract(CanonicalJSONError, "/direction", models.AxisSpec, axis_id="bad", direction="e\u0301", sign_convention="positive")
        self.assertContract(
            ContractShapeError, "/axes/1", models.CoordinateSpec, kind="applicable", reference_frame_id="e\u0301", handedness="left", axes=[self.axis, object()]
        )

    def test_constructor_nested_ownership_respects_earlier_shape(self) -> None:
        axis_fields = dict(axis_id="test.x", direction="forward", sign_convention="positive")
        self.assertContract(
            ContractShapeError, "/axes/0", models.CoordinateSpec, kind="applicable", reference_frame_id="test.frame", handedness="left", axes=[axis_fields]
        )
        self.assertContract(
            ContractShapeError, "/reference_frame_id", models.CoordinateSpec, kind="applicable", reference_frame_id=1, handedness="left", axes=[axis_fields]
        )
        self.assertContract(ContractShapeError, "/members/0", models.EnumerationSpec, members=[dict(code="test.a", label="A", kind="known")])

    def test_plain_nested_mapping_validators_never_construct_models(self) -> None:
        from unittest.mock import patch

        from xplane_fdau.measurements import _definition_validation as validation

        coordinates = dict(
            kind="applicable",
            reference_frame_id="test.frame",
            handedness="right",
            axes=[dict(axis_id="test.x", direction="forward", sign_convention="positive")],
        )
        enumeration = dict(members=[dict(code="test.a", label="A", kind="known")])
        with (
            patch.object(models.AxisSpec, "__post_init__", side_effect=AssertionError("constructed axis")),
            patch.object(models.EnumerationMember, "__post_init__", side_effect=AssertionError("constructed member")),
        ):
            for phase in range(3):
                validation._validate_coordinates_fields(coordinates, phase, path="/coordinates")
                validation._validate_enumeration_fields(enumeration, phase, path="/enumeration")
        self.assertEqual(list, type(coordinates["axes"]))

    def test_mapping_validation_preserves_semantic_property_order(self) -> None:
        from xplane_fdau.measurements import _definition_validation as validation

        with self.assertRaises(ContractShapeError) as caught:
            validation._validate_axis_fields(dict(axis_id=1, direction="x"), 0, path="/coordinates/axes/0")
        self.assertEqual("/coordinates/axes/0/axis_id", caught.exception.path)
        coordinates = dict(
            kind="applicable",
            reference_frame_id="test.frame",
            handedness="right",
            axes=[dict(axis_id="test.x", direction="forward", sign_convention="positive"), dict(axis_id="test.x", direction="", sign_convention="positive")],
        )
        with self.assertRaises(ContractValidationError) as caught:
            validation._validate_coordinates_fields(coordinates, 2)
        self.assertEqual("/axes/1/axis_id", caught.exception.path)
        with self.assertRaises(ContractValidationError) as caught:
            validation._validate_enumeration_fields(
                dict(members=[dict(code="test.a", label="A", kind="known"), dict(code="test.a", label="", kind="known")]), 2
            )
        self.assertEqual("/members/1/code", caught.exception.path)

    def test_null_tag_does_not_hide_later_shape_errors(self) -> None:
        self.assertContract(ContractShapeError, "/reference_frame_id", models.CoordinateSpec, kind=None, reference_frame_id=1)
        self.assertContract(ContractShapeError, "/axes/0", models.CoordinateSpec, kind=None, axes=[object()])
        self.assertContract(CanonicalJSONError, "/kind", models.CoordinateSpec, kind=None)

    def test_default_collection_limit_accepts_65535_members(self) -> None:
        members = tuple(models.EnumerationMember(code=f"test.member_{index:05d}", label="Member", kind="known") for index in range(65535))
        self.assertEqual(65535, len(cast(tuple[models.EnumerationMember, ...], models.EnumerationSpec(members=members).members)))

    def test_mapping_unknown_property_uses_json_pointer_escaping(self) -> None:
        from xplane_fdau.measurements import _definition_validation as validation

        with self.assertRaises(ContractShapeError) as caught:
            validation._validate_axis_fields(
                dict(axis_id="test.x", direction="x", sign_convention="positive") | {"extra~/name": 1}, 0, path="/coordinates/axes/0"
            )
        self.assertEqual("/coordinates/axes/0/extra~0~1name", caught.exception.path)


class MeasurementDefinitionTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertTrue(hasattr(models, "MeasurementDefinition"), "measurement definition has not been delivered")
        from xplane_fdau.contracts import Authority, ProvenanceSource, RepresentationSpec, UnitSpec

        self.fields: dict[str, Any] = dict(
            definition_id="test.definition",
            definition_revision=1,
            authority=Authority(authority_id="test.authority", authority_revision=1),
            provenance=[ProvenanceSource(source_id="test.source", scope="Synthetic", source_revision=1)],
            title="Synthetic",
            description="Synthetic measurement",
            limitations=[],
            quantity_id="test.quantity",
            representation=RepresentationSpec(kind="real"),
            unit=UnitSpec(kind="unitless"),
            coordinates=models.CoordinateSpec(kind="not_applicable"),
            freshness=models.FreshnessSpec(fresh_for_ns=0),
            interpolation_policy="hold",
            discontinuity_policy="preserve",
            allowed_validity=["valid"],
            allowed_quality=[],
            sensitivity="unknown",
            applicability=[],
            numeric=models.NumericSpec(storage_precision_bits=64, resolution=1.0),
        )

    def make(self, **changes: Any) -> Any:
        return models.MeasurementDefinition(**(self.fields | changes))

    def assertInvalid(self, error: type[FDAUContractError], path: str, **changes: Any) -> None:
        with self.assertRaises(error) as caught:
            self.make(**changes)
        self.assertEqual(path, caught.exception.path)
        self.assertEqual("<memory>", caught.exception.source)
        self.assertIsNone(caught.exception.line)
        self.assertIsNone(caught.exception.column)

    def test_representation_matrix(self) -> None:
        from xplane_fdau.contracts import PayloadSpec, RepresentationSpec, ScalarRepresentation, UnitSpec, ValueRepresentation

        enumeration = models.EnumerationSpec(members=[models.EnumerationMember(code="test.code", label="Code", kind="known")])
        for kind in ValueRepresentation:
            elements = list(ScalarRepresentation) if kind in ("fixed_array", "variable_array") else [None]
            for element in elements:
                with self.subTest(kind=kind, element=element):
                    shape: dict[str, Any] = dict(kind=kind)
                    if element is not None:
                        shape["element_representation"] = element
                    if kind in ("vector", "fixed_array"):
                        shape["length"] = 2
                    if kind == "variable_array":
                        shape.update(minimum_length=0, maximum_length=2)
                    if kind == "referenced_bytes":
                        shape["payload"] = PayloadSpec(allowed_media_types=["application/octet-stream"], allowed_storage_roles=["test.role"])
                    selected = element or kind
                    numeric = selected in ("integer", "real", "vector")
                    fields: dict[str, Any] = self.fields | dict(representation=RepresentationSpec(**shape))
                    fields.pop("numeric")
                    if numeric:
                        fields["numeric"] = models.NumericSpec(storage_precision_bits=64, resolution=1 if selected == "integer" else 1.0)
                    if selected == "enumeration":
                        fields["enumeration"] = enumeration
                    model = models.MeasurementDefinition(**fields)
                    self.assertEqual(kind, model.representation.kind)
                    for name, value, needed in (("numeric", self.fields["numeric"], numeric), ("enumeration", enumeration, selected == "enumeration")):
                        bad = fields.copy()
                        if needed:
                            bad.pop(name)
                        else:
                            bad[name] = value
                        with self.assertRaises(ContractValidationError) as caught:
                            models.MeasurementDefinition(**bad)
                        self.assertEqual("/" + name, caught.exception.path)
                    linear_fields: dict[str, Any] = fields | {"interpolation_policy": "linear"}
                    if kind in ("real", "vector") or (element in ("integer", "real")):
                        models.MeasurementDefinition(**linear_fields)
                    else:
                        with self.assertRaises(ContractValidationError) as caught:
                            models.MeasurementDefinition(**linear_fields)
                        self.assertEqual("/interpolation_policy", caught.exception.path)
                    fields["unit"] = UnitSpec(kind="unit", quantity_id="test.quantity", unit_id="test.unit")
                    if numeric:
                        models.MeasurementDefinition(**fields)
                    else:
                        with self.assertRaises(ContractValidationError) as caught:
                            models.MeasurementDefinition(**fields)
                        self.assertEqual("/unit", caught.exception.path)

    def test_numeric_domains_and_cross_fields(self) -> None:
        from xplane_fdau.contracts import RepresentationSpec, UnitSpec

        self.assertInvalid(ContractShapeError, "/numeric/resolution", numeric=models.NumericSpec(storage_precision_bits=64, resolution=1))
        for kind in ("integer", "fixed_array", "variable_array", "vector"):
            fields: dict[str, Any] = dict(kind=kind)
            if kind in ("fixed_array", "variable_array"):
                fields["element_representation"] = "integer"
            if kind in ("fixed_array", "vector"):
                fields["length"] = 2
            if kind == "variable_array":
                fields.update(minimum_length=0, maximum_length=2)
            representation = RepresentationSpec(**fields)
            if kind != "vector":
                self.assertInvalid(ContractShapeError, "/numeric/resolution", representation=representation)
                numeric = models.NumericSpec(storage_precision_bits=64, resolution=1, minimum=-(2**63), maximum=2**63 - 1)
            else:
                numeric = self.fields["numeric"]
            if kind == "integer":
                self.assertInvalid(
                    ContractValidationError, "/interpolation_policy", representation=representation, numeric=numeric, interpolation_policy="linear"
                )
            else:
                self.make(representation=representation, numeric=numeric, interpolation_policy="linear")
        self.assertInvalid(ContractValidationError, "/unit/quantity_id", unit=UnitSpec(kind="unit", quantity_id="test.other", unit_id="test.unit"))
        axes = [models.AxisSpec(axis_id=f"test.axis_{i}", direction="forward", sign_convention="positive") for i in range(2)]
        coordinates = models.CoordinateSpec(kind="applicable", reference_frame_id="test.frame", handedness="right", axes=axes)
        self.assertInvalid(ContractValidationError, "/coordinates/axes", coordinates=coordinates)
        self.make(representation=RepresentationSpec(kind="vector", length=2), coordinates=coordinates)
        self.assertInvalid(ContractValidationError, "/coordinates/axes", representation=RepresentationSpec(kind="vector", length=3), coordinates=coordinates)
        with self.assertRaises(ContractShapeError):
            RepresentationSpec(kind="fixed_array", element_representation="vector", length=2)

    def test_binary64_triples_for_real_vector_and_real_arrays(self) -> None:
        from xplane_fdau.contracts import RepresentationSpec
        from xplane_fdau.measurements._definition_validation import _validate_definition_fields

        representations: tuple[dict[str, Any], ...] = (
            dict(kind="real"),
            dict(kind="vector", length=2),
            dict(kind="fixed_array", element_representation="real", length=2),
            dict(kind="variable_array", element_representation="real", minimum_length=0, maximum_length=2),
        )
        triple: dict[str, Any] = dict(storage_precision_bits=64, resolution=1.0, minimum=0.0, maximum=2.0)
        for representation in representations:
            with self.subTest(kind=representation["kind"], case="binary64 acceptance"):
                numeric = models.NumericSpec(**triple)
                definition = self.make(representation=RepresentationSpec(**representation), numeric=numeric)
                self.assertIs(numeric, definition.numeric)
                for field in ("resolution", "minimum", "maximum"):
                    self.assertIs(float, type(getattr(numeric, field)))
                for phase in range(3):
                    _validate_definition_fields(self.raw() | dict(representation=representation, numeric=triple), phase)
            # Plain mappings isolate each bound mismatch from NumericSpec's own
            # constructor, proving the enclosing definition rejects the integer.
            for field in ("resolution", "minimum", "maximum"):
                with self.subTest(kind=representation["kind"], integer_field=field):
                    fields = self.raw() | dict(representation=representation, numeric=triple | {field: 1})
                    with self.assertRaises(ContractShapeError) as caught:
                        for phase in range(3):
                            _validate_definition_fields(fields, phase)
                    self.assertEqual("/numeric/" + field, caught.exception.path)

    def test_metadata_and_collections(self) -> None:
        from xplane_fdau.contracts import ProvenanceSource

        self.make(title="t" * 256, description="d" * 4096, limitations=["l" * 1024])
        for name, bad, error, path in (
            ("title", "t" * 257, ContractValidationError, "/title"),
            ("description", "d" * 4097, ContractValidationError, "/description"),
            ("limitations", [""], ContractValidationError, "/limitations/0"),
            ("limitations", ["l" * 1025], ContractValidationError, "/limitations/0"),
            ("limitations", ["a", "a"], ContractValidationError, "/limitations/1"),
            ("limitations", ["x"] * 257, ContractShapeError, "/limitations"),
            ("provenance", [], ContractValidationError, "/provenance"),
            ("provenance", self.fields["provenance"] * 2, ContractValidationError, "/provenance/1"),
            ("provenance", self.fields["provenance"] * 257, ContractShapeError, "/provenance"),
            ("allowed_validity", [], ContractValidationError, "/allowed_validity"),
            ("allowed_validity", ["valid", "invalid"], ContractValidationError, "/allowed_validity/1"),
            ("allowed_validity", ["valid", "valid"], ContractValidationError, "/allowed_validity/1"),
            ("allowed_quality", ["stale", "stale"], ContractValidationError, "/allowed_quality/1"),
            ("allowed_quality", ["stale", "dropped"], ContractValidationError, "/allowed_quality/1"),
            ("allowed_quality", ["future"], ContractShapeError, "/allowed_quality/0"),
            ("definition_id", "bad", ContractValidationError, "/definition_id"),
            ("definition_revision", 0, ContractValidationError, "/definition_revision"),
            ("definition_revision", 2**63, CanonicalJSONError, "/definition_revision"),
            ("definition_revision", True, ContractShapeError, "/definition_revision"),
        ):
            self.assertInvalid(error, path, **{name: bad})
        selectors = [models.ApplicabilitySelector(class_id="test.a", value="A"), models.ApplicabilitySelector(class_id="test.b", value="B")]
        self.make(applicability=selectors)
        self.assertInvalid(ContractValidationError, "/applicability/1/class_id", applicability=selectors[::-1])
        self.assertInvalid(ContractValidationError, "/applicability/1/class_id", applicability=selectors[:1] * 2)
        self.assertInvalid(ContractShapeError, "/applicability", applicability=selectors[:1] * 257)
        sources = [ProvenanceSource(source_id="test.z", scope="Z", source_revision=1), ProvenanceSource(source_id="test.a", scope="A", source_version="1")]
        self.assertEqual(tuple(sources), self.make(provenance=sources).provenance)
        self.make(allowed_validity=["invalid"], allowed_quality=[])

    def test_constructor_signature_order(self) -> None:
        required = [
            "definition_id",
            "definition_revision",
            "authority",
            "provenance",
            "title",
            "description",
            "limitations",
            "quantity_id",
            "representation",
            "unit",
            "coordinates",
            "freshness",
            "interpolation_policy",
            "discontinuity_policy",
            "allowed_validity",
            "allowed_quality",
            "sensitivity",
            "applicability",
        ]
        parameters = inspect.signature(models.MeasurementDefinition).parameters
        self.assertEqual([*required, "numeric", "enumeration"], list(parameters))
        for name, parameter in parameters.items():
            self.assertIs(inspect.Parameter.KEYWORD_ONLY, parameter.kind)
            self.assertIs(inspect.Parameter.empty if name in required else _OMITTED, parameter.default)
        for name in required:
            fields = self.fields.copy()
            fields.pop(name)
            with self.assertRaises(TypeError):
                models.MeasurementDefinition(**fields)
        with self.assertRaises(TypeError):
            self.make(content_hash="0" * 64)

    def test_nulls_ownership_immutability_and_no_iterable_consumption(self) -> None:
        for name in self.fields:
            self.assertInvalid(CanonicalJSONError, "/" + name, **{name: None})
        for name in ("authority", "representation", "unit", "coordinates", "freshness", "numeric"):
            self.assertInvalid(ContractShapeError, "/" + name, **{name: {}})
        self.assertInvalid(ContractShapeError, "/provenance/0", provenance=[{}])
        self.assertInvalid(ContractShapeError, "/applicability/0", applicability=[{}])

        def forbidden() -> Any:
            raise AssertionError("consumed iterator")
            yield

        self.assertInvalid(ContractShapeError, "/limitations", limitations=forbidden())
        self.assertInvalid(ContractShapeError, "/limitations", limitations={"x"})
        limitations = ["z", "a"]
        model = self.make(limitations=limitations)
        limitations.append("changed")
        self.assertEqual(("z", "a"), model.limitations)
        self.assertEqual(tuple(self.fields["provenance"]), model.provenance)
        self.assertFalse(hasattr(model, "__dict__"))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            model.title = "changed"
        self.assertEqual(models.InterpolationPolicy.HOLD, model.interpolation_policy)
        self.assertEqual(models.DiscontinuityPolicy.PRESERVE, model.discontinuity_policy)
        self.assertEqual(models.Sensitivity.UNKNOWN, model.sensitivity)
        self.assertIs(self.fields["authority"], model.authority)

    def raw(self) -> dict[str, Any]:
        from xplane_fdau.contracts.provenance import _authority_wire, _provenance_source_wire
        from xplane_fdau.contracts.values import _representation_spec_wire, _unit_spec_wire

        return self.fields | dict(
            authority=_authority_wire(self.fields["authority"]),
            provenance=[_provenance_source_wire(s) for s in self.fields["provenance"]],
            representation=_representation_spec_wire(self.fields["representation"]),
            unit=_unit_spec_wire(self.fields["unit"]),
            coordinates=dict(kind="not_applicable"),
            numeric=dict(storage_precision_bits=64, resolution=1.0),
            freshness=dict(fresh_for_ns=0),
        )

    def test_validation_order_is_independent_of_signature_order(self) -> None:
        from xplane_fdau.measurements._definition_validation import _validate_definition_fields

        fields = self.raw() | dict(numeric=dict(storage_precision_bits=64, resolution=0.0), freshness=dict(fresh_for_ns=2, stale_after_ns=1))
        with self.assertRaises(ContractValidationError) as caught:
            _validate_definition_fields(fields, 2)
        self.assertEqual("/numeric/resolution", caught.exception.path)
        fields = self.raw() | dict(unit=dict(kind="unit", quantity_id="test.other", unit_id="test.unit"), applicability=[dict(class_id="test.a", value=1)])
        with self.assertRaises(ContractShapeError) as caught:
            for phase in range(3):
                _validate_definition_fields(fields, phase)
        self.assertEqual("/applicability/0/value", caught.exception.path)
        self.assertInvalid(ContractShapeError, "/sensitivity", title="e\u0301", sensitivity=1)
        self.assertInvalid(ContractShapeError, "/title", title=1, applicability=[{}])
        self.assertInvalid(ContractShapeError, "/applicability/0", quantity_id="bad", applicability=[{}])

    def test_plain_mapping_validation_has_no_build_side_effects(self) -> None:
        from unittest.mock import patch

        from xplane_fdau.contracts import Authority, RepresentationSpec
        from xplane_fdau.measurements._definition_validation import _validate_definition_fields

        with (
            patch.object(Authority, "__post_init__", side_effect=AssertionError("built authority")),
            patch.object(RepresentationSpec, "__post_init__", side_effect=AssertionError("built representation")),
        ):
            for phase in range(3):
                _validate_definition_fields(self.raw(), phase, path="/entry")
        fields = self.raw() | {"sensitive~/payload": "DO_NOT_ECHO"}
        with self.assertRaises(ContractShapeError) as caught:
            _validate_definition_fields(fields, 0)
        self.assertEqual("/sensitive~0~1payload", caught.exception.path)
        self.assertNotIn("DO_NOT_ECHO", str(caught.exception))

    def test_cross_field_errors_retain_nested_semantic_order(self) -> None:
        from xplane_fdau.measurements._definition_validation import _validate_definition_fields

        cases = (
            (dict(unit=dict(kind="unit", quantity_id="test.other", unit_id="bad")), "/unit/quantity_id"),
            (dict(representation=dict(kind="boolean"), numeric=dict(storage_precision_bits=64, resolution=0.0)), "/numeric"),
            (
                dict(
                    coordinates=dict(
                        kind="applicable",
                        reference_frame_id="test.frame",
                        handedness="right",
                        axes=[dict(axis_id="bad", direction="forward", sign_convention="positive")] * 2,
                    )
                ),
                "/coordinates/axes",
            ),
            (
                dict(
                    provenance=[
                        dict(source_id="test.source", scope="Synthetic", source_revision=1),
                        dict(source_id="test.source", scope="Synthetic", source_revision=1, locator=""),
                    ]
                ),
                "/provenance/1",
            ),
        )
        for changes, path in cases:
            with self.subTest(path=path), self.assertRaises(ContractValidationError) as caught:
                for phase in range(3):
                    _validate_definition_fields(self.raw() | changes, phase)
            self.assertEqual(path, caught.exception.path)

    def test_raw_nested_shape_domain_and_semantic_staging(self) -> None:
        from xplane_fdau.measurements._definition_validation import _validate_definition_fields

        cases = (
            (dict(authority=dict(authority_id="e\u0301", authority_revision=True)), ContractShapeError, "/authority/authority_revision"),
            (dict(provenance=[dict(source_id="test.source", scope="Synthetic", source_revision=None)]), CanonicalJSONError, "/provenance/0/source_revision"),
            (dict(provenance=[dict(source_id="test.source", scope="Synthetic")]), ContractValidationError, "/provenance/0/source_revision"),
            (
                dict(provenance=[dict(source_id="test.source", scope="Synthetic", source_revision=1, source_version="1")]),
                ContractValidationError,
                "/provenance/0/source_version",
            ),
            (
                dict(provenance=[dict(source_id="test.source", scope="Synthetic", source_version="x\x00")]),
                ContractValidationError,
                "/provenance/0/source_version",
            ),
            (dict(representation=dict(kind=None, length=True)), ContractShapeError, "/representation/length"),
            (dict(representation=dict(kind=None)), CanonicalJSONError, "/representation/kind"),
            (dict(representation=dict(kind="vector", length=0)), ContractValidationError, "/representation/length"),
            (
                dict(representation=dict(kind="referenced_bytes", payload=dict(allowed_media_types=["invalid"], allowed_storage_roles=[1]))),
                ContractShapeError,
                "/representation/payload/allowed_storage_roles/0",
            ),
            (dict(title="e\u0301", allowed_quality=["future"]), ContractShapeError, "/allowed_quality/0"),
            (
                dict(unit=dict(kind="unit", quantity_id="test.other", unit_id="test.unit"), applicability=[dict(class_id="test.a", value="e\u0301")]),
                CanonicalJSONError,
                "/applicability/0/value",
            ),
            (dict(numeric=dict(storage_precision_bits=0, resolution=0.0)), ContractValidationError, "/numeric/storage_precision_bits"),
            (dict(numeric=dict(storage_precision_bits=64, resolution=1.0, minimum=1)), ContractShapeError, "/numeric/minimum"),
            (dict(numeric=dict(storage_precision_bits=64, resolution=1.0, maximum=float("inf"))), CanonicalJSONError, "/numeric/maximum"),
        )
        for changes, error, path in cases:
            with self.subTest(path=path), self.assertRaises(error) as caught:
                for phase in range(3):
                    _validate_definition_fields(self.raw() | changes, phase)
            self.assertEqual(path, caught.exception.path)

    def test_null_resolution_does_not_select_an_integer_domain(self) -> None:
        from xplane_fdau.measurements._definition_validation import _validate_definition_fields

        fields = self.raw() | dict(numeric=dict(storage_precision_bits=64, resolution=None, minimum=1.0))
        with self.assertRaises(FDAUContractError) as caught:
            for phase in range(3):
                _validate_definition_fields(fields, phase)
        self.assertIsInstance(caught.exception, CanonicalJSONError)
        self.assertEqual("/numeric/resolution", caught.exception.path)

    def test_every_definition_sequence_is_copied_and_bounded(self) -> None:
        from xplane_fdau.contracts import ProvenanceSource

        provenance = list(self.fields["provenance"])
        limitations = ["z", "a"]
        validity = ["invalid", "valid"]
        quality = ["dropped", "stale"]
        applicability = [models.ApplicabilitySelector(class_id="test.a", value="A")]
        definition = self.make(provenance=provenance, limitations=limitations, allowed_validity=validity, allowed_quality=quality, applicability=applicability)
        for items in (provenance, limitations, validity, quality, applicability):
            items.clear()
        self.assertEqual(("z", "a"), definition.limitations)
        self.assertEqual(("invalid", "valid"), definition.allowed_validity)
        self.assertEqual(("dropped", "stale"), definition.allowed_quality)
        self.assertEqual("test.source", definition.provenance[0].source_id)
        self.assertEqual("test.a", definition.applicability[0].class_id)
        self.make(
            provenance=[ProvenanceSource(source_id="test.source", scope="Synthetic", source_revision=i + 1) for i in range(256)],
            limitations=[str(i) for i in range(256)],
            applicability=[models.ApplicabilitySelector(class_id=f"test.class_{i:03}", value="A") for i in range(256)],
        )
        for name in ("provenance", "limitations", "allowed_validity", "allowed_quality", "applicability"):
            self.assertInvalid(ContractShapeError, "/" + name, **{name: iter(())})
