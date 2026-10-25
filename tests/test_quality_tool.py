"""Behavioral tests for the locked four-check routine gate."""

from __future__ import annotations

import subprocess
import unittest

from tools import quality


class QualityToolTests(unittest.TestCase):
    def test_routine_executes_exactly_four_locked_checks(self) -> None:
        executed = []

        def runner(command, **kwargs):
            executed.append(command)
            return subprocess.CompletedProcess(command, 0, stdout="")

        self.assertEqual(0, quality.run_steps(quality.CHECK_STEPS, runner))
        prefix = ("uv", "run", "--locked", "--all-groups")
        scopes = ("src/xplane_fdau", "tests", "tools", ".codex/skills")
        self.assertEqual(
            [
                (*prefix, "ruff", "check", *scopes),
                (*prefix, "ruff", "format", "--check", *scopes),
                (*prefix, "ty", "check"),
                (*prefix, "python", "-m", "unittest", "discover", "-q"),
            ],
            executed,
        )

    def test_routine_failure_stops_without_running_later_checks(self) -> None:
        for failed_at in range(4):
            with self.subTest(failed_at=failed_at):
                executed = []

                def runner(command, failed_at=failed_at, executed=executed, **kwargs):
                    executed.append(command)
                    return subprocess.CompletedProcess(command, 7 if len(executed) - 1 == failed_at else 0, stdout="")

                self.assertEqual(7, quality.run_steps(quality.CHECK_STEPS, runner))
                self.assertEqual(failed_at + 1, len(executed))

    def test_standalone_unittest_remains_available(self) -> None:
        executed = []

        def runner(command, **kwargs):
            executed.append(command)
            return subprocess.CompletedProcess(command, 0, stdout="")

        self.assertEqual(0, quality.run_steps(quality.COMMANDS["test"], runner))
        self.assertEqual([("uv", "run", "--locked", "--all-groups", "python", "-m", "unittest", "discover", "-q")], executed)

    def test_deep_analysis_is_absent_from_routine_invocations(self) -> None:
        commands = [word for step in quality.CHECK_STEPS for word in step.command]
        for tool in ("bandit", "detect-secrets", "interrogate", "vulture", "coverage", "xenon", "lizard", "pip-audit"):
            self.assertNotIn(tool, commands)
