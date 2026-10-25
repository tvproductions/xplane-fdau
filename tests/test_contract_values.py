"""Behavioral contracts for exact values and metadata-only payload claims."""

import copy
import json
import math
import pickle
import unittest
from dataclasses import FrozenInstanceError
from typing import override
from unittest import mock

from xplane_fdau.contracts import _value_io, canonical_bytes
from xplane_fdau.contracts._json_parse import _parse_json_document
from xplane_fdau.contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError
from xplane_fdau.contracts.values import InlineValue, PayloadReference, PayloadSpec, RepresentationSpec, RetentionStatus, ShapeSpec, UnitSpec


class InlineValueTests(unittest.TestCase):
    def test_numeric_representations_reject_coercion(self) -> None:
        for representation, value in (("integer", True), ("real", True), ("real", 1), ("boolean", 1)):
            with self.subTest(representation=representation, value=value):
                with self.assertRaises(ContractShapeError) as caught:
                    InlineValue(representation=representation, value=value)
                self.assertEqual("/value", caught.exception.path)
        self.assertIs(type(InlineValue(representation="integer", value=1).value), int)
        self.assertIs(type(InlineValue(representation="real", value=1.0).value), float)

    def test_scalar_domain_boundaries(self) -> None:
        accepted = (
            ("integer", -(2**63)),
            ("integer", 2**63 - 1),
            ("real", -0.0),
            ("real", float.fromhex("0x0.0000000000001p-1022")),
            ("real", float.fromhex("0x1.fffffffffffffp+1023")),
            ("string", "x"),
            ("string", "x" * 16384),
            ("enumeration", "test.unknown"),
            ("enumeration", "test.reserved"),
        )
        for representation, value in accepted:
            with self.subTest(representation=representation):
                self.assertEqual(value, InlineValue(representation=representation, value=value).value)
        rejected = (
            ("integer", 2**63, CanonicalJSONError),
            ("integer", -(2**63) - 1, CanonicalJSONError),
            ("real", math.nan, CanonicalJSONError),
            ("real", math.inf, CanonicalJSONError),
            ("string", "", ContractValidationError),
            ("string", "x" * 16385, ContractValidationError),
            ("string", "e\u0301", CanonicalJSONError),
            ("string", "\ud800", CanonicalJSONError),
            ("enumeration", "Reserved", ContractValidationError),
        )
        for representation, value, error in rejected:
            with self.subTest(representation=representation):
                with self.assertRaises(error) as caught:
                    InlineValue(representation=representation, value=value)
                self.assertEqual("/value", caught.exception.path)

    def test_sequences_copy_preserve_order_and_exact_element_type(self) -> None:
        original = [2.0, 1.0]
        vector = InlineValue(representation="vector", value=original)
        original[0] = 99.0
        self.assertEqual((2.0, 1.0), vector.value)
        for representation in ("fixed_array", "variable_array"):
            for element, values in (
                ("boolean", [True, False]),
                ("integer", [2, 1]),
                ("real", [2.0, 1.0]),
                ("string", ["b", "a"]),
                ("enumeration", ["test.b", "test.a"]),
            ):
                with self.subTest(representation=representation, element=element):
                    value = InlineValue(representation=representation, element_representation=element, value=values)
                    self.assertEqual(tuple(values), value.value)
            self.assertEqual((), InlineValue(representation=representation, element_representation="integer", value=[]).value)
        for values in ([1], [True], [[1.0]]):
            with self.assertRaises(ContractShapeError) as caught:
                InlineValue(representation="vector", value=values)
            self.assertEqual("/value/0", caught.exception.path)
        with self.assertRaises(ContractShapeError):
            InlineValue(representation="fixed_array", element_representation="integer", value=[1, True])

    def test_variants_reject_missing_irrelevant_and_byte_values(self) -> None:
        for args in (
            {"representation": "referenced_bytes", "value": b"x"},
            {"representation": "unknown", "value": 1},
            {"representation": "integer", "value": 1, "element_representation": None},
            {"representation": "fixed_array", "value": []},
            {"representation": "fixed_array", "element_representation": "vector", "value": []},
        ):
            with self.subTest(args=args), self.assertRaises(ContractShapeError):
                InlineValue(**args)  # ty: ignore[invalid-argument-type]  # intentionally malformed fields

    def test_vector_bounds_and_frozen_model(self) -> None:
        vector = InlineValue(representation="vector", value=[0.0] * 65535)
        self.assertIsInstance(vector.value, tuple)
        self.assertEqual(65535, len(vector.value))  # ty: ignore[invalid-argument-type]
        for values in ([], [0.0] * 65536):
            with self.assertRaises(ContractValidationError):
                InlineValue(representation="vector", value=values)
        value = InlineValue(representation="integer", value=1)
        with self.assertRaises(FrozenInstanceError):
            value.value = 2  # ty: ignore[invalid-assignment]
        self.assertFalse(hasattr(value, "__dict__"))
        with self.assertRaises(TypeError):
            InlineValue("integer", 1)  # ty: ignore[missing-argument, too-many-positional-arguments]


