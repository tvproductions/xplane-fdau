from __future__ import annotations

from dataclasses import dataclass
import difflib
import hashlib
from pathlib import Path
import re
from typing import NoReturn

from backlog.audit import audit_repository
from backlog.model import AuditLoad


@dataclass(frozen=True, slots=True)
class MutationPlan:
    root: Path
    target: Path
    original: bytes
    candidate: bytes
    original_sha256: str
    candidate_sha256: str
    diff: str
    summary: str
    rationale: str | None
    audit: AuditLoad


class MutationRefusal(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _refuse(code: str, message: str) -> NoReturn:
    raise MutationRefusal(code, message)


def _target(root: Path) -> tuple[Path, Path]:
    resolved = root.resolve()
    target = resolved / "BACKLOG.md"
    try:
        if target.is_symlink() or not target.is_file():
            _refuse("mutation.target", "BACKLOG.md must be a regular non-symlink file")
        if target.resolve().parent != resolved:
            _refuse("mutation.target", "BACKLOG.md must remain inside the repository root")
    except OSError as error:
        _refuse("mutation.target", f"cannot inspect BACKLOG.md: {error}")
    return resolved, target


def _read_target(target: Path) -> tuple[bytes, str]:
    try:
        original = target.read_bytes()
    except OSError as error:
        _refuse("mutation.target", f"cannot read BACKLOG.md: {error}")
    try:
        return original, original.decode("utf-8")
    except UnicodeDecodeError as error:
        _refuse("mutation.target", f"BACKLOG.md is not strict UTF-8: {error}")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _has_errors(loaded: AuditLoad) -> bool:
    return any(finding.severity == "error" for finding in loaded.findings)


def _selection_line(text: str, line_number: int, replacement: str) -> str:
    lines = text.splitlines(keepends=True)
    index = line_number - 1
    if not 0 <= index < len(lines):
        _refuse("mutation.audit", "active-child source line is outside BACKLOG.md")
    original = lines[index]
    if original.endswith("\r\n"):
        terminator = "\r\n"
    elif original.endswith("\n"):
        terminator = "\n"
    else:
        terminator = ""
    lines[index] = replacement + terminator
    return "".join(lines)


def _validate_target_hash(target_sha256: str | None, original_sha256: str) -> None:
    if target_sha256 is None:
        return
    if re.fullmatch(r"[0-9a-f]{64}", target_sha256) is None:
        _refuse("mutation.target-sha256", "target SHA-256 must be 64 lowercase hexadecimal characters")
    if target_sha256 != original_sha256:
        _refuse("mutation.stale", "BACKLOG.md no longer matches the requested target SHA-256")


def plan_selection(
    root: Path,
    child: str | None,
    *,
    expect_current: str | None,
    target_sha256: str | None = None,
) -> MutationPlan:
    """Plan an exact active-child edit without writing the repository."""
    resolved, target = _target(root)
    original, original_text = _read_target(target)
    original_sha256 = _sha256(original)
    _validate_target_hash(target_sha256, original_sha256)

    current_audit = audit_repository(resolved, backlog_text=original_text)
    if _has_errors(current_audit):
        _refuse("mutation.audit", "BACKLOG.md cannot be edited while the repository audit has errors")
    selection = current_audit.sources.selection
    if selection is None:
        _refuse("mutation.audit", "repository audit did not provide one BACKLOG.md selection source")
    if selection.source.path != "BACKLOG.md":
        _refuse("mutation.audit", "repository audit did not provide one BACKLOG.md selection source")
    if selection.child != expect_current:
        _refuse("mutation.expected-selection", "active-child selection differs from the expected current value")
    local_children = {item.id for item in current_audit.snapshot.roadmap.local_children}
    if child is not None and child not in local_children:
        _refuse("mutation.target", "active-child target must be a local roadmap child")
    if child == selection.child:
        _refuse("mutation.target", "active-child target would not change BACKLOG.md")

    replacement = "- Active child: —." if child is None else f"- Active child: `{child}`."
    candidate_text = _selection_line(original_text, selection.source.line, replacement)
    candidate = candidate_text.encode("utf-8")
    candidate_audit = audit_repository(resolved, backlog_text=candidate_text)
    if _has_errors(candidate_audit):
        _refuse("mutation.audit", "planned active-child selection fails repository audit")
    diff = "".join(
        difflib.unified_diff(
            original_text.splitlines(keepends=True),
            candidate_text.splitlines(keepends=True),
            fromfile="a/BACKLOG.md",
            tofile="b/BACKLOG.md",
        )
    )
    summary = "Clear active child selection." if child is None else f"Select active child `{child}`."
    return MutationPlan(
        resolved,
        target,
        original,
        candidate,
        original_sha256,
        _sha256(candidate),
        diff,
        summary,
        "Requested active-child selection.",
        candidate_audit,
    )
