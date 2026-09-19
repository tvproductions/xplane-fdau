"""Run deterministic repository hygiene and optional dependency inquiry."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
Runner = Callable[..., subprocess.CompletedProcess[str]]
LOCAL_COMMANDS = (
    ("git", "status", "--short", "--branch"),
    ("git", "status", "--short", "--branch", "--ignored=matching"),
    ("uv", "lock", "--check", "--offline"),
    ("uv", "run", "--offline", "--frozen", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit"),
    ("uv", "run", "--offline", "--frozen", "mkdocs", "build", "--strict"),
    ("uv", "run", "--offline", "--frozen", "python", "tools/quality.py", "pre-commit"),
)
DEPENDENCY_COMMAND = ("uv", "tree", "--outdated", "--depth", "1", "--locked", "--format", "json")


@dataclass(frozen=True, slots=True)
class ArtifactDirectory:
    """Record the exact temporary directory and parent created for one run."""

    path: Path
    parent: Path
    directory_identity: os.stat_result
    parent_identity: os.stat_result


@dataclass(frozen=True, order=True)
class OutdatedDependency:
    """Describe one stale direct dependency."""

    name: str
    current: str
    latest: str
    group: str


def find_outdated_dependencies(payload: dict[str, Any]) -> list[OutdatedDependency]:
    """Return stale dependencies referenced directly by workspace roots."""
    roots = payload.get("roots")
    resolution = payload.get("resolution")
    if not isinstance(roots, list) or not roots:
        raise ValueError("uv dependency data has no non-empty roots list")
    if not isinstance(resolution, dict):
        raise ValueError("uv dependency data has no resolution mapping")

    outdated: list[OutdatedDependency] = []
    processed = 0
    for root_reference in roots:
        root_id = root_reference.get("id") if isinstance(root_reference, dict) else root_reference
        if not isinstance(root_id, str) or not root_id:
            raise ValueError("uv dependency data contains an invalid root reference")
        root = resolution.get(root_id)
        if not isinstance(root, dict):
            raise ValueError(f"uv dependency root does not resolve: {root_id}")
        kind = root.get("kind")
        if kind == "package":
            group = "runtime"
        elif isinstance(kind, dict) and isinstance(kind.get("group"), str) and kind["group"]:
            group = "development"
        else:
            raise ValueError(f"uv dependency root has an unsupported kind: {root_id}")

        dependencies = root.get("dependencies")
        if not isinstance(dependencies, list):
            raise ValueError(f"uv dependency root has no dependencies list: {root_id}")
        for dependency in dependencies:
            dependency_id = dependency.get("id") if isinstance(dependency, dict) else None
            if not isinstance(dependency_id, str) or not dependency_id:
                raise ValueError(f"uv dependency root contains an invalid dependency reference: {root_id}")
            record = resolution.get(dependency_id)
            if not isinstance(record, dict):
                raise ValueError(f"uv dependency does not resolve: {dependency_id}")
            name, current, latest = record.get("name"), record.get("version"), record.get("latest_version")
            if not isinstance(name, str) or not name or not isinstance(current, str) or not current:
                raise ValueError(f"uv dependency has invalid metadata: {dependency_id}")
            if latest is not None and not isinstance(latest, str):
                raise ValueError(f"uv dependency has an invalid latest version: {dependency_id}")
            processed += 1
            if latest is not None:
                outdated.append(OutdatedDependency(name=name, current=current, latest=latest, group=group))
    if processed == 0:
        raise ValueError("uv dependency data contains no direct dependencies")
    return sorted(set(outdated))


def run_command(command: tuple[str, ...], runner: Runner) -> int:
    """Run one local check and report the exact failed command."""
    print("+ " + " ".join(command), flush=True)
    try:
        result = runner(command, cwd=ROOT, check=False, shell=False, env={**os.environ, "UV_OFFLINE": "1"})
    except OSError as error:
        print(f"hygiene failed: {' '.join(command)} (could not start: {error})", file=sys.stderr)
        return 1
    if result.returncode != 0:
        print(f"hygiene failed: {' '.join(command)} (exit {result.returncode})", file=sys.stderr)
    return result.returncode


def create_artifact_dir() -> ArtifactDirectory:
    """Create one external directory and record its exact identity."""
    parent = Path(tempfile.gettempdir()).resolve()
    root = ROOT.resolve()
    if parent == root or root in parent.parents:
        raise ValueError(f"temporary directory is inside the checkout: {parent}")
    parent_identity = parent.stat(follow_symlinks=False)
    created = Path(tempfile.mkdtemp(prefix="xplane-fdau-hygiene-", dir=parent))
    try:
        directory_identity = created.stat(follow_symlinks=False)
    except OSError as error:
        raise RuntimeError(f"artifact directory created but not inspected; preserved {created}: {error}") from error
    return ArtifactDirectory(created, parent, directory_identity, parent_identity)


def artifact_commands(directory: Path, version: str) -> tuple[tuple[str, ...], ...]:
    """Name the exact wheel and sdist expected from the current project."""
    wheel = directory / f"xplane_fdau-{version}-py3-none-any.whl"
    sdist = directory / f"xplane_fdau-{version}.tar.gz"
    return (
        ("uv", "build", "--offline", "--no-sources", "--out-dir", str(directory)),
        ("uv", "run", "--offline", "--frozen", "twine", "check", "--strict", str(wheel), str(sdist)),
        ("uv", "run", "--offline", "--frozen", "python", "tools/release.py", "check-dist", str(directory)),
    )


def verified_cleanup_target(owned: ArtifactDirectory) -> Path:
    """Return the created path only while its parent and identity still match."""
    root = ROOT.resolve()
    path = owned.path
    parent = owned.parent
    if path.parent != parent or parent == root or root in parent.parents or path == root or root in path.parents:
        raise ValueError(f"unsafe artifact directory location: {path}")
    for candidate in (parent, path):
        if candidate.is_symlink() or candidate.is_junction():
            raise ValueError(f"artifact directory link is unsafe: {candidate}")
    if parent.resolve(strict=True) != parent or path.resolve(strict=True) != path:
        raise ValueError(f"artifact directory location changed: {path}")
    current_parent = parent.stat(follow_symlinks=False)
    current_directory = path.stat(follow_symlinks=False)
    if not stat.S_ISDIR(current_parent.st_mode) or not stat.S_ISDIR(current_directory.st_mode):
        raise ValueError(f"artifact directory is no longer a directory: {path}")
    if not os.path.samestat(owned.parent_identity, current_parent):
        raise ValueError(f"artifact directory parent identity changed: {parent}")
    if not os.path.samestat(owned.directory_identity, current_directory):
        raise ValueError(f"artifact directory identity changed: {path}")
    return path


def run_local_hygiene(
    runner: Runner = subprocess.run,
    create_directory: Callable[[], ArtifactDirectory] = create_artifact_dir,
    cleanup: Callable[[Path], None] = shutil.rmtree,
) -> int:
    """Run offline checks, inspect one fresh artifact pair, then remove it safely."""
    for command in LOCAL_COMMANDS:
        code = run_command(command, runner)
        if code != 0:
            return code
    try:
        version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
        if not isinstance(version, str) or not version:
            raise ValueError("project version is missing")
        owned = create_directory()
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        print(f"hygiene artifact preparation failed: {error}", file=sys.stderr)
        return 1
    print(f"hygiene artifact directory: {owned.path}", flush=True)
    for command in (*artifact_commands(owned.path, version), *LOCAL_COMMANDS[:2]):
        code = run_command(command, runner)
        if code != 0:
            print(f"preserved artifact directory: {owned.path}", file=sys.stderr)
            return code
    try:
        target = verified_cleanup_target(owned)
        cleanup(target)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"hygiene cleanup failed; preserved artifact directory {owned.path}: {error}", file=sys.stderr)
        return 1
    print(f"removed artifact directory: {owned.path}", flush=True)
    return 0


def audit_dependencies(runner: Runner = subprocess.run) -> int:
    """Report stale direct dependencies without changing files."""
    print("+ " + " ".join(DEPENDENCY_COMMAND), flush=True)
    result = runner(DEPENDENCY_COMMAND, cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr or "dependency registry inquiry failed", file=sys.stderr)
        return result.returncode
    try:
        payload = json.loads(result.stdout)
        if not isinstance(payload, dict):
            raise ValueError("uv dependency data is not an object")
        outdated = find_outdated_dependencies(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"invalid uv dependency data: {exc}", file=sys.stderr)
        return 2
    if outdated:
        print("Outdated direct dependencies:")
        for item in outdated:
            print(f"  {item.group}: {item.name} {item.current} -> {item.latest}")
        return 1
    print("All direct dependencies are current.")
    return 0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse the requested hygiene mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", action="store_true", help="Query package metadata before local hygiene.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested hygiene workflow."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.dependencies:
        dependency_result = audit_dependencies()
        if dependency_result != 0:
            return dependency_result
    return run_local_hygiene()


if __name__ == "__main__":
    raise SystemExit(main())
