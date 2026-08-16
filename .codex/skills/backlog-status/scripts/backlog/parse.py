from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Literal, cast

from backlog.model import (
    CHILD_STATUSES,
    GATE_STATES,
    Artifacts,
    Backlog,
    BacklogChild,
    BacklogReleaseGate,
    ChildStatus,
    Epic,
    ExternalBoundary,
    GateItem,
    GateState,
    GateSummary,
    Milestone,
    HistoricalArtifact,
    PlanArtifact,
    RepositorySnapshot,
    ReleaseGate,
    Roadmap,
    RoadmapChild,
    SourceLocation,
    SpecificationArtifact,
)


_IDENTITY = re.compile(r"`([A-Z][0-9]+(?:\.[0-9]+)?)`")
_EPIC_IDENTITY = re.compile(r"`([A-Z][0-9]*)`")
_LOCAL_CHILD_IDENTITY = re.compile(r"`([A-Z][0-9]+\.[0-9]+)`")
_LINK = re.compile(r"\[([^]]+)]\(([^)]+)\)")
_SEPARATOR = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+$")
_EPIC_HEADING = re.compile(r"^#{2,3} ([A-Z][0-9]*) — (.+) epic$")
_INVALID_EPIC_HEADING = re.compile(r"^# [A-Z][0-9]* — .+ epic$")
_GATE_HEADING = re.compile(r"^### ([A-Z][0-9]+(?:\.[0-9]+)?) — (.+)$")
_TASK_ITEM = re.compile(r"^- \[([ x])\] (.+)$")
_GATE_COUNT = re.compile(r"([0-9]+)/([0-9]+)")
_METADATA = re.compile(r"^- \*\*([^*:]+):\*\* (.*)$")

_MILESTONE_HEADER = ("Milestone", "Outcome")
_CHILD_HEADER = ("Child", "Outcome", "Depends on")
_STANDARDS_CHILD_HEADER = (*_CHILD_HEADER, "External prerequisite")
_RELEASE_GATE_HEADER = ("Gate", "Outcome", "Depends on")
_BOUNDARY_HEADER = ("Boundary", "Outcome", "Owner", "xplane-fdau handoff condition")
_INVENTORY_HEADER = (
    "Child",
    "Outcome",
    "Status",
    "Depends on",
    "Spec",
    "Plan",
    "Gates",
    "Review",
    "Resume",
    "Reason",
)
_DASHBOARD_HEADER = ("Gate", "Outcome", "Gate state", "Prerequisites", "Evidence")
_ACTIVE_SPECIFICATION_KEYS = (
    "Governance",
    "Status",
    "Date",
    "Decision owner",
    "Roadmap epic",
    "Roadmap children",
    "Approval",
)
_ACTIVE_PLAN_KEYS = (
    "Governance",
    "Status",
    "Date",
    "Roadmap child",
    "Source specification",
    "Approval",
    "Completion evidence",
)
_HISTORICAL_KEYS = ("Governance", "Status", "Disposition")
_ACTIVE_SPECIFICATION_STATUSES = ("draft", "approved", "implemented", "superseded")
_ACTIVE_PLAN_STATUSES = ("draft", "approved", "in_progress", "completed", "superseded")
_HISTORICAL_STATUSES = ("completed", "superseded")


class MarkdownParseError(ValueError):
    def __init__(self, path: Path, line: int, message: str) -> None:
        self.path = path
        self.line = line
        self.message = message
        super().__init__(f"{path.as_posix()}:{line}: {message}")


@dataclass(frozen=True, slots=True)
class _Line:
    number: int
    text: str


def _read(path: Path) -> tuple[_Line, ...]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise MarkdownParseError(path, 1, f"cannot read UTF-8 Markdown: {error}") from error
    return tuple(_Line(index, line) for index, line in enumerate(text.splitlines(), start=1))


def _source(path: Path, line: int) -> SourceLocation:
    return SourceLocation(path.name if path.is_absolute() else path.as_posix(), line)


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise MarkdownParseError(path, 1, "artifact path must be inside the repository root") from error


