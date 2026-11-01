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
