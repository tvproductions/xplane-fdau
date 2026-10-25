"""Run bounded Cosmic Ray work only in a disposable source copy."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable
from pathlib import Path

Runner = Callable[..., subprocess.CompletedProcess[str]]
_SELECTED_TESTS = ("tests.test_contract_values", "tests.test_canonical_json", "tests.test_contract_identity", "tests.test_contract_provenance")
_TEST_SCRIPT = """import sys
from pathlib import Path
import importlib.util
import unittest
sys.stdout.reconfigure(encoding="utf-8", errors="strict")
sys.stderr.reconfigure(encoding="utf-8", errors="strict")
sys.path.insert(0, str(Path("src").resolve()))
origin = importlib.util.find_spec("xplane_fdau").origin
if Path(origin).resolve() != Path("src/xplane_fdau/__init__.py").resolve():
    raise RuntimeError("mutation test imported outside disposable source")
suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:])
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() and result.testsRun else 1)
"""


def _copy_sources(root: Path, destination: Path) -> None:
    """Copy source and tests while rejecting links to any external file."""
    for name in ("src", "tests"):
        source = root / name
        paths = (source, *source.rglob("*"))
        if any(path.is_symlink() or path.is_junction() for path in paths):
            raise ValueError("mutation inputs must not contain links")
        shutil.copytree(source, destination / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def _write_config(root: Path, destination: Path, command: tuple[str, ...]) -> Path:
    """Use the reviewed scope/timeout and native Cosmic Ray configuration."""
    settings = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["cosmic-ray"]
    paths = settings["module-path"]
    timeout = settings["timeout"]
    if not isinstance(paths, list) or not paths or type(timeout) not in (int, float) or not 0 < timeout <= 60:
        raise ValueError("mutation scope or finite timeout is invalid")
    for name in paths:
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or not (destination / path).is_file():
            raise ValueError("mutation scope must name existing contained source files")
    # Cosmic Ray uses POSIX shlex.split on all platforms, then shell=False.
    # Forward slashes preserve a Windows executable path through that parser.
    native_command = shlex.join((command[0].replace("\\", "/"), *command[1:]))
    config = destination / "mutation.toml"
    config.write_text(
        f"[cosmic-ray]\nmodule-path = {json.dumps(paths)}\ntimeout = {timeout}\n"
        f'test-command = {json.dumps(native_command)}\n[cosmic-ray.distributor]\nname = "local"\n',
        encoding="utf-8",
    )
    return config


def _outcome(rows: list[object]) -> int:
    """Distinguish meaningful survivors from missing or invalid native results."""
    if not rows:
        return 2
    code = 0
    for row in rows:
        if not isinstance(row, list) or len(row) != 2 or not isinstance(row[1], dict):
            return 2
        result = row[1]
        if result.get("worker_outcome") != "normal" or result.get("test_outcome") not in ("killed", "survived"):
            return 2
        if result["test_outcome"] == "survived":
            code = 1
    return code


def run_mutation(root: Path, output: Path, runner: Runner = subprocess.run) -> int:
    """Baseline an isolated copy, then retain native results before cleanup."""
    try:
        with output.open("x", encoding="utf-8", newline="\n") as report, tempfile.TemporaryDirectory(prefix="fdau-mutation-") as directory:
            copy = Path(directory)
            _copy_sources(root, copy)
            script = copy / "run_selected_tests.py"
            script.write_text(_TEST_SCRIPT, encoding="utf-8")
            launch = ("uv", "run", "--project", str(root.resolve()), "--locked", "--all-groups", "python")
            tests = (*launch, "-B", script.name, *_SELECTED_TESTS)
            config = _write_config(root, copy, tests)
            if runner(tests, cwd=copy, check=False, timeout=60).returncode:
                json.dump({"baseline": "FAIL", "results": []}, report)
                return 2
            native = (*launch, "-c", "from cosmic_ray.cli import main; main()")
            session = "session.sqlite"
            for args in (("init", config.name, session), ("exec", config.name, session)):
                if runner((*native, *args), cwd=copy, check=False, timeout=3600).returncode:
                    json.dump({"baseline": "PASS", "execution": "ERROR", "results": []}, report)
                    return 2
            dump = runner((*native, "dump", session), cwd=copy, check=False, timeout=60, capture_output=True, text=True, encoding="utf-8", errors="strict")
            if dump.returncode:
                return 2
            rows = [json.loads(line) for line in dump.stdout.splitlines() if line.strip()]
            json.dump(
                {"baseline": "PASS", "scope": tomllib.loads(config.read_text(encoding="utf-8"))["cosmic-ray"]["module-path"], "results": rows}, report, indent=2
            )
            report.write("\n")
            return _outcome(rows)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(f"mutation: {error}", file=sys.stderr)
        return 2