def _cells(path: Path, line: _Line, expected: int) -> tuple[str, ...]:
    if not line.text.startswith("|") or not line.text.endswith("|"):
        raise MarkdownParseError(path, line.number, "managed table row must begin and end with '|'")
    values = tuple(cell.strip() for cell in line.text[1:-1].split("|"))
    if len(values) != expected:
        raise MarkdownParseError(path, line.number, f"managed table row requires {expected} cells")
    return values


def _identity(path: Path, line: int, value: str) -> str:
    match = _IDENTITY.fullmatch(value)
    if match is None:
        raise MarkdownParseError(path, line, f"invalid identity cell: {value!r}")
    return match.group(1)


def _find_heading(path: Path, lines: tuple[_Line, ...], heading: str) -> int:
    indexes = [index for index, line in enumerate(lines) if line.text == heading]
    if len(indexes) != 1:
        line = lines[indexes[1]].number if len(indexes) > 1 else lines[0].number if lines else 1
        raise MarkdownParseError(path, line, f"requires exactly one heading: {heading}")
    return indexes[0]


def _section_end(lines: tuple[_Line, ...], start: int, level: int) -> int:
    for index in range(start + 1, len(lines)):
        text = lines[index].text
        if text.startswith("#") and len(text) > level and text[level] != "#":
            return index
    return len(lines)


def _table(
    path: Path,
    lines: tuple[_Line, ...],
    start: int,
    end: int,
    header: tuple[str, ...],
    label: str,
) -> tuple[tuple[_Line, tuple[str, ...]], ...]:
    header_line = "| " + " | ".join(header) + " |"
    indexes = [index for index in range(start, end) if lines[index].text == header_line]
    if len(indexes) != 1:
        if len(indexes) > 1:
            line = lines[indexes[1]].number
        elif start < len(lines):
            line = lines[start].number
        elif lines:
            line = lines[-1].number
        else:
            line = 1
        raise MarkdownParseError(path, line, f"requires exactly one {label} table header")
    index = indexes[0]
    separator = lines[index + 1] if index + 1 < end else None
    separator_cells = () if separator is None else tuple(separator.text.strip("|").split("|"))
    if separator is None or _SEPARATOR.fullmatch(separator.text) is None or len(separator_cells) != len(header):
        line = lines[index + 1].number if index + 1 < end else lines[index].number
        raise MarkdownParseError(path, line, f"invalid managed table separator for {label}")

    rows: list[tuple[_Line, tuple[str, ...]]] = []
    for row_index in range(index + 2, end):
        line = lines[row_index]
        if not line.text.startswith("|"):
            break
        try:
            values = _cells(path, line, len(header))
        except MarkdownParseError as error:
            if error.message.startswith("managed table row requires"):
                raise MarkdownParseError(path, line.number, f"{label} row requires {len(header)} cells") from error
            raise
        rows.append((line, values))
    return tuple(rows)


def _dependencies(path: Path, line: int, value: str) -> tuple[str, ...]:
    if value == "—":
        return ()
    parts = value.split(", ")
    if ", ".join(parts) != value:
        raise MarkdownParseError(path, line, f"invalid dependency list: {value!r}")
    return tuple(_identity(path, line, part) for part in parts)


def _repository_relative_path(path: Path, line: int, target: str, message: str) -> str:
    parts = target.split("/")
    has_uri_scheme = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) is not None
    if not target or target.startswith("/") or "\\" in target or has_uri_scheme or any(part in {"", ".", ".."} for part in parts):
        raise MarkdownParseError(path, line, message)
    return target


def _repository_link(path: Path, line: int, value: str) -> str:
    match = _LINK.fullmatch(value)
    if match is None:
        raise MarkdownParseError(path, line, f"invalid repository-relative link: {value!r}")
    target = match.group(2)
    return _repository_relative_path(path, line, target, f"invalid repository-relative link: {value!r}")


def _optional_link(path: Path, line: int, value: str) -> str | None:
    return None if value == "—" else _repository_link(path, line, value)


def _status(path: Path, line: int, value: str) -> ChildStatus:
    if not value.startswith("`") or not value.endswith("`"):
        raise MarkdownParseError(path, line, f"invalid child status: {value!r}")
    status = value[1:-1]
    if status not in CHILD_STATUSES:
        raise MarkdownParseError(path, line, f"invalid child status: {value!r}")
    return status


