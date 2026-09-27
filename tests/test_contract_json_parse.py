"""Strict lexical JSON parsing for canonical contracts."""

from __future__ import annotations

import unittest

from xplane_fdau.contracts import CanonicalJSONError, ContractParseError, FDAUContractError
from xplane_fdau.contracts._json_parse import _NumberToken, _materialize_number, _parse_json_document


class ContractJSONParseTests(unittest.TestCase):
    def test_escaped_duplicate_key_has_pointer_path(self) -> None:
        with self.assertRaises(ContractParseError) as caught:
            _parse_json_document(b'{"a":1,"\\u0061":2}')
        self.assertEqual("/a", caught.exception.path)

    def test_nested_duplicate_escapes_pointer_tokens(self) -> None:
        with self.assertRaises(ContractParseError) as caught:
            _parse_json_document(b'{"a/b":{"~x":1,"\\u007ex":2}}')
        self.assertEqual("/a~1b/~0x", caught.exception.path)

    def test_duplicate_precedes_numeric_domain_error(self) -> None:
        with self.assertRaises(ContractParseError) as caught:
            _parse_json_document(b'{"a":9223372036854775808,"a":0}')
        self.assertEqual("/a", caught.exception.path)

    def test_preserves_integer_and_real_tokens(self) -> None:
        self.assertEqual(
            [_NumberToken("1", False), _NumberToken("1.0", True), _NumberToken("1e0", True), _NumberToken("-0", False)],
            _parse_json_document("[1,1.0,1e0,-0]"),
        )

    def test_rejects_utf8_bom_and_syntax_with_context(self) -> None:
        for data in (b"\xef\xbb\xbf{}", b"\xff", b'{\n"test.x":"\xff"}'):
            with self.subTest(data=data), self.assertRaises(ContractParseError) as caught:
                _parse_json_document(data, source="sample.json")
            self.assertEqual("sample.json", caught.exception.source)
            self.assertIsNone(caught.exception.line)
            self.assertIsNone(caught.exception.column)
        with self.assertRaises(ContractParseError) as caught:
            _parse_json_document(b'{\n"a":}', source="sample.json")
        self.assertEqual(("sample.json", 2, 5), (caught.exception.source, caught.exception.line, caught.exception.column))

    def test_non_json_constants_are_parse_errors(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token), self.assertRaises(ContractParseError):
                _parse_json_document(token)

    def test_materializes_signed_integer_boundaries_and_negative_zero(self) -> None:
        for token, expected in (("-9223372036854775808", -(2**63)), ("9223372036854775807", 2**63 - 1), ("-0", 0)):
            with self.subTest(token=token):
                self.assertEqual(expected, _materialize_number(_NumberToken(token, False)))

    def test_rejects_integer_overflow_with_path(self) -> None:
        for token in ("9223372036854775808", "-9223372036854775809", "9" * 5000):
            with self.subTest(token=token[:20]), self.assertRaises(CanonicalJSONError) as caught:
                _materialize_number(_NumberToken(token, False), source="sample.json", path="/test.x")
            self.assertEqual("/test.x", caught.exception.path)
            self.assertEqual("sample.json", caught.exception.source)

    def test_rejects_real_overflow_and_nonzero_underflow(self) -> None:
        for token in ("1e999", "1e-999", "-1e-999"):
            with self.subTest(token=token), self.assertRaises(CanonicalJSONError) as caught:
                _materialize_number(_NumberToken(token, True), path="/value")
            self.assertEqual("/value", caught.exception.path)

    def test_exact_zero_real_with_nonzero_exponent_is_accepted(self) -> None:
        for token in ("0e999", "0e-999", "-0.0e+37"):
            with self.subTest(token=token):
                self.assertEqual(0.0, _materialize_number(_NumberToken(token, True)))

    def test_error_context_is_read_only(self) -> None:
        error = FDAUContractError("bad", source="sample.json", path="/x", contract_family="test.family", identity="id")
        self.assertEqual(("sample.json", "/x", "test.family", "id"), (error.source, error.path, error.contract_family, error.identity))
        with self.assertRaises(AttributeError):
            setattr(error, "path", "/other")


if __name__ == "__main__":
    unittest.main()
