from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess

from backlog.model import (
    Artifacts,
    Backlog,
    BacklogChild,
    BacklogReleaseGate,
    Epic,
    ExternalBoundary,
    Finding,
    GateItem,
    GateSummary,
    GitState,
    HistoricalArtifact,
    Milestone,
    PlanArtifact,
    RecentCommit,
    Recommendation,
    RepositorySnapshot,
    ReleaseGate,
    Roadmap,
    RoadmapChild,
    SpecificationArtifact,
    StatusReport,
)


_MISSING = "—"


def with_dependency_readiness(snapshot: RepositorySnapshot) -> RepositorySnapshot:
    statuses = {child.id: child.status for child in snapshot.backlog.children}
    children = tuple(
        replace(
            child,
            dependency_ready=all(dependency == "M0" or statuses.get(dependency) in {"verified", "released"} for dependency in child.dependencies),
        )
        for child in snapshot.backlog.children
    )
    return replace(snapshot, backlog=replace(snapshot.backlog, children=children))


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def observe_git(root: Path, limit: int = 5) -> GitState:
    branch = _git(root, "branch", "--show-current").strip()
    dirty = bool(_git(root, "status", "--porcelain").strip())
    log = _git(root, "log", f"-{limit}", "--format=%H%x00%s")
    commits = tuple(RecentCommit(sha, subject) for line in log.splitlines() for sha, subject in (line.split("\x00", 1),))
    return GitState(branch, dirty, commits)


def build_report(snapshot: RepositorySnapshot, git: GitState) -> StatusReport:
    return StatusReport(
        schema_version=1,
        repository="xplane-fdau",
        valid=True,
        roadmap=snapshot.roadmap,
        backlog=snapshot.backlog,
        artifacts=snapshot.artifacts,
        findings=(),
        recommendation=None,
        git=git,
    )


def _value(value: str | None) -> str:
    return _MISSING if value is None else value


def _values(values: tuple[str, ...]) -> str:
    return _MISSING if not values else ", ".join(values)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _gate_items(child: BacklogChild) -> list[str]:
    lines: list[str] = []
    for item in child.gates.items:
        lines.append(f"      {item.ordinal}. satisfied={_yes_no(item.satisfied)} evidence={_values(item.evidence)} statement={item.statement}")
    return lines


def _artifacts(lines: list[str], artifacts: Artifacts) -> None:
    lines.append("Artifacts:")
    lines.append("  Active specifications:")
    for artifact in artifacts.specifications:
        lines.append(
            f"    {artifact.path}  status={artifact.status} epic={artifact.epic} children={_values(artifact.children)} approval={_value(artifact.approval)}"
        )
    lines.append("  Active plans:")
    for artifact in artifacts.plans:
        lines.append(
            "    "
            f"{artifact.path}  status={artifact.status} child={artifact.child} "
            f"source-specification={artifact.source_specification} "
            f"approval={_value(artifact.approval)} "
            f"completion-evidence={_value(artifact.completion_evidence)}"
        )
    lines.append("  Historical artifacts:")
    for artifact in artifacts.historical:
        lines.append(f"    {artifact.path}  status={artifact.status} disposition={artifact.disposition}")


