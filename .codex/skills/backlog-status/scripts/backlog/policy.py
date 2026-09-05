from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import subprocess
from typing import Literal, TypeAlias

from backlog.model import AuditPolicy, HistoricalAdmission, SpecificationArtifact
from backlog.parse import MarkdownParseError, parse_artifact


EvidenceSlot: TypeAlias = Literal["gate", "review", "completion", "release"]

POLICY_PATH = "docs/superpowers/specs/2026-09-05-t1-3-audit-policy-supplement-design.md"
_TABLE_HEADER = "| Child | Historical plan | SHA-256 |"
_TABLE_SEPARATOR = "| --- | --- | --- |"
_ADMISSION_ROW = re.compile(r"^\| `([A-Z][0-9]+\.[0-9]+)` \| `([^`]+)` \| `([0-9a-f]{64})` \|$")
_APPROVAL = re.compile(r"^(\d{4}-\d{2}-\d{2}) — (\S(?:.*\S)?)$")
_ALLOWED_KINDS: dict[EvidenceSlot, frozenset[str]] = {
    "gate": frozenset({"verification", "artifact"}),
    "review": frozenset({"review"}),
    "completion": frozenset({"verification", "artifact"}),
    "release": frozenset({"verification", "artifact"}),
}


class PolicyError(ValueError):
    def __init__(self, code: str, path: str, line: int | None, message: str) -> None:
        self.code = code
        self.path = path
        self.line = line
        self.message = message
        location = path if line is None else f"{path}:{line}"
        super().__init__(f"{location}: {message}")


def allowed_kinds(slot: EvidenceSlot) -> frozenset[str]:
    return _ALLOWED_KINDS[slot]


def _git_blob(root: Path, object_name: str) -> bytes:
    completed = subprocess.run(
        ("git", "-C", str(root), "show", object_name),
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise PolicyError("policy.unavailable", POLICY_PATH, 1, "policy must exist in both the Git index and HEAD")
    return completed.stdout


def _approval_line(lines: tuple[str, ...]) -> tuple[int, str] | None:
    prefix = "- **Approval:** "
    matches = [(index, line[len(prefix) :]) for index, line in enumerate(lines, start=1) if line.startswith(prefix)]
    return matches[0] if len(matches) == 1 else None


def _validate_approval(lines: tuple[str, ...], artifact: SpecificationArtifact) -> None:
    if artifact.status not in {"approved", "implemented"} or artifact.approval is None:
        raise PolicyError("policy.unapproved", POLICY_PATH, artifact.source.line, "policy must be approved or implemented")
    located = _approval_line(lines)
    if located is None:
        raise PolicyError("policy.invalid", POLICY_PATH, None, "policy requires exactly one Approval metadata field")
    line, value = located
    match = _APPROVAL.fullmatch(value)
    if match is None:
        raise PolicyError("policy.invalid", POLICY_PATH, line, "policy Approval metadata is malformed")
    try:
        date.fromisoformat(match.group(1))
    except ValueError as error:
        raise PolicyError("policy.invalid", POLICY_PATH, line, "policy Approval date is invalid") from error


def _validate_plan_path(value: str, line: int) -> str:
    parts = value.split("/")
    if not value.startswith("docs/superpowers/plans/") or not value.endswith(".md") or "\\" in value or any(part in {"", ".", ".."} for part in parts):
        raise PolicyError("policy.invalid", POLICY_PATH, line, "historical plan must be a repository-relative plan path")
    return value


def _historical_admissions(lines: tuple[str, ...]) -> tuple[HistoricalAdmission, ...]:
    headers = [index for index, line in enumerate(lines) if line == _TABLE_HEADER]
    if len(headers) != 1:
        line = headers[1] + 1 if len(headers) > 1 else None
        raise PolicyError("policy.invalid", POLICY_PATH, line, "policy requires exactly one historical admission table")
    header = headers[0]
    if header + 1 >= len(lines) or lines[header + 1] != _TABLE_SEPARATOR:
        raise PolicyError("policy.invalid", POLICY_PATH, header + 2, "historical admission table separator is invalid")
    admissions: list[HistoricalAdmission] = []
    seen_children: set[str] = set()
    seen_paths: set[str] = set()
    for index in range(header + 2, len(lines)):
        text = lines[index]
        if not text.startswith("|"):
            break
        match = _ADMISSION_ROW.fullmatch(text)
        if match is None:
            raise PolicyError("policy.invalid", POLICY_PATH, index + 1, "historical admission row is invalid")
        child, plan, digest = match.groups()
        plan = _validate_plan_path(plan, index + 1)
        if child in seen_children or plan in seen_paths:
            raise PolicyError("policy.invalid", POLICY_PATH, index + 1, "historical admission child and plan must be unique")
        seen_children.add(child)
        seen_paths.add(plan)
        admissions.append(HistoricalAdmission(child, plan, digest))
    if not admissions:
        raise PolicyError("policy.invalid", POLICY_PATH, header + 1, "historical admission table must contain a row")
    return tuple(admissions)


def load_policy(root: Path) -> AuditPolicy:
    resolved = root.resolve()
    path = resolved / POLICY_PATH
    try:
        content = path.read_bytes()
    except OSError as error:
        raise PolicyError("policy.unavailable", POLICY_PATH, 1, f"cannot read policy: {error}") from error
    index_content = _git_blob(resolved, f":{POLICY_PATH}")
    head_content = _git_blob(resolved, f"HEAD:{POLICY_PATH}")
    if content != index_content or content != head_content:
        raise PolicyError("policy.unavailable", POLICY_PATH, 1, "policy bytes must match the Git index and HEAD")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PolicyError("policy.invalid", POLICY_PATH, 1, "policy must be UTF-8 Markdown") from error
    lines = tuple(text.splitlines())
    try:
        parsed = parse_artifact(resolved, path, "specification")
    except MarkdownParseError as error:
        raise PolicyError("policy.invalid", POLICY_PATH, error.line, error.message) from error
    if not isinstance(parsed, SpecificationArtifact):
        raise PolicyError("policy.invalid", POLICY_PATH, parsed.source.line, "policy must use active design metadata")
    _validate_approval(lines, parsed)
    return AuditPolicy(_historical_admissions(lines))
