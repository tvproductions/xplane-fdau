"""Tests for the repository hygiene command boundary."""

from __future__ import annotations

import importlib.util
import io
import os
import shutil
import tempfile
import tomllib
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Protocol, cast, override
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
        self.assertEqual(EXPECTED_PREFIX, [command for command, _ in calls[: len(EXPECTED_PREFIX)]])
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


class OwnedDirectory(Protocol):
    path: Path


class HygieneArtifactTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        """Load the script and the package version for each artifact scenario."""
        self.module = load_hygiene()
        self.version = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]

    def owned_fixture(self, parent: Path) -> OwnedDirectory:
        """Make one external child whose ownership identity is test controlled."""
        created = Path(tempfile.mkdtemp(prefix="hygiene-test-", dir=parent))
        owned = self.module.ArtifactDirectory(
            path=created,
            parent=parent.resolve(),
            directory_identity=created.stat(follow_symlinks=False),
            parent_identity=parent.stat(follow_symlinks=False),
        )
        return cast(OwnedDirectory, owned)

    def test_each_success_builds_one_fresh_exact_pair_then_checks_final_status(self) -> None:
        events: list[tuple[str, object]] = []
        owned_paths: list[Path] = []
        with tempfile.TemporaryDirectory(prefix="hygiene-test-parent-") as temporary:
            parent = Path(temporary)
            self.assertNotIn(self.module.ROOT.resolve(), parent.resolve().parents)

            def create_directory() -> OwnedDirectory:
                owned = self.owned_fixture(parent)
                owned_paths.append(owned.path)
                return owned

            def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
                events.append(("run", command))
                return subprocess.CompletedProcess(command, 0)

            def cleanup(target: Path) -> None:
                events.append(("cleanup", target))
                shutil.rmtree(target)

            for _ in range(2):
                events.clear()
                self.assertEqual(0, self.module.run_local_hygiene(runner, create_directory=create_directory, cleanup=cleanup))
                directory = owned_paths[-1]
                wheel = directory / f"xplane_fdau-{self.version}-py3-none-any.whl"
                sdist = directory / f"xplane_fdau-{self.version}.tar.gz"
                artifact = [
                    ("uv", "build", "--offline", "--no-sources", "--out-dir", str(directory)),
                    ("uv", "run", "--offline", "--frozen", "twine", "check", "--strict", str(wheel), str(sdist)),
                    ("uv", "run", "--offline", "--frozen", "python", "tools/release.py", "check-dist", str(directory)),
                ]
                commands = [value for kind, value in events if kind == "run"]
                self.assertEqual(EXPECTED_PREFIX + artifact + EXPECTED_PREFIX[:2], commands)
                self.assertEqual([("cleanup", directory)], [event for event in events if event[0] == "cleanup"])
                self.assertEqual(("cleanup", directory), events[-1])
                self.assertFalse(directory.exists())
        self.assertEqual(2, len(set(owned_paths)))

    def test_artifact_and_final_status_failures_preserve_exact_directory(self) -> None:
        for phase in ("build", "twine", "release", "final-normal", "final-ignored"):
            for mode in ("exit", "launch"):
                with self.subTest(phase=phase, mode=mode):
                    with tempfile.TemporaryDirectory(prefix="hygiene-test-parent-") as temporary:
                        parent = Path(temporary)
                        owned = self.owned_fixture(parent)
                        commands: list[tuple[str, ...]] = []
                        cleanup_calls: list[Path] = []
                        failed_at = len(EXPECTED_PREFIX) + {"build": 0, "twine": 1, "release": 2, "final-normal": 3, "final-ignored": 4}[phase]

                        def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
                            commands.append(command)
                            if len(commands) - 1 == failed_at:
                                if mode == "launch":
                                    raise OSError("injected launch error")
                                return subprocess.CompletedProcess(command, 7)
                            return subprocess.CompletedProcess(command, 0)

                        stderr = io.StringIO()
                        with redirect_stderr(stderr):
                            code = self.module.run_local_hygiene(
                                runner,
                                create_directory=lambda: owned,
                                cleanup=cleanup_calls.append,
                            )
                        self.assertNotEqual(0, code)
                        self.assertEqual(failed_at + 1, len(commands))
                        self.assertIn(" ".join(commands[-1]), stderr.getvalue())
                        self.assertIn("injected launch error" if mode == "launch" else "exit 7", stderr.getvalue())
                        self.assertIn(str(owned.path), stderr.getvalue())
                        self.assertEqual([], cleanup_calls)
                        self.assertTrue(owned.path.is_dir())

    def test_cleanup_refuses_replaced_child_and_parent(self) -> None:
        for replacement in ("child", "parent"):
            with self.subTest(replacement=replacement):
                with tempfile.TemporaryDirectory(prefix="hygiene-test-top-") as temporary:
                    top = Path(temporary)
                    parent = top / "parent"
                    parent.mkdir()
                    owned = self.owned_fixture(parent)
                    if replacement == "child":
                        moved = parent / "moved-child"
                        owned.path.rename(moved)
                        owned.path.mkdir()
                    else:
                        moved = top / "moved-parent"
                        parent.rename(moved)
                        parent.mkdir()
                        owned.path.mkdir()
                    with self.assertRaises((ValueError, OSError)):
                        self.module.verified_cleanup_target(owned)
                    self.assertTrue(moved.exists())
                    self.assertTrue(owned.path.exists())

    def test_cleanup_refuses_links_and_checkout_containment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hygiene-test-top-") as temporary:
            top = Path(temporary)
            parent = top / "parent"
            parent.mkdir()
            owned = self.owned_fixture(parent)
            with patch.object(self.module, "ROOT", top):
                with self.assertRaises(ValueError):
                    self.module.verified_cleanup_target(owned)
            with patch.object(Path, "is_symlink", return_value=True):
                with self.assertRaises(ValueError):
                    self.module.verified_cleanup_target(owned)
            with patch.object(Path, "is_junction", return_value=True):
                with self.assertRaises(ValueError):
                    self.module.verified_cleanup_target(owned)
            self.assertTrue(owned.path.is_dir())

    def test_cleanup_refuses_renamed_child_and_changed_parent_resolution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hygiene-test-top-") as temporary:
            top = Path(temporary)
            parent = top / "parent"
            parent.mkdir()
            owned = self.owned_fixture(parent)
            moved = parent / "moved-child"
            owned.path.rename(moved)
            with self.assertRaises((ValueError, OSError)):
                self.module.verified_cleanup_target(owned)
            self.assertTrue(moved.is_dir())

        with tempfile.TemporaryDirectory(prefix="hygiene-test-top-") as temporary:
            top = Path(temporary)
            parent = top / "parent"
            parent.mkdir()
            owned = self.owned_fixture(parent)
            original_resolve = Path.resolve

            def changed_parent(path: Path, strict: bool = False) -> Path:
                if path == parent:
                    return top / "different-parent"
                return original_resolve(path, strict=strict)

            with patch.object(Path, "resolve", changed_parent):
                with self.assertRaises(ValueError):
                    self.module.verified_cleanup_target(owned)
            self.assertTrue(owned.path.is_dir())

    def test_creation_identity_capture_error_reports_created_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hygiene-test-top-") as temporary:
            parent = Path(temporary).resolve()
            created = parent / "xplane-fdau-hygiene-created"
            created.mkdir()
            original_stat = Path.stat

            def fail_created_stat(path: Path, *, follow_symlinks: bool = True) -> os.stat_result:
                if path == created:
                    raise OSError("identity capture failed")
                return original_stat(path, follow_symlinks=follow_symlinks)

            def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
                return subprocess.CompletedProcess(command, 0)

            stderr = io.StringIO()
            with (
                patch.object(self.module.tempfile, "gettempdir", return_value=str(parent)),
                patch.object(self.module.tempfile, "mkdtemp", return_value=str(created)),
                patch.object(Path, "stat", fail_created_stat),
                redirect_stderr(stderr),
            ):
                self.assertNotEqual(0, self.module.run_local_hygiene(runner))
            self.assertIn(str(created), stderr.getvalue())
            self.assertIn("identity capture failed", stderr.getvalue())
            self.assertTrue(created.is_dir())

    def test_real_directory_symlink_is_refused_when_host_allows_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hygiene-test-top-") as temporary:
            top = Path(temporary)
            parent = top / "parent"
            parent.mkdir()
            owned = self.owned_fixture(parent)
            moved = parent / "original-child"
            owned.path.rename(moved)
            try:
                owned.path.symlink_to(moved, target_is_directory=True)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"host cannot create directory symlink: {error}")
            with self.assertRaises(ValueError):
                self.module.verified_cleanup_target(owned)
            self.assertTrue(moved.is_dir())

    def test_creation_and_cleanup_errors_report_and_preserve(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hygiene-test-parent-") as temporary:
            parent = Path(temporary)
            owned = self.owned_fixture(parent)

            def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
                return subprocess.CompletedProcess(command, 0)

            for create_directory, cleanup, expected in (
                (lambda: (_ for _ in ()).throw(OSError("create failed")), shutil.rmtree, "create failed"),
                (lambda: owned, lambda path: (_ for _ in ()).throw(OSError("delete failed")), "delete failed"),
            ):
                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    self.assertNotEqual(
                        0,
                        self.module.run_local_hygiene(runner, create_directory=create_directory, cleanup=cleanup),
                    )
                self.assertIn(expected, stderr.getvalue())
                self.assertTrue(owned.path.is_dir())


if __name__ == "__main__":
    unittest.main()
