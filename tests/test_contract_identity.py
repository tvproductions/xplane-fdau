"""C1.2 scalar identity validation contracts."""

from __future__ import annotations

import unittest
from typing import Protocol

from xplane_fdau.contracts import _identity_validation as identity
from xplane_fdau.contracts.errors import FDAUContractError, CanonicalJSONError, ContractShapeError, ContractValidationError


class _Validator(Protocol):
    def __call__(self, value: object, *, path: str) -> object: ...


class IdentityValidationTests(unittest.TestCase):
    def assert_rejected(self, operation: _Validator, value: object, error: type[FDAUContractError], path: str) -> None:
        with self.assertRaises(error) as caught:
            operation(value, path=path)
        self.assertEqual(caught.exception.path, path)

    def test_identifier_grammar_and_length(self) -> None:
        longest = "a." + "b" * 253
        self.assertEqual(identity._identifier(longest, path="/id"), longest)
        for value in ("a", "A.b", "a.B", "é.a", longest + "b"):
            with self.subTest(value=value):
                self.assert_rejected(identity._identifier, value, ContractValidationError, "/id")
        self.assert_rejected(identity._identifier, 1, ContractShapeError, "/id")

    def test_revisions_and_counters_reject_bool_and_out_of_range(self) -> None:
        self.assertEqual(identity._revision(1, path="/revision"), 1)
        self.assertEqual(identity._revision(2**63 - 1, path="/revision"), 2**63 - 1)
        self.assertEqual(identity._counter(0, path="/generation"), 0)
        self.assertEqual(identity._counter(2**63 - 1, path="/sequence"), 2**63 - 1)
        for operation, bad, error, path in (
            (identity._revision, True, ContractShapeError, "/revision"),
            (identity._revision, 0, ContractValidationError, "/revision"),
            (identity._revision, 2**63, ContractValidationError, "/revision"),
            (identity._counter, False, ContractShapeError, "/generation"),
            (identity._counter, -1, ContractValidationError, "/sequence"),
            (identity._counter, 2**63, ContractValidationError, "/sequence"),
        ):
            with self.subTest(value=bad, path=path):
                self.assert_rejected(operation, bad, error, path)

    def test_uuid_version_variant_and_lowercase(self) -> None:
        for value in (
            "12345678-1234-1234-8234-123456789abc",
            "12345678-1234-8234-b234-123456789abc",
        ):
            self.assertEqual(identity._uuid(value, path="/record_id"), value)
        for value in (
            "12345678-1234-1234-8234-123456789ABC",
            "00000000-0000-0000-0000-000000000000",
            "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "12345678-1234-0234-8234-123456789abc",
            "12345678-1234-9234-8234-123456789abc",
            "12345678-1234-1234-7234-123456789abc",
        ):
            with self.subTest(value=value):
                self.assert_rejected(identity._uuid, value, ContractValidationError, "/record_id")

    def test_sha256_version_and_nfc_text(self) -> None:
        self.assertEqual(identity._sha256("a" * 64, path="/hash"), "a" * 64)
        self.assert_rejected(identity._sha256, "A" * 64, ContractValidationError, "/hash")
        self.assert_rejected(identity._sha256, "a" * 63, ContractValidationError, "/hash")
        self.assertEqual(identity._version_text("v1", path="/version"), "v1")
        for value, error in (
            ("", ContractValidationError),
            ("e\u0301", CanonicalJSONError),
            ("\ud800", CanonicalJSONError),
            ("v\n1", ContractValidationError),
            ("v\u200d1", ContractValidationError),
            ("x" * 129, ContractValidationError),
        ):
            with self.subTest(value=repr(value)):
                self.assert_rejected(identity._version_text, value, error, "/version")
        self.assertEqual(identity._nfc_text("scope", path="/scope", maximum=1024), "scope")
        with self.assertRaises(ContractValidationError) as caught:
            identity._nfc_text("x" * 1025, path="/scope", maximum=1024)
        self.assertEqual(caught.exception.path, "/scope")


if __name__ == "__main__":
    unittest.main()
