from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
import sys
from typing import TextIO

from backlog.parse import MarkdownParseError, parse_repository
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
    with redirect_stderr(errors):
        try:
            arguments = parser.parse_args(argv)
        except SystemExit as error:
            return 2 if error.code is None else int(error.code)
    selected_root = repository_root() if root is None else root
    try:
        snapshot = with_dependency_readiness(parse_repository(selected_root))
        report = build_report(snapshot, observe_git(selected_root))
    except (MarkdownParseError, OSError, subprocess.SubprocessError) as error:
        print(error, file=errors)
        return 1
    output.write(render_json(report) if arguments.as_json else render_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
