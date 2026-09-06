from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from pathlib import Path
from io import TextIOWrapper
import subprocess
import sys
from typing import TextIO

from backlog.audit import audit_repository
from backlog.model import Finding, GitState
from backlog.report import build_report, observe_git, render_human, render_json, with_dependency_readiness


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def main(
    argv: list[str] | None = None,
    *,
    root: Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    output = sys.stdout if stdout is None else stdout
    errors = sys.stderr if stderr is None else stderr
    parser = argparse.ArgumentParser(prog="backlog-status")
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="report repository delivery status")
    status.add_argument("--json", action="store_true", dest="as_json")
    commands.add_parser("audit", help="audit repository structure, adherence, and evidence")
    commands.add_parser("next", help="recommend the next Superpowers lifecycle action")
    with redirect_stderr(errors):
        try:
            arguments = parser.parse_args(argv)
        except SystemExit as error:
            return 2 if error.code is None else int(error.code)
    selected_root = repository_root() if root is None else root
    loaded = audit_repository(selected_root)
    snapshot = with_dependency_readiness(loaded.snapshot)
    findings = loaded.findings
    try:
        git = observe_git(selected_root)
    except (OSError, subprocess.SubprocessError) as error:
        git = GitState("", False, ())
        findings = (*findings, Finding("git.unavailable", "error", ".", None, None, None, f"cannot observe Git: {error}"))
    report = build_report(snapshot, git, findings)
    output.write(render_json(report) if arguments.command == "status" and arguments.as_json else render_human(report))
    return 0 if report.valid else 1


if __name__ == "__main__":
    if isinstance(sys.stdout, TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    raise SystemExit(main())
