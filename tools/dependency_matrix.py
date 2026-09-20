"""Run the explicit Python source and installed-wheel closeout matrix."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import tarfile
import tempfile
import tomllib
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


PYTHONS = ("3.12", "3.13", "3.14")
PACKAGE = "xplane_fdau"
Runner = Callable[[tuple[str, ...], Path], int]


@dataclass(frozen=True, slots=True)
class OwnedTempDirectory:
    """Record the created directory and its parent for checked cleanup."""

    path: Path
    parent: Path
    identity: os.stat_result
    parent_identity: os.stat_result


TempFactory = Callable[[Path], OwnedTempDirectory]


@dataclass(frozen=True, slots=True)
class MatrixCommand:
    """One executed command and its observed exit code."""

    command: tuple[str, ...]
    cwd: Path
    exit_code: int


@dataclass(frozen=True, slots=True)
class MatrixResult:
    """Evidence from one build and the three supported interpreters."""

    success: bool
    commands: tuple[MatrixCommand, ...]
    artifact_hashes: dict[str, str]
    preserved_failure_paths: tuple[Path, ...]
    error: str | None = None


def expected_artifact_names(version: str) -> set[str]:
    """Name the only release artifacts accepted by this matrix."""
    return {f"{PACKAGE}-{version}-py3-none-any.whl", f"{PACKAGE}-{version}.tar.gz"}


def source_test_command(interpreter: Path) -> tuple[str, ...]:
    """Run source unittest under one external interpreter without changing project .venv."""
    return (str(interpreter), "-m", "unittest", "discover", "-q")


def installed_interpreter(venv_dir: Path, os_name: str) -> Path:
    """Locate the interpreter in a uv venv on Windows or POSIX."""
    return venv_dir / ("Scripts/python.exe" if os_name == "nt" else "bin/python")


def create_temp_directory(root: Path, *, parent: Path | None = None) -> OwnedTempDirectory:
    """Create an external temporary directory and record its filesystem identity."""
    resolved_root = root.resolve(strict=True)
    resolved_parent = (parent or Path(tempfile.gettempdir())).resolve(strict=True)
    if resolved_parent == resolved_root or resolved_root in resolved_parent.parents:
        raise ValueError(f"matrix temporary parent is inside checkout: {resolved_parent}")
    if resolved_parent.is_symlink() or resolved_parent.is_junction():
        raise ValueError(f"matrix temporary parent is a link: {resolved_parent}")
    parent_identity = resolved_parent.stat(follow_symlinks=False)
    created = Path(tempfile.mkdtemp(prefix="xplane-fdau-matrix-", dir=resolved_parent))
    try:
        identity = created.stat(follow_symlinks=False)
    except OSError as error:
        raise RuntimeError(f"matrix temporary directory preserved at {created}: {error}") from error
    return OwnedTempDirectory(created, resolved_parent, identity, parent_identity)


def _cleanup_target(root: Path, owned: OwnedTempDirectory) -> Path:
    """Require the same external directory before recursive removal."""
    resolved_root = root.resolve(strict=True)
    path, parent = owned.path, owned.parent
    if path.parent != parent or parent == resolved_root or resolved_root in parent.parents:
        raise ValueError(f"unsafe matrix temporary location: {path}")
    if path.is_symlink() or path.is_junction() or parent.is_symlink() or parent.is_junction():
        raise ValueError(f"matrix temporary location became a link: {path}")
    if parent.resolve(strict=True) != parent or path.resolve(strict=True) != path:
        raise ValueError(f"matrix temporary location changed: {path}")
    current_parent = parent.stat(follow_symlinks=False)
    current_path = path.stat(follow_symlinks=False)
    if not stat.S_ISDIR(current_parent.st_mode) or not stat.S_ISDIR(current_path.st_mode):
        raise ValueError(f"matrix temporary location is no longer a directory: {path}")
    if not os.path.samestat(owned.parent_identity, current_parent):
        raise ValueError(f"matrix temporary parent identity changed: {parent}")
    if not os.path.samestat(owned.identity, current_path):
        raise ValueError(f"matrix temporary directory identity changed: {path}")
    return path


def _member_parts(name: str, *, label: str) -> tuple[str, ...]:
    if "\\" in name or name.startswith("/"):
        raise ValueError(f"{label} has unsafe member: {name}")
    parts = PurePosixPath(name).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{label} has unsafe member: {name}")
    return parts


def _inspect_payload(wheel: Path, sdist: Path, version: str) -> None:
    """Reject repository tooling in either payload before invoking external checks."""
    wheel_roots = {PACKAGE, f"{PACKAGE}-{version}.dist-info"}
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            parts = _member_parts(name.rstrip("/"), label="wheel")
            if parts[0] not in wheel_roots:
                raise ValueError(f"wheel contains repository tooling or unexpected member: {name}")
    sdist_root = f"{PACKAGE}-{version}"
    allowed_sdist = {PACKAGE, "PKG-INFO", "pyproject.toml", "pyproject.toml.orig", "README.md", "LICENSE"}
    with tarfile.open(sdist, "r:gz") as archive:
        for member in archive.getmembers():
            parts = _member_parts(member.name.rstrip("/"), label="sdist")
            if parts == (sdist_root,) and member.isdir():
                continue
            if parts[0] != sdist_root or len(parts) < 2 or parts[1] not in allowed_sdist:
                raise ValueError(f"sdist contains repository tooling or unexpected member: {member.name}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _project_version(root: Path) -> str:
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    if not isinstance(version, str) or not version:
        raise ValueError("project version is missing")
    return version


def _default_runner(command: tuple[str, ...], cwd: Path) -> int:
    return subprocess.run(command, cwd=cwd, shell=False, check=False).returncode


def run_matrix(root: Path, runner: Runner = _default_runner, make_temp: TempFactory = create_temp_directory) -> MatrixResult:
    """Build once, verify exact artifacts, and exercise source and installed wheel."""
    root = root.resolve(strict=True)
    commands: list[MatrixCommand] = []
    hashes: dict[str, str] = {}
    owned: OwnedTempDirectory | None = None

    def run(command: tuple[str, ...], cwd: Path) -> None:
        try:
            exit_code = runner(command, cwd)
        except OSError as error:
            commands.append(MatrixCommand(command, cwd, -1))
            raise RuntimeError(f"could not start {command}: {error}") from error
        commands.append(MatrixCommand(command, cwd, exit_code))
        if exit_code != 0:
            raise RuntimeError(f"command exited {exit_code}: {command}")

    try:
        version = _project_version(root)
        owned = make_temp(root)
        artifact_dir = owned.path
        if artifact_dir == root or root in artifact_dir.parents:
            raise ValueError(f"matrix temporary directory is inside checkout: {artifact_dir}")
        run(("uv", "build", "--offline", "--no-sources", "--out-dir", str(artifact_dir)), root)
        entries = list(artifact_dir.iterdir())
        marker = artifact_dir / ".gitignore"
        if marker in entries:
            if marker.is_symlink() or not marker.is_file() or marker.read_bytes() != b"*":
                raise ValueError("matrix output has unexpected .gitignore marker")
            entries.remove(marker)
        actual = {path.name for path in entries}
        expected = expected_artifact_names(version)
        if actual != expected or any(not path.is_file() or path.is_symlink() for path in entries):
            raise ValueError(f"matrix artifacts differ from exact pair: expected {sorted(expected)}, found {sorted(actual)}")
        wheel = artifact_dir / f"{PACKAGE}-{version}-py3-none-any.whl"
        sdist = artifact_dir / f"{PACKAGE}-{version}.tar.gz"
        _inspect_payload(wheel, sdist, version)
        hashes = {wheel.name: _sha256(wheel), sdist.name: _sha256(sdist)}
        run(("uv", "run", "--offline", "--frozen", "twine", "check", "--strict", str(wheel), str(sdist)), root)
        run(("uv", "run", "--offline", "--frozen", "python", "tools/release.py", "check-dist", str(artifact_dir)), root)
        requirements = artifact_dir / "source-requirements.txt"
        run(
            ("uv", "--quiet", "export", "--frozen", "--all-groups", "--no-emit-project", "--format", "requirements.txt", "--output-file", str(requirements)),
            root,
        )
        if requirements.is_symlink() or not requirements.is_file() or not 0 < requirements.stat().st_size <= 1024 * 1024:
            raise ValueError(f"matrix lock export is missing or invalid: {requirements}")
        for python_version in PYTHONS:
            source_dir = artifact_dir / f"source-{python_version}"
            run(("uv", "venv", str(source_dir), "--python", python_version), root)
            source_interpreter = installed_interpreter(source_dir, os.name)
            run(("uv", "pip", "sync", "--python", str(source_interpreter), str(requirements)), root)
            run(("uv", "pip", "install", "--python", str(source_interpreter), "--editable", str(root)), root)
            run(source_test_command(source_interpreter), root)
            venv_dir = artifact_dir / f"venv-{python_version}"
            run(("uv", "venv", str(venv_dir), "--python", python_version), root)
            interpreter = installed_interpreter(venv_dir, os.name)
            run(("uv", "pip", "install", "--python", str(interpreter), str(wheel)), root)
            run((str(interpreter), str(root / "tools/installed_smoke.py"), version), artifact_dir)
        shutil.rmtree(_cleanup_target(root, owned))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, zipfile.BadZipFile, tarfile.TarError) as error:
        preserved = (owned.path,) if owned is not None else ()
        return MatrixResult(False, tuple(commands), hashes, preserved, str(error))
    return MatrixResult(True, tuple(commands), hashes, ())
