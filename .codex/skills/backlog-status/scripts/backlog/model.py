from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeAlias


NodeKind: TypeAlias = Literal["milestone", "epic", "local_child", "release_gate", "external_boundary"]
ChildStatus: TypeAlias = Literal[
    "queued",
    "designing",
    "specified",
    "planned",
    "in_progress",
    "implemented",
    "reviewed",
    "verified",
    "blocked",
    "deferred",
    "released",
]
GateState: TypeAlias = Literal["waiting", "ready", "satisfied"]
Severity: TypeAlias = Literal["error", "warning"]
Action: TypeAlias = Literal[
    "refine_spec",
    "request_spec_review",
    "write_plan",
    "execute_plan",
    "request_review",
    "verify",
    "wait",
]

NODE_KINDS = ("milestone", "epic", "local_child", "release_gate", "external_boundary")
CHILD_STATUSES = (
    "queued",
    "designing",
    "specified",
    "planned",
    "in_progress",
    "implemented",
    "reviewed",
    "verified",
    "blocked",
    "deferred",
    "released",
)
GATE_STATES = ("waiting", "ready", "satisfied")


@dataclass(frozen=True, slots=True)
class SourceLocation:
    path: str
    line: int


@dataclass(frozen=True, slots=True)
class Milestone:
    id: str
    kind: Literal["milestone"]
    title: str
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class Epic:
    id: str
    kind: Literal["epic"]
    title: str
    children: tuple[str, ...]
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class RoadmapChild:
    id: str
    kind: Literal["local_child"]
    epic: str
    title: str
    dependencies: tuple[str, ...]
    external_prerequisite: str | None
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class ReleaseGate:
    id: str
    kind: Literal["release_gate"]
    title: str
    dependencies: tuple[str, ...]
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class ExternalBoundary:
    id: str
    kind: Literal["external_boundary"]
    title: str
    owner: str
    handoff_condition: str
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class Roadmap:
    milestones: tuple[Milestone, ...]
    epics: tuple[Epic, ...]
    local_children: tuple[RoadmapChild, ...]
    release_gates: tuple[ReleaseGate, ...]
    external_boundaries: tuple[ExternalBoundary, ...]


@dataclass(frozen=True, slots=True)
class GateItem:
    ordinal: int
    statement: str
    satisfied: bool
    evidence: tuple[str, ...]
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class GateSummary:
    satisfied: int
    total: int
    items: tuple[GateItem, ...]


@dataclass(frozen=True, slots=True)
class BacklogChild:
    id: str
    status: ChildStatus
    dependencies: tuple[str, ...]
    specification: str | None
    plan: str | None
    gates: GateSummary
    review_evidence: str | None
    resume_state: ChildStatus | None
    reason: str | None
    dependency_ready: bool
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class BacklogReleaseGate:
    id: str
    state: GateState
    evidence: tuple[str, ...]
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class Backlog:
    active_child: str | None
    children: tuple[BacklogChild, ...]
    release_gates: tuple[BacklogReleaseGate, ...]
    source_path: str


@dataclass(frozen=True, slots=True)
class SpecificationArtifact:
    path: str
    governance: Literal["active"]
    status: Literal["draft", "approved", "implemented", "superseded"]
    epic: str
    children: tuple[str, ...]
    approval: str | None
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class PlanArtifact:
    path: str
    governance: Literal["active"]
    status: Literal["draft", "approved", "in_progress", "completed", "superseded"]
    child: str
    source_specification: str
    approval: str | None
    completion_evidence: str | None
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class HistoricalArtifact:
    path: str
    governance: Literal["historical"]
    status: Literal["completed", "superseded"]
    disposition: str
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class Artifacts:
    specifications: tuple[SpecificationArtifact, ...]
    plans: tuple[PlanArtifact, ...]
    historical: tuple[HistoricalArtifact, ...]


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    severity: Severity
    path: str
    line: int | None
    node: str | None
    gate: int | None
    message: str


@dataclass(frozen=True, slots=True)
class Recommendation:
    action: Action
    child: str | None
    reason: str
    command: str | None


@dataclass(frozen=True, slots=True)
class RecentCommit:
    sha: str
    subject: str


@dataclass(frozen=True, slots=True)
class GitState:
    branch: str
    dirty: bool
    recent_commits: tuple[RecentCommit, ...]


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    root: Path
    roadmap: Roadmap
    backlog: Backlog
    artifacts: Artifacts


@dataclass(frozen=True, slots=True)
class StatusReport:
    schema_version: int
    repository: str
    valid: bool
    roadmap: Roadmap
    backlog: Backlog
    artifacts: Artifacts
    findings: tuple[Finding, ...]
    recommendation: Recommendation | None
    git: GitState
