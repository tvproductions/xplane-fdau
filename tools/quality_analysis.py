"""Measure original Python sources and execute explicit engineering checks."""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import os
import re
import signal
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from contextlib import suppress
from pathlib import Path
from typing import Any, Protocol, cast

Runner = Callable[..., subprocess.CompletedProcess[str]]
_EXCLUDED_DIRECTORIES = frozenset({"__pycache__", "archives", "node_modules", "out", "output", "outputs", "plugins", "site", "venv"})


class AnalysisStep(Protocol):
    """Read-only command description accepted from the quality entry point."""

    @property
    def name(self) -> str:
        """Return the human-readable check identity."""
        ...

    @property
    def command(self) -> tuple[str, ...]:
        """Return the argument vector without shell interpretation."""
        ...

    @property
    def tracked_paths(self) -> tuple[str, ...]:
        """Return optional Git-tracked scopes appended to this command."""
        ...


def cognitive_status() -> dict[str, str]:
    """Expose the user-deferred prerequisite without inventing a measurement."""
    return {"status": "UNKNOWN", "reason": "pending shared cognitive library extraction from gzkit and reviewed starter integration"}


def _source_files(root: Path, paths: Sequence[str], errors: list[str]) -> list[Path]:
    selected: set[Path] = set()

    def visit(path: Path) -> None:
        try:
            if path.is_symlink() or path.is_junction():
                errors.append(f"source link is forbidden: {path}")
            elif path.is_dir():
                for child in sorted(path.iterdir()):
                    if child.name.startswith(".") or child.name in _EXCLUDED_DIRECTORIES:
                        continue
                    visit(child)
            elif path.is_file() and path.suffix == ".py":
                selected.add(path)
        except OSError as error:
            errors.append(f"cannot inspect {path}: {error}")

    for name in paths:
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"scope must be contained and relative: {name}")
            continue
        candidate = root
        for part in relative.parts:
            candidate /= part
            if candidate.is_symlink() or candidate.is_junction():
                errors.append(f"source link is forbidden: {candidate}")
                break
        else:
            if not candidate.exists():
                errors.append(f"missing source scope: {name}")
            else:
                visit(candidate)
    if not selected:
        errors.append("scope contains no Python files")
    return sorted(selected)


