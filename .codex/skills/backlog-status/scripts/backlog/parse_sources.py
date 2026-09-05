from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import cast

from backlog.model import (
    ArtifactMetadataSource,
    ArtifactSources,
    Backlog,
    BacklogSources,
    DesignAcceptanceSource,
    GateHeadingSource,
    HistoricalArtifact,
    InventoryRowSource,
    PlanArtifact,
    ReleaseDashboardSource,
    RoadmapSources,
    SelectionSource,
    SourceLocation,
    SourceValue,
    SpecificationArtifact,
    StatementSource,
)
from backlog.parse import MarkdownParseError


_GATE_HEADING = re.compile(r"^### ([A-Z][0-9]+\.[0-9]+) — (.+)$")
_TASK_ITEM = re.compile(r"^- \[([ x])\] (.+)$")
_LIST_ITEM = re.compile(r"^(?:- |[0-9]+\. )(.+)$")
_METADATA = re.compile(r"^- \*\*([^*:]+):\*\* (.*)$")
_INVENTORY_HEADER = "| Child | Outcome | Status | Depends on | Spec | Plan | Gates | Review | Resume | Reason |"
_DASHBOARD_HEADER = "| Gate | Outcome | Gate state | Prerequisites | Evidence |"


@dataclass(frozen=True, slots=True)
class _Line:
    number: int
    text: str


def _read(path: Path) -> tuple[_Line, ...]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise MarkdownParseError(path, 1, f"cannot read UTF-8 Markdown: {error}", code="input.unreadable") from error
    return tuple(_Line(index, line) for index, line in enumerate(text.splitlines(), start=1))


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise MarkdownParseError(path, 1, "artifact path must be inside the repository root", code="input.outside-root") from error


def _source(path: Path, line: int) -> SourceLocation:
    return SourceLocation(path.name if path.is_absolute() else path.as_posix(), line)


def _find_heading(path: Path, lines: tuple[_Line, ...], heading: str, *, required: bool) -> int | None:
    indexes = [index for index, line in enumerate(lines) if line.text == heading]
    if not indexes and not required:
        return None
    if len(indexes) != 1:
        line = lines[indexes[1]].number if len(indexes) > 1 else lines[0].number if lines else 1
        raise MarkdownParseError(path, line, f"requires exactly one heading: {heading}", code="markdown.heading")
    return indexes[0]


def _section_end(lines: tuple[_Line, ...], start: int, level: int) -> int:
    for index in range(start + 1, len(lines)):
        text = lines[index].text
        if text.startswith("#") and len(text) > level and text[level] != "#":
            return index
    return len(lines)


def _rows(path: Path, lines: tuple[_Line, ...], header: str) -> tuple[tuple[_Line, tuple[str, ...]], ...]:
    indexes = [index for index, line in enumerate(lines) if line.text == header]
    if len(indexes) != 1:
        line = lines[indexes[1]].number if len(indexes) > 1 else 1
        raise MarkdownParseError(path, line, "source table header is ambiguous", code="markdown.table-header")
    rows: list[tuple[_Line, tuple[str, ...]]] = []
    for line in lines[indexes[0] + 2 :]:
        if not line.text.startswith("|"):
            break
        rows.append((line, tuple(cell.strip() for cell in line.text[1:-1].split("|"))))
    return tuple(rows)


def _identity(value: str) -> str:
    return value.removeprefix("`").removesuffix("`")


def _dependencies(value: str) -> tuple[str, ...]:
    return () if value == "—" else tuple(_identity(part) for part in value.split(", "))


def _task_statements(path: Path, lines: tuple[_Line, ...], start: int, end: int) -> tuple[StatementSource, ...]:
    statements: list[StatementSource] = []
    item_line: _Line | None = None
    checked = False
    fragments: list[str] = []

    def finish() -> None:
        if item_line is not None:
            statements.append(StatementSource(" ".join(fragments), _source(path, item_line.number), checked))

    for line in lines[start:end]:
        match = _TASK_ITEM.fullmatch(line.text)
        if match is not None:
            finish()
            item_line = line
            checked = match.group(1) == "x"
            fragments = [match.group(2)]
        elif line.text[:1].isspace() and item_line is not None:
            fragments.append(" ".join(line.text.split()))
        elif line.text:
            finish()
            item_line = None
            fragments = []
    finish()
    return tuple(statements)


def parse_roadmap_sources(path: Path) -> RoadmapSources:
    lines = _read(path)
    heading = _find_heading(path, lines, "## Version 0.1.0 release gates", required=False)
    if heading is None:
        return RoadmapSources(())
    return RoadmapSources(_task_statements(path, lines, heading + 1, _section_end(lines, heading, 2)))


