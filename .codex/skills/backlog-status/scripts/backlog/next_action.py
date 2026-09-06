from __future__ import annotations

from backlog.model import Action, BacklogChild, ChildStatus, Finding, Recommendation, RepositorySnapshot


_AUDIT_COMMAND = "uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit"
_STATUS_ACTIONS: dict[ChildStatus, tuple[Action, str, str | None]] = {
    "queued": (
        "refine_spec",
        "is queued and requires a governing specification.",
        "Use superpowers:brainstorming to refine the governing specification.",
    ),
    "designing": (
        "request_spec_review",
        "has a draft governing specification that requires review.",
        "Use superpowers:requesting-code-review to review the governing specification.",
    ),
    "specified": (
        "write_plan",
        "is specified and requires an approved single-child implementation plan.",
        "Use superpowers:writing-plans to create the single-child implementation plan.",
    ),
    "planned": (
        "execute_plan",
        "has an approved implementation plan ready to execute.",
        "Use superpowers:subagent-driven-development or superpowers:executing-plans to execute the approved plan.",
    ),
    "in_progress": (
        "execute_plan",
        "is in progress under its approved implementation plan.",
        "Use superpowers:subagent-driven-development or superpowers:executing-plans to execute the approved plan.",
    ),
    "implemented": (
        "request_review",
        "is implemented and requires independent review.",
        "Use superpowers:requesting-code-review to review the completed implementation.",
    ),
    "reviewed": (
        "verify",
        "has accepted independent review and requires acceptance-gate verification.",
        "Use gzs-quality-gate and record every acceptance-gate evidence artifact.",
    ),
    "verified": ("wait", "is verified and has no remaining lifecycle action.", None),
    "released": ("wait", "is released and has no remaining lifecycle action.", None),
    "blocked": ("wait", "is blocked.", None),
    "deferred": ("wait", "is deferred.", None),
}


def _for_child(child: BacklogChild) -> Recommendation:
    if child.status in {"blocked", "deferred"}:
        return Recommendation("wait", child.id, child.reason or _STATUS_ACTIONS[child.status][1], None)
    action, reason, command = _STATUS_ACTIONS[child.status]
    return Recommendation(action, child.id, f"{child.id} {reason}", command)


def recommend_next(snapshot: RepositorySnapshot, findings: tuple[Finding, ...]) -> Recommendation:
    """Recommend one read-only lifecycle action from audited repository state."""
    active = snapshot.backlog.active_child
    if any(finding.severity == "error" for finding in findings):
        return Recommendation("wait", active, "Resolve audit errors before requesting a next action.", _AUDIT_COMMAND)

    children = {child.id: child for child in snapshot.backlog.children}
    if active is not None:
        return _for_child(children[active])

    for roadmap_child in snapshot.roadmap.local_children:
        child = children.get(roadmap_child.id)
        if child is not None and child.dependency_ready and child.status not in {"verified", "released"}:
            return _for_child(child)

    return Recommendation("wait", None, "No dependency-ready unfinished local child is available.", None)
