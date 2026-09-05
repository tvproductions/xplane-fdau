from __future__ import annotations

import hashlib
import re

from backlog.adherence import adherence_findings
from backlog.evidence import ObservationError, evidence_findings, observed_bytes
from backlog.findings import finding_key
from backlog.model import AuditLoad, BacklogChild, Finding, SourceLocation
from backlog.policy import allowed_kinds
from backlog.rules import structural_findings


_STAGES = ("queued", "designing", "specified", "planned", "in_progress", "implemented", "reviewed", "verified")
_EXECUTING = frozenset({"in_progress", "implemented", "reviewed", "verified"})
_COMPLETED = frozenset({"implemented", "reviewed", "verified"})


def _finding(code: str, source: SourceLocation, child: str, message: str, gate: int | None = None) -> Finding:
    return Finding(code, "error", source.path, source.line, child, gate, message)


def _state(child: BacklogChild) -> str | None:
    return child.resume_state if child.status in {"blocked", "deferred"} else child.status


def _ready(loaded: AuditLoad, dependencies: tuple[str, ...]) -> bool:
    states = {child.id: child.status for child in loaded.snapshot.backlog.children}
    milestones = {node.id for node in loaded.snapshot.roadmap.milestones}
    return all(dependency in milestones or states.get(dependency) == "verified" for dependency in dependencies)


def _dependencies(loaded: AuditLoad, child: BacklogChild) -> bool:
    nodes = [node for node in loaded.snapshot.roadmap.local_children if node.id == child.id]
    return len(nodes) == 1 and _ready(loaded, nodes[0].dependencies)


def _specification(loaded: AuditLoad, child: BacklogChild, state: str) -> bool:
    specs = [spec for spec in loaded.snapshot.artifacts.specifications if spec.path == child.specification]
    if len(specs) != 1:
        return False
    spec = specs[0]
    return child.id in spec.children and (
        spec.status == "draft" if state == "designing" else spec.status in {"approved", "implemented"} and bool(spec.approval)
    )


def _suspension(child: BacklogChild) -> list[Finding]:
    suspended = child.status in {"blocked", "deferred"}
    valid = child.resume_state in _STAGES and bool(child.reason and child.reason.strip()) if suspended else child.resume_state is None and child.reason is None
    if valid:
        return []
    return [
        _finding(
            "lifecycle.suspension",
            child.source,
            child.id,
            "suspended children require a nonsuspended Resume state and nonempty Reason; other states require both absent",
        )
    ]


def _ordered(paths: tuple[str, ...], source: SourceLocation, node: str, gate: int | None = None) -> list[Finding]:
    findings = []
    if paths != tuple(sorted(paths)):
        findings.append(_finding("evidence.order", source, node, "evidence links must be in lexical path order", gate))
    if len(paths) != len(set(paths)):
        findings.append(_finding("evidence.duplicate", source, node, "evidence links must not repeat a path", gate))
    return findings


def _child_evidence(loaded: AuditLoad, child: BacklogChild, state: str | None) -> list[Finding]:
    findings: list[Finding] = []
    require_head = state == "verified"
    for item in child.gates.items:
        findings.extend(_ordered(item.evidence, item.source, child.id, item.ordinal))
        if item.satisfied and not item.evidence:
            findings.append(_finding("lifecycle.gates", item.source, child.id, "satisfied gate requires eligible evidence", item.ordinal))
        for path in item.evidence:
            findings.extend(evidence_findings(loaded.snapshot.root, path, child.id, item.ordinal, kinds=allowed_kinds("gate"), require_head=require_head))
    if state == "verified" and (not child.gates.items or not all(item.satisfied for item in child.gates.items)):
        findings.append(_finding("lifecycle.gates", child.source, child.id, "verified child requires every acceptance gate satisfied"))
    if child.review_evidence is not None:
        findings.extend(
            evidence_findings(loaded.snapshot.root, child.review_evidence, child.id, None, kinds=allowed_kinds("review"), require_head=require_head)
        )
    elif state in {"reviewed", "verified"}:
        findings.append(_finding("lifecycle.review", child.source, child.id, "reviewed and verified children require accepted child-level Review evidence"))
    return findings


def historical_plan_findings(loaded: AuditLoad, child: BacklogChild) -> tuple[Finding, ...]:
    """Admit only typed policy pins with all verified historical prerequisites."""
    problems: list[str] = []
    state = _state(child)
    if state != "verified":
        problems.append("historical admission requires effective verified state")
    pins = [] if loaded.policy is None else [pin for pin in loaded.policy.historical if pin.child == child.id and pin.plan == child.plan]
    if len(pins) != 1:
        problems.append("linked child and historical plan do not match an approved policy admission")
    plans = [plan for plan in loaded.snapshot.artifacts.historical if plan.path == child.plan]
    if len(plans) != 1 or plans[0].status != "completed" or re.search(rf"(?<![A-Za-z0-9.]){re.escape(child.id)}(?![A-Za-z0-9.])", plans[0].disposition) is None:
        problems.append("historical plan requires completed metadata and a disposition naming this child")
    if not _specification(loaded, child, "verified"):
        problems.append("historical admission requires an approved covering design")
    if "ROADMAP.md" in loaded.invalid_paths or not _dependencies(loaded, child):
        problems.append("historical admission requires verified roadmap prerequisites")
    if _child_evidence(loaded, child, "verified"):
        problems.append("historical admission requires eligible HEAD-backed review and all-gate evidence")
    governing_paths = {child.plan, child.specification}
    relevant = [
        finding
        for finding in (*structural_findings(loaded), *adherence_findings(loaded))
        if finding.node == child.id or finding.node is None and finding.path in governing_paths
    ]
    if relevant:
        problems.append("historical admission requires valid structure and governing acceptance criteria")
    if child.plan is not None:
        try:
            content = observed_bytes(loaded.snapshot.root, child.plan, require_head=True)
            if len(pins) == 1 and hashlib.sha256(content).hexdigest() != pins[0].sha256:
                problems.append("historical plan bytes differ from the approved digest")
        except ObservationError as error:
            problems.append(str(error))
    if problems:
        return (_finding("lifecycle.historical-plan", child.source, child.id, "; ".join(problems)),)
    return ()


