from __future__ import annotations

import sys
from typing import TypeAlias

from backlog.model import (
    AuditLoad,
    BacklogChild,
    Epic,
    ExternalBoundary,
    Finding,
    Milestone,
    ReleaseGate,
    RoadmapChild,
    SourceLocation,
)


RoadmapNode: TypeAlias = Milestone | Epic | RoadmapChild | ReleaseGate | ExternalBoundary


def _finding(code: str, path: str, line: int | None, node: str | None, message: str) -> Finding:
    return Finding(code, "error", path, line, node, None, message)


def _key(finding: Finding) -> tuple[int, str, int, str, str, int]:
    return (
        0 if finding.severity == "error" else 1,
        finding.path,
        finding.line if finding.line is not None else sys.maxsize,
        finding.code,
        finding.node or "",
        finding.gate if finding.gate is not None else sys.maxsize,
    )


def _fold(value: str) -> str:
    return " ".join(value.split())


def _source_for_child(loaded: AuditLoad, index: int, child: BacklogChild) -> SourceLocation:
    if index < len(loaded.sources.inventory_rows):
        return loaded.sources.inventory_rows[index].source
    return child.source


def _roadmap_findings(loaded: AuditLoad) -> list[Finding]:
    if "ROADMAP.md" in loaded.invalid_paths:
        return []
    roadmap = loaded.snapshot.roadmap
    findings: list[Finding] = []
    nodes = (
        *roadmap.milestones,
        *roadmap.epics,
        *roadmap.local_children,
        *roadmap.release_gates,
        *roadmap.external_boundaries,
    )
    identities: dict[str, list[RoadmapNode]] = {}
    for node in nodes:
        identities.setdefault(node.id, []).append(node)
    for identity, entries in identities.items():
        ordered = sorted(entries, key=lambda entry: entry.source.line)
        kinds = {entry.kind for entry in ordered}
        for entry in ordered[1:]:
            code = "roadmap.duplicate-id" if len(kinds) == 1 else "roadmap.kind-conflict"
            findings.append(_finding(code, entry.source.path, entry.source.line, identity, f"roadmap identity {identity} is not unique"))

    epics: dict[str, list[Epic]] = {}
    for epic in roadmap.epics:
        epics.setdefault(epic.id, []).append(epic)
    for child in roadmap.local_children:
        prefix = child.id.rsplit(".", 1)[0]
        owner = epics.get(child.epic, [])
        if prefix != child.epic or len(owner) != 1 or child.id not in owner[0].children:
            findings.append(
                _finding(
                    "roadmap.epic-mismatch",
                    child.source.path,
                    child.source.line,
                    child.id,
                    f"local child {child.id} is inconsistent with epic {child.epic}",
                )
            )

    m0_entries = identities.get("M0", [])
    valid_m0 = len(m0_entries) == 1 and m0_entries[0].kind == "milestone"
    valid_local = {child.id: child for child in roadmap.local_children if len(identities.get(child.id, ())) == 1}
    dependency_nodes: tuple[RoadmapChild | ReleaseGate, ...] = (*roadmap.local_children, *roadmap.release_gates)
    valid_edges: dict[str, tuple[str, ...]] = {}
    for node in dependency_nodes:
        seen: set[str] = set()
        edges: list[str] = []
        source_valid = node.id in valid_local
        for dependency in node.dependencies:
            if dependency in seen:
                findings.append(
                    _finding(
                        "roadmap.duplicate-dependency",
                        node.source.path,
                        node.source.line,
                        node.id,
                        f"dependency {dependency} is repeated for {node.id}",
                    )
                )
                source_valid = False
                continue
            seen.add(dependency)
            entries = identities.get(dependency, [])
            if dependency == "M0":
                if not valid_m0:
                    findings.append(
                        _finding(
                            "roadmap.unknown-dependency",
                            node.source.path,
                            node.source.line,
                            node.id,
                            "M0 is not a valid milestone prerequisite",
                        )
                    )
                    source_valid = False
                continue
            if not entries:
                findings.append(
                    _finding(
                        "roadmap.unknown-dependency",
                        node.source.path,
                        node.source.line,
                        node.id,
                        f"dependency {dependency} is unknown",
                    )
                )
                source_valid = False
            elif len(entries) != 1:
                source_valid = False
            elif entries[0].kind != "local_child":
                findings.append(
                    _finding(
                        "roadmap.dependency-kind",
                        node.source.path,
                        node.source.line,
                        node.id,
                        f"dependency {dependency} is not a local child",
                    )
                )
                source_valid = False
            else:
                edges.append(dependency)
        if source_valid and isinstance(node, RoadmapChild):
            valid_edges[node.id] = tuple(edge for edge in edges if edge in valid_local)

    colors = {child_id: "white" for child_id in valid_local}

    def walk(child_id: str) -> None:
        colors[child_id] = "gray"
        for dependency in valid_edges.get(child_id, ()):
            color = colors[dependency]
            if color == "white":
                walk(dependency)
            elif color == "gray":
                source = valid_local[child_id].source
                findings.append(
                    _finding(
                        "roadmap.dependency-cycle",
                        source.path,
                        source.line,
                        child_id,
                        f"local dependency cycle closes from {child_id} to {dependency}",
                    )
                )
        colors[child_id] = "black"

    for child in roadmap.local_children:
        if child.id in colors and colors[child.id] == "white":
            walk(child.id)
    return findings


