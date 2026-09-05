from __future__ import annotations

from datetime import date
from pathlib import Path, PurePosixPath
import re

from backlog.findings import finding_key
from backlog.model import (
    ArtifactMetadataSource,
    AuditLoad,
    BacklogChild,
    ChildStatus,
    Finding,
    HistoricalArtifact,
    PlanArtifact,
    SourceLocation,
    SpecificationArtifact,
)


_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_APPROVAL = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}) — (\S.*)")
_IDENTITY = re.compile(r"(?<![A-Z0-9.])([A-Z][0-9]*(?:\.[0-9]+)?)(?![A-Z0-9.])")
_PATH_REFERENCE = re.compile(r"(?:`([^`]+\.md)`|\[[^]]+\]\(([^)]+\.md)\))")
_GOVERNED_STATES: tuple[ChildStatus, ...] = (
    "designing",
    "specified",
    "planned",
    "in_progress",
    "implemented",
    "reviewed",
    "verified",
    "released",
)


def _finding(
    code: str,
    source: SourceLocation,
    message: str,
    *,
    node: str | None = None,
    gate: int | None = None,
) -> Finding:
    return Finding(code, "error", source.path, source.line, node, gate, message)


def _fold(value: str) -> str:
    return " ".join(value.split())


def _metadata_by_path(loaded: AuditLoad) -> dict[str, ArtifactMetadataSource]:
    return {source.path: source for source in loaded.sources.artifact_metadata}


def _child_source(loaded: AuditLoad, index: int, child: BacklogChild) -> SourceLocation:
    if index < len(loaded.sources.inventory_rows):
        return loaded.sources.inventory_rows[index].source
    return child.source


def _fixed_metadata_source(artifact: SpecificationArtifact | PlanArtifact | HistoricalArtifact, offset: int) -> SourceLocation:
    return SourceLocation(artifact.path, artifact.source.line + offset)


def _valid_calendar_date(value: str | None) -> bool:
    if value is None or _DATE.fullmatch(value) is None:
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _valid_approval(value: str | None) -> bool:
    if value is None:
        return False
    match = _APPROVAL.fullmatch(value)
    return match is not None and _valid_calendar_date(match.group(1))


def _metadata_findings(loaded: AuditLoad) -> list[Finding]:
    findings: list[Finding] = []
    metadata = _metadata_by_path(loaded)
    active: tuple[SpecificationArtifact | PlanArtifact, ...] = (
        *loaded.snapshot.artifacts.specifications,
        *loaded.snapshot.artifacts.plans,
    )
    for artifact in active:
        sources = metadata[artifact.path]
        date_source = sources.date
        if date_source is None or not _valid_calendar_date(date_source.value):
            source = date_source.source if date_source is not None else artifact.source
            family = "spec" if isinstance(artifact, SpecificationArtifact) else "plan"
            findings.append(_finding(f"artifact.{family}.date", source, "active artifact Date must be an exact calendar date"))
        requires_approval = artifact.status != "draft"
        if requires_approval and not _valid_approval(artifact.approval):
            approval_source = sources.approval
            source = approval_source.source if approval_source is not None else artifact.source
            findings.append(_finding("artifact.approval", source, "approved-or-later artifact requires YYYY-MM-DD — owner approval"))
        if isinstance(artifact, PlanArtifact) and artifact.status == "completed" and artifact.completion_evidence is None:
            findings.append(
                _finding(
                    "artifact.plan.completion",
                    _fixed_metadata_source(artifact, 8),
                    "completed active plan requires completion evidence",
                    node=artifact.child,
                )
            )
    return findings


def _resolved_regular_markdown(root: Path, target: str) -> tuple[Path | None, str | None]:
    if PurePosixPath(target).suffix.lower() != ".md":
        return None, "path"
    candidate = root.joinpath(*PurePosixPath(target).parts)
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None, "path"
    try:
        if not resolved.is_file():
            return None, "missing"
    except OSError:
        return None, "missing"
    return resolved, None


def _historical_findings(loaded: AuditLoad) -> list[Finding]:
    if "ROADMAP.md" in loaded.invalid_paths:
        return []
    findings: list[Finding] = []
    identities = {
        *(node.id for node in loaded.snapshot.roadmap.milestones),
        *(node.id for node in loaded.snapshot.roadmap.local_children),
    }
    root = loaded.snapshot.root
    for artifact in loaded.snapshot.artifacts.historical:
        named_identity = any(match.group(1) in identities for match in _IDENTITY.finditer(artifact.disposition))
        replacement_exists = False
        for match in _PATH_REFERENCE.finditer(artifact.disposition):
            target = match.group(1) or match.group(2)
            _resolved, problem = _resolved_regular_markdown(root, target)
            if problem is None:
                replacement_exists = True
                break
        if not named_identity and not replacement_exists:
            findings.append(
                _finding(
                    "artifact.historical.disposition",
                    _fixed_metadata_source(artifact, 4),
                    "historical disposition must name a known milestone or child, or an existing replacement artifact",
                )
            )
    return findings


