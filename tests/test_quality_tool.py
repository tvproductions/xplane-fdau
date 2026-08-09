"""Tests for the repository quality gate."""

from __future__ import annotations

import unittest

from tools import quality


class QualityToolTests(unittest.TestCase):
    def test_check_uses_unittest_and_all_blocking_gates(self) -> None:
        names = tuple(step.name for step in quality.CHECK_STEPS)

        self.assertIn("unittest", names)
        self.assertIn("ruff check", names)
        self.assertIn("ty check", names)
        self.assertNotIn("xpwebapi", " ".join(" ".join(step.command) for step in quality.CHECK_STEPS))

    def test_quality_targets_only_the_renamed_runtime_root(self) -> None:
        commands = " ".join(" ".join(step.command) for steps in quality.COMMANDS.values() for step in steps)

        self.assertEqual(("xplane_fdau", "tests", "tools"), quality.SOURCE_PATHS)
        self.assertIn("xplane_fdau", commands)
        self.assertNotIn("xplane_fdr", commands)
