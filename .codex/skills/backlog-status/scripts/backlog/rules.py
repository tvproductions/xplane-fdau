from __future__ import annotations

from typing import TypeAlias

from backlog.findings import finding_key
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


def _fold(value: str) -> str:
    return " ".join(value.split())


def _source_for_child(loaded: AuditLoad, index: int, child: BacklogChild) -> SourceLocation:
    if index < len(loaded.sources.inventory_rows):
        return loaded.sources.inventory_rows[index].source
    return child.source


def _roadmap_identities(loaded: AuditLoad) -> dict[str, list[RoadmapNode]]:
    roadmap = loaded.snapshot.roadmap
    nodes: tuple[RoadmapNode, ...] = (
        *roadmap.milestones,
        *roadmap.epics,
        *roadmap.local_children,
        *roadmap.release_gates,
        *roadmap.external_boundaries,
    )
    identities: dict[str, list[RoadmapNode]] = {}
    for node in nodes:
        identities.setdefault(node.id, []).append(node)
    return identities


def _roadmap_findings(loaded: AuditLoad) -> list[Finding]:
    if "ROADMAP.md" in loaded.invalid_paths:
        return []
    roadmap = loaded.snapshot.roadmap
    findings: list[Finding] = []
    identities = _roadmap_identities(loaded)
    for identity, entries in identities.items():
        ordered = sorted(entries, key=lambda entry: entry.source.line)
        prior_kinds: set[str] = set()
        for index, entry in enumerate(ordered):
            if index == 0:
                prior_kinds.add(entry.kind)
                continue
            code = "roadmap.duplicate-id" if entry.kind in prior_kinds else "roadmap.kind-conflict"
            findings.append(_finding(code, entry.source.path, entry.source.line, identity, f"roadmap identity {identity} is not unique"))
            prior_kinds.add(entry.kind)

    epics: dict[str, list[Epic]] = {}
    for epic in roadmap.epics:
        epics.setdefault(epic.id, []).append(epic)
    for child in roadmap.local_children:
        owner = epics.get(child.epic, [])
        if len(owner) != 1 or child.id not in owner[0].children:
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
            elif len(entries) != 1:
                continue
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
            else:
                edges.append(dependency)
        if node.id in valid_local and isinstance(node, RoadmapChild):
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
    if "ROADMAP.md" in loaded.invalid_paths:
        return findings

    all_nodes = _roadmap_identities(loaded)
    roadmap_children: dict[str, list[RoadmapChild]] = {}
    for child in roadmap.local_children:
        roadmap_children.setdefault(child.id, []).append(child)
    expected = {
        child_id: children_for_id[0] for child_id, children_for_id in roadmap_children.items() if len(children_for_id) == 1 and len(all_nodes[child_id]) == 1
    }
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
        if child_id in roadmap_children:
            continue
        for index, child in rows:
            source = _source_for_child(loaded, index, child)
            if child_id in all_nodes and len(all_nodes[child_id]) != 1:
                continue
            code = "backlog.child-kind" if child_id in all_nodes else "backlog.unknown-child"
            findings.append(_finding(code, source.path, source.line, child_id, f"backlog child {child_id} is not a roadmap local child"))
    for child_id in expected:
        if child_id not in rows_by_child:
            findings.append(_finding("backlog.missing-child", backlog.source_path, None, child_id, f"backlog child {child_id} is missing"))

    local_rows_valid = len(expected) == len(roadmap.local_children) and all(len(rows) == 1 and child_id in expected for child_id, rows in rows_by_child.items())
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

    selection_entries = all_nodes.get(backlog.active_child, []) if backlog.active_child is not None else []
    if backlog.active_child is not None and (not selection_entries or len(selection_entries) == 1 and selection_entries[0].kind != "local_child"):
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

    for heading in loaded.sources.gate_headings:
        if heading.child in roadmap_children and heading.child not in expected:
            continue
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
    if "BACKLOG.md" in loaded.invalid_paths:
        return []
    rows_by_gate: dict[str, list[int]] = {}
    for index, gate in enumerate(loaded.snapshot.backlog.release_gates):
        rows_by_gate.setdefault(gate.id, []).append(index)
    findings: list[Finding] = []
    for gate_id, indexes in rows_by_gate.items():
        if len(indexes) == 1:
            continue
        for index in indexes:
            source = loaded.sources.release_dashboard[index].source if index < len(loaded.sources.release_dashboard) else None
            findings.append(
                _finding(
                    "release.inventory",
                    "BACKLOG.md",
                    source.line if source is not None else None,
                    gate_id,
                    f"release dashboard entry {gate_id} is not unique",
                )
            )
    if "ROADMAP.md" in loaded.invalid_paths:
        return findings

    identities = _roadmap_identities(loaded)
    roadmap_gates: dict[str, list[ReleaseGate]] = {}
    for gate in loaded.snapshot.roadmap.release_gates:
        roadmap_gates.setdefault(gate.id, []).append(gate)
    expected = {gate_id: gates[0] for gate_id, gates in roadmap_gates.items() if len(gates) == 1 and len(identities[gate_id]) == 1}
    for gate_id in expected:
        if gate_id not in rows_by_gate:
            findings.append(_finding("release.inventory", "BACKLOG.md", None, gate_id, f"release gate {gate_id} is missing from the dashboard"))
    for gate_id, indexes in rows_by_gate.items():
        if len(indexes) != 1:
            continue
        entries = identities.get(gate_id, [])
        index = indexes[0]
        source = loaded.sources.release_dashboard[index].source if index < len(loaded.sources.release_dashboard) else None
        if not entries:
            findings.append(
                _finding(
                    "release.inventory",
                    "BACKLOG.md",
                    source.line if source is not None else None,
                    gate_id,
                    f"release dashboard entry {gate_id} is not a roadmap release gate",
                )
            )
        elif gate_id not in expected:
            if len(entries) == 1:
                findings.append(
                    _finding(
                        "release.inventory",
                        "BACKLOG.md",
                        source.line if source is not None else None,
                        gate_id,
                        f"release dashboard entry {gate_id} is not a roadmap release gate",
                    )
                )
        elif index < len(loaded.sources.release_dashboard):
            dashboard = loaded.sources.release_dashboard[index]
            roadmap_gate = expected[gate_id]
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
    return tuple(sorted(findings, key=finding_key))


