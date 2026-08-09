"""Run repository quality gates."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass

SOURCE_PATHS = ("xplane_fdr", "tests", "tools")
PYTHON_QUALITY_PATHS = SOURCE_PATHS
SECRET_SCAN_PATHS = (".",)
SECRET_BASELINE = ".secrets.baseline"
COVERAGE_MINIMUM = "40"
XENON_MAX_ABSOLUTE = "C"
XENON_MAX_MODULES = "B"
XENON_MAX_AVERAGE = "A"


@dataclass(frozen=True)
class Step:
    """Describe one executable quality check."""

    name: str
    command: tuple[str, ...]
    tracked_paths: tuple[str, ...] = ()


def uv(*args: str) -> tuple[str, ...]:
    """Build a command that executes a development tool through uv."""
    return ("uv", "run", *args)


COMMANDS: dict[str, tuple[Step, ...]] = {
    "lint": (Step("ruff check", uv("ruff", "check", *SOURCE_PATHS)),),
    "format-check": (Step("ruff format --check", uv("ruff", "format", "--check", *SOURCE_PATHS)),),
    "format": (Step("ruff format", uv("ruff", "format", *SOURCE_PATHS)),),
    "typecheck": (Step("ty check", uv("ty", "check")),),
    "test": (Step("unittest", uv("python", "-m", "unittest", "discover", "-v")),),
    "coverage": (
        Step("coverage run", uv("coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-t", ".")),
        Step("coverage report", uv("coverage", "report", f"--fail-under={COVERAGE_MINIMUM}")),
    ),
    "security": (
        Step("bandit", uv("bandit", "-q", "-r", "xplane_fdr")),
        Step("detect-secrets baseline", uv("detect-secrets-hook", "--baseline", SECRET_BASELINE), tracked_paths=SECRET_SCAN_PATHS),
        Step("detect-secrets report", uv("detect-secrets", "audit", "--report", SECRET_BASELINE)),
    ),
    "docs": (Step("interrogate", uv("interrogate", "-v", "-f", "40", "xplane_fdr")),),
    "dead-code": (Step("vulture", uv("vulture", *PYTHON_QUALITY_PATHS, "--min-confidence", "80")),),
    "metrics": (
        Step("lizard report", uv("lizard", "xplane_fdr", "-i", "-1")),
        Step("cohesion report", uv("cohesion", "-d", "xplane_fdr")),
    ),
    "wily": (
        Step("wily build", uv("wily", "build", "xplane_fdr")),
        Step("wily report", uv("wily", "report", "xplane_fdr")),
    ),
    "complexity": (
        Step(
            "xenon complexity",
            uv(
                "xenon",
                "--max-absolute",
                XENON_MAX_ABSOLUTE,
                "--max-modules",
                XENON_MAX_MODULES,
                "--max-average",
                XENON_MAX_AVERAGE,
                "xplane_fdr",
            ),
        ),
    ),
    "pre-commit": (Step("pre-commit", uv("pre-commit", "run", "--all-files")),),
}

CHECK_STEPS = (
    *COMMANDS["lint"],
    *COMMANDS["format-check"],
    *COMMANDS["typecheck"],
    *COMMANDS["test"],
    *COMMANDS["coverage"],
    *COMMANDS["security"],
    *COMMANDS["docs"],
    *COMMANDS["dead-code"],
    *COMMANDS["complexity"],
)


def run_steps(steps: Sequence[Step], runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run) -> int:
    """Run steps in order and stop at the first failed command."""
    for step in steps:
        command = step.command
        if step.tracked_paths:
            tracked = runner(("git", "ls-files", "--", *step.tracked_paths), check=False, capture_output=True, text=True)
            if tracked.returncode != 0:
                return tracked.returncode
            command = (*command, *(line for line in tracked.stdout.splitlines() if line))

        print(f"==> {step.name}: {' '.join(command)}", flush=True)
        result = runner(command, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse the requested quality gate."""
    parser = argparse.ArgumentParser(description="Run xplane-fdr quality gates.")
    parser.add_argument("gate", choices=(*COMMANDS, "check"), help="Quality gate to run; 'check' runs the blocking suite.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the selected quality gate."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_steps(CHECK_STEPS if args.gate == "check" else COMMANDS[args.gate])


if __name__ == "__main__":
    raise SystemExit(main())