def _ordinary_plan(loaded: AuditLoad, child: BacklogChild, state: str | None) -> list[Finding]:
    required = state in {"planned", *_EXECUTING}
    plans = [plan for plan in loaded.snapshot.artifacts.plans if plan.path == child.plan]
    if len(plans) != 1:
        return [_finding("lifecycle.plan", child.source, child.id, "lifecycle state requires an approved active plan")] if required else []
    plan = plans[0]
    findings = []
    expected = "completed" if state in _COMPLETED else "in_progress" if state == "in_progress" else "approved"
    if required and (plan.status != expected or not plan.approval or plan.child != child.id or plan.source_specification != child.specification):
        findings.append(
            _finding("lifecycle.plan", child.source, child.id, f"{state} child requires a {expected} approved single-child plan citing its governing design")
        )
    if plan.completion_evidence is None and state in _COMPLETED:
        findings.append(_finding("lifecycle.completion", plan.source, child.id, "completed plan requires eligible child-level completion evidence"))
    return findings


def _plan_completion_findings(loaded: AuditLoad) -> list[Finding]:
    verified_plans = {child.plan for child in loaded.snapshot.backlog.children if "BACKLOG.md" not in loaded.invalid_paths and _state(child) == "verified"}
    findings = []
    for plan in loaded.snapshot.artifacts.plans:
        if plan.completion_evidence is not None:
            findings.extend(
                evidence_findings(
                    loaded.snapshot.root,
                    plan.completion_evidence,
                    plan.child,
                    None,
                    kinds=allowed_kinds("completion"),
                    require_head=plan.path in verified_plans,
                )
            )
    return findings


def _child_findings(loaded: AuditLoad, child: BacklogChild) -> list[Finding]:
    findings = _suspension(child)
    state = _state(child)
    if state not in _STAGES and state != "released":
        findings.append(_finding("lifecycle.state", child.source, child.id, "unsupported effective lifecycle state"))
    if state in _STAGES[1:] and child.specification not in loaded.invalid_paths and not _specification(loaded, child, state):
        findings.append(_finding("lifecycle.specification", child.source, child.id, f"{state} child requires its stage's covering governing design"))
    if child.status == "in_progress" and loaded.snapshot.backlog.active_child != child.id:
        findings.append(_finding("lifecycle.selection", child.source, child.id, "currently in_progress child must be selected"))
    if state in _EXECUTING and "ROADMAP.md" not in loaded.invalid_paths and not _dependencies(loaded, child):
        findings.append(_finding("lifecycle.dependencies", child.source, child.id, "execution claims require verified roadmap prerequisites"))
    historical = any(plan.path == child.plan for plan in loaded.snapshot.artifacts.historical)
    if historical:
        findings.extend(historical_plan_findings(loaded, child))
    elif child.plan not in loaded.invalid_paths:
        findings.extend(_ordinary_plan(loaded, child, state))
    findings.extend(_child_evidence(loaded, child, state))
    return findings


def _release_findings(loaded: AuditLoad) -> list[Finding]:
    findings = []
    definitions = {gate.id: gate for gate in loaded.snapshot.roadmap.release_gates}
    for gate in loaded.snapshot.backlog.release_gates:
        findings.extend(_ordered(gate.evidence, gate.source, gate.id))
        definition = definitions.get(gate.id)
        if "ROADMAP.md" not in loaded.invalid_paths and definition is not None:
            ready = _ready(loaded, definition.dependencies)
            if ready == (gate.state == "waiting"):
                findings.append(_finding("release.prerequisites", gate.source, gate.id, "dashboard state does not match roadmap prerequisite states"))
        if gate.state == "satisfied" and not gate.evidence:
            findings.append(_finding("release.evidence", gate.source, gate.id, "satisfied release gate requires eligible HEAD-backed evidence"))
        for path in gate.evidence:
            findings.extend(
                evidence_findings(loaded.snapshot.root, path, gate.id, None, kinds=allowed_kinds("release"), require_head=gate.state == "satisfied")
            )
    return findings


def lifecycle_findings(loaded: AuditLoad) -> tuple[Finding, ...]:
    """Validate current-state sufficiency without inferring past transitions."""
    findings = _plan_completion_findings(loaded)
    if "BACKLOG.md" in loaded.invalid_paths:
        return tuple(sorted(findings, key=finding_key))
    for child in loaded.snapshot.backlog.children:
        findings.extend(_child_findings(loaded, child))
    findings.extend(_release_findings(loaded))
    return tuple(sorted(findings, key=finding_key))
