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
                "bandit",
                "detect-secrets baseline",
                "detect-secrets report",
                "interrogate",
                "vulture",
                "xenon complexity",
                "live-state preflight",
                "coverage run",
                "coverage report",
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
        preflight = (
            "uv",
            "run",
            "python",
            "-m",
            "unittest",
            "tests.test_backlog_status_cli.BacklogStatusCliTests.test_current_repository_status_reports_human_and_json",
            "tests.test_project_metadata.ProjectMetadataTests.test_runtime_package_uses_only_installed_src_layout",
        )
        self.assertIn(preflight, executed)
        coverage_suites = [command for command in executed if command[:4] == ("uv", "run", "coverage", "run")]
        self.assertEqual(1, len(coverage_suites), coverage_suites)
        self.assertIn("unittest", coverage_suites[0])
        self.assertLess(executed.index(preflight), executed.index(coverage_suites[0]))
        self.assertIn(("uv", "run", "coverage", "report", "--fail-under=40"), executed)
        self.assertIn(("uv", "run", "xenon"), tuple(command[:3] for command in executed))

        standalone: list[tuple[str, ...]] = []

        def standalone_runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            standalone.append(command)
            return subprocess.CompletedProcess(command, 0)

        self.assertEqual(0, quality.run_steps(quality.COMMANDS["test"], standalone_runner))
        self.assertEqual(("uv", "run", "python", "-m", "unittest", "discover", "-v"), standalone[0])

    def test_quality_targets_only_the_renamed_runtime_root(self) -> None:
        self.assertEqual("src/xplane_fdau", quality.SOURCE_PATH)
        self.assertEqual(("src/xplane_fdau", "tests", "tools"), quality.SOURCE_PATHS)
        source_steps = {
            "ruff check",
            "ruff format --check",
            "ruff format",
            "bandit",
            "interrogate",
            "vulture",
            "lizard report",
            "cohesion report",
            "wily build",
            "wily report",
            "xenon complexity",
        }
        for steps in quality.COMMANDS.values():
            for step in steps:
                if step.name in source_steps:
                    self.assertIn(quality.SOURCE_PATH, step.command)
                    self.assertNotIn("xplane_fdau", step.command)
        commands = " ".join(" ".join(step.command) for steps in quality.COMMANDS.values() for step in steps)
        self.assertNotIn("xplane_fdr", commands)