def _gate_count(path: Path, line: int, value: str) -> tuple[int, int]:
    if value == "—":
        return 0, 0
    match = _GATE_COUNT.fullmatch(value)
    if match is None:
        raise MarkdownParseError(path, line, f"invalid gate count: {value!r}")
    return int(match.group(1)), int(match.group(2))


def _links(path: Path, line: int, value: str) -> tuple[str, ...]:
    matches = tuple(_LINK.finditer(value))
    if not matches:
        raise MarkdownParseError(path, line, "evidence requires one or more repository-relative links")
    remainder = _LINK.sub("", value)
    if remainder.strip():
        raise MarkdownParseError(path, line, "evidence links must be separated only by whitespace")
    return tuple(_repository_link(path, line, match.group(0)) for match in matches)


def _artifact_metadata(path: Path) -> tuple[_Line, tuple[tuple[_Line, str, str], ...]]:
    lines = _read(path)
    if not lines or not lines[0].text.startswith("# "):
        raise MarkdownParseError(path, 1, "artifact requires a title")
    if len(lines) < 2 or lines[1].text != "":
        line = lines[1].number if len(lines) > 1 else lines[0].number
        raise MarkdownParseError(path, line, "missing Governance metadata")
    if len(lines) < 3 or _METADATA.fullmatch(lines[2].text) is None:
        line = lines[2].number if len(lines) > 2 else lines[1].number
        raise MarkdownParseError(path, line, "missing Governance metadata")
    metadata: list[tuple[_Line, str, str]] = []
    for line in lines[2:]:
        match = _METADATA.fullmatch(line.text)
        if match is None:
            break
        metadata.append((line, match.group(1), match.group(2)))
    if not metadata or metadata[0][1] != "Governance":
        raise MarkdownParseError(path, lines[2].number, "missing Governance metadata")
    return lines[0], tuple(metadata)


def _metadata_values(
    path: Path,
    metadata: tuple[tuple[_Line, str, str], ...],
    expected: tuple[str, ...],
    label: str,
) -> dict[str, str]:
    keys = tuple(key for _line, key, _value in metadata)
    if keys != expected:
        mismatch = next((index for index, (actual, wanted) in enumerate(zip(keys, expected, strict=False)) if actual != wanted), None)
        if mismatch is not None:
            line = metadata[mismatch][0].number
        elif len(metadata) > len(expected):
            line = metadata[len(expected)][0].number
        else:
            line = metadata[-1][0].number + 1
        raise MarkdownParseError(path, line, f"{label} metadata keys must match the managed family")
    return {key: value for _line, key, value in metadata}


def _artifact_status(path: Path, line: int, value: str, allowed: tuple[str, ...], label: str) -> str:
    if value not in allowed:
        raise MarkdownParseError(path, line, f"invalid {label} status: {value!r}")
    return value


def _artifact_epic(path: Path, line: int, value: str) -> str:
    match = _EPIC_IDENTITY.fullmatch(value)
    if match is None:
        raise MarkdownParseError(path, line, "Roadmap epic requires one epic identity")
    return match.group(1)


def _artifact_children(path: Path, line: int, value: str) -> tuple[str, ...]:
    parts = value.split(", ")
    if not value or ", ".join(parts) != value:
        raise MarkdownParseError(path, line, "Roadmap children requires local-child identities")
    children: list[str] = []
    for part in parts:
        match = _LOCAL_CHILD_IDENTITY.fullmatch(part)
        if match is None:
            raise MarkdownParseError(path, line, "Roadmap children requires local-child identities")
        children.append(match.group(1))
    return tuple(children)


def _artifact_child(path: Path, line: int, value: str) -> str:
    try:
        child = _identity(path, line, value)
    except MarkdownParseError as error:
        raise MarkdownParseError(path, line, "Roadmap child requires one identity") from error
    if "." not in child:
        raise MarkdownParseError(path, line, "Roadmap child requires one identity")
    return child


def _artifact_relative_value(path: Path, line: int, value: str, label: str) -> str:
    match = re.fullmatch(r"`([^`]+)`", value)
    if match is None:
        raise MarkdownParseError(path, line, f"{label} requires a repository-relative path")
    target = match.group(1)
    return _repository_relative_path(path, line, target, f"{label} requires a repository-relative path")


def _optional_artifact_value(value: str) -> str | None:
    return None if value == "—" else value