def render_human(report: StatusReport) -> str:
    lines = [
        f"Repository: {report.repository}",
        "Authority: roadmap=ROADMAP.md backlog=BACKLOG.md",
        f"Active child: {_value(report.backlog.active_child)}",
        "Roadmap:",
        "  Milestones:",
    ]
    for milestone in report.roadmap.milestones:
        lines.append(f"    {milestone.id}  {milestone.title}")
    lines.append("  Epics:")
    for epic in report.roadmap.epics:
        lines.append(f"    {epic.id}  {epic.title}  children={_values(epic.children)}")
    lines.append(f"  {len(report.roadmap.local_children)} local children:")
    for child in report.roadmap.local_children:
        lines.append(
            "    "
            f"{child.id}  epic={child.epic} dependencies={_values(child.dependencies)} "
            f"external-prerequisite={_value(child.external_prerequisite)} title={child.title}"
        )
    lines.append("  Release gates:")
    for gate in report.roadmap.release_gates:
        lines.append(f"    {gate.id}  dependencies={_values(gate.dependencies)} title={gate.title}")
    lines.append("  External boundaries:")
    for boundary in report.roadmap.external_boundaries:
        lines.append(f"    {boundary.id}  title={boundary.title} owner={boundary.owner} handoff-condition={boundary.handoff_condition}")

    lines.append("Backlog children:")
    for child in report.backlog.children:
        lines.append(f"  {child.id}  {child.status}  dependency-ready={_yes_no(child.dependency_ready)}  gates={child.gates.satisfied}/{child.gates.total}")
        lines.append(f"    dependencies: {_values(child.dependencies)}")
        lines.append(f"    specification: {_value(child.specification)}")
        lines.append(f"    plan: {_value(child.plan)}")
        lines.append(f"    review: {_value(child.review_evidence)}")
        lines.append(f"    resume: {_value(child.resume_state)}")
        lines.append(f"    reason: {_value(child.reason)}")
        lines.extend(_gate_items(child))

    lines.append("Backlog release gates:")
    for gate in report.backlog.release_gates:
        lines.append(f"  {gate.id}  state={gate.state} evidence={_values(gate.evidence)}")
    _artifacts(lines, report.artifacts)
    lines.append("Findings: none" if not report.findings else "Findings:")
    for finding in report.findings:
        lines.append(
            "  "
            f"{finding.severity} {finding.code} {finding.path}:{_value(str(finding.line) if finding.line is not None else None)} "
            f"node={_value(finding.node)} gate={_value(str(finding.gate) if finding.gate is not None else None)} "
            f"{finding.message}"
        )
    lines.append("Recommendation: unavailable until T1.4" if report.recommendation is None else "Recommendation:")
    if report.recommendation is not None:
        recommendation = report.recommendation
        lines.append(
            f"  action={recommendation.action} child={_value(recommendation.child)} reason={recommendation.reason} command={_value(recommendation.command)}"
        )
    lines.append(f"Git: branch={report.git.branch} dirty={_yes_no(report.git.dirty)}")
    lines.append("Recent commits:")
    for commit in report.git.recent_commits:
        lines.append(f"  {commit.sha}  {commit.subject}")
    return "\n".join(lines) + "\n"


def _milestone_dict(milestone: Milestone) -> dict[str, object]:
    return {"id": milestone.id, "kind": milestone.kind, "title": milestone.title}


def _epic_dict(epic: Epic) -> dict[str, object]:
    return {
        "id": epic.id,
        "kind": epic.kind,
        "title": epic.title,
        "children": list(epic.children),
    }


def _roadmap_child_dict(child: RoadmapChild) -> dict[str, object]:
    return {
        "id": child.id,
        "kind": child.kind,
        "epic": child.epic,
        "title": child.title,
        "dependencies": list(child.dependencies),
        "external_prerequisite": child.external_prerequisite,
    }


def _release_gate_dict(gate: ReleaseGate) -> dict[str, object]:
    return {"id": gate.id, "kind": gate.kind, "title": gate.title, "dependencies": list(gate.dependencies)}


def _external_boundary_dict(boundary: ExternalBoundary) -> dict[str, object]:
    return {
        "id": boundary.id,
        "kind": boundary.kind,
        "title": boundary.title,
        "owner": boundary.owner,
        "handoff_condition": boundary.handoff_condition,
    }


def _roadmap_dict(roadmap: Roadmap) -> dict[str, object]:
    return {
        "milestones": [_milestone_dict(item) for item in roadmap.milestones],
        "epics": [_epic_dict(item) for item in roadmap.epics],
        "local_children": [_roadmap_child_dict(item) for item in roadmap.local_children],
        "release_gates": [_release_gate_dict(item) for item in roadmap.release_gates],
        "external_boundaries": [_external_boundary_dict(item) for item in roadmap.external_boundaries],
    }


