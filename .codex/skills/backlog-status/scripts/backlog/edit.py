from __future__ import annotations

from dataclasses import dataclass
import difflib
import hashlib
from pathlib import Path
import re
from typing import Literal, NoReturn

from backlog.audit import audit_repository
from backlog.model import AuditLoad, BacklogChild, ChildStatus, GateItem


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
_NONSUSPENDED = frozenset({"queued", "designing", "specified", "planned", "in_progress", "implemented", "reviewed", "verified"})
_LINK_CELLS = {"designing": ("specification", 4, "design"), "planned": ("plan", 5, "plan"), "reviewed": ("review", 7, "review")}
_GATE_MARKER = re.compile(r"^- \[([ x])\] ")


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


def _validate_gate_evidence(evidence: tuple[str, ...]) -> tuple[str, ...]:
    if not evidence:
        _refuse("mutation.evidence", "gate recording requires one or more evidence paths")
    normalized: list[str] = []
    for path in evidence:
        if not isinstance(path, str):
            _refuse("mutation.evidence", "evidence paths must be repository-relative Markdown paths")
        parts = path.split("/")
        if (
            not path.endswith(".md")
            or path.startswith("/")
            or "\\" in path
            or ":" in path
            or any(part in {"", ".", ".."} for part in parts)
            or any(character in path for character in ("|", "\n", "\r", "(", ")"))
        ):
            _refuse("mutation.evidence", "evidence paths must be repository-relative Markdown paths")
        normalized.append("/".join(parts))
    if len(normalized) != len(set(normalized)):
        _refuse("mutation.evidence", "evidence paths must not repeat after normalization")
    return tuple(sorted(normalized))


def _gate_item(child: BacklogChild, ordinal: int) -> GateItem:
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1 or ordinal > len(child.gates.items):
        _refuse("mutation.gate", "gate ordinal must name one existing positive gate")
    return child.gates.items[ordinal - 1]


def _gate_edit(text: str, item: GateItem, *, close: bool, suffix: str = "") -> str:
    """Edit only one parsed gate marker and its block's final content line."""
    lines = text.splitlines(keepends=True)
    start = item.source.line - 1
    if not 0 <= start < len(lines):
        _refuse("mutation.audit", "gate source line is outside BACKLOG.md")

    def split_terminator(line: str) -> tuple[str, str]:
        if line.endswith("\r\n"):
            return line[:-2], "\r\n"
        if line.endswith("\n"):
            return line[:-1], "\n"
        return line, ""

    first, first_terminator = split_terminator(lines[start])
    marker = _GATE_MARKER.match(first)
    expected = " " if close else "x"
    if marker is None or marker.group(1) != expected:
        _refuse("mutation.audit", "parsed gate marker no longer matches BACKLOG.md")
    lines[start] = f"{first[:3]}{'x' if close else ' '}{first[4:]}{first_terminator}"

    end = start + 1
    while end < len(lines):
        content, _ = split_terminator(lines[end])
        if _GATE_MARKER.match(content) is not None or content.startswith("#") or content and not content[:1].isspace():
            break
        end += 1
    content_indexes = [index for index in range(start, end) if split_terminator(lines[index])[0].strip()]
    if not content_indexes:
        _refuse("mutation.audit", "gate block has no content line")
    last = content_indexes[-1]
    if close:
        content, terminator = split_terminator(lines[last])
        lines[last] = f"{content}{suffix}{terminator}"
    else:
        fragments: list[tuple[str, tuple[int, int] | None]] = []

        def append_fragment(value: str, line: int, offset: int, *, normalize: bool) -> None:
            if fragments:
                fragments.append((" ", None))
            if not normalize:
                fragments.extend((character, (line, offset + position)) for position, character in enumerate(value))
                return
            for match in re.finditer(r"\S+", value):
                if match.start() > 0 and fragments[-1][0] != " ":
                    fragments.append((" ", (line, match.start() - 1)))
                fragments.extend((character, (line, match.start() + position)) for position, character in enumerate(match.group(0)))

        append_fragment(first[marker.end() :], start, marker.end(), normalize=False)
        for index in range(start + 1, end):
            continuation, _ = split_terminator(lines[index])
            append_fragment(continuation, index, 0, normalize=True)
        logical = "".join(character for character, _ in fragments)
        marker_offset = logical.find(" — Evidence: ")
        if marker_offset < 0:
            _refuse("mutation.audit", "parsed gate evidence suffix no longer matches BACKLOG.md")
        source = next((origin for _character, origin in fragments[marker_offset:] if origin is not None), None)
        if source is None:
            _refuse("mutation.audit", "parsed gate evidence suffix no longer matches BACKLOG.md")
        source_line, source_offset = source
        content, terminator = split_terminator(lines[source_line])
        lines[source_line] = f"{content[:source_offset]}{terminator}"
        for index in range(source_line + 1, end):
            content, terminator = split_terminator(lines[index])
            if content.strip():
                lines[index] = terminator
    return "".join(lines)


