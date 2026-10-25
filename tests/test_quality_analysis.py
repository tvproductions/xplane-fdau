"""Behavioral tests for complete, bounded original-source analysis."""

from __future__ import annotations

import copy
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path
from typing import override
from unittest.mock import patch

from tools import quality
from tools.quality import Step


def function_source(name: str, score: int) -> str:
    branches = "".join(f"    if value == {index}:\n        pass\n" for index in range(score - 1))
    return f"def {name}(value):\n{branches}    return value\n"


class LizardMeasurementTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertIsNotNone(importlib.util.find_spec("tools.quality_analysis"), "explicit analysis support is missing")
        self.analysis = importlib.import_module("tools.quality_analysis")
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def write(self, name: str, content: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    def measure(self, paths=("src",)):
        return self.analysis.measure_lizard(self.root, paths)

    def test_function_ceiling_boundary_preserves_independent_averages(self) -> None:
        for score, expected in ((20, 0), (21, 1)):
            with self.subTest(score=score):
                self.write("src/example.py", function_source("large", score) + "".join(function_source(f"small_{i}", 1) for i in range(6)))
                report = self.measure()
                self.assertEqual(score, report["maximum"])
                self.assertLess(report["overall_mean"], 5)
                self.assertEqual(expected, self.analysis.evaluate_lizard(report))

    def test_module_mean_is_unrounded_and_overall_mean_is_weighted(self) -> None:
        self.write("src/small.py", "".join(function_source(f"small_{i}", 1) for i in range(10)))
        for second, expected in ((10, 0), (11, 1)):
            with self.subTest(second=second):
                self.write("src/wide.py", function_source("first", 10) + function_source("second", second))
                report = self.measure()
                self.assertEqual((20 + second) / 12, report["overall_mean"])
                module = next(item for item in report["files"] if item["path"] == "src/wide.py")
                self.assertEqual((10 + second) / 2, module["mean"])
                self.assertEqual(expected, self.analysis.evaluate_lizard(report))

    def test_overall_mean_boundary_is_separate_from_module_and_maximum(self) -> None:
        for score, expected in ((5, 0), (6, 1)):
            with self.subTest(score=score):
                self.write("src/example.py", function_source("branching", score))
                report = self.measure()
                self.assertEqual(score, report["overall_mean"])
                self.assertEqual(expected, self.analysis.evaluate_lizard(report))

    def test_nested_async_and_methods_are_discovered_once_and_paths_deduplicate(self) -> None:
        self.write(
            "src/example.py",
            "class Example:\n    def method(self):\n        return 1\nasync def outer():\n    def inner():\n        return 2\n    return inner()\n",
        )
        report = self.measure(("src", "src/example.py"))
        self.assertEqual([], report["errors"])
        self.assertEqual(3, report["function_count"])
        self.assertEqual(1, len(report["files"]))
        self.assertEqual(0, self.analysis.evaluate_lizard(report))

    def test_function_free_modules_have_null_measurements(self) -> None:
        self.write("src/data.py", "VALUE = 1\n")
        report = self.measure()
        self.assertEqual(0, report["function_count"])
        self.assertIsNone(report["maximum"])
        self.assertIsNone(report["overall_mean"])
        self.assertIsNone(report["files"][0]["mean"])
        self.assertEqual(0, self.analysis.evaluate_lizard(report))

    def test_unsupported_original_function_never_silently_leaves_denominator(self) -> None:
        self.write("src/example.py", "def inline(): return 1\n")
        report = self.measure()
        if report["errors"]:
            self.assertEqual(2, self.analysis.evaluate_lizard(report))
            self.assertIn("discovery", str(report["errors"]).lower())
        else:
            self.assertEqual(1, report["function_count"])
            self.assertEqual(0, self.analysis.evaluate_lizard(report))

    def test_missing_escaping_empty_and_invalid_source_fail_closed(self) -> None:
        for paths, source in ((("missing",), None), (("../outside",), None), (("src",), ""), (("src",), "def invalid(\n")):
            with self.subTest(paths=paths, source=source):
                directory = self.root / "src"
                directory.mkdir(exist_ok=True)
                if source is not None:
                    self.write("src/example.py", source)
                report = self.measure(paths)
                if source == "":
                    self.assertEqual(0, self.analysis.evaluate_lizard(report))
                else:
                    self.assertEqual(2, self.analysis.evaluate_lizard(report))
                    self.assertTrue(report["errors"])

    def test_real_source_link_is_rejected_when_host_supports_links(self) -> None:
        self.write("real.py", function_source("real", 1))
        link = self.root / "link.py"
        try:
            link.symlink_to(self.root / "real.py")
        except OSError as error:
            self.skipTest(f"host does not permit source symlink fixture: {error}")
        report = self.measure(("link.py",))
        self.assertEqual(2, self.analysis.evaluate_lizard(report))

    def test_corrupted_or_inconsistent_native_reports_are_errors(self) -> None:
        self.write("src/example.py", function_source("valid", 1))
        original = self.measure()
        for field, value in (("version", None), ("files", []), ("function_count", 2), ("maximum", 99), ("overall_mean", 0), ("errors", ["missing function"])):
            with self.subTest(field=field):
                report = copy.deepcopy(original)
                report[field] = value
                self.assertEqual(2, self.analysis.evaluate_lizard(report))
        for score in (0, -1, True, None, "1"):
            with self.subTest(score=score):
                report = copy.deepcopy(original)
                report["files"][0]["functions"][0]["score"] = score
                self.assertEqual(2, self.analysis.evaluate_lizard(report))


class AnalysisExecutionTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertIsNotNone(importlib.util.find_spec("tools.quality_analysis"), "explicit analysis support is missing")
        self.analysis = importlib.import_module("tools.quality_analysis")

    def test_all_available_checks_run_after_failure_and_launch_error(self) -> None:
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            if command == ("missing",):
                raise FileNotFoundError("missing analyzer")
            return subprocess.CompletedProcess(command, 1 if command == ("failed",) else 0)

        steps = tuple(Step(name, (name,)) for name in ("failed", "missing", "last"))
        self.assertNotEqual(0, self.analysis.run_analysis(steps, runner))
        self.assertEqual([("failed",), ("missing",), ("last",)], calls)

    def test_required_unknown_is_explicit_and_cannot_return_success(self) -> None:
        result = self.analysis.cognitive_status()
        self.assertEqual("UNKNOWN", result["status"])
        self.assertIn("extraction", result["reason"])
        self.assertNotIn("score", result)

    def test_analysis_cli_records_unknown_and_runs_independent_commands_after_failure(self) -> None:
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        output = directory / "analysis.json"
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 1 if command == ("failed",) else 0)

        with (
            patch.dict(quality.COMMANDS, {"analysis": (Step("failed", ("failed",)), Step("last", ("last",)))}),
            patch.object(quality.subprocess, "run", side_effect=runner),
            patch.object(self.analysis, "measure_lizard", return_value={"errors": ["discovery unavailable"]}),
        ):
            try:
                code = quality.main(["analysis", "--output", str(output)])
            except SystemExit as error:
                self.fail(f"explicit analysis CLI is unavailable: {error}")
        self.assertEqual(2, code)
        self.assertEqual([("failed",), ("last",)], calls)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("UNKNOWN", report["cognitive"]["status"])
        self.assertEqual(1, report["other_checks_exit_code"])

    def test_analysis_report_does_not_overwrite_an_existing_file(self) -> None:
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        output = directory / "preserve.json"
        output.write_text("preserve", encoding="utf-8")
        try:
            code = quality.main(["analysis", "--output", str(output)])
        except SystemExit as error:
            self.fail(f"analysis output guard is unavailable: {error}")
        self.assertEqual(2, code)
        self.assertEqual("preserve", output.read_text(encoding="utf-8"))

    def test_exact_hash_export_is_audited_without_a_second_resolver_and_cleaned(self) -> None:
        self.assertTrue(hasattr(self.analysis, "audit_dependencies"), "locked audit composition is unavailable")
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        calls = []
        exported = []

        def runner(command, **kwargs):
            calls.append(command)
            if command[:2] == ("uv", "export"):
                target = Path(command[command.index("--output-file") + 1])
                target.write_text("example==1.0 --hash=sha256:" + "a" * 64 + "\n", encoding="utf-8")
                exported.append(target)
            else:
                self.assertTrue(exported[0].is_file())
                self.assertIn("--no-deps", command)
                self.assertIn("--disable-pip", command)
                self.assertIn("--require-hashes", command)
                self.assertIn("--hash=sha256:", exported[0].read_text(encoding="utf-8"))
            return subprocess.CompletedProcess(command, 0)

        self.assertEqual(0, self.analysis.audit_dependencies(directory, runner))
        self.assertIn("--locked", calls[0])
        self.assertIn("--all-groups", calls[0])
        self.assertIn("--no-emit-project", calls[0])
        self.assertEqual(2, len(calls))
        self.assertEqual((sys.executable, "-m", "pip_audit"), calls[1][:3])
        self.assertFalse(exported[0].exists())

    def test_nonexact_or_unhashed_exports_stop_before_the_auditor(self) -> None:
        self.assertTrue(hasattr(self.analysis, "audit_dependencies"), "locked audit composition is unavailable")
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for content in ("example>=1.0 --hash=sha256:" + "a" * 64, "example==1.0\n"):
            with self.subTest(content=content):
                calls = []

                def runner(command, content=content, calls=calls, **kwargs):
                    calls.append(command)
                    target = Path(command[command.index("--output-file") + 1])
                    target.write_text(content, encoding="utf-8")
                    return subprocess.CompletedProcess(command, 0)

                self.assertEqual(2, self.analysis.audit_dependencies(directory, runner))
                self.assertEqual(1, len(calls))

    def test_timeout_stops_the_owned_child_tree_before_temporary_cleanup(self) -> None:
        self.assertTrue(hasattr(self.analysis, "run_bounded"), "owned process-tree timeout is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "child-survived"
            ready = root / "ready"
            child = "import pathlib,time; time.sleep(2); pathlib.Path('child-survived').write_bytes(b'leaked')"
            parent = f"import pathlib,subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}]); pathlib.Path('ready').write_bytes(b'ready'); time.sleep(3)"
            with self.assertRaises(subprocess.TimeoutExpired):
                self.analysis.run_bounded((sys.executable, "-c", parent), cwd=root, check=False, timeout=1)
            self.assertTrue(ready.is_file(), "fixture did not start before the deadline")
            time.sleep(2.5)
            self.assertFalse(marker.exists(), "timed-out child survived the owning runner")


class ImportBoundaryTests(unittest.TestCase):
    def test_real_analyzer_accepts_package_and_rejects_direct_and_indirect_edges(self) -> None:
        root = Path(__file__).resolve().parents[1]
        policy = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["tool"].get("importlinter")
        self.assertIsNotNone(policy, "required import boundaries are not configured")
        command = (sys.executable, "-c", "from importlinter.cli import lint_imports_command; lint_imports_command()", "--no-cache", "--no-logo")
        positive = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=30)
        self.assertEqual(0, positive.returncode, positive.stdout + positive.stderr)
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            # Reuse the actual policy, not a second weaker fixture contract.
            (fixture / "pyproject.toml").write_bytes((root / "pyproject.toml").read_bytes())
            package = fixture / "xplane_fdau"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            for name in ("contracts", "formats", "sinks", "cli", "bridge"):
                (package / f"{name}.py").write_text("", encoding="utf-8")
            environment = dict(os.environ, PYTHONPATH=str(fixture))
            for source, target in (
                ("contracts", "formats"),
                ("contracts", "sinks"),
                ("contracts", "cli"),
                ("formats", "sinks"),
                ("formats", "cli"),
                ("sinks", "cli"),
            ):
                for indirect in (False, True):
                    with self.subTest(source=source, target=target, indirect=indirect):
                        path = package / f"{source}.py"
                        bridge = package / "bridge.py"
                        path.write_text(f"import xplane_fdau.{'bridge' if indirect else target}\n", encoding="utf-8")
                        bridge.write_text(f"import xplane_fdau.{target}\n" if indirect else "", encoding="utf-8")
                        result = subprocess.run(
                            command, cwd=fixture, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=30
                        )
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn("BROKEN", result.stdout, result.stdout + result.stderr)
                        path.write_text("", encoding="utf-8")
                        bridge.write_text("", encoding="utf-8")
