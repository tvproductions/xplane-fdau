"""Closed acquisition evidence vocabularies and validation contracts."""

from __future__ import annotations

import unittest
from enum import StrEnum

from xplane_fdau.contracts.errors import CanonicalJSONError, ContractShapeError, ContractValidationError
from xplane_fdau.measurements import QualityFlag, ValidityState, _quality

VALIDITY_VALUES = ("valid", "invalid", "unknown", "not_applicable")
QUALITY_VALUES = (
    "conversion_failed",
    "discontinuous",
    "dropped",
    "duplicate",
    "orphaned",
    "out_of_declared_range",
    "precision_lost",
    "provider_degraded",
    "read_error",
    "reordered",
    "rounded",
    "saturated",
    "stale",
    "type_mismatch",
    "unavailable",
)
REJECTED_TERMS = (
    "VALID",
    " valid",
    "within_tolerance",
    "outside_tolerance",
    "indeterminate",
    "warning",
    "critical",
    "finding",
)


class MeasurementQualityVocabularyTests(unittest.TestCase):
    def test_exact_vocabularies(self) -> None:
        for vocabulary, expected in ((ValidityState, VALIDITY_VALUES), (QualityFlag, QUALITY_VALUES)):
            with self.subTest(vocabulary=vocabulary.__name__):
                self.assertTrue(issubclass(vocabulary, StrEnum))
                self.assertEqual(expected, tuple(member.value for member in vocabulary))
                self.assertEqual(tuple(value.upper() for value in expected), tuple(vocabulary.__members__))
                for value in expected:
                    member = vocabulary(value)
                    self.assertIs(member, vocabulary[value.upper()])
                    self.assertEqual(value, str(member))

    def test_closed_vocabularies(self) -> None:
        for vocabulary in (ValidityState, QualityFlag):
            for value in REJECTED_TERMS:
                with self.subTest(vocabulary=vocabulary.__name__, value=value), self.assertRaises(ValueError):
                    vocabulary(value)


class MeasurementQualityInputTests(unittest.TestCase):
    def test_scalar_and_collection_conversion(self) -> None:
        for text in VALIDITY_VALUES:
            self.assertIs(ValidityState[text.upper()], _quality._validity_state(text))
            self.assertIs(ValidityState[text.upper()], _quality._validity_state(ValidityState[text.upper()]))
        result = _quality._quality_flags(QUALITY_VALUES)
        self.assertIs(type(result), tuple)
        self.assertEqual(QUALITY_VALUES, tuple(flag.value for flag in result))
        self.assertTrue(all(type(flag) is QualityFlag for flag in result))
        self.assertEqual(
            (QualityFlag.ROUNDED, QualityFlag.STALE),
            _quality._quality_flags([QualityFlag.ROUNDED, "stale"]),
        )

    def test_empty_flags_do_not_infer_validity(self) -> None:
        self.assertEqual((), _quality._quality_flags([]))
        self.assertEqual((), _quality._quality_flags(()))
        for text in VALIDITY_VALUES:
            self.assertIs(ValidityState[text.upper()], _quality._validity_state(text))
        self.assertRaises(TypeError, _quality._validity_state)

    def test_duplicate_and_reverse_order_are_rejected(self) -> None:
        cases = [("stale", "stale"), ("stale", "rounded")]
        cases.extend((QUALITY_VALUES[right], QUALITY_VALUES[left]) for left in range(15) for right in range(left + 1, 15))
        for values in cases:
            original = list(values)
            with self.subTest(values=values), self.assertRaises(ContractValidationError) as caught:
                _quality._quality_flags(original)
            self.assertEqual("/quality/1", caught.exception.path)
            self.assertEqual(list(values), original)

    def test_defensive_copy(self) -> None:
        values = ["rounded", "stale"]
        accepted = _quality._quality_flags(values)
        values[0] = "unavailable"
        values.append("warning")
        self.assertEqual((QualityFlag.ROUNDED, QualityFlag.STALE), accepted)

    def test_foreign_types_and_operational_terms(self) -> None:
        class ForeignQuality(StrEnum):
            STALE = "stale"

        class ForeignValidity(StrEnum):
            UNKNOWN = "unknown"

        for value in (*REJECTED_TERMS, ForeignQuality.STALE, 7, True, b"stale", {}, []):
            with self.subTest(value=repr(value)), self.assertRaises(ContractShapeError) as caught:
                _quality._quality_flags([value])
            self.assertEqual("/quality/0", caught.exception.path)
        for value in (*REJECTED_TERMS, ForeignValidity.UNKNOWN, QualityFlag.STALE, 7, True, b"unknown", {}, []):
            with self.subTest(value=repr(value)), self.assertRaises(ContractShapeError) as caught:
                _quality._validity_state(value)
            self.assertEqual("/validity", caught.exception.path)

    def test_rejects_nonsequence_containers_without_consuming_iterators(self) -> None:
        items = (value for value in ("stale",))
        for value in ("stale", b"stale", {"stale"}, frozenset({"stale"}), {"stale": True}, items):
            with self.subTest(value=type(value)), self.assertRaises(ContractShapeError) as caught:
                _quality._quality_flags(value)
            self.assertEqual("/quality", caught.exception.path)
        self.assertEqual("stale", next(items))

    def test_nulls_are_canonical_domain_errors(self) -> None:
        for operation, value, path in (
            (_quality._validity_state, None, "/validity"),
            (_quality._quality_flags, None, "/quality"),
            (_quality._quality_flags, [None], "/quality/0"),
        ):
            with self.subTest(path=path), self.assertRaises(CanonicalJSONError) as caught:
                operation(value)
            self.assertEqual(path, caught.exception.path)

    def test_shape_precedes_collection_semantics(self) -> None:
        for values, expected, path in (
            (["stale", "rounded", 7], ContractShapeError, "/quality/2"),
            (["stale", "rounded", None], CanonicalJSONError, "/quality/2"),
            ([None, "warning"], ContractShapeError, "/quality/1"),
            (["stale", "stale", "warning"], ContractShapeError, "/quality/2"),
        ):
            with self.subTest(values=values), self.assertRaises(expected) as caught:
                _quality._quality_flags(values)
            self.assertEqual(path, caught.exception.path)

    def test_nested_paths_and_context(self) -> None:
        with self.assertRaises(ContractValidationError) as caught:
            _quality._quality_flags(["stale", "stale"], path="/samples/2/quality")
        self.assertEqual("/samples/2/quality/1", caught.exception.path)
        self.assertEqual("<memory>", caught.exception.source)
        self.assertIsNone(caught.exception.line)
        self.assertIsNone(caught.exception.column)
        with self.assertRaises(ContractShapeError) as scalar:
            _quality._validity_state("warning", path="/samples/2/validity")
        self.assertEqual("/samples/2/validity", scalar.exception.path)

    def test_sixteen_flags_rejects_duplicate_at_index_15(self) -> None:
        values = (*(flag.value for flag in QualityFlag), "unavailable")
        with self.assertRaises(ContractValidationError) as caught:
            _quality._quality_flags(values)
        self.assertEqual("/quality/15", caught.exception.path)
