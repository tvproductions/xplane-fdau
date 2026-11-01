"""Closed acquisition evidence vocabularies and validation contracts."""

from __future__ import annotations

import unittest
from enum import StrEnum

from xplane_fdau.measurements import QualityFlag, ValidityState

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
