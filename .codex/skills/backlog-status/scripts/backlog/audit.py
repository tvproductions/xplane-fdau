from __future__ import annotations

from pathlib import Path
from dataclasses import replace
from typing import Literal

from backlog.findings import finding_key
from backlog.adherence import adherence_findings
from backlog.lifecycle import lifecycle_findings
from backlog.rules import release_authorization_findings, structural_findings
from backlog.model import (
    Artifacts,
    AuditLoad,
    AuditSources,
    Backlog,
    DesignAcceptanceSource,
    Finding,
    HistoricalArtifact,
    PlanArtifact,
    RepositorySnapshot,
    Roadmap,
    SpecificationArtifact,
)
from backlog.parse import (
    MarkdownParseError,
    parse_backlog,
    parse_artifact,
    parse_roadmap,
)
from backlog.parse_sources import parse_artifact_sources, parse_backlog_sources, parse_roadmap_sources
from backlog.policy import PolicyError, load_policy


def _empty_roadmap() -> Roadmap:
    return Roadmap((), (), (), (), ())


def _empty_backlog() -> Backlog:
    return Backlog(None, (), (), "BACKLOG.md")


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _parse_finding(root: Path, error: MarkdownParseError) -> Finding:
    return Finding(
        error.code,
        "error",
        _relative_path(root, error.path),
        error.line,
        error.node,
        error.gate,
        error.message,
    )


def load_audit(root: Path) -> AuditLoad:
    resolved = root.resolve()
    findings: list[Finding] = []
    invalid_paths: set[str] = set()
    inventory_sources = ()
    selection_source = None
    dashboard_sources = ()
    gate_heading_sources = ()
    backlog_release_sources = ()
    roadmap_release_sources = ()
    roadmap_cross_epic_sources = ()
    backlog_current_section = None
    roadmap_release_section = None
    artifact_metadata_sources = []
    design_acceptance_sources: list[DesignAcceptanceSource] = []

    roadmap_path = resolved / "ROADMAP.md"
    try:
        roadmap = parse_roadmap(roadmap_path)
        roadmap_sources = parse_roadmap_sources(roadmap_path)
        roadmap_release_sources = roadmap_sources.release_items
        roadmap_cross_epic_sources = roadmap_sources.cross_epic_designs
        roadmap_release_section = roadmap_sources.release_section
    except MarkdownParseError as error:
        roadmap = _empty_roadmap()
        relative = _relative_path(resolved, error.path)
        invalid_paths.add(relative)
        findings.append(_parse_finding(resolved, error))

    backlog_path = resolved / "BACKLOG.md"
    try:
        backlog = parse_backlog(backlog_path)
        backlog_sources = parse_backlog_sources(backlog_path, backlog)
        inventory_sources = backlog_sources.inventory_rows
        selection_source = backlog_sources.selection
        dashboard_sources = backlog_sources.release_dashboard
        gate_heading_sources = backlog_sources.gate_headings
        backlog_release_sources = backlog_sources.release_statements
        backlog_current_section = backlog_sources.current_section
    except MarkdownParseError as error:
        backlog = _empty_backlog()
        relative = _relative_path(resolved, error.path)
        invalid_paths.add(relative)
        findings.append(_parse_finding(resolved, error))

    specifications: list[SpecificationArtifact] = []
    plans: list[PlanArtifact] = []
    historical: list[HistoricalArtifact] = []
    artifact_roots: tuple[tuple[Path, Literal["specification", "plan"]], ...] = (
        (resolved / "docs/superpowers/specs", "specification"),
        (resolved / "docs/superpowers/plans", "plan"),
    )
    for directory, family in artifact_roots:
        try:
            paths = sorted(directory.glob("*.md"))
        except OSError as error:
            relative = _relative_path(resolved, directory)
            invalid_paths.add(relative)
            findings.append(Finding("input.unreadable", "error", relative, 1, None, None, f"cannot list artifacts: {error}"))
            continue
        for path in paths:
            try:
                artifact = parse_artifact(resolved, path, family)
                source_facts = parse_artifact_sources(resolved, path, artifact)
            except MarkdownParseError as error:
                relative = _relative_path(resolved, error.path)
                invalid_paths.add(relative)
                findings.append(_parse_finding(resolved, error))
                continue
            artifact_metadata_sources.append(source_facts.metadata)
            design_acceptance_sources.extend(source_facts.acceptance)
            if isinstance(artifact, HistoricalArtifact):
                historical.append(artifact)
            elif isinstance(artifact, SpecificationArtifact):
                specifications.append(artifact)
            else:
                plans.append(artifact)

    try:
        policy = load_policy(resolved)
    except PolicyError as error:
        policy = None
        invalid_paths.add(error.path)
        findings.append(Finding(error.code, "error", error.path, error.line, None, None, error.message))

    snapshot = RepositorySnapshot(
        resolved,
        roadmap,
        backlog,
        Artifacts(
            tuple(sorted(specifications, key=lambda artifact: artifact.path)),
            tuple(sorted(plans, key=lambda artifact: artifact.path)),
            tuple(sorted(historical, key=lambda artifact: artifact.path)),
        ),
    )
    sources = AuditSources(
        tuple(inventory_sources),
        selection_source,
        tuple(dashboard_sources),
        tuple(gate_heading_sources),
        tuple(sorted(artifact_metadata_sources, key=lambda source: source.path)),
        tuple(sorted(design_acceptance_sources, key=lambda source: (source.path, source.source.line))),
        tuple(backlog_release_sources),
        tuple(roadmap_release_sources),
        tuple(roadmap_cross_epic_sources),
        backlog_current_section,
        roadmap_release_section,
    )
    return AuditLoad(
        snapshot,
        tuple(sorted(findings, key=finding_key)),
        frozenset(invalid_paths),
        sources,
        policy,
    )


def audit_repository(root: Path) -> AuditLoad:
    loaded = load_audit(root)
    findings = (
        *loaded.findings,
        *structural_findings(loaded),
        *adherence_findings(loaded),
        *lifecycle_findings(loaded),
        *release_authorization_findings(loaded),
    )
    return replace(loaded, findings=tuple(sorted(findings, key=finding_key)))