def _prefixed_statements(
    path: Path,
    lines: tuple[_Line, ...],
    start: int,
    end: int,
    prefix: str,
) -> tuple[StatementSource, ...]:
    statements: list[StatementSource] = []
    for index in range(start, end):
        line = lines[index]
        if not line.text.startswith(prefix):
            continue
        fragments = [line.text]
        cursor = index + 1
        while cursor < end and lines[cursor].text[:1].isspace():
            fragments.append(" ".join(lines[cursor].text.split()))
            cursor += 1
        statements.append(StatementSource(" ".join(fragments), _source(path, line.number)))
    return tuple(statements)


def parse_backlog_sources(path: Path, backlog: Backlog) -> BacklogSources:
    lines = _read(path)
    inventory = tuple(InventoryRowSource(_identity(values[0]), values[1], _source(path, line.number)) for line, values in _rows(path, lines, _INVENTORY_HEADER))
    dashboard = tuple(
        ReleaseDashboardSource(
            _identity(values[0]),
            values[1],
            _dependencies(values[3]),
            _source(path, line.number),
        )
        for line, values in _rows(path, lines, _DASHBOARD_HEADER)
    )
    current_heading = cast(int, _find_heading(path, lines, "## Current position", required=True))
    current_end = _section_end(lines, current_heading, 2)
    selection_line = next(line for line in lines[current_heading + 1 : current_end] if line.text.startswith("- Active child:"))
    acceptance_heading = cast(int, _find_heading(path, lines, "## Local-child acceptance gates", required=True))
    acceptance_end = _section_end(lines, acceptance_heading, 2)
    gate_headings: list[GateHeadingSource] = []
    for line in lines[acceptance_heading + 1 : acceptance_end]:
        match = _GATE_HEADING.fullmatch(line.text)
        if match is not None:
            gate_headings.append(GateHeadingSource(match.group(1), match.group(2), _source(path, line.number)))
    return BacklogSources(
        inventory,
        SelectionSource(backlog.active_child, _source(path, selection_line.number)),
        dashboard,
        tuple(gate_headings),
        _prefixed_statements(
            path,
            lines,
            current_heading + 1,
            current_end,
            "- Release, tag, and package publication:",
        ),
    )


def _metadata_source(
    root: Path,
    path: Path,
    lines: tuple[_Line, ...],
) -> ArtifactMetadataSource:
    relative_path = _relative_path(root, path)
    metadata: dict[str, tuple[_Line, str]] = {}
    for line in lines[2:]:
        match = _METADATA.fullmatch(line.text)
        if match is None:
            break
        metadata[match.group(1)] = (line, match.group(2))

    def value(key: str) -> SourceValue:
        line, raw = metadata[key]
        return SourceValue(None if raw == "—" else raw, SourceLocation(relative_path, line.number))

    return ArtifactMetadataSource(
        relative_path,
        value("Governance"),
        value("Status"),
        value("Date") if "Date" in metadata else None,
        value("Approval") if "Approval" in metadata else None,
    )


def _acceptance_statements(root: Path, path: Path, lines: tuple[_Line, ...], start: int, end: int) -> tuple[StatementSource, ...]:
    relative_path = _relative_path(root, path)
    statements: list[tuple[bool, StatementSource]] = []
    item_line: _Line | None = None
    is_list = False
    fragments: list[str] = []

    def finish() -> None:
        if item_line is not None:
            statements.append(
                (
                    is_list,
                    StatementSource(" ".join(fragments), SourceLocation(relative_path, item_line.number)),
                )
            )

    for line in lines[start:end]:
        match = _LIST_ITEM.fullmatch(line.text)
        if match is not None:
            finish()
            item_line = line
            is_list = True
            fragments = [match.group(1)]
            continue
        if not line.text:
            finish()
            item_line = None
            fragments = []
            continue
        if item_line is None:
            item_line = line
            is_list = False
            fragments = [" ".join(line.text.split())]
        else:
            fragments.append(" ".join(line.text.split()))
    finish()
    listed = tuple(source for list_item, source in statements if list_item)
    return listed or tuple(source for _list_item, source in statements)


def parse_artifact_sources(
    root: Path,
    path: Path,
    artifact: SpecificationArtifact | PlanArtifact | HistoricalArtifact,
) -> ArtifactSources:
    lines = _read(path)
    metadata = _metadata_source(root, path, lines)
    if not isinstance(artifact, SpecificationArtifact):
        return ArtifactSources(metadata, ())
    heading = _find_heading(path, lines, "## Acceptance criteria", required=False)
    if heading is None:
        return ArtifactSources(metadata, ())
    end = _section_end(lines, heading, 2)
    relative_path = _relative_path(root, path)
    sections: list[DesignAcceptanceSource] = []
    for index in range(heading + 1, end):
        line = lines[index]
        match = _GATE_HEADING.fullmatch(line.text)
        if match is None:
            continue
        section_end = min(_section_end(lines, index, 3), end)
        sections.append(
            DesignAcceptanceSource(
                relative_path,
                match.group(1),
                match.group(2),
                _acceptance_statements(root, path, lines, index + 1, section_end),
                SourceLocation(relative_path, line.number),
            )
        )
    return ArtifactSources(metadata, tuple(sections))