def _parse_artifact(root: Path, path: Path, family: str) -> SpecificationArtifact | PlanArtifact | HistoricalArtifact:
    title, metadata = _artifact_metadata(path)
    governance = metadata[0][2]
    if governance == "historical":
        values = _metadata_values(path, metadata, _HISTORICAL_KEYS, "historical")
        status_line = metadata[1][0].number
        status = _artifact_status(path, status_line, values["Status"], _HISTORICAL_STATUSES, "historical")
        return HistoricalArtifact(
            _relative_path(root, path),
            "historical",
            cast(Literal["completed", "superseded"], status),
            values["Disposition"],
            SourceLocation(_relative_path(root, path), title.number),
        )
    if governance != "active":
        raise MarkdownParseError(path, metadata[0][0].number, f"invalid Governance metadata: {governance!r}")
    if family == "specification":
        values = _metadata_values(path, metadata, _ACTIVE_SPECIFICATION_KEYS, "active design")
        status = _artifact_status(path, metadata[1][0].number, values["Status"], _ACTIVE_SPECIFICATION_STATUSES, "active design")
        relative_path = _relative_path(root, path)
        return SpecificationArtifact(
            relative_path,
            "active",
            cast(Literal["draft", "approved", "implemented", "superseded"], status),
            _artifact_epic(path, metadata[4][0].number, values["Roadmap epic"]),
            _artifact_children(path, metadata[5][0].number, values["Roadmap children"]),
            _optional_artifact_value(values["Approval"]),
            SourceLocation(relative_path, title.number),
        )
    values = _metadata_values(path, metadata, _ACTIVE_PLAN_KEYS, "active plan")
    status = _artifact_status(path, metadata[1][0].number, values["Status"], _ACTIVE_PLAN_STATUSES, "active plan")
    relative_path = _relative_path(root, path)
    return PlanArtifact(
        relative_path,
        "active",
        cast(Literal["draft", "approved", "in_progress", "completed", "superseded"], status),
        _artifact_child(path, metadata[3][0].number, values["Roadmap child"]),
        _artifact_relative_value(path, metadata[4][0].number, values["Source specification"], "Source specification"),
        _optional_artifact_value(values["Approval"]),
        None
        if values["Completion evidence"] == "—"
        else _artifact_relative_value(path, metadata[6][0].number, values["Completion evidence"], "Completion evidence"),
        SourceLocation(relative_path, title.number),
    )


def _gate_items(
    path: Path,
    lines: tuple[_Line, ...],
    start: int,
    end: int,
) -> tuple[GateItem, ...]:
    items: list[GateItem] = []
    item_line: _Line | None = None
    checked = False
    fragments: list[str] = []

    def finish_item() -> None:
        if item_line is None:
            return
        content = " ".join(fragments)
        marker = " — Evidence: "
        statement, separator, evidence_text = content.partition(marker)
        statement = statement.strip()
        if not statement:
            raise MarkdownParseError(path, item_line.number, "gate task item requires a statement")
        if checked:
            if not separator:
                raise MarkdownParseError(path, item_line.number, "checked gate requires evidence")
            evidence = _links(path, item_line.number, evidence_text)
        else:
            if separator:
                raise MarkdownParseError(path, item_line.number, "unchecked gate cannot contain evidence")
            evidence = ()
        items.append(
            GateItem(
                ordinal=len(items) + 1,
                statement=statement,
                satisfied=checked,
                evidence=evidence,
                source=_source(path, item_line.number),
            )
        )

    for index in range(start, end):
        line = lines[index]
        if not line.text:
            continue
        match = _TASK_ITEM.fullmatch(line.text)
        if match is not None:
            finish_item()
            item_line = line
            checked = match.group(1) == "x"
            fragments = [match.group(2)]
            continue
        if line.text.startswith("- ["):
            raise MarkdownParseError(path, line.number, f"invalid gate task item: {line.text!r}")
        if line.text[:1].isspace() and item_line is not None:
            fragments.append(" ".join(line.text.split()))
            continue
        raise MarkdownParseError(path, line.number, "invalid gate task item")
    finish_item()
    return tuple(items)