def _design_findings(loaded: AuditLoad) -> list[Finding]:
    if "ROADMAP.md" in loaded.invalid_paths:
        return []
    findings: list[Finding] = []
    roadmap_children = {child.id: child for child in loaded.snapshot.roadmap.local_children}
    roadmap_epics = {epic.id for epic in loaded.snapshot.roadmap.epics}
    order = {child.id: index for index, child in enumerate(loaded.snapshot.roadmap.local_children)}
    declarations = loaded.sources.roadmap_cross_epic_designs
    for design in loaded.snapshot.artifacts.specifications:
        epic_source = _fixed_metadata_source(design, 6)
        children_source = _fixed_metadata_source(design, 7)
        if design.epic not in roadmap_epics:
            findings.append(_finding("artifact.spec.unknown-epic", epic_source, f"design names unknown roadmap epic {design.epic}"))
        seen: set[str] = set()
        for child in design.children:
            if child in seen:
                findings.append(_finding("artifact.spec.duplicate-child", children_source, f"design repeats child {child}", node=child))
            elif child not in roadmap_children:
                findings.append(_finding("artifact.spec.unknown-child", children_source, f"design names unknown child {child}", node=child))
            seen.add(child)
        known = tuple(child for child in design.children if child in order)
        if len(known) == len(design.children) and len(set(known)) == len(known):
            expected = tuple(sorted(known, key=order.__getitem__))
            if known != expected:
                findings.append(_finding("artifact.spec.child-order", children_source, "design children are not in roadmap order"))
        covered_epics = {roadmap_children[child].epic for child in known}
        if len(covered_epics) > 1:
            allowed = False
            for declaration in declarations:
                if declaration.anchor_epic != design.epic:
                    continue
                member_set = set(declaration.members)
                if all("." not in member for member in member_set):
                    allowed = covered_epics <= member_set
                else:
                    allowed = set(known) <= member_set
                if allowed:
                    break
            if not allowed:
                findings.append(
                    _finding(
                        "artifact.spec.cross-epic",
                        children_source,
                        "design crosses epics without a recognized roadmap declaration",
                    )
                )
        elif covered_epics and design.epic not in covered_epics:
            findings.append(_finding("artifact.spec.epic", epic_source, "design children do not belong to its named epic"))
    return findings


def _plan_definition_findings(loaded: AuditLoad) -> list[Finding]:
    findings: list[Finding] = []
    roadmap_children = {child.id for child in loaded.snapshot.roadmap.local_children}
    specifications = {item.path: item for item in loaded.snapshot.artifacts.specifications}
    for plan in loaded.snapshot.artifacts.plans:
        child_source = _fixed_metadata_source(plan, 5)
        source_source = _fixed_metadata_source(plan, 6)
        if "ROADMAP.md" not in loaded.invalid_paths and plan.child not in roadmap_children:
            findings.append(_finding("artifact.plan.unknown-child", child_source, f"plan names unknown child {plan.child}", node=plan.child))
        source_design = specifications.get(plan.source_specification)
        if plan.source_specification in loaded.invalid_paths:
            continue
        if source_design is None:
            findings.append(
                _finding(
                    "artifact.plan.source",
                    source_source,
                    "active plan must cite an active governing design",
                    node=plan.child,
                )
            )
        elif source_design.status not in {"approved", "implemented"} or plan.child not in source_design.children:
            findings.append(
                _finding(
                    "artifact.plan.source",
                    source_source,
                    "active plan source must be an approved governing design that covers its child",
                    node=plan.child,
                )
            )
    return findings


def _effective_state(child: BacklogChild) -> ChildStatus:
    if child.status in {"blocked", "deferred"} and child.resume_state is not None:
        return child.resume_state
    return child.status


def _gate_drift_findings(
    loaded: AuditLoad,
    child: BacklogChild,
    design: SpecificationArtifact,
) -> list[Finding]:
    sections = tuple(section for section in loaded.sources.design_acceptance if section.path == design.path and section.child == child.id)
    if len(sections) != 1:
        return [
            _finding(
                "artifact.gate-drift",
                design.source,
                f"governing design requires exactly one acceptance subsection for {child.id}",
                node=child.id,
            )
        ]
    section = sections[0]
    roadmap_child = next((item for item in loaded.snapshot.roadmap.local_children if item.id == child.id), None)
    findings: list[Finding] = []
    if roadmap_child is None or _fold(section.title) != _fold(roadmap_child.title):
        findings.append(
            _finding(
                "artifact.gate-drift",
                section.source,
                f"governing design acceptance title differs for {child.id}",
                node=child.id,
            )
        )
    if section.resolution_problem is not None:
        findings.append(
            _finding(
                "artifact.gate-drift",
                section.resolution_problem.source,
                f"managed acceptance reference is unresolved: {section.resolution_problem.value}",
                node=child.id,
            )
        )
        return findings
    expected = tuple(_fold(statement.value) for statement in section.statements)
    actual = tuple(_fold(item.statement) for item in child.gates.items)
    for index, (design_statement, backlog_statement) in enumerate(zip(expected, actual, strict=False), start=1):
        if design_statement != backlog_statement:
            source = section.statements[index - 1].source
            findings.append(
                _finding(
                    "artifact.gate-drift",
                    source,
                    f"governing design gate {index} differs from BACKLOG.md",
                    node=child.id,
                    gate=index,
                )
            )
    if len(expected) != len(actual):
        findings.append(
            _finding(
                "artifact.gate-drift",
                section.source,
                f"governing design acceptance count differs for {child.id}",
                node=child.id,
            )
        )
    return findings


