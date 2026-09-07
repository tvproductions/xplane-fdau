from __future__ import annotations

from dataclasses import dataclass
import difflib
import hashlib
from pathlib import Path
import re
from typing import Literal, NoReturn

from backlog.audit import audit_repository
from backlog.model import AuditLoad, BacklogChild, ChildStatus


_TRANSITIONS = frozenset(
    {
        ("queued", "designing"),
        ("designing", "specified"),
        ("specified", "planned"),
        ("planned", "in_progress"),
        ("in_progress", "implemented"),
        ("implemented", "reviewed"),
        ("reviewed", "verified"),
        ("specified", "designing"),
        ("planned", "specified"),
        ("in_progress", "planned"),
        ("implemented", "in_progress"),
        ("reviewed", "implemented"),
        ("verified", "reviewed"),
    }
)
_NONSUSPENDED = frozenset(
    {"queued", "designing", "specified", "planned", "in_progress", "implemented", "reviewed", "verified"}
)
_LINK_CELLS = {"designing": ("specification", 4, "design"), "planned": ("plan", 5, "plan"), "reviewed": ("review", 7, "review")}


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


def _inventory_line(text: str, line_number: int, replacements: dict[int, str]) -> str:
    """Replace only named managed inventory cells, retaining cell whitespace and line ending."""
    lines = text.splitlines(keepends=True)
    index = line_number - 1
    if not 0 <= index < len(lines):
        _refuse("mutation.audit", "inventory source line is outside BACKLOG.md")
    original = lines[index]
    if original.endswith("\r\n"):
        content, terminator = original[:-2], "\r\n"
    elif original.endswith("\n"):
        content, terminator = original[:-1], "\n"
    else:
        content, terminator = original, ""
    cells = content.split("|")
    if len(cells) != 12 or cells[0] or cells[-1]:
        _refuse("mutation.audit", "inventory source line is not a managed ten-cell row")
    for cell_index, value in replacements.items():
        if not 0 <= cell_index < 10:
            _refuse("mutation.audit", "inventory replacement names an invalid managed cell")
        existing = cells[cell_index + 1]
        leading = existing[: len(existing) - len(existing.lstrip())]
        trailing = existing[len(existing.rstrip()) :]
        cells[cell_index + 1] = f"{leading}{value}{trailing}"
    lines[index] = "|".join(cells) + terminator
    return "".join(lines)


def _validate_link(path: str | None, label: str) -> str | None:
    if path is None:
        return None
    if not path or any(character in path for character in ("|", "\n", "\r")):
        _refuse("mutation.link", f"{label} link must be a nonempty single Markdown-table cell path")
    return path


def _validate_reason(reason: str) -> None:
    if not reason or reason != reason.strip() or any(character in reason for character in ("|", "\n", "\r")):
        _refuse("mutation.reason", "reason must be nonempty, trimmed, and free of table delimiters or line breaks")


def _prepare_child(
    root: Path, child_id: str, target_sha256: str | None
) -> tuple[Path, Path, bytes, str, str, AuditLoad, BacklogChild, int]:
    resolved, target = _target(root)
    original, original_text = _read_target(target)
    original_sha256 = _sha256(original)
    _validate_target_hash(target_sha256, original_sha256)
    current_audit = audit_repository(resolved, backlog_text=original_text)
    if _has_errors(current_audit):
        _refuse("mutation.audit", "BACKLOG.md cannot be edited while the repository audit has errors")
    children = [item for item in current_audit.snapshot.backlog.children if item.id == child_id]
    rows = [item for item in current_audit.sources.inventory_rows if item.child == child_id and item.source.path == "BACKLOG.md"]
    if len(children) != 1 or len(rows) != 1:
        _refuse("mutation.target", "mutation target must be one local backlog child")
    return resolved, target, original, original_text, original_sha256, current_audit, children[0], rows[0].source.line


def _finish_plan(
    resolved: Path,
    target: Path,
    original: bytes,
    original_text: str,
    original_sha256: str,
    candidate_text: str,
    summary: str,
    rationale: str,
) -> MutationPlan:
    candidate = candidate_text.encode("utf-8")
    candidate_audit = audit_repository(resolved, backlog_text=candidate_text)
    if _has_errors(candidate_audit):
        _refuse("mutation.audit", "planned lifecycle mutation fails repository audit")
    diff = "".join(
        difflib.unified_diff(
            original_text.splitlines(keepends=True),
            candidate_text.splitlines(keepends=True),
            fromfile="a/BACKLOG.md",
            tofile="b/BACKLOG.md",
        )
    )
    return MutationPlan(
        resolved,
        target,
        original,
        candidate,
        original_sha256,
        _sha256(candidate),
        diff,
        summary,
        rationale,
        candidate_audit,
    )


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