class PayloadReferenceTests(unittest.TestCase):
    def claim(self, **changes: object) -> PayloadReference:
        fields = {
            "media_type": "application/octet-stream",
            "byte_length": 0,
            "sha256": "a" * 64,
            "storage_role": "test.raw_payload",
            "retention_status": "retained",
        }
        return PayloadReference(**(fields | changes))  # ty: ignore[invalid-argument-type]

    def test_original_metadata_survives_every_retention_status_without_io(self) -> None:
        with (
            mock.patch("builtins.open", side_effect=AssertionError("unexpected storage access")),
            mock.patch("pathlib.Path.open", side_effect=AssertionError("unexpected storage access")),
        ):
            for status in RetentionStatus:
                for length in (0, 2**63 - 1):
                    claim = self.claim(retention_status=status, byte_length=length)
                    self.assertEqual(
                        ("application/octet-stream", length, "a" * 64, "test.raw_payload", status),
                        (claim.media_type, claim.byte_length, claim.sha256, claim.storage_role, claim.retention_status),
                    )

    def test_invalid_claim_fields_report_their_property(self) -> None:
        cases = (
            ("byte_length", True, ContractShapeError),
            ("byte_length", -1, ContractValidationError),
            ("byte_length", 2**63, CanonicalJSONError),
            ("sha256", "A" * 64, ContractValidationError),
            ("sha256", "a" * 63, ContractValidationError),
            ("storage_role", "raw", ContractValidationError),
            ("retention_status", "unknown", ContractShapeError),
        )
        for field, value, error in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaises(error) as caught:
                    self.claim(**{field: value})
                self.assertEqual("/" + field, caught.exception.path)

    def test_media_type_grammar_and_total_bound(self) -> None:
        self.assertEqual("a/" + "b" * 125, self.claim(media_type="a/" + "b" * 125).media_type)
        for media in ("Application/json", "application/json;charset=utf-8", "application/ json", "a/b/c", "a/", "/b", "a/" + "b" * 126, "", " a/b"):
            with self.subTest(media=media):
                with self.assertRaises(ContractValidationError) as caught:
                    self.claim(media_type=media)
                self.assertEqual("/media_type", caught.exception.path)


