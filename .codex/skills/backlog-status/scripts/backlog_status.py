from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from pathlib import Path
from io import TextIOWrapper
import re
import subprocess
import sys
from typing import TextIO

from backlog.audit import audit_repository
from backlog.edit import (
    MutationPlan,
    MutationRefusal,
    plan_selection,
    plan_transition,
    plan_record_gate,
    plan_reopen_gate,
    plan_suspend,
    plan_resume,
    publish_mutation,
)
from backlog.model import AuditLoad, CHILD_STATUSES, Finding, GitState
from backlog.report import build_report, observe_git, render_human, render_json, with_dependency_readiness


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _target_hash(value: str) -> str:
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise argparse.ArgumentTypeError("target SHA-256 must be 64 lowercase hexadecimal characters")
    return value


def _ordinal(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("gate ordinal must be a positive integer") from error
    if number < 1:
        raise argparse.ArgumentTypeError("gate ordinal must be a positive integer")
    return number


def _mutation_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target-sha256", type=_target_hash)
    parser.add_argument("--apply", action="store_true")


def _mutation_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    statuses = tuple(status for status in CHILD_STATUSES if status != "released")
    nonsuspended = tuple(status for status in statuses if status not in {"blocked", "deferred"})
    selection = commands.add_parser("select", help="select or clear the active local child")
    selection.add_argument("child")
    selection.add_argument("--expect-current", required=True)
    transition = commands.add_parser("transition", help="transition one local child")
    transition.add_argument("child")
    transition.add_argument("target", choices=nonsuspended)
    transition.add_argument("--expect", required=True, choices=statuses)
    for option in ("specification", "plan", "review"):
        transition.add_argument(f"--{option}")
    record = commands.add_parser("record-gate", help="record evidence for one open gate")
    record.add_argument("child")
    record.add_argument("ordinal", type=_ordinal)
    record.add_argument("--expect-open", required=True, action="store_true")
    record.add_argument("--evidence", required=True, action="append")
    reopen = commands.add_parser("reopen-gate", help="reopen one closed gate")
    reopen.add_argument("child")
    reopen.add_argument("ordinal", type=_ordinal)
    reopen.add_argument("--expect-closed", required=True, action="store_true")
    reopen.add_argument("--reason", required=True)
    suspend = commands.add_parser("suspend", help="suspend one local child")
    suspend.add_argument("child")
    suspend.add_argument("target", choices=("blocked", "deferred"))
    suspend.add_argument("--expect", required=True, choices=nonsuspended)
    suspend.add_argument("--reason", required=True)
    resume = commands.add_parser("resume", help="restore a suspended local child")
    resume.add_argument("child")
    resume.add_argument("--expect", required=True, choices=("blocked", "deferred"))
    resume.add_argument("--resume", required=True, choices=nonsuspended)
    resume.add_argument("--reason", required=True)
    for command in (selection, transition, record, reopen, suspend, resume):
        _mutation_options(command)


def _plan_mutation(root: Path, args: argparse.Namespace) -> MutationPlan:
    if args.command == "select":
        return plan_selection(
            root,
            None if args.child == "none" else args.child,
            expect_current=None if args.expect_current == "none" else args.expect_current,
            target_sha256=args.target_sha256,
        )
    if args.command == "transition":
        return plan_transition(
            root,
            args.child,
            args.target,
            expect=args.expect,
            specification=args.specification,
            plan=args.plan,
            review=args.review,
            target_sha256=args.target_sha256,
        )
    if args.command == "record-gate":
        return plan_record_gate(root, args.child, args.ordinal, expect_open=args.expect_open, evidence=tuple(args.evidence), target_sha256=args.target_sha256)
    if args.command == "reopen-gate":
        return plan_reopen_gate(root, args.child, args.ordinal, expect_closed=args.expect_closed, reason=args.reason, target_sha256=args.target_sha256)
    if args.command == "suspend":
        return plan_suspend(root, args.child, args.target, expect=args.expect, reason=args.reason, target_sha256=args.target_sha256)
    return plan_resume(root, args.child, expect=args.expect, resume=args.resume, reason=args.reason, target_sha256=args.target_sha256)


def _mutation_heading(plan: MutationPlan, *, applied: bool) -> str:
    lines = [
        f"Mutation: {plan.summary}",
        f"Mode: {'applied' if applied else 'dry-run'}",
        "Target: BACKLOG.md",
        f"Original SHA-256: {plan.original_sha256}",
        f"Candidate SHA-256: {plan.candidate_sha256}",
    ]
    if plan.rationale is not None:
        lines.append(f"Rationale: {plan.rationale}")
    return "\n".join(lines) + "\nDiff:\n" + plan.diff.replace("\r\n", "\n").rstrip("\n") + "\nPost-change audit:\n"


def _published_reporting_failure(loaded: AuditLoad, error: Exception) -> str:
    """Retain the completed audit even if normal report assembly is unavailable."""
    message = f"mutation.published: BACKLOG.md was published, but reporting failed; do not retry: {error}\nPost-change audit:\n"
    try:
        report = build_report(with_dependency_readiness(loaded.snapshot), GitState("", False, ()), loaded.findings)
        return message + render_human(report)
    except Exception:
        lines = ["Full report unavailable; completed audit results follow.", f"Active child: {loaded.snapshot.backlog.active_child or '—'}"]
        lines.append("Findings:" if loaded.findings else "Findings: none")
        lines.extend(f"  {item.severity} {item.code} {item.path}:{item.line} node={item.node} gate={item.gate} {item.message}" for item in loaded.findings)
        return message + "\n".join(lines) + "\n"


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
    _mutation_commands(commands)
    with redirect_stderr(errors):
        try:
            arguments = parser.parse_args(argv)
        except SystemExit as error:
            return 2 if error.code is None else int(error.code)
    selected_root = repository_root() if root is None else root
    plan: MutationPlan | None = None
    published = False
    if arguments.command in {"status", "audit", "next"}:
        loaded = audit_repository(selected_root)
    else:
        try:
            plan = _plan_mutation(selected_root, arguments)
            loaded = publish_mutation(plan) if arguments.apply else plan.audit
            published = arguments.apply
        except MutationRefusal as error:
            code = error.code if error.code.startswith("mutation.") else f"mutation.audit ({error.code})"
            output.write(f"{code}: {error}\n")
            return 1
    try:
        heading = _mutation_heading(plan, applied=published) if plan is not None else ""
        snapshot = with_dependency_readiness(loaded.snapshot)
        findings = loaded.findings
        try:
            git = observe_git(selected_root)
        except (OSError, subprocess.SubprocessError) as error:
            git = GitState("", False, ())
            findings = (*findings, Finding("git.unavailable", "error", ".", None, None, None, f"cannot observe Git: {error}"))
            if published:
                findings = (*findings, Finding("mutation.published", "error", "BACKLOG.md", None, None, None, "BACKLOG.md was published; do not retry."))
        report = build_report(snapshot, git, findings)
        output.write(heading + (render_json(report) if arguments.command == "status" and arguments.as_json else render_human(report)))
        return 0 if report.valid else 1
    except Exception as error:
        if not published:
            raise
        message = _published_reporting_failure(loaded, error)
        try:
            output.write(message)
        except Exception:
            errors.write(message)
        return 1


if __name__ == "__main__":
    if isinstance(sys.stdout, TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    raise SystemExit(main())