def _backlog_findings(loaded: AuditLoad) -> list[Finding]:
    if "BACKLOG.md" in loaded.invalid_paths:
        return []
    backlog = loaded.snapshot.backlog
    roadmap = loaded.snapshot.roadmap
    findings: list[Finding] = []
    children = tuple(enumerate(backlog.children))
    rows_by_child: dict[str, list[tuple[int, BacklogChild]]] = {}
    for index, child in children:
        rows_by_child.setdefault(child.id, []).append((index, child))

    all_nodes = {
        node.id: node
        for node in (
            *roadmap.milestones,
            *roadmap.epics,
            *roadmap.local_children,
            *roadmap.release_gates,
            *roadmap.external_boundaries,
        )
    }
    expected = {child.id: child for child in roadmap.local_children}
    for child_id, rows in rows_by_child.items():
        for index, child in rows[1:]:
            source = _source_for_child(loaded, index, child)
            findings.append(
                _finding(
                    "backlog.duplicate-child",
                    source.path,
                    source.line,
                    child_id,
                    f"backlog child {child_id} appears more than once",
                )
            )
        if child_id in expected:
            continue
        for index, child in rows:
            source = _source_for_child(loaded, index, child)
            code = "backlog.child-kind" if child_id in all_nodes else "backlog.unknown-child"
            findings.append(_finding(code, source.path, source.line, child_id, f"backlog child {child_id} is not a roadmap local child"))
    for child_id in expected:
        if child_id not in rows_by_child:
            findings.append(_finding("backlog.missing-child", backlog.source_path, None, child_id, f"backlog child {child_id} is missing"))

    roadmap_valid = "ROADMAP.md" not in loaded.invalid_paths
    local_rows_valid = roadmap_valid and all(len(rows) == 1 and child_id in expected for child_id, rows in rows_by_child.items())
    if local_rows_valid and set(rows_by_child) == set(expected):
        actual_order = tuple(child.id for _index, child in children)
        expected_order = tuple(child.id for child in roadmap.local_children)
        if actual_order != expected_order:
            for index, child_id in enumerate(actual_order):
                if child_id != expected_order[index]:
                    source = _source_for_child(loaded, index, backlog.children[index])
                    findings.append(
                        _finding(
                            "backlog.child-order",
                            source.path,
                            source.line,
                            child_id,
                            "backlog local-child inventory is not in roadmap order",
                        )
                    )
                    break

    if roadmap_valid:
        for index, child in children:
            if child.id not in expected or len(rows_by_child[child.id]) != 1:
                continue
            source = _source_for_child(loaded, index, child)
            expected_child = expected[child.id]
            outcome = loaded.sources.inventory_rows[index].outcome if index < len(loaded.sources.inventory_rows) else ""
            if _fold(outcome) != _fold(expected_child.title):
                findings.append(
                    _finding(
                        "backlog.outcome-drift",
                        source.path,
                        source.line,
                        child.id,
                        f"backlog outcome for {child.id} differs from ROADMAP.md",
                    )
                )
            if child.dependencies != expected_child.dependencies:
                findings.append(
                    _finding(
                        "backlog.dependency-drift",
                        source.path,
                        source.line,
                        child.id,
                        f"backlog dependencies for {child.id} differ from ROADMAP.md",
                    )
                )

    if backlog.active_child is not None and backlog.active_child not in expected:
        source = loaded.sources.selection.source if loaded.sources.selection is not None else None
        findings.append(
            _finding(
                "backlog.invalid-selection",
                backlog.source_path,
                source.line if source is not None else None,
                backlog.active_child,
                f"active child {backlog.active_child} is not a roadmap local child",
            )
        )

    for index, child in children:
        source = _source_for_child(loaded, index, child)
        actual_satisfied = sum(item.satisfied for item in child.gates.items)
        if (child.gates.satisfied, child.gates.total) != (actual_satisfied, len(child.gates.items)):
            findings.append(
                _finding(
                    "backlog.gate-count",
                    source.path,
                    source.line,
                    child.id,
                    f"displayed gate count for {child.id} differs from its task list",
                )
            )

    if roadmap_valid:
        for heading in loaded.sources.gate_headings:
            expected_child = expected.get(heading.child)
            inventory = rows_by_child.get(heading.child, [])
            if expected_child is None or len(inventory) != 1:
                findings.append(
                    _finding(
                        "backlog.orphan-gates",
                        heading.source.path,
                        heading.source.line,
                        heading.child,
                        f"acceptance-gate heading {heading.child} has no unique roadmap-backed inventory child",
                    )
                )
            elif _fold(heading.title) != _fold(expected_child.title):
                findings.append(
                    _finding(
                        "backlog.gate-title",
                        heading.source.path,
                        heading.source.line,
                        heading.child,
                        f"acceptance-gate title for {heading.child} differs from ROADMAP.md",
                    )
                )
    return findings