def _gate_item_dict(gate: GateItem) -> dict[str, object]:
    return {
        "ordinal": gate.ordinal,
        "statement": gate.statement,
        "satisfied": gate.satisfied,
        "evidence": list(gate.evidence),
    }


def _gate_summary_dict(summary: GateSummary) -> dict[str, object]:
    return {
        "satisfied": summary.satisfied,
        "total": summary.total,
        "items": [_gate_item_dict(item) for item in summary.items],
    }


def _backlog_child_dict(item: BacklogChild) -> dict[str, object]:
    return {
        "id": item.id,
        "status": item.status,
        "dependencies": list(item.dependencies),
        "specification": item.specification,
        "plan": item.plan,
        "gates": _gate_summary_dict(item.gates),
        "review_evidence": item.review_evidence,
        "resume_state": item.resume_state,
        "reason": item.reason,
        "dependency_ready": item.dependency_ready,
    }


def _backlog_release_gate_dict(gate: BacklogReleaseGate) -> dict[str, object]:
    return {"id": gate.id, "state": gate.state, "evidence": list(gate.evidence)}


def _backlog_dict(backlog: Backlog) -> dict[str, object]:
    return {
        "active_child": backlog.active_child,
        "children": [_backlog_child_dict(item) for item in backlog.children],
        "release_gates": [_backlog_release_gate_dict(item) for item in backlog.release_gates],
    }


def _specification_dict(specification: SpecificationArtifact) -> dict[str, object]:
    return {
        "path": specification.path,
        "governance": specification.governance,
        "status": specification.status,
        "epic": specification.epic,
        "children": list(specification.children),
        "approval": specification.approval,
    }


def _plan_dict(plan: PlanArtifact) -> dict[str, object]:
    return {
        "path": plan.path,
        "governance": plan.governance,
        "status": plan.status,
        "child": plan.child,
        "source_specification": plan.source_specification,
        "approval": plan.approval,
        "completion_evidence": plan.completion_evidence,
    }


def _historical_dict(artifact: HistoricalArtifact) -> dict[str, object]:
    return {
        "path": artifact.path,
        "governance": artifact.governance,
        "status": artifact.status,
        "disposition": artifact.disposition,
    }


def _artifacts_dict(artifacts: Artifacts) -> dict[str, object]:
    return {
        "specifications": [_specification_dict(item) for item in artifacts.specifications],
        "plans": [_plan_dict(item) for item in artifacts.plans],
        "historical": [_historical_dict(item) for item in artifacts.historical],
    }


def _finding_dict(finding: Finding) -> dict[str, object]:
    return {
        "code": finding.code,
        "severity": finding.severity,
        "path": finding.path,
        "line": finding.line,
        "node": finding.node,
        "gate": finding.gate,
        "message": finding.message,
    }


def _recommendation_dict(recommendation: Recommendation) -> dict[str, object]:
    return {
        "action": recommendation.action,
        "child": recommendation.child,
        "reason": recommendation.reason,
        "command": recommendation.command,
    }


def _git_dict(git: GitState) -> dict[str, object]:
    return {
        "branch": git.branch,
        "dirty": git.dirty,
        "recent_commits": [{"sha": item.sha, "subject": item.subject} for item in git.recent_commits],
    }


def report_dict(report: StatusReport) -> dict[str, object]:
    return {
        "schema_version": report.schema_version,
        "repository": report.repository,
        "valid": report.valid,
        "roadmap": _roadmap_dict(report.roadmap),
        "backlog": _backlog_dict(report.backlog),
        "artifacts": _artifacts_dict(report.artifacts),
        "findings": [_finding_dict(item) for item in report.findings],
        "recommendation": None if report.recommendation is None else _recommendation_dict(report.recommendation),
        "git": _git_dict(report.git),
    }


def render_json(report: StatusReport) -> str:
    return json.dumps(report_dict(report), ensure_ascii=False, allow_nan=False, indent=2) + "\n"