def plan_transition(
    root: Path,
    child: str,
    target: ChildStatus,
    *,
    expect: ChildStatus,
    specification: str | None = None,
    plan: str | None = None,
    review: str | None = None,
    target_sha256: str | None = None,
) -> MutationPlan:
    """Plan one exact nonsuspended lifecycle transition."""
    resolved, backlog_path, original, original_text, original_sha256, _, current, line = _prepare_child(root, child, target_sha256)
    if current.status != expect:
        _refuse("mutation.expected-status", "child status differs from the expected current status")
    if (expect, target) not in _TRANSITIONS:
        _refuse("mutation.transition", "requested lifecycle transition is outside the closed transition graph")
    supplied = {"specification": specification, "plan": plan, "review": review}
    allowed = _LINK_CELLS.get(target)
    if any(value is not None for value in supplied.values()):
        if allowed is None or any(name != allowed[0] and value is not None for name, value in supplied.items()):
            _refuse("mutation.link", "a lifecycle link may update only the target stage's managed link cell")
        _validate_link(supplied[allowed[0]], allowed[2])
    replacements = {2: f"`{target}`"}
    if allowed is not None and supplied[allowed[0]] is not None:
        replacements[allowed[1]] = f"[{allowed[2]}]({supplied[allowed[0]]})"
    if expect == "reviewed" and target == "implemented":
        replacements[7] = "—"
    candidate_text = _inventory_line(original_text, line, replacements)
    rationale = f"Requested lifecycle transition from `{expect}` to `{target}`."
    return _finish_plan(
        resolved,
        backlog_path,
        original,
        original_text,
        original_sha256,
        candidate_text,
        f"Transition `{child}` from `{expect}` to `{target}`.",
        rationale,
    )


def plan_suspend(
    root: Path,
    child: str,
    target: Literal["blocked", "deferred"],
    *,
    expect: ChildStatus,
    reason: str,
    target_sha256: str | None = None,
) -> MutationPlan:
    """Plan suspension while retaining the exact resume state."""
    _validate_reason(reason)
    resolved, backlog_path, original, original_text, original_sha256, _, current, line = _prepare_child(root, child, target_sha256)
    if current.status != expect:
        _refuse("mutation.expected-status", "child status differs from the expected current status")
    if expect not in _NONSUSPENDED:
        _refuse("mutation.transition", "only a nonsuspended lifecycle state may be suspended")
    candidate_text = _inventory_line(original_text, line, {2: f"`{target}`", 8: f"`{expect}`", 9: reason})
    rationale = f"Suspended `{expect}` child as `{target}`: {reason}"
    return _finish_plan(
        resolved,
        backlog_path,
        original,
        original_text,
        original_sha256,
        candidate_text,
        f"Suspend `{child}` as `{target}`.",
        rationale,
    )


def plan_resume(
    root: Path,
    child: str,
    *,
    expect: Literal["blocked", "deferred"],
    resume: ChildStatus,
    reason: str,
    target_sha256: str | None = None,
) -> MutationPlan:
    """Plan restoration of one suspended child."""
    _validate_reason(reason)
    resolved, backlog_path, original, original_text, original_sha256, _, current, line = _prepare_child(root, child, target_sha256)
    if current.status != expect:
        _refuse("mutation.expected-status", "child status differs from the expected suspended status")
    if expect not in {"blocked", "deferred"}:
        _refuse("mutation.transition", "only a blocked or deferred child may be resumed")
    if current.resume_state != resume:
        _refuse("mutation.resume", "stored resume state differs from the requested resume state")
    candidate_text = _inventory_line(original_text, line, {2: f"`{resume}`", 8: "—", 9: "—"})
    rationale = f"Resumed `{resume}` child from `{expect}`: {reason}"
    return _finish_plan(
        resolved,
        backlog_path,
        original,
        original_text,
        original_sha256,
        candidate_text,
        f"Resume `{child}` as `{resume}`.",
        rationale,
    )
