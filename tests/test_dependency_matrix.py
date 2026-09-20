"""Offline contract tests for the explicit dependency verification matrix."""

from __future__ import annotations

import hashlib
import io
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import override

from tools.dependency_matrix import (
    create_temp_directory,
    expected_artifact_names,
    installed_interpreter,
    run_matrix,
    source_test_command,
)


PYTHONS = ("3.12", "3.13", "3.14")
VERSION = "0.1.0"
WHEEL_NAME = "xplane_fdau-0.1.0-py3-none-any.whl"
SDIST_NAME = "xplane_fdau-0.1.0.tar.gz"


class MatrixContractTests(unittest.TestCase):
    def test_exact_artifact_pair(self) -> None:
        self.assertEqual(expected_artifact_names(VERSION), {WHEEL_NAME, SDIST_NAME})

    def test_source_command_for_every_python(self) -> None:
        for version in PYTHONS:
            with self.subTest(version=version):
                interpreter = installed_interpreter(Path("source") / version, "nt")
                self.assertEqual(source_test_command(interpreter), (str(interpreter), "-m", "unittest", "discover", "-q"))

    def test_installed_interpreter_on_both_platforms(self) -> None:
        self.assertEqual(installed_interpreter(Path("venv"), "nt"), Path("venv") / "Scripts" / "python.exe")
        self.assertEqual(installed_interpreter(Path("venv"), "posix"), Path("venv") / "bin" / "python")


class MatrixRunTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "checkout"
        self.root.mkdir()
        (self.root / "pyproject.toml").write_text('[project]\nversion = "0.1.0"\n', encoding="utf-8")
        self.external = self.base / "external"
        self.external.mkdir()
        self.artifact_dir: Path | None = None
        self.calls: list[tuple[tuple[str, ...], Path]] = []
        self.hashes: dict[str, str] = {}

    def make_temp(self, root: Path):
        owned = create_temp_directory(root, parent=self.external)
        self.artifact_dir = owned.path
        return owned

    def fake_artifacts(self, directory: Path, *, wheel_leak: bool = False, sdist_leak: bool = False) -> None:
        wheel = directory / WHEEL_NAME
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("xplane_fdau/__init__.py", '__version__ = "0.1.0"\n')
            if wheel_leak:
                archive.writestr("tools/dependency_refresh.py", "bad")
        sdist = directory / SDIST_NAME
        with tarfile.open(sdist, "w:gz") as archive:
            root_member = tarfile.TarInfo("xplane_fdau-0.1.0")
            root_member.type = tarfile.DIRTYPE
            archive.addfile(root_member)
            for name in ("xplane_fdau-0.1.0/xplane_fdau/__init__.py", *(["xplane_fdau-0.1.0/tools/dependency_refresh.py"] if sdist_leak else [])):
                payload = b"test payload"
                member = tarfile.TarInfo(name)
                member.size = len(payload)
                archive.addfile(member, io.BytesIO(payload))
        self.hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in (WHEEL_NAME, SDIST_NAME)}

    def runner(self, command: tuple[str, ...], cwd: Path) -> int:
        self.calls.append((command, cwd))
        if command[:2] == ("uv", "build"):
            self.fake_artifacts(Path(command[-1]))
        if command[:3] == ("uv", "--quiet", "export"):
            Path(command[-1]).write_text("packaging==26.3\n", encoding="utf-8")
        return 0

    def test_builds_exact_pair_validates_it_and_reports_hashes(self) -> None:
        result = run_matrix(self.root, self.runner, self.make_temp)
        self.assertTrue(result.success, result.error)
        self.assertEqual(result.artifact_hashes, self.hashes)
        self.assertEqual(result.preserved_failure_paths, ())
        self.assertIsNotNone(self.artifact_dir)
        assert self.artifact_dir is not None
        self.assertFalse(self.artifact_dir.exists())
        self.assertEqual(
            [command for command, _ in self.calls[:3]],
            [
                ("uv", "build", "--offline", "--no-sources", "--out-dir", str(self.artifact_dir)),
                ("uv", "run", "--offline", "--frozen", "twine", "check", "--strict", str(self.artifact_dir / WHEEL_NAME), str(self.artifact_dir / SDIST_NAME)),
                ("uv", "run", "--offline", "--frozen", "python", "tools/release.py", "check-dist", str(self.artifact_dir)),
            ],
        )
        self.assertEqual([(entry.command, entry.exit_code) for entry in result.commands], [(command, 0) for command, _ in self.calls])

    def test_accepts_only_uv_generated_gitignore_beside_exact_artifact_pair(self) -> None:
        def runner(command: tuple[str, ...], cwd: Path) -> int:
            result = self.runner(command, cwd)
            if command[:2] == ("uv", "build"):
                (Path(command[-1]) / ".gitignore").write_bytes(b"*")
            return result

        result = run_matrix(self.root, runner, self.make_temp)
        self.assertTrue(result.success, result.error)
        self.assertEqual(result.artifact_hashes, self.hashes)

    def test_rejects_unexpected_uv_gitignore_contents(self) -> None:
        def runner(command: tuple[str, ...], cwd: Path) -> int:
            self.calls.append((command, cwd))
            if command[:2] == ("uv", "build"):
                directory = Path(command[-1])
                self.fake_artifacts(directory)
                (directory / ".gitignore").write_bytes(b"unexpected")
            return 0

        result = run_matrix(self.root, runner, self.make_temp)
        self.assertFalse(result.success)
        self.assertIn(".gitignore", result.error or "")

    def test_rejects_extra_artifact_before_validation_and_preserves_directory(self) -> None:
        def runner(command: tuple[str, ...], cwd: Path) -> int:
            self.calls.append((command, cwd))
            if command[:2] == ("uv", "build"):
                directory = Path(command[-1])
                self.fake_artifacts(directory)
                (directory / "extra.txt").write_text("extra", encoding="utf-8")
            return 0

        result = run_matrix(self.root, runner, self.make_temp)
        self.assertFalse(result.success)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result.preserved_failure_paths, (self.artifact_dir,))

    def test_rejects_repository_tooling_in_wheel_before_installed_smoke(self) -> None:
        def runner(command: tuple[str, ...], cwd: Path) -> int:
            self.calls.append((command, cwd))
            if command[:2] == ("uv", "build"):
                self.fake_artifacts(Path(command[-1]), wheel_leak=True)
            return 0

        result = run_matrix(self.root, runner, self.make_temp)
        self.assertFalse(result.success)
        self.assertEqual(len(self.calls), 1)
        self.assertIn("tools/dependency_refresh.py", result.error or "")
        self.assertEqual(result.preserved_failure_paths, (self.artifact_dir,))

    def test_rejects_repository_tooling_in_sdist(self) -> None:
        def runner(command: tuple[str, ...], cwd: Path) -> int:
            self.calls.append((command, cwd))
            if command[:2] == ("uv", "build"):
                self.fake_artifacts(Path(command[-1]), sdist_leak=True)
            return 0

        result = run_matrix(self.root, runner, self.make_temp)
        self.assertFalse(result.success)
        self.assertIn("tools/dependency_refresh.py", result.error or "")
        self.assertEqual(result.preserved_failure_paths, (self.artifact_dir,))

    def test_runs_source_and_one_wheel_install_and_smoke_for_each_python(self) -> None:
        result = run_matrix(self.root, self.runner, self.make_temp)
        self.assertTrue(result.success, result.error)
        assert self.artifact_dir is not None
        wheel = self.artifact_dir / WHEEL_NAME
        self.assertEqual(len(self.calls), 25)
        export = self.calls[3][0]
        self.assertEqual(export[:3], ("uv", "--quiet", "export"))
        self.assertEqual(export[-1], str(self.artifact_dir / "source-requirements.txt"))
        for index, version in enumerate(PYTHONS):
            source_venv, source_sync, source_install, source_test, venv, install, smoke = self.calls[4 + index * 7 : 11 + index * 7]
            source_dir = self.artifact_dir / f"source-{version}"
            source_interpreter = installed_interpreter(source_dir, __import__("os").name)
            self.assertEqual(source_venv, (("uv", "venv", str(source_dir), "--python", version), self.root))
            self.assertEqual(
                source_sync, (("uv", "pip", "sync", "--python", str(source_interpreter), str(self.artifact_dir / "source-requirements.txt")), self.root)
            )
            self.assertEqual(source_install, (("uv", "pip", "install", "--python", str(source_interpreter), "--editable", str(self.root)), self.root))
            self.assertEqual(source_test, (source_test_command(source_interpreter), self.root))
            venv_dir = self.artifact_dir / f"venv-{version}"
            self.assertEqual(venv, (("uv", "venv", str(venv_dir), "--python", version), self.root))
            interpreter = installed_interpreter(venv_dir, __import__("os").name)
            self.assertEqual(install, (("uv", "pip", "install", "--python", str(interpreter), str(wheel)), self.root))
            self.assertEqual(smoke, ((str(interpreter), str(self.root / "tools/installed_smoke.py"), VERSION), self.artifact_dir))
            self.assertFalse(self.root == source_dir or self.root in source_dir.parents)
            self.assertFalse(self.root == venv_dir or self.root in venv_dir.parents)

    def test_failed_command_records_exit_and_preserves_artifacts(self) -> None:
        def runner(command: tuple[str, ...], cwd: Path) -> int:
            result = self.runner(command, cwd)
            if self.artifact_dir is not None and command == source_test_command(
                installed_interpreter(self.artifact_dir / "source-3.13", __import__("os").name)
            ):
                return 7
            return result

        result = run_matrix(self.root, runner, self.make_temp)
        self.assertFalse(result.success)
        assert self.artifact_dir is not None
        self.assertEqual(result.commands[-1].command, source_test_command(installed_interpreter(self.artifact_dir / "source-3.13", __import__("os").name)))
        self.assertEqual(result.commands[-1].exit_code, 7)
        self.assertEqual(result.preserved_failure_paths, (self.artifact_dir,))
        assert self.artifact_dir is not None
        self.assertTrue(self.artifact_dir.exists())

    def test_cleanup_rejects_replaced_directory_identity(self) -> None:
        def runner(command: tuple[str, ...], cwd: Path) -> int:
            self.runner(command, cwd)
            if command[0].endswith("python.exe") or command[0].endswith("/python"):
                if command[-1] == VERSION and "venv-3.14" in command[0]:
                    assert self.artifact_dir is not None
                    self.artifact_dir.rename(self.external / "preserved-original")
                    self.artifact_dir.mkdir()
            return 0

        result = run_matrix(self.root, runner, self.make_temp)
        self.assertFalse(result.success)
        self.assertIn("identity changed", result.error or "")
        self.assertEqual(result.preserved_failure_paths, (self.artifact_dir,))
        assert self.artifact_dir is not None
        self.assertTrue(self.artifact_dir.exists())


if __name__ == "__main__":
    unittest.main()