def _backlog_link_findings(loaded: AuditLoad) -> list[Finding]:
    findings: list[Finding] = []
    root = loaded.snapshot.root
    specifications = {item.path: item for item in loaded.snapshot.artifacts.specifications}
    plans = {item.path: item for item in loaded.snapshot.artifacts.plans}
    historical_paths = {item.path for item in loaded.snapshot.artifacts.historical}
    for index, child in enumerate(loaded.snapshot.backlog.children):
        source = _child_source(loaded, index, child)
        state = _effective_state(child)
        governing: SpecificationArtifact | None = None
        if child.specification is not None:
            _resolved, problem = _resolved_regular_markdown(root, child.specification)
            if problem is not None:
                code = "artifact.spec.missing" if problem == "missing" else "artifact.spec.path"
                findings.append(_finding(code, source, f"specification link is {problem}", node=child.id))
            elif child.specification in loaded.invalid_paths:
                pass
            elif state != "queued":
                governing = specifications.get(child.specification)
                if governing is None:
                    findings.append(_finding("artifact.spec.governing", source, "lifecycle requires an active governing design", node=child.id))
                else:
                    allowed_statuses = {"draft"} if state == "designing" else {"approved", "implemented"}
                    if governing.status not in allowed_statuses:
                        findings.append(_finding("artifact.spec.status", source, f"design status {governing.status} cannot govern {state}", node=child.id))
                    if child.id not in governing.children:
                        findings.append(_finding("artifact.spec.coverage", source, "linked design does not cover backlog child", node=child.id))
                    if "ROADMAP.md" not in loaded.invalid_paths and governing.status in allowed_statuses and child.id in governing.children:
                        findings.extend(_gate_drift_findings(loaded, child, governing))
        elif state in _GOVERNED_STATES:
            findings.append(_finding("artifact.spec.required", source, f"{state} child requires a governing design", node=child.id))

        if state == "queued" and any(item.satisfied for item in child.gates.items):
            findings.append(_finding("artifact.spec.context-gate", source, "queued contextual reference cannot justify a checked gate", node=child.id))

        linked_plan: PlanArtifact | None = None
        if child.plan is not None:
            _resolved, problem = _resolved_regular_markdown(root, child.plan)
            if problem is not None:
                code = "artifact.plan.missing" if problem == "missing" else "artifact.plan.path"
                findings.append(_finding(code, source, f"plan link is {problem}", node=child.id))
            elif child.plan not in loaded.invalid_paths:
                linked_plan = plans.get(child.plan)
                if linked_plan is None and child.plan not in historical_paths:
                    findings.append(_finding("artifact.plan.governing", source, "plan link must select an active implementation plan", node=child.id))
                elif linked_plan is not None and linked_plan.child != child.id:
                    findings.append(_finding("artifact.plan.child", source, "linked plan covers a different child", node=child.id))
                elif linked_plan is not None and child.specification is not None and linked_plan.source_specification != child.specification:
                    findings.append(_finding("artifact.plan.source", source, "linked plan cites a different governing design", node=child.id))
        if state in {"planned", "in_progress", "implemented", "reviewed", "verified", "released"} and child.plan is None:
            findings.append(_finding("artifact.plan.required", source, f"{state} child requires an implementation plan", node=child.id))
        if linked_plan is not None and linked_plan.child == child.id:
            expected_status: str | None = None
            if state == "planned":
                expected_status = "approved"
            elif state == "in_progress":
                expected_status = "in_progress"
            elif state in {"implemented", "reviewed", "verified", "released"}:
                expected_status = "completed"
            if expected_status is not None and linked_plan.status != expected_status:
                findings.append(_finding("artifact.plan.status", source, f"{state} child requires a {expected_status} plan", node=child.id))
    return findings


def adherence_findings(loaded: AuditLoad) -> tuple[Finding, ...]:
    """Return governance-artifact and acceptance-criteria adherence findings."""
    findings = [
        *_metadata_findings(loaded),
        *_historical_findings(loaded),
        *_design_findings(loaded),
        *_plan_definition_findings(loaded),
        *_backlog_link_findings(loaded),
    ]
    return tuple(sorted(findings, key=finding_key))
