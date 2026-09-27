"""Independent binary64 spelling vectors from RFC 8785 and Node/V8."""

from __future__ import annotations

from pathlib import Path
import struct
import unittest

from xplane_fdau.contracts import CanonicalJSONError, canonical_bytes
from xplane_fdau.contracts._binary64 import _ecmascript_number_token
from xplane_fdau.contracts.canonical_json import _encode_document


def _from_bits(bits: str) -> float:
    return struct.unpack(">d", bytes.fromhex(bits))[0]


class ContractBinary64Tests(unittest.TestCase):
    def test_rfc_8785_appendix_b_vectors(self) -> None:
        vectors = (
            ("0000000000000000", "0"),
            ("8000000000000000", "0"),
            ("0000000000000001", "5e-324"),
            ("8000000000000001", "-5e-324"),
            ("7fefffffffffffff", "1.7976931348623157e+308"),
            ("ffefffffffffffff", "-1.7976931348623157e+308"),
            ("4340000000000000", "9007199254740992"),
            ("c340000000000000", "-9007199254740992"),
            ("4430000000000000", "295147905179352830000"),
            ("44b52d02c7e14af5", "9.999999999999997e+22"),
            ("44b52d02c7e14af6", "1e+23"),
            ("44b52d02c7e14af7", "1.0000000000000001e+23"),
            ("444b1ae4d6e2ef4e", "999999999999999700000"),
            ("444b1ae4d6e2ef4f", "999999999999999900000"),
            ("444b1ae4d6e2ef50", "1e+21"),
            ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"),
            ("3eb0c6f7a0b5ed8d", "0.000001"),
            ("41b3de4355555553", "333333333.3333332"),
            ("41b3de4355555554", "333333333.33333325"),
            ("41b3de4355555555", "333333333.3333333"),
            ("41b3de4355555556", "333333333.3333334"),
            ("41b3de4355555557", "333333333.33333343"),
            ("becbf647612f3696", "-0.0000033333333333333333"),
            ("43143ff3c1cb0959", "1424953923781206.2"),
        )
        for bits, expected in vectors:
            self.assertEqual(expected, _ecmascript_number_token(_from_bits(bits)), bits)

    def test_frozen_v8_oracle_covers_all_finite_exponents(self) -> None:
        rows = []
        for line in (Path(__file__).parent / "data" / "c1_1_binary64_oracle.tsv").read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                continue
            bits, separator, expected = line.partition("\t")
            self.assertEqual("\t", separator)
            self.assertRegex(bits, r"[0-9a-f]{16}\Z")
            self.assertTrue(expected)
            self.assertLess((int(bits, 16) >> 52) & 0x7FF, 2047)
            rows.append((bits, expected))
        self.assertGreaterEqual(len(rows), 4096)
        self.assertEqual(len(rows), len({bits for bits, _ in rows}))
        self.assertEqual(set(range(2047)), {(int(bits, 16) >> 52) & 0x7FF for bits, _ in rows})
        for bits, expected in rows:
            self.assertEqual(expected, _ecmascript_number_token(_from_bits(bits)), bits)

    def test_project_real_tokens_preserve_real_type(self) -> None:
        cases = (
            (1.0, b"1.0\n"),
            (-0.0, b"0.0\n"),
            (1e-6, b"0.000001\n"),
            (1e-7, b"1e-7\n"),
            (1e20, b"100000000000000000000.0\n"),
            (1e21, b"1e+21\n"),
            (_from_bits("0000000000000001"), b"5e-324\n"),
            (_from_bits("7fefffffffffffff"), b"1.7976931348623157e+308\n"),
            (_from_bits("43143ff3c1cb0959"), b"1424953923781206.2\n"),
        )
        for value, expected in cases:
            self.assertEqual(expected, _encode_document(value))

    def test_nonfinite_values_rejected_with_path(self) -> None:
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(CanonicalJSONError) as caught:
                canonical_bytes({"test.x": {"value.x": value}})
            self.assertEqual("/test.x/value.x", caught.exception.path)
            with self.assertRaises(CanonicalJSONError):
                _ecmascript_number_token(value)


if __name__ == "__main__":
    unittest.main()