def release_authorization_findings(loaded: AuditLoad) -> tuple[Finding, ...]:
    """Enforce the two exact managed release-prohibition forms independently."""
    findings = []
    if "BACKLOG.md" not in loaded.invalid_paths:
        statements = loaded.sources.backlog_release_statements
        expected = "- Release, tag, and package publication: prohibited pending their separate gates and authorization."
        if len(statements) != 1 or _fold(statements[0].value) != expected:
            source = statements[-1].source if statements else loaded.sources.backlog_current_section
            findings.append(
                _finding(
                    "release.authorization",
                    "BACKLOG.md",
                    source.line if source else 1,
                    None,
                    "Current position requires exactly one unchanged release prohibition",
                )
            )
        for child in loaded.snapshot.backlog.children:
            if child.status == "released":
                findings.append(
                    _finding(
                        "release.prohibited-state",
                        child.source.path,
                        child.source.line,
                        child.id,
                        "released child state is prohibited by the current release policy",
                    )
                )
    if "ROADMAP.md" not in loaded.invalid_paths:
        expected = "A separate release review authorizes publication."
        statements = [item for item in loaded.sources.roadmap_release_items if _fold(item.value) == expected]
        if len(statements) != 1 or statements[0].checked is not False:
            source = statements[-1].source if statements else loaded.sources.roadmap_release_section
            findings.append(
                _finding(
                    "release.authorization",
                    "ROADMAP.md",
                    source.line if source else 1,
                    None,
                    "release gates require exactly one open separate publication authorization checkbox",
                )
            )
    return tuple(sorted(findings, key=finding_key))
