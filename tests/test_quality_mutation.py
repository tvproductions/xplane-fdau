"""Isolation and outcome controls for the explicit mutation command."""

import importlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class MutationExecutionTests(unittest.TestCase):
    def test_native_output_is_utf8_even_with_a_legacy_windows_stream_encoding(self) -> None:
        self.assertIsNotNone(importlib.util.find_spec("tools.quality_mutation"))
        mutation = importlib.import_module("tools.quality_mutation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "src/xplane_fdau"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")
            (root / "unicode_tests.py").write_text(
                "import unittest\nclass UnicodeFailure(unittest.TestCase):\n    def test_failure(self):\n        self.fail('caf\u00e9')\n", encoding="utf-8"
            )
            result = subprocess.run(
                (
                    "uv",
                    "run",
                    "--project",
                    str(Path(__file__).resolve().parents[1]),
                    "--locked",
                    "--all-groups",
                    "python",
                    "-c",
                    mutation._TEST_SCRIPT,
                    "unicode_tests",
                ),
                cwd=root,
                env=dict(os.environ, PYTHONIOENCODING="cp1252"),
                capture_output=True,
                check=False,
                timeout=15,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("caf\u00e9".encode(), result.stdout)
            result.stdout.decode("utf-8", errors="strict")

    def test_native_outcomes_never_certify_survivors_missing_or_abnormal_results(self) -> None:
        self.assertIsNotNone(importlib.util.find_spec("tools.quality_mutation"), "isolated mutation entry point is missing")
        mutation = importlib.import_module("tools.quality_mutation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            original = root / "src" / "example.py"
            original.write_text("VALUE = 1\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                '[cosmic-ray]\nmodule-path = ["src/example.py"]\ntimeout = 30\n[cosmic-ray.distributor]\nname = "local"\n', encoding="utf-8"
            )
            for outcome, expected in (("killed", 0), ("survived", 1), ("incompetent", 2), (None, 2)):
                with self.subTest(outcome=outcome):
                    calls = []
                    workspaces = []

                    def runner(command, calls=calls, workspaces=workspaces, outcome=outcome, **kwargs):
                        calls.append(command)
                        self.assertEqual(("uv", "run", "--project", str(root), "--locked", "--all-groups", "python"), command[:7])
                        copy = kwargs["cwd"]
                        workspaces.append(copy)
                        self.assertNotEqual(root, copy)
                        self.assertEqual("VALUE = 1\n", (copy / "src/example.py").read_text(encoding="utf-8"))
                        result = {"worker_outcome": "normal", "test_outcome": outcome} if outcome is not None else None
                        output = json.dumps([{"job_id": "fixture"}, result]) + "\n" if "dump" in command else ""
                        return subprocess.CompletedProcess(command, 0, stdout=output)

                    output = root / f"{outcome}.json"
                    self.assertEqual(expected, mutation.run_mutation(root, output, runner=runner))
                    self.assertEqual("VALUE = 1\n", original.read_text(encoding="utf-8"))
                    self.assertTrue(output.is_file())
                    self.assertFalse(workspaces[0].exists())
                    self.assertIn("init", calls[1])
                    self.assertIn("exec", calls[2])
                    self.assertIn("dump", calls[3])

    def test_existing_report_is_preserved_before_any_mutation(self) -> None:
        self.assertIsNotNone(importlib.util.find_spec("tools.quality_mutation"), "isolated mutation entry point is missing")
        mutation = importlib.import_module("tools.quality_mutation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "existing.json"
            output.write_text("preserve", encoding="utf-8")
            self.assertEqual(2, mutation.run_mutation(root, output))
            self.assertEqual("preserve", output.read_text(encoding="utf-8"))
