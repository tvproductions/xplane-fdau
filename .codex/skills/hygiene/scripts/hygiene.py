"""Run deterministic repository hygiene and optional dependency inquiry."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
Runner = Callable[..., subprocess.CompletedProcess[str]]
LOCAL_COMMANDS = (
    ("git", "status", "--short", "--branch"),
    ("uv", "lock", "--check", "--offline"),
    ("uv", "run", "python", "tools/quality.py", "check"),
    ("uv", "run", "python", "tools/quality.py", "pre-commit"),
)
DEPENDENCY_COMMAND = ("uv", "tree", "--outdated", "--depth", "1", "--locked", "--format", "json")


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


def run_local_hygiene(runner: Runner = subprocess.run) -> int:
    """Run the deterministic local hygiene sequence."""
    for command in LOCAL_COMMANDS:
        print("+ " + " ".join(command), flush=True)
        result = runner(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
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
