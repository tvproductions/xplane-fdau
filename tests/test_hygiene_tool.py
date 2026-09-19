"""Tests for the repository hygiene command boundary."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


SCRIPT = Path(".codex/skills/hygiene/scripts/hygiene.py")
EXPECTED_PREFIX = [
    ("git", "status", "--short", "--branch"),
    ("git", "status", "--short", "--branch", "--ignored=matching"),
    ("uv", "lock", "--check", "--offline"),
    ("uv", "run", "--offline", "--frozen", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit"),
    ("uv", "run", "--offline", "--frozen", "mkdocs", "build", "--strict"),
    ("uv", "run", "--offline", "--frozen", "python", "tools/quality.py", "pre-commit"),
]


def load_hygiene() -> ModuleType:
    """Load the local hygiene script with dataclass module registration."""
    spec = importlib.util.spec_from_file_location("hygiene", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("hygiene script must be importable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


class HygieneCommandTests(unittest.TestCase):
    def test_local_gate_uses_ordered_offline_commands(self) -> None:
        module = load_hygiene()
        calls: list[tuple[tuple[str, ...], dict[str, object]]] = []

        def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0)

        self.assertEqual(0, module.run_local_hygiene(runner))
        self.assertEqual(EXPECTED_PREFIX, [command for command, _ in calls])
        for command, kwargs in calls:
            with self.subTest(command=command):
                self.assertEqual(module.ROOT, kwargs["cwd"])
                self.assertIs(False, kwargs["check"])
                self.assertIs(False, kwargs["shell"])
                env = kwargs["env"]
                if not isinstance(env, dict):
                    self.fail("runner environment must be a dictionary")
                self.assertEqual("1", env["UV_OFFLINE"])
                self.assertEqual(os.environ.get("PATH"), env.get("PATH"))
        self.assertNotIn(("uv", "run", "python", "tools/quality.py", "check"), [command for command, _ in calls])
        for command, _ in calls:
            self.assertNotIn(command[:2], [("uv", "tree"), ("git", "add"), ("git", "commit")])

    def test_launch_error_stops_before_later_commands(self) -> None:
        module = load_hygiene()
        calls: list[tuple[str, ...]] = []
        failed = EXPECTED_PREFIX[2]

        def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            if command == failed:
                raise OSError("uv executable unavailable")
            return subprocess.CompletedProcess(command, 0)

        with patch("sys.stderr") as stderr:
            self.assertNotEqual(0, module.run_local_hygiene(runner))
        self.assertEqual(EXPECTED_PREFIX[:3], calls)
        reported = " ".join(str(call) for call in stderr.write.call_args_list)
        self.assertIn(" ".join(failed), reported)
        self.assertIn("uv executable unavailable", reported)


if __name__ == "__main__":
    unittest.main()
