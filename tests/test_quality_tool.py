"""Tests for the repository quality gate."""

from __future__ import annotations

import unittest
import subprocess

from tools import quality


class QualityToolTests(unittest.TestCase):
    def test_check_uses_unittest_and_all_blocking_gates(self) -> None:
        names = tuple(step.name for step in quality.CHECK_STEPS)

        self.assertEqual(
            (
                "ruff check",
                "ruff format --check",
                "ty check",
                "coverage run",
                "coverage report",
                "bandit",
                "detect-secrets baseline",
                "detect-secrets report",
                "interrogate",
                "vulture",
                "xenon complexity",
            ),
            names,
        )
        self.assertNotIn("xpwebapi", " ".join(" ".join(step.command) for step in quality.CHECK_STEPS))

    def test_check_executes_full_suite_once_and_keeps_standalone_test(self) -> None:
        executed: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            executed.append(command)
            return subprocess.CompletedProcess(command, 0, stdout="xplane_fdau/__init__.py\n")

        self.assertEqual(0, quality.run_steps(quality.CHECK_STEPS, runner))
        suite_commands = [command for command in executed if "unittest" in command]
        self.assertEqual(1, len(suite_commands), suite_commands)
        self.assertEqual(("uv", "run", "coverage", "run"), suite_commands[0][:4])
        self.assertIn(("uv", "run", "coverage", "report", "--fail-under=40"), executed)
        self.assertIn(("uv", "run", "xenon"), tuple(command[:3] for command in executed))

        standalone: list[tuple[str, ...]] = []

        def standalone_runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            standalone.append(command)
            return subprocess.CompletedProcess(command, 0)

        self.assertEqual(0, quality.run_steps(quality.COMMANDS["test"], standalone_runner))
        self.assertEqual(("uv", "run", "python", "-m", "unittest", "discover", "-v"), standalone[0])

    def test_quality_targets_only_the_renamed_runtime_root(self) -> None:
        commands = " ".join(" ".join(step.command) for steps in quality.COMMANDS.values() for step in steps)

        self.assertEqual(("xplane_fdau", "tests", "tools"), quality.SOURCE_PATHS)
        self.assertIn("xplane_fdau", commands)
        self.assertNotIn("xplane_fdr", commands)