def _measure_file(root: Path, path: Path, analyzer: Callable[..., Any], errors: list[str]) -> dict[str, Any]:
    data = path.read_bytes()
    text = data.decode("utf-8-sig")
    tree = ast.parse(text, filename=str(path))
    expected = {node.lineno for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    measured = analyzer(str(path), text).function_list
    actual = [function.start_line for function in measured]
    relative = path.relative_to(root).as_posix()
    if len(actual) != len(set(actual)) or set(actual) != expected:
        errors.append(f"function discovery mismatch in {relative}: missing={sorted(expected - set(actual))}, extra={sorted(set(actual) - expected)}")
    functions = []
    for function in measured:
        score = function.cyclomatic_complexity
        if type(score) is not int or score < 1:
            errors.append(f"invalid native complexity score in {relative}:{function.start_line}")
            continue
        functions.append({"name": function.long_name, "line": function.start_line, "score": score})
    scores = [item["score"] for item in functions]
    return {"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "functions": functions, "mean": sum(scores) / len(scores) if scores else None}


def measure_lizard(root: Path, paths: Sequence[str]) -> dict[str, object]:
    """Record native scores, exact source identities and every discovery error."""
    errors: list[str] = []
    files: list[dict[str, Any]] = []
    version: str | None = None
    try:
        import lizard

        version = importlib.metadata.version("lizard")
        if root.is_symlink() or root.is_junction():
            raise ValueError("source root is a link")
        root = root.resolve(strict=True)
        for path in _source_files(root, paths, errors):
            try:
                files.append(_measure_file(root, path, lizard.analyze_file.analyze_source_code, errors))
            except (OSError, UnicodeError, SyntaxError, ValueError) as error:
                errors.append(f"cannot measure {path}: {error}")
    except (ImportError, importlib.metadata.PackageNotFoundError, OSError, ValueError) as error:
        errors.append(f"analyzer unavailable: {error}")
    scores = [function["score"] for file in files for function in file["functions"]]
    return {
        "schema_version": 1,
        "tool": "lizard",
        "version": version,
        "files": files,
        "function_count": len(scores),
        "maximum": max(scores) if scores else None,
        "overall_mean": sum(scores) / len(scores) if scores else None,
        "errors": errors,
    }


def _validated_scores(file: object) -> list[int]:
    """Reject malformed per-module native scores and inconsistent means."""
    if not isinstance(file, dict) or not isinstance(file.get("functions"), list):
        raise ValueError("invalid measured module")
    scores = [function.get("score") for function in file["functions"] if isinstance(function, dict)]
    if len(scores) != len(file["functions"]) or any(type(score) is not int or score < 1 for score in scores):
        raise ValueError("invalid native function scores")
    if file.get("mean") != (sum(scores) / len(scores) if scores else None):
        raise ValueError("inconsistent module mean")
    return cast(list[int], scores)


def evaluate_lizard(report: Mapping[str, object]) -> int:
    """Enforce 20/10/5 without rounding or accepting incomplete discovery."""
    if report.get("schema_version") != 1 or report.get("tool") != "lizard" or not report.get("version") or report.get("errors") != []:
        return 2
    files = report.get("files")
    if not isinstance(files, list) or not files:
        return 2
    all_scores: list[int] = []
    failed = False
    for file in files:
        try:
            scores = _validated_scores(file)
        except ValueError:
            return 2
        failed |= any(score > 20 for score in scores) or sum(scores) > 10 * len(scores)
        all_scores.extend(scores)
    if report.get("function_count") != len(all_scores) or report.get("maximum") != (max(all_scores) if all_scores else None):
        return 2
    if report.get("overall_mean") != (sum(all_scores) / len(all_scores) if all_scores else None):
        return 2
    failed |= sum(all_scores) > 5 * len(all_scores)
    return int(failed)


def run_analysis(steps: Sequence[AnalysisStep], runner: Runner = subprocess.run) -> int:
    """Run every independent check, retaining a nonzero result after failures."""
    result = 0
    for step in steps:
        command = step.command
        try:
            if step.tracked_paths:
                tracked = runner(
                    ("git", "ls-files", "-z", "--", *step.tracked_paths), capture_output=True, text=True, encoding="utf-8", errors="strict", check=False
                )
                if tracked.returncode:
                    result = 2
                    continue
                command = (*command, *(name for name in tracked.stdout.split("\0") if name))
            print(f"==> {step.name}: {' '.join(command)}", flush=True)
            code = runner(command, check=False).returncode
            result = max(result, 0 if code == 0 else 1 if code == 1 else 2)
        except (OSError, UnicodeError) as error:
            print(f"{step.name}: {error}", file=sys.stderr)
            result = 2
    return result


def _validate_export(path: Path) -> None:
    """Require exact registry requirements with SHA-256 hashes before auditing."""
    from packaging.requirements import Requirement

    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("missing or invalid requirements export")
    content = path.read_text(encoding="utf-8").replace("\\\n", " ")
    count = 0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s+--hash=", line)
        requirement = Requirement(parts[0])
        pins = list(requirement.specifier)
        if requirement.url is not None or len(pins) != 1 or pins[0].operator != "==" or "*" in pins[0].version:
            raise ValueError("audit requires exact registry versions")
        if len(parts) < 2 or any(re.fullmatch(r"sha256:[0-9a-fA-F]{64}", part.strip()) is None for part in parts[1:]):
            raise ValueError("audit requires SHA-256 hashes for every requirement")
        count += 1
    if not count:
        raise ValueError("audit export contains no requirements")


def _stop_owned_tree(process: subprocess.Popen[Any]) -> None:
    """Terminate only the process group/tree started by the bounded runner."""
    if os.name == "nt":
        executable = Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "System32/taskkill.exe"
        result = subprocess.run(
            (str(executable), "/PID", str(process.pid), "/T", "/F"), check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10
        )
        if result.returncode and process.poll() is None:
            raise OSError("cannot terminate the owned process tree")
    else:
        with suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)


def run_bounded(command: Sequence[str], *, timeout: float, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """Apply a total deadline and reap owned children before callers clean up."""
    kwargs.pop("check", None)
    if kwargs.pop("capture_output", False):
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with subprocess.Popen(command, start_new_session=os.name != "nt", **kwargs) as process:
        try:
            output, error = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _stop_owned_tree(process)
            process.communicate()
            raise
        return subprocess.CompletedProcess(command, process.returncode, output, error)


def audit_dependencies(root: Path, runner: Runner = run_bounded) -> int:
    """Audit a hashed exact lock export without invoking a second resolver."""
    try:
        with tempfile.TemporaryDirectory(prefix="fdau-audit-") as directory:
            target = Path(directory) / "requirements.txt"
            export = ("uv", "export", "--quiet", "--locked", "--all-groups", "--no-emit-project", "--format", "requirements.txt", "--output-file", str(target))
            if runner(export, cwd=root, check=False, timeout=60).returncode:
                return 2
            _validate_export(target)
            command = (
                "uv",
                "run",
                "--locked",
                "--all-groups",
                "python",
                "-m",
                "pip_audit",
                "--requirement",
                str(target),
                "--no-deps",
                "--disable-pip",
                "--require-hashes",
                "--format",
                "json",
                "--timeout",
                "30",
            )
            code = runner(command, cwd=root, check=False, timeout=600).returncode
            return 0 if code == 0 else 1 if code == 1 else 2
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"dependency audit: {error}", file=sys.stderr)
        return 2