def _release_findings(loaded: AuditLoad) -> list[Finding]:
    if "BACKLOG.md" in loaded.invalid_paths or "ROADMAP.md" in loaded.invalid_paths:
        return []
    roadmap_gates = {gate.id: gate for gate in loaded.snapshot.roadmap.release_gates}
    rows_by_gate: dict[str, list[int]] = {}
    for index, gate in enumerate(loaded.snapshot.backlog.release_gates):
        rows_by_gate.setdefault(gate.id, []).append(index)
    findings: list[Finding] = []
    for gate_id in roadmap_gates:
        if gate_id not in rows_by_gate:
            findings.append(_finding("release.inventory", "BACKLOG.md", None, gate_id, f"release gate {gate_id} is missing from the dashboard"))
    for gate_id, indexes in rows_by_gate.items():
        for index in indexes:
            source = loaded.sources.release_dashboard[index].source if index < len(loaded.sources.release_dashboard) else None
            if gate_id not in roadmap_gates or len(indexes) > 1:
                findings.append(
                    _finding(
                        "release.inventory",
                        "BACKLOG.md",
                        source.line if source is not None else None,
                        gate_id,
                        f"release dashboard entry {gate_id} is not a unique roadmap release gate",
                    )
                )
            elif index < len(loaded.sources.release_dashboard):
                dashboard = loaded.sources.release_dashboard[index]
                roadmap_gate = roadmap_gates[gate_id]
                if _fold(dashboard.outcome) != _fold(roadmap_gate.title) or dashboard.dependencies != roadmap_gate.dependencies:
                    findings.append(
                        _finding(
                            "release.definition-drift",
                            dashboard.source.path,
                            dashboard.source.line,
                            gate_id,
                            f"release dashboard definition for {gate_id} differs from ROADMAP.md",
                        )
                    )
    return findings


def structural_findings(loaded: AuditLoad) -> tuple[Finding, ...]:
    """Return independent roadmap, backlog, and dashboard consistency findings."""
    findings = [*_roadmap_findings(loaded), *_backlog_findings(loaded), *_release_findings(loaded)]
    return tuple(sorted(findings, key=_key))