def parse_roadmap(path: Path) -> Roadmap:
    lines = _read(path)
    milestone_heading = _find_heading(path, lines, "## Milestones")
    milestone_rows = _table(
        path,
        lines,
        milestone_heading + 1,
        _section_end(lines, milestone_heading, 2),
        _MILESTONE_HEADER,
        "milestone",
    )
    milestones = tuple(
        Milestone(_identity(path, line.number, values[0]), "milestone", values[1], _source(path, line.number)) for line, values in milestone_rows
    )

    epics: list[Epic] = []
    children: list[RoadmapChild] = []
    for index, heading in enumerate(lines):
        if _INVALID_EPIC_HEADING.fullmatch(heading.text) is not None:
            raise MarkdownParseError(path, heading.number, "invalid managed epic heading")
        match = _EPIC_HEADING.fullmatch(heading.text)
        if match is None:
            continue
        epic_id, title = match.groups()
        level = len(heading.text) - len(heading.text.lstrip("#"))
        end = _section_end(lines, index, level)
        header = _STANDARDS_CHILD_HEADER if epic_id == "S" else _CHILD_HEADER
        rows = _table(path, lines, index + 1, end, header, "standards" if epic_id == "S" else "child")
        epic_children: list[str] = []
        for line, values in rows:
            child_id = _identity(path, line.number, values[0])
            external_prerequisite = None
            if len(values) == 4:
                if not values[3]:
                    raise MarkdownParseError(path, line.number, "standards row requires 4 cells")
                external_prerequisite = None if values[3] == "—" else values[3]
            children.append(
                RoadmapChild(
                    child_id,
                    "local_child",
                    epic_id,
                    values[1],
                    _dependencies(path, line.number, values[2]),
                    external_prerequisite,
                    _source(path, line.number),
                )
            )
            epic_children.append(child_id)
        epics.append(Epic(epic_id, "epic", title, tuple(epic_children), _source(path, heading.number)))

    release_heading = _find_heading(path, lines, "## Release gates")
    release_rows = _table(
        path,
        lines,
        release_heading + 1,
        _section_end(lines, release_heading, 2),
        _RELEASE_GATE_HEADER,
        "release gate",
    )
    release_gates = tuple(
        ReleaseGate(
            _identity(path, line.number, values[0]),
            "release_gate",
            values[1],
            _dependencies(path, line.number, values[2]),
            _source(path, line.number),
        )
        for line, values in release_rows
    )

    boundary_heading = _find_heading(path, lines, "## External consumer and downstream boundaries")
    boundary_rows = _table(
        path,
        lines,
        boundary_heading + 1,
        _section_end(lines, boundary_heading, 2),
        _BOUNDARY_HEADER,
        "external boundary",
    )
    external_boundaries = tuple(
        ExternalBoundary(
            _identity(path, line.number, values[0]),
            "external_boundary",
            values[1],
            values[2],
            values[3],
            _source(path, line.number),
        )
        for line, values in boundary_rows
    )
    return Roadmap(tuple(milestones), tuple(epics), tuple(children), release_gates, external_boundaries)


def _active_child(path: Path, lines: tuple[_Line, ...]) -> str | None:
    current_heading = _find_heading(path, lines, "## Current position")
    end = _section_end(lines, current_heading, 2)
    selections = [line for line in lines[current_heading + 1 : end] if line.text.startswith("- Active child:")]
    if len(selections) != 1:
        line = selections[1].number if len(selections) > 1 else lines[current_heading].number
        raise MarkdownParseError(path, line, "requires exactly one managed active child line")
    line = selections[0]
    if line.text == "- Active child: —.":
        return None
    match = re.fullmatch(r"- Active child: (`[A-Z][0-9]+(?:\.[0-9]+)?`)\.", line.text)
    if match is None:
        raise MarkdownParseError(path, line.number, "active child selection is invalid")
    return _identity(path, line.number, match.group(1))


def _gate_heading(
    path: Path,
    lines: tuple[_Line, ...],
    child_id: str,
    start: int,
    end: int,
) -> tuple[int, int] | None:
    found: list[tuple[int, int]] = []
    for index in range(start, end):
        line = lines[index]
        match = _GATE_HEADING.fullmatch(line.text)
        if match is not None and match.group(1) == child_id:
            found.append((index, _section_end(lines, index, 3)))
    if len(found) > 1:
        raise MarkdownParseError(path, lines[found[1][0]].number, f"duplicate acceptance-gate heading for {child_id}")
    return found[0] if found else None


