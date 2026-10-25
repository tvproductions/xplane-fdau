"""Run repository quality gates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

if bool(__package__):
    from . import quality_analysis, quality_mutation
else:
    import quality_analysis
    import quality_mutation

SOURCE_PATH = "src/xplane_fdau"
SOURCE_PATHS = (SOURCE_PATH, "tests", "tools", ".codex/skills")
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
    return ("uv", "run", "--locked", "--all-groups", *args)


COMMANDS: dict[str, tuple[Step, ...]] = {
    "lint": (Step("ruff check", uv("ruff", "check", *SOURCE_PATHS)),),
    "format-check": (Step("ruff format --check", uv("ruff", "format", "--check", *SOURCE_PATHS)),),
    "format": (Step("ruff format", uv("ruff", "format", *SOURCE_PATHS)),),
    "typecheck": (Step("ty check", uv("ty", "check")),),
    "test": (Step("unittest", uv("python", "-m", "unittest", "discover", "-q")),),
    "preflight": (
        Step(
            "live-state preflight",
            uv(
                "python",
                "-m",
                "unittest",
                "tests.test_backlog_status_cli.BacklogStatusCliTests.test_current_repository_status_reports_human_and_json",
                "tests.test_project_metadata.ProjectMetadataTests.test_runtime_package_uses_only_installed_src_layout",
            ),
        ),
    ),
    "coverage": (
        Step("coverage run", uv("coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-t", ".")),
        Step("coverage report", uv("coverage", "report", f"--fail-under={COVERAGE_MINIMUM}")),
    ),
    "security": (
        Step("bandit", uv("bandit", "-q", "-r", SOURCE_PATH)),
        Step("detect-secrets baseline", uv("detect-secrets-hook", "--baseline", SECRET_BASELINE), tracked_paths=SECRET_SCAN_PATHS),
        Step("detect-secrets report", uv("detect-secrets", "audit", "--report", SECRET_BASELINE)),
    ),
    "docs": (Step("interrogate", uv("interrogate", "-v", "-f", "40", SOURCE_PATH)),),
    "dead-code": (Step("vulture", uv("vulture", *PYTHON_QUALITY_PATHS, "--min-confidence", "80")),),
    "metrics": (
        Step("lizard report", uv("lizard", SOURCE_PATH, "-i", "-1")),
        Step("cohesion report", uv("cohesion", "-d", SOURCE_PATH)),
    ),
    "wily": (
        Step("wily build", uv("wily", "build", SOURCE_PATH)),
        Step("wily report", uv("wily", "report", SOURCE_PATH)),
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
                SOURCE_PATH,
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
)

COMMANDS["analysis"] = (
    Step("Ruff C901", uv("ruff", "check", "--select", "C901", *SOURCE_PATHS)),
    Step("Bandit", uv("bandit", "-r", SOURCE_PATH, "tools", ".codex/skills")),
    *COMMANDS["security"][1:],
    *COMMANDS["docs"],
    *COMMANDS["dead-code"],
    Step("cohesion report", uv("cohesion", "-d", SOURCE_PATH)),
    Step("dependency declarations", uv("deptry", "src", "--config", "pyproject.toml", "--no-ansi")),
    Step("import boundaries", uv("lint-imports")),
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
    parser = argparse.ArgumentParser(description="Run xplane-fdau quality gates.")
    parser.add_argument("gate", choices=(*COMMANDS, "check", "vulnerabilities", "mutation"), help="Quality gate to run; 'check' runs the blocking suite.")
    parser.add_argument("--output", type=Path, help="New analysis or mutation JSON report path; existing files are preserved.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the selected quality gate."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.output is not None and args.gate not in ("analysis", "mutation"):
        print("--output is supported only for analysis or mutation", file=sys.stderr)
        return 2
    if args.gate == "mutation":
        if args.output is None:
            print("mutation requires --output for retained native results", file=sys.stderr)
            return 2
        return quality_mutation.run_mutation(Path.cwd(), args.output, runner=quality_analysis.run_bounded)
    if args.gate == "vulnerabilities":
        return quality_analysis.audit_dependencies(Path.cwd())
    if args.gate == "analysis":
        return run_deeper_analysis(args.output)
    return run_steps(CHECK_STEPS if args.gate == "check" else COMMANDS[args.gate])


def run_deeper_analysis(output: Path | None) -> int:
    """Record available static results and the explicit cognitive prerequisite."""
    try:
        # Reserve exclusively before running tools so a prior report survives intact.
        with output.open("x", encoding="utf-8", newline="\n") if output is not None else _stdout_report() as destination:
            report = {
                "lizard": quality_analysis.measure_lizard(Path.cwd(), SOURCE_PATHS),
                "cognitive": quality_analysis.cognitive_status(),
                "other_checks_exit_code": quality_analysis.run_analysis(COMMANDS["analysis"], runner=subprocess.run),
            }
            json.dump(report, destination, indent=2)
            destination.write("\n")
            # Required cognitive proof is unavailable; this command cannot pass yet.
            return max(2, quality_analysis.evaluate_lizard(report["lizard"]), report["other_checks_exit_code"])
    except (OSError, ValueError) as error:
        print(f"analysis report: {error}", file=sys.stderr)
        return 2


def _stdout_report():
    """Borrow standard output without closing the process-owned stream."""
    from contextlib import nullcontext

    return nullcontext(sys.stdout)


if __name__ == "__main__":
    raise SystemExit(main())