class DeclarationTests(unittest.TestCase):
    def test_allow_list_count_limits_are_distinct_from_entry_validation(self) -> None:
        for field, prefix in (("allowed_media_types", "a/x"), ("allowed_storage_roles", "test.x")):
            with self.subTest(field=field):
                values = [f"{prefix}{index:05d}" for index in range(65535)]
                arguments = {"allowed_media_types": ["a/b"], "allowed_storage_roles": ["test.raw"]}
                arguments[field] = values
                declared = PayloadSpec(**arguments)
                self.assertEqual(tuple(values), getattr(declared, field))
                arguments[field] = [*values, f"{prefix}65535"]
                with self.assertRaises(ContractValidationError) as caught:
                    PayloadSpec(**arguments)
                self.assertEqual("/" + field, caught.exception.path)

    def test_all_owned_metadata_models_are_frozen_slotted_and_keyword_only(self) -> None:
        payload = PayloadSpec(allowed_media_types=["a/b"], allowed_storage_roles=["test.raw"])
        cases = (
            (
                PayloadReference(media_type="a/b", byte_length=1, sha256="a" * 64, storage_role="test.raw", retention_status="retained"),
                ("a/b", 1, "a" * 64, "test.raw", "retained"),
                "byte_length",
                2,
            ),
            (payload, (["a/b"], ["test.raw"]), "allowed_media_types", ("a/c",)),
            (RepresentationSpec(kind="integer"), ("integer",), "kind", "real"),
            (ShapeSpec(kind="scalar"), ("scalar",), "kind", "fixed"),
            (UnitSpec(kind="unitless"), ("unitless",), "kind", "unit"),
        )
        for value, positional, attribute, replacement in cases:
            with self.subTest(model=type(value).__name__):
                self.assertRaises(FrozenInstanceError, setattr, value, attribute, replacement)
                self.assertRaises(TypeError, vars, value)
                self.assertRaises(TypeError, type(value), *positional)

    def test_shape_errors_precede_canonical_and_semantic_errors_across_fields(self) -> None:
        for minimum in (-1, 2**63):
            with self.subTest(minimum=minimum), self.assertRaises(ContractShapeError) as caught:
                RepresentationSpec(kind="variable_array", element_representation="integer", minimum_length=minimum, maximum_length="wrong")
            self.assertEqual("/maximum_length", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            PayloadReference(media_type="\ud801", byte_length=True, sha256="a" * 64, storage_role="test.raw", retention_status="retained")
        self.assertEqual("/byte_length", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            PayloadSpec(allowed_media_types=["a/c", "a/b"], allowed_storage_roles=[True])
        self.assertEqual("/allowed_storage_roles/0", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            PayloadSpec(allowed_media_types=None, allowed_storage_roles=[True])
        self.assertEqual("/allowed_storage_roles/0", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            RepresentationSpec(kind="vector", length=None, maximum_length=1)
        self.assertEqual("/maximum_length", caught.exception.path)

    def test_variant_names_require_exact_strings(self) -> None:
        class CallerString(str):
            """A caller wrapper must be normalized before entering the data domain."""

        for constructor, kind in ((ShapeSpec, "scalar"), (UnitSpec, "unitless")):
            with self.subTest(model=constructor.__name__), self.assertRaises(ContractShapeError) as caught:
                constructor(kind=CallerString(kind))
            self.assertEqual("/kind", caught.exception.path)

    def test_owned_payload_and_serializer_reject_type_equality_spoofs(self) -> None:
        class EqualityType(type):
            @override
            def __eq__(cls, other: object) -> bool:
                return True

            @override
            def __ne__(cls, other: object) -> bool:
                return False

            __hash__ = type.__hash__

        class CallerObject(metaclass=EqualityType):
            """Type equality does not make an object an owned contract model."""

        value = CallerObject()
        with self.assertRaises(ContractShapeError) as caught:
            RepresentationSpec(kind="referenced_bytes", payload=value)
        self.assertEqual("/payload", caught.exception.path)
        with self.assertRaises(CanonicalJSONError) as caught:
            canonical_bytes(value)
        self.assertEqual("", caught.exception.path)

    def test_array_domains_precede_semantics_across_elements(self) -> None:
        for representation, values in (("string", ["", "\u1f71"]), ("enumeration", ["Bad", "\u1f71"])):
            with self.subTest(representation=representation), self.assertRaises(CanonicalJSONError) as caught:
                InlineValue(representation="fixed_array", element_representation=representation, value=values)
            self.assertEqual("/value/1", caught.exception.path)
        with self.assertRaises(CanonicalJSONError) as caught:
            InlineValue(representation="vector", value=[float("inf"), *([0.0] * 65535)])
        self.assertEqual("/value/0", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            InlineValue(representation="fixed_array", element_representation="integer", value=[None, "wrong"])
        self.assertEqual("/value/1", caught.exception.path)

    def test_representation_variants_and_bounds(self) -> None:
        for kind in ("boolean", "integer", "real", "string", "enumeration"):
            self.assertEqual(kind, RepresentationSpec(kind=kind).kind)
        for kind, args in (
            ("vector", {"length": 1}),
            ("vector", {"length": 1024}),
            ("fixed_array", {"element_representation": "integer", "length": 65535}),
            ("variable_array", {"element_representation": "real", "minimum_length": 0, "maximum_length": 0}),
            ("referenced_bytes", {"payload": PayloadSpec(allowed_media_types=["a/b"], allowed_storage_roles=["test.raw"])}),
        ):
            self.assertEqual(kind, RepresentationSpec(kind=kind, **args).kind)
        for args in (
            {"kind": "vector", "length": 0},
            {"kind": "vector", "length": 1025},
            {"kind": "fixed_array", "element_representation": "integer", "length": 65536},
            {"kind": "variable_array", "element_representation": "real", "minimum_length": 2, "maximum_length": 1},
        ):
            with self.subTest(args=args), self.assertRaises(ContractValidationError):
                RepresentationSpec(**args)  # ty: ignore[invalid-argument-type]
        for args in (
            {"kind": "vector"},
            {"kind": "vector", "length": True},
            {"kind": "integer", "length": None},
            {"kind": "referenced_bytes", "payload": {}},
            {"kind": "fixed_array", "length": 1, "element_representation": "vector"},
        ):
            with self.subTest(args=args), self.assertRaises(ContractShapeError):
                RepresentationSpec(**args)  # ty: ignore[invalid-argument-type]
        with self.assertRaises(CanonicalJSONError):
            RepresentationSpec(kind="vector", length=2**63)

    def test_payload_allow_lists_are_copied_and_not_sorted_or_deduplicated(self) -> None:
        media = ["a/b", "a/c"]
        roles = ["test.a", "test.b"]
        spec = PayloadSpec(allowed_media_types=media, allowed_storage_roles=roles)
        media[0] = "wrong/type"
        roles.reverse()
        self.assertEqual(("a/b", "a/c"), spec.allowed_media_types)
        self.assertEqual(("test.a", "test.b"), spec.allowed_storage_roles)
        for values in ([], ["a/c", "a/b"], ["a/b", "a/b"], ["a/b"] * 65536):
            with self.subTest(values=values[:2]), self.assertRaises(ContractValidationError):
                PayloadSpec(allowed_media_types=values, allowed_storage_roles=["test.raw"])
        for values in (["raw"], ["test.b", "test.a"], ["test.a", "test.a"]):
            with self.assertRaises(ContractValidationError):
                PayloadSpec(allowed_media_types=["a/b"], allowed_storage_roles=values)

    def test_shape_and_unit_variant_contracts(self) -> None:
        self.assertEqual("scalar", ShapeSpec(kind="scalar").kind)
        self.assertEqual(65535, ShapeSpec(kind="fixed", length=65535).length)
        self.assertEqual(0, ShapeSpec(kind="variable", minimum_length=0, maximum_length=0).maximum_length)
        for args in ({"kind": "fixed", "length": 0}, {"kind": "fixed", "length": 65536}, {"kind": "variable", "minimum_length": 2, "maximum_length": 1}):
            with self.assertRaises(ContractValidationError):
                ShapeSpec(**args)  # ty: ignore[invalid-argument-type]
        for args in ({"kind": "scalar", "length": None}, {"kind": "fixed", "length": True}, {"kind": "variable", "maximum_length": 1}):
            with self.assertRaises(ContractShapeError):
                ShapeSpec(**args)  # ty: ignore[invalid-argument-type]
        self.assertEqual("unitless", UnitSpec(kind="unitless").kind)
        self.assertEqual("test.metre", UnitSpec(kind="unit", quantity_id="test.distance", unit_id="test.metre").unit_id)
        for args in ({"kind": "unitless", "unit_id": None}, {"kind": "unit", "quantity_id": "test.distance"}):
            with self.assertRaises(ContractShapeError):
                UnitSpec(**args)  # ty: ignore[invalid-argument-type]
        with self.assertRaises(ContractValidationError) as caught:
            UnitSpec(kind="unit", quantity_id="distance", unit_id="test.metre")
        self.assertEqual("/quantity_id", caught.exception.path)


class WireValueTests(unittest.TestCase):
    def test_deepcopy_preserves_omitted_variant_fields_and_canonical_bytes(self) -> None:
        cases = (
            (InlineValue(representation="integer", value=1), b'{"representation":"integer","value":1}\n'),
            (RepresentationSpec(kind="boolean"), b'{"kind":"boolean"}\n'),
            (RepresentationSpec(kind="vector", length=2), b'{"kind":"vector","length":2}\n'),
            (ShapeSpec(kind="scalar"), b'{"kind":"scalar"}\n'),
            (UnitSpec(kind="unitless"), b'{"kind":"unitless"}\n'),
        )
        for model, expected in cases:
            with self.subTest(model=model):
                for restored in (copy.deepcopy(model), pickle.loads(pickle.dumps(model))):
                    self.assertEqual(expected, canonical_bytes(restored))
                    self.assertEqual(model, restored)

    def test_mixed_invalid_variants_share_semantic_shape_precedence(self) -> None:
        cases = (
            (
                InlineValue,
                _value_io._inline_value_from_wire,
                {"representation": "integer", "element_representation": None, "value": True},
                "/element_representation",
            ),
            (
                InlineValue,
                _value_io._inline_value_from_wire,
                {"representation": "vector", "element_representation": None, "value": [True]},
                "/element_representation",
            ),
            (
                RepresentationSpec,
                _value_io._representation_spec_from_wire,
                {"kind": "vector", "element_representation": False, "length": True},
                "/element_representation",
            ),
            (
                RepresentationSpec,
                _value_io._representation_spec_from_wire,
                {"kind": "fixed_array", "element_representation": None, "length": True},
                "/element_representation",
            ),
            (ShapeSpec, _value_io._shape_spec_from_wire, {"kind": "variable", "length": None, "minimum_length": False, "maximum_length": 1}, "/length"),
        )
        for cls, reader, fields, path in cases:
            with self.subTest(fields=fields):
                for build in (
                    lambda cls=cls, fields=fields: cls(**fields),  # ty: ignore[invalid-argument-type]  # intentionally invalid constructor input
                    lambda reader=reader, fields=fields: reader(fields),
                    lambda reader=reader, fields=fields: reader(_parse_json_document(json.dumps(fields))),
                ):
                    with self.assertRaises(ContractShapeError) as caught:
                        build()
                    self.assertEqual(path, caught.exception.path)

    def test_null_is_rejected_consistently_for_every_required_value_field(self) -> None:
        cases = (
            (InlineValue, _value_io._inline_value_from_wire, {"representation": "vector", "value": None}, "/value"),
            (
                PayloadReference,
                _value_io._payload_reference_from_wire,
                {"media_type": None, "byte_length": 0, "sha256": "a" * 64, "storage_role": "test.raw", "retention_status": "retained"},
                "/media_type",
            ),
            (PayloadSpec, _value_io._payload_spec_from_wire, {"allowed_media_types": None, "allowed_storage_roles": ["test.raw"]}, "/allowed_media_types"),
            (RepresentationSpec, _value_io._representation_spec_from_wire, {"kind": "vector", "length": None}, "/length"),
            (RepresentationSpec, _value_io._representation_spec_from_wire, {"kind": "referenced_bytes", "payload": None}, "/payload"),
            (ShapeSpec, _value_io._shape_spec_from_wire, {"kind": "fixed", "length": None}, "/length"),
            (UnitSpec, _value_io._unit_spec_from_wire, {"kind": "unit", "quantity_id": None, "unit_id": "test.unit"}, "/quantity_id"),
        )
        for cls, reader, fields, path in cases:
            with self.subTest(model=cls):
                for build in (lambda cls=cls, fields=fields: cls(**fields), lambda reader=reader, fields=fields: reader(fields)):  # ty: ignore[invalid-argument-type]
                    with self.assertRaises(CanonicalJSONError) as caught:
                        build()
                    self.assertEqual(path, caught.exception.path)

    def test_null_and_array_domain_paths_match_programmatic_construction(self) -> None:
        cases = (("integer", None, "/value"), ("vector", [1.0, None], "/value/1"), ("fixed_array", [1, None], "/value/1"))
        for representation, value, path in cases:
            fields = {"representation": representation, "value": value}
            if representation == "fixed_array":
                fields["element_representation"] = "integer"
            with self.subTest(representation=representation):
                for build in (lambda fields=fields: InlineValue(**fields), lambda fields=fields: _value_io._inline_value_from_wire(fields)):  # ty: ignore[invalid-argument-type]
                    with self.assertRaises(CanonicalJSONError) as caught:
                        build()
                    self.assertEqual(path, caught.exception.path)

    def test_declaration_error_precedence_matches_construction(self) -> None:
        cases = (
            (ShapeSpec, _value_io._shape_spec_from_wire, {"kind": "variable", "minimum_length": True}, "/minimum_length"),
            (UnitSpec, _value_io._unit_spec_from_wire, {"kind": "unit", "quantity_id": 1}, "/quantity_id"),
            (
                RepresentationSpec,
                _value_io._representation_spec_from_wire,
                {"kind": "fixed_array", "element_representation": "vector"},
                "/element_representation",
            ),
        )
        for cls, reader, fields, path in cases:
            with self.subTest(fields=fields):
                for build in (lambda cls=cls, fields=fields: cls(**fields), lambda reader=reader, fields=fields: reader(fields)):  # ty: ignore[invalid-argument-type]
                    with self.assertRaises(ContractShapeError) as caught:
                        build()
                    self.assertEqual(path, caught.exception.path)

    def test_literal_canonical_vectors_and_parsed_roundtrips(self) -> None:
        cases = (
            (InlineValue(representation="integer", value=1), "inline_value", b'{"representation":"integer","value":1}\n'),
            (InlineValue(representation="real", value=1.0), "inline_value", b'{"representation":"real","value":1.0}\n'),
            (InlineValue(representation="vector", value=[2.0, 1.0]), "inline_value", b'{"representation":"vector","value":[2.0,1.0]}\n'),
            (
                InlineValue(representation="fixed_array", element_representation="boolean", value=[True, False]),
                "inline_value",
                b'{"element_representation":"boolean","representation":"fixed_array","value":[true,false]}\n',
            ),
            (
                PayloadReference(media_type="a/b", byte_length=2, sha256="a" * 64, storage_role="test.raw", retention_status="missing"),
                "payload_reference",
                b'{"byte_length":2,"media_type":"a/b","retention_status":"missing","sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","storage_role":"test.raw"}\n',
            ),
            (
                PayloadSpec(allowed_media_types=["a/b"], allowed_storage_roles=["test.raw"]),
                "payload_spec",
                b'{"allowed_media_types":["a/b"],"allowed_storage_roles":["test.raw"]}\n',
            ),
            (RepresentationSpec(kind="integer"), "representation_spec", b'{"kind":"integer"}\n'),
            (RepresentationSpec(kind="vector", length=2), "representation_spec", b'{"kind":"vector","length":2}\n'),
            (
                RepresentationSpec(kind="fixed_array", element_representation="real", length=2),
                "representation_spec",
                b'{"element_representation":"real","kind":"fixed_array","length":2}\n',
            ),
            (
                RepresentationSpec(kind="variable_array", element_representation="real", minimum_length=0, maximum_length=2),
                "representation_spec",
                b'{"element_representation":"real","kind":"variable_array","maximum_length":2,"minimum_length":0}\n',
            ),
            (
                RepresentationSpec(kind="referenced_bytes", payload=PayloadSpec(allowed_media_types=["a/b"], allowed_storage_roles=["test.raw"])),
                "representation_spec",
                b'{"kind":"referenced_bytes","payload":{"allowed_media_types":["a/b"],"allowed_storage_roles":["test.raw"]}}\n',
            ),
            (ShapeSpec(kind="scalar"), "shape_spec", b'{"kind":"scalar"}\n'),
            (ShapeSpec(kind="fixed", length=2), "shape_spec", b'{"kind":"fixed","length":2}\n'),
            (ShapeSpec(kind="variable", minimum_length=0, maximum_length=2), "shape_spec", b'{"kind":"variable","maximum_length":2,"minimum_length":0}\n'),
            (UnitSpec(kind="unitless"), "unit_spec", b'{"kind":"unitless"}\n'),
            (
                UnitSpec(kind="unit", quantity_id="test.distance", unit_id="test.metre"),
                "unit_spec",
                b'{"kind":"unit","quantity_id":"test.distance","unit_id":"test.metre"}\n',
            ),
        )
        for model, stem, expected in cases:
            with self.subTest(stem=stem, expected=expected):
                self.assertEqual(expected, canonical_bytes(model))
                reader = getattr(_value_io, "_" + stem + "_from_wire")
                restored = reader(_parse_json_document(expected))
                self.assertEqual(model, restored)
                self.assertEqual(expected, canonical_bytes(restored))

    def test_lexical_real_tokens_and_integer_overflow(self) -> None:
        for token in ("1.0", "1e0"):
            model = _value_io._inline_value_from_wire(_parse_json_document('{"representation":"real","value":' + token + "}"))
            self.assertEqual(b'{"representation":"real","value":1.0}\n', canonical_bytes(model))
        for representation, token, error in (
            ("real", "1", ContractShapeError),
            ("integer", "1.0", ContractShapeError),
            ("integer", "9223372036854775808", CanonicalJSONError),
            ("real", "1e999", CanonicalJSONError),
            ("real", "1e-999", CanonicalJSONError),
        ):
            with self.subTest(representation=representation, token=token):
                with self.assertRaises(error) as caught:
                    _value_io._inline_value_from_wire(_parse_json_document('{"representation":"' + representation + '","value":' + token + "}"))
                self.assertEqual("/value", caught.exception.path)

    def test_constructor_and_loaded_domain_paths_match_with_prefix(self) -> None:
        cases = (
            ("integer", True, ContractShapeError),
            ("integer", 2**63, CanonicalJSONError),
            ("string", "e\u0301", CanonicalJSONError),
            ("enumeration", "label", ContractValidationError),
            ("vector", [1.0, True], ContractShapeError),
        )
        for representation, value, error in cases:
            with self.subTest(representation=representation):
                with self.assertRaises(error) as constructed:
                    InlineValue(representation=representation, value=value)
                with self.assertRaises(error) as loaded:
                    _value_io._inline_value_from_wire({"representation": representation, "value": value}, path="/test.value", source="claim.json")
                self.assertEqual("/test.value" + constructed.exception.path, loaded.exception.path)
                self.assertEqual("claim.json", loaded.exception.source)
                self.assertIsNone(loaded.exception.line)
                self.assertIsNone(loaded.exception.column)

    def test_value_primitives_reject_subclasses_with_type_equality_override(self) -> None:
        class EqualityType(type):
            @override
            def __eq__(cls, other: object) -> bool:
                return other is float or other is str

            @override
            def __ne__(cls, other: object) -> bool:
                return other is not float and other is not str

            __hash__ = type.__hash__

        class CallerFloat(float, metaclass=EqualityType):
            pass

        class CallerString(str, metaclass=EqualityType):
            pass

        with self.assertRaises(ContractShapeError) as caught:
            InlineValue(representation="real", value=CallerFloat(1.0))
        self.assertEqual("/value", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            ShapeSpec(kind=CallerString("scalar"))
        self.assertEqual("/kind", caught.exception.path)

    def test_irrelevant_fields_cannot_impersonate_omission_with_equality(self) -> None:
        class CallerValue:
            @override
            def __eq__(self, other: object) -> bool:
                return True

            @override
            def __ne__(self, other: object) -> bool:
                return False

        with self.assertRaises(ContractShapeError) as caught:
            InlineValue(representation="integer", element_representation=CallerValue(), value=1)
        self.assertEqual("/element_representation", caught.exception.path)
        with self.assertRaises(ContractShapeError) as caught:
            RepresentationSpec(kind="integer", length=CallerValue())
        self.assertEqual("/length", caught.exception.path)

    def test_inline_text_accepts_scalars_adjacent_to_surrogates(self) -> None:
        for text, utf8 in (("\ud7ff", b"\xed\x9f\xbf"), ("\ue000", b"\xee\x80\x80")):
            with self.subTest(scalar=ord(text)):
                expected = b'{"representation":"string","value":"' + utf8 + b'"}\n'
                model = InlineValue(representation="string", value=text)
                self.assertEqual(expected, canonical_bytes(model))
                restored = _value_io._inline_value_from_wire(_parse_json_document(expected))
                self.assertEqual(text, restored.value)
                self.assertEqual(expected, canonical_bytes(restored))

    def test_payload_error_precedence_across_all_fields(self) -> None:
        base = {"media_type": "a/b", "byte_length": 0, "sha256": "a" * 64, "storage_role": "test.raw", "retention_status": "retained"}
        cases = (
            (base | {"media_type": "INVALID", "byte_length": True}, ContractShapeError, "/byte_length"),
            ({k: v for k, v in (base | {"media_type": "e\u0301/b"}).items() if k != "storage_role"}, ContractShapeError, "/storage_role"),
            (base | {"byte_length": -1, "storage_role": "test.e\u0301"}, CanonicalJSONError, "/storage_role"),
            (base | {"media_type": 1, "retention_status": "bad"}, ContractShapeError, "/media_type"),
            (base | {"media_type": "BAD", "sha256": "a" * 16385}, ContractValidationError, "/media_type"),
        )
        for fields, error, path in cases:
            with self.subTest(fields=fields):
                with self.assertRaises(error) as caught:
                    _value_io._payload_reference_from_wire(fields)
                self.assertEqual(path, caught.exception.path)
                if set(fields) == set(base):
                    with self.assertRaises(error) as constructed:
                        PayloadReference(**fields)  # ty: ignore[invalid-argument-type]
                    self.assertEqual(path, constructed.exception.path)

    def test_payload_allow_list_errors_follow_domain_tiers_and_property_order(self) -> None:
        cases = (
            (["BAD", ""], ["test.raw"], ContractValidationError, "/allowed_media_types/0"),
            (["BAD"], ["e\u0301"], CanonicalJSONError, "/allowed_storage_roles/0"),
        )
        for media, roles, error, path in cases:
            fields = {"allowed_media_types": media, "allowed_storage_roles": roles}
            with self.subTest(path=path):
                for build in (
                    lambda fields=fields: PayloadSpec(**fields),
                    lambda fields=fields: _value_io._payload_spec_from_wire(fields),
                    lambda fields=fields: _value_io._payload_spec_from_wire(_parse_json_document(json.dumps(fields))),
                ):
                    with self.assertRaises(error) as caught:
                        build()
                    self.assertEqual(path, caught.exception.path)

    def test_shape_errors_outrank_array_domain_errors_and_null_is_not_omission(self) -> None:
        with self.assertRaises(ContractShapeError) as caught:
            _value_io._inline_value_from_wire({"representation": "vector", "value": [math.inf, True]})
        self.assertEqual("/value/1", caught.exception.path)
        for fields in ({"kind": "scalar", "length": None}, {"kind": "fixed"}, {"kind": "scalar", "extra": 1}):
            with self.assertRaises(ContractShapeError):
                _value_io._shape_spec_from_wire(fields)
        with self.assertRaises(CanonicalJSONError):
            _value_io._inline_value_from_wire({"representation": "integer", "value": None})
        with self.assertRaises(ContractShapeError) as caught:
            _value_io._representation_spec_from_wire(
                {"kind": "referenced_bytes", "payload": {"allowed_media_types": ["INVALID"], "allowed_storage_roles": [False]}}, path="/declaration"
            )
        self.assertEqual("/declaration/payload/allowed_storage_roles/0", caught.exception.path)

    def test_owned_class_dispatch_rejects_subclasses_and_other_objects(self) -> None:
        class Unowned(InlineValue):
            pass

        for value in (Unowned(representation="integer", value=1), [1], 1, object(), {"unqualified": 1}):
            with self.assertRaises(CanonicalJSONError):
                canonical_bytes(value)
        self.assertEqual(b"{}\n", canonical_bytes({}))