def _dashboard(path: Path, lines: tuple[_Line, ...]) -> tuple[BacklogReleaseGate, ...]:
    heading = _find_heading(path, lines, "## Release-gate dashboard")
    rows = _table(path, lines, heading + 1, _section_end(lines, heading, 2), _DASHBOARD_HEADER, "release dashboard")
    gates: list[BacklogReleaseGate] = []
    for line, values in rows:
        gate_id = _identity(path, line.number, values[0])
        if not values[2].startswith("`") or not values[2].endswith("`") or values[2][1:-1] not in GATE_STATES:
            raise MarkdownParseError(path, line.number, f"invalid release-gate state: {values[2]!r}")
        _dependencies(path, line.number, values[3])
        evidence = () if values[4] == "—" else _links(path, line.number, values[4])
        gates.append(BacklogReleaseGate(gate_id, cast(GateState, values[2][1:-1]), evidence, _source(path, line.number)))
    return tuple(gates)


def parse_backlog(path: Path) -> Backlog:
    lines = _read(path)
    active_child = _active_child(path, lines)
    inventory_heading = _find_heading(path, lines, "## Local child inventory")
    inventory_rows = _table(
        path,
        lines,
        inventory_heading + 1,
        _section_end(lines, inventory_heading, 2),
        _INVENTORY_HEADER,
        "inventory",
    )
    acceptance_heading = _find_heading(path, lines, "## Local-child acceptance gates")
    acceptance_end = _section_end(lines, acceptance_heading, 2)
    children: list[BacklogChild] = []
    for line, values in inventory_rows:
        child_id = _identity(path, line.number, values[0])
        displayed_satisfied, displayed_total = _gate_count(path, line.number, values[6])
        gate_items: tuple[GateItem, ...] = ()
        if values[6] != "—":
            gate_heading = _gate_heading(path, lines, child_id, acceptance_heading + 1, acceptance_end)
            if gate_heading is None:
                raise MarkdownParseError(path, line.number, f"missing acceptance-gate heading for {child_id}")
            gate_items = _gate_items(path, lines, gate_heading[0] + 1, gate_heading[1])
        reason = None if values[9] == "—" else values[9]
        if reason == "":
            raise MarkdownParseError(path, line.number, "reason cell must not be empty")
        children.append(
            BacklogChild(
                child_id,
                _status(path, line.number, values[2]),
                _dependencies(path, line.number, values[3]),
                _optional_link(path, line.number, values[4]),
                _optional_link(path, line.number, values[5]),
                GateSummary(displayed_satisfied, displayed_total, gate_items),
                _optional_link(path, line.number, values[7]),
                None if values[8] == "—" else _status(path, line.number, values[8]),
                reason,
                False,
                _source(path, line.number),
            )
        )
    return Backlog(active_child, tuple(children), _dashboard(path, lines), path.name if path.is_absolute() else path.as_posix())


def parse_artifacts(root: Path) -> Artifacts:
    resolved = root.resolve()
    specifications: list[SpecificationArtifact] = []
    plans: list[PlanArtifact] = []
    historical: list[HistoricalArtifact] = []
    for directory, family in (
        (resolved / "docs/superpowers/specs", "specification"),
        (resolved / "docs/superpowers/plans", "plan"),
    ):
        for path in sorted(directory.glob("*.md")):
            parsed = _parse_artifact(resolved, path, family)
            if isinstance(parsed, HistoricalArtifact):
                historical.append(parsed)
            elif isinstance(parsed, SpecificationArtifact):
                specifications.append(parsed)
            else:
                plans.append(parsed)
    return Artifacts(
        tuple(sorted(specifications, key=lambda artifact: artifact.path)),
        tuple(sorted(plans, key=lambda artifact: artifact.path)),
        tuple(sorted(historical, key=lambda artifact: artifact.path)),
    )


def parse_repository(root: Path) -> RepositorySnapshot:
    resolved = root.resolve()
    return RepositorySnapshot(
        root=resolved,
        roadmap=parse_roadmap(resolved / "ROADMAP.md"),
        backlog=parse_backlog(resolved / "BACKLOG.md"),
        artifacts=parse_artifacts(resolved),
    )
