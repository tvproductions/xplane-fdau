"""Canonical FDAU JSON byte profile."""

from __future__ import annotations

import hashlib
import unittest
from typing import override

import xplane_fdau
import xplane_fdau.contracts as contracts
from xplane_fdau.contracts import CanonicalJSONError, canonical_bytes
from xplane_fdau.contracts._json_parse import _parse_json_document
from xplane_fdau.contracts.canonical_json import _encode_document


class CanonicalJSONTests(unittest.TestCase):
    def test_owned_utc_scalar_preserves_all_nine_digits(self) -> None:
        from xplane_fdau.contracts.timing import UtcInstant

        self.assertEqual(b'"0001-01-01T00:00:00.000000001Z"\n', canonical_bytes(UtcInstant(value="0001-01-01T00:00:00.000000001Z")))

    def test_parameter_root_rejects_caller_objects_without_comparison_hooks(self) -> None:
        class RaisingType(type):
            @override
            def __ne__(cls, other: object) -> bool:
                raise AssertionError("caller comparison must not run")

        class CallerMapping(dict[str, object], metaclass=RaisingType):
            pass

        with self.assertRaises(CanonicalJSONError) as caught:
            canonical_bytes(CallerMapping())
        self.assertEqual("", caught.exception.path)

    def test_parameter_primitives_require_exact_types_despite_caller_equality(self) -> None:
        class EqualityType(type):
            @override
            def __eq__(cls, other: object) -> bool:
                return True

            @override
            def __ne__(cls, other: object) -> bool:
                return False

            __hash__ = type.__hash__

        class CallerString(str, metaclass=EqualityType):
            pass

        class CallerInteger(int, metaclass=EqualityType):
            pass

        class CallerFloat(float, metaclass=EqualityType):
            pass

        class CallerBoolean(metaclass=EqualityType):
            pass

        for value in (CallerString("text"), CallerInteger(1), CallerFloat(1.0), CallerBoolean()):
            with self.subTest(kind=type(value).__name__), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes({"test.value": value})
            self.assertEqual("/test.value", caught.exception.path)
        with self.assertRaises(CanonicalJSONError) as caught:
            canonical_bytes({CallerString("test.key"): 0})
        self.assertEqual("", caught.exception.path)

    def test_parameter_text_accepts_scalars_adjacent_to_surrogates(self) -> None:
        for text, utf8 in (("\ud7ff", b"\xed\x9f\xbf"), ("\ue000", b"\xee\x80\x80")):
            with self.subTest(scalar=ord(text)):
                self.assertEqual(b'{"test.text":"' + utf8 + b'"}\n', canonical_bytes({"test.text": text}))

    def test_parse_canonical_convergence_and_digest(self) -> None:
        expected = b'{"test.x":1}\n'
        self.assertEqual(expected, canonical_bytes({"test.x": 1}))
        self.assertEqual(expected, _encode_document(_parse_json_document(' { "test.x" : 1 } ')))
        self.assertEqual(expected, _encode_document(_parse_json_document('{"test.x":1}')))
        self.assertEqual("c7a95602104d7db4d2fca0e277f6e064854c886d32328a57cb4d28ab10467424", hashlib.sha256(canonical_bytes({"test.x": 1})).hexdigest())
        ordered = _encode_document(_parse_json_document('{"test.a":1,"test.x":2}'))
        reordered = _encode_document(_parse_json_document(' { "test.x": 2, "test.a": 1 } '))
        self.assertEqual(b'{"test.a":1,"test.x":2}\n', ordered)
        self.assertEqual(ordered, reordered)
        self.assertEqual(hashlib.sha256(ordered).digest(), hashlib.sha256(reordered).digest())

    def test_public_contract_exports_leave_root_unchanged(self) -> None:
        self.assertEqual(["__version__"], xplane_fdau.__all__)
        self.assertEqual(
            {
                "FDAUContractError",
                "ContractParseError",
                "ContractShapeError",
                "ContractValidationError",
                "CanonicalJSONError",
                "UnsupportedContractVersionError",
                "ContractHashError",
                "canonical_bytes",
                "DefinitionRef",
                "RecordRef",
                "AlgorithmRef",
                "Authority",
                "ProvenanceSource",
                "ProducerIdentity",
                "ProviderIdentity",
                "AdapterIdentity",
                "ValueRepresentation",
                "ScalarRepresentation",
                "RetentionStatus",
                "InlineValue",
                "PayloadReference",
                "PayloadSpec",
                "RepresentationSpec",
                "ShapeSpec",
                "UnitSpec",
            },
            set(contracts.__all__),
        )

    def test_empty_parameter_object_and_root_rejection(self) -> None:
        self.assertEqual(b"{}\n", canonical_bytes({}))
        for value in (0, [], "text"):
            with self.subTest(value=value), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes(value)
            self.assertEqual("", caught.exception.path)

    def test_unicode_scalar_key_order_and_array_order(self) -> None:
        self.assertEqual(
            '{"a":[2,1],"\ue000":"A","😀":"B"}\n'.encode(),
            _encode_document({"😀": "B", "\ue000": "A", "a": [2, 1]}),
        )

    def test_string_escapes_and_utf8(self) -> None:
        value = 'é\b\t\n\f\r\x0f"\\/😀'
        expected = '"é\\b\\t\\n\\f\\r\\u000f\\"\\\\/😀"\n'.encode()
        self.assertEqual(expected, _encode_document(value))

    def test_integer_boolean_and_negative_zero_tokens(self) -> None:
        self.assertEqual(
            b"[-9223372036854775808,9223372036854775807,true,false,0]\n",
            _encode_document(_parse_json_document("[-9223372036854775808,9223372036854775807,true,false,-0]")),
        )

    def test_parameter_value_validation_has_pointer_paths(self) -> None:
        cases = (
            ({"test.x": "e\u0301"}, "/test.x"),
            ({"test.x": "\ud800"}, "/test.x"),
            ({"test.x": None}, "/test.x"),
            ({"test.x": b"bytes"}, "/test.x"),
            ({"test.x": 2**63}, "/test.x"),
            ({"Bad": 1}, "/Bad"),
            ({1: 0}, ""),
        )
        for value, path in cases:
            with self.subTest(value=repr(value)), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes(value)
            self.assertEqual(path, caught.exception.path)

    def test_scalar_subclasses_cannot_control_emitted_number_text(self) -> None:
        class LabeledInteger(int):
            @override
            def __str__(self) -> str:
                return "not a number"

        class LabeledReal(float):
            @override
            def as_integer_ratio(self) -> tuple[int, int]:
                return 0, 1

        for value in (LabeledInteger(1), LabeledReal(1.5)):
            with self.subTest(value=type(value).__name__), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes({"test.x": value})
            self.assertEqual("/test.x", caught.exception.path)

    def test_parameter_errors_follow_canonical_key_order(self) -> None:
        for value in (
            {"z": 1, "test.a": None},
            {"test.a": None, "z": 1},
        ):
            with self.subTest(keys=list(value)), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes(value)
            self.assertEqual("/test.a", caught.exception.path)
        for value in ({"z": 1, "bad": 1}, {"bad": 1, "z": 1}):
            with self.subTest(keys=list(value)), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes(value)
            self.assertEqual("/bad", caught.exception.path)

    def test_escaped_surrogate_pair_becomes_one_scalar(self) -> None:
        self.assertEqual('"😀"\n'.encode(), _encode_document(_parse_json_document('"\\ud83d\\ude00"')))

    def test_non_nfc_parsed_text_rejected_after_parse(self) -> None:
        with self.assertRaises(CanonicalJSONError) as caught:
            _encode_document(_parse_json_document('{"a":"e\\u0301"}'))
        self.assertEqual("/a", caught.exception.path)

    def test_parameter_depth_boundary(self) -> None:
        value: object = 1
        for _ in range(32):
            value = {"test.x": value}
        self.assertTrue(canonical_bytes(value).endswith(b"\n"))
        with self.assertRaises(CanonicalJSONError):
            canonical_bytes({"test.x": value})

    def test_document_depth_boundary(self) -> None:
        value: object = 1
        for _ in range(64):
            value = {"x": value}
        self.assertTrue(_encode_document(value).endswith(b"\n"))
        with self.assertRaises(CanonicalJSONError):
            _encode_document({"x": value})

    def test_container_member_boundary(self) -> None:
        value = {f"x{i}": 0 for i in range(65535)}
        self.assertTrue(_encode_document(value).endswith(b"\n"))
        value["extra"] = 0
        with self.assertRaises(CanonicalJSONError):
            _encode_document(value)

    def test_parameter_text_boundaries_and_unicode_interior(self) -> None:
        for text in ("x", "x" * 16384, " "):
            with self.subTest(length=len(text)):
                self.assertEqual(b'{"test.text":"' + text.encode() + b'"}\n', canonical_bytes({"test.text": text}))
        self.assertEqual('{"test.text":"q\u0301"}\n'.encode(), canonical_bytes({"test.text": "q\u0301"}))
        self.assertEqual(b'{"test.text":" \\u001f"}\n', canonical_bytes({"test.text": " \x1f"}))
        for text in ("", "x" * 16385, "\ud801", "\udbff", "\udc00", "\udfff", "\u1f71"):
            with self.subTest(text=repr(text)), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes({"test.text": text})
            self.assertEqual("/test.text", caught.exception.path)

    def test_array_depth_is_counted_for_lists_and_tuples(self) -> None:
        for factory in (list, tuple):
            with self.subTest(container=factory.__name__):
                parameter: object = 0
                for _ in range(31):
                    parameter = factory((parameter,))
                self.assertTrue(canonical_bytes({"test.array": parameter}).endswith(b"\n"))
                with self.assertRaises(CanonicalJSONError) as caught:
                    canonical_bytes({"test.array": factory((parameter,))})
                self.assertEqual("/test.array" + "/0" * 31, caught.exception.path)
                document: object = 0
                for _ in range(64):
                    document = factory((document,))
                self.assertTrue(_encode_document(document).endswith(b"\n"))
                with self.assertRaises(CanonicalJSONError) as caught:
                    _encode_document(factory((document,)))
                self.assertEqual("/0" * 64, caught.exception.path)

    def test_public_array_length_and_exact_container_contract(self) -> None:
        class DerivedList(list[object]):
            """A caller-owned collection subtype is outside the data-only domain."""

        class DerivedTuple(tuple[object, ...]):
            """Tuple subtypes also require explicit normalization by the caller."""

        for factory in (list, tuple):
            values = factory(0 for _ in range(65535))
            self.assertTrue(canonical_bytes({"test.array": values}).endswith(b"\n"))
            with self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes({"test.array": factory(0 for _ in range(65536))})
            self.assertEqual("/test.array", caught.exception.path)
        for value in (DerivedList((1,)), DerivedTuple((1,))):
            with self.subTest(container=type(value).__name__), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes({"test.array": value})
            self.assertEqual("/test.array", caught.exception.path)

    def test_raw_numeric_boundaries_and_negative_real_are_canonical(self) -> None:
        self.assertEqual(b'{"test.real":-1.25}\n', canonical_bytes({"test.real": -1.25}))
        self.assertEqual(b'{"test.real":-1.0}\n', canonical_bytes({"test.real": -1.0}))
        for number in (-(2**63), 2**63 - 1):
            self.assertEqual(f'{{"test.integer":{number}}}\n'.encode(), canonical_bytes({"test.integer": number}))
        for number in (-(2**63) - 1, 2**63):
            with self.subTest(number=number), self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes({"test.integer": number})
            self.assertEqual("/test.integer", caught.exception.path)

    def test_parameter_identifier_length_boundary(self) -> None:
        identifier = "a." + "b" * 253
        self.assertEqual(f'{{"{identifier}":0}}\n'.encode(), canonical_bytes({identifier: 0}))
        with self.assertRaises(CanonicalJSONError) as caught:
            canonical_bytes({identifier + "b": 0})
        self.assertEqual("/" + identifier + "b", caught.exception.path)


if __name__ == "__main__":
    unittest.main()