def _gate_count(child: BacklogChild, item: GateItem, *, satisfied: bool) -> str:
    values = tuple(satisfied if candidate.ordinal == item.ordinal else candidate.satisfied for candidate in child.gates.items)
    return f"{sum(values)}/{len(values)}"


def _prepare_child(root: Path, child_id: str, target_sha256: str | None) -> tuple[Path, Path, bytes, str, str, AuditLoad, BacklogChild, int]:
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
    *,
    preserve_candidate_finding: bool = False,
) -> MutationPlan:
    candidate = candidate_text.encode("utf-8")
    candidate_audit = audit_repository(resolved, backlog_text=candidate_text)
    if _has_errors(candidate_audit):
        if preserve_candidate_finding:
            finding = next(finding for finding in candidate_audit.findings if finding.severity == "error")
            _refuse(finding.code, f"planned gate mutation fails repository audit: {finding.message}")
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


def plan_record_gate(
    root: Path,
    child: str,
    ordinal: int,
    *,
    expect_open: bool,
    evidence: tuple[str, ...],
    target_sha256: str | None = None,
) -> MutationPlan:
    """Plan closing one open gate with eligible evidence."""
    paths = _validate_gate_evidence(evidence)
    resolved, backlog_path, original, original_text, original_sha256, _, current, line = _prepare_child(root, child, target_sha256)
    if current.status != "reviewed":
        _refuse("mutation.transition", "gate recording requires an explicitly reviewed child")
    item = _gate_item(current, ordinal)
    if not expect_open or item.satisfied:
        _refuse("mutation.expected-gate", "gate state differs from the expected open value")
    suffix = " — Evidence: " + " ".join(f"[verification]({path})" for path in paths)
    candidate_text = _gate_edit(original_text, item, close=True, suffix=suffix)
    candidate_text = _inventory_line(candidate_text, line, {6: _gate_count(current, item, satisfied=True)})
    rationale = f"Recorded gate `{ordinal}` for `{child}` with eligible evidence."
    return _finish_plan(
        resolved,
        backlog_path,
        original,
        original_text,
        original_sha256,
        candidate_text,
        f"Record gate `{ordinal}` for `{child}`.",
        rationale,
        preserve_candidate_finding=True,
    )


def plan_reopen_gate(
    root: Path,
    child: str,
    ordinal: int,
    *,
    expect_closed: bool,
    reason: str,
    target_sha256: str | None = None,
) -> MutationPlan:
    """Plan reopening one closed gate with explicit rationale."""
    _validate_reason(reason)
    resolved, backlog_path, original, original_text, original_sha256, _, current, line = _prepare_child(root, child, target_sha256)
    if current.status != "reviewed":
        _refuse("mutation.transition", "gate reopening requires an explicitly reviewed child")
    item = _gate_item(current, ordinal)
    if not expect_closed or not item.satisfied:
        _refuse("mutation.expected-gate", "gate state differs from the expected closed value")
    candidate_text = _gate_edit(original_text, item, close=False)
    candidate_text = _inventory_line(candidate_text, line, {6: _gate_count(current, item, satisfied=False)})
    rationale = f"Reopened gate `{ordinal}` for `{child}`: {reason}"
    return _finish_plan(
        resolved,
        backlog_path,
        original,
        original_text,
        original_sha256,
        candidate_text,
        f"Reopen gate `{ordinal}` for `{child}`.",
        rationale,
        preserve_candidate_finding=True,
    )
