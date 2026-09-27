"""Canonical FDAU JSON byte profile."""

from __future__ import annotations

import unittest

from xplane_fdau.contracts import CanonicalJSONError, canonical_bytes
from xplane_fdau.contracts._json_parse import _parse_json_document
from xplane_fdau.contracts.canonical_json import _encode_document


class CanonicalJSONTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
