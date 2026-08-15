"""Contract tests for the hand-authored roadmap and backlog authorities."""

from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "ROADMAP.md"
BACKLOG = ROOT / "BACKLOG.md"

MILESTONE_HEADER = ("Milestone", "Outcome")
CHILD_HEADER = ("Child", "Outcome", "Depends on")
STANDARDS_HEADER = ("Child", "Outcome", "Depends on", "External prerequisite")
GATE_HEADER = ("Gate", "Outcome", "Depends on")
BOUNDARY_HEADER = ("Boundary", "Owner", "xplane-fdau handoff condition")
INVENTORY_HEADER = (
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def table_rows(text: str, header: tuple[str, ...]) -> list[tuple[str, ...]]:
    lines = text.splitlines()
    expected = tuple(header)
    rows: list[tuple[str, ...]] = []
    for index, line in enumerate(lines):
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        if cells != expected:
            continue
        for row in lines[index + 2 :]:
            if not row.startswith("|"):
                break
            values = tuple(cell.strip() for cell in row.strip().strip("|").split("|"))
            if len(values) != len(expected):
                break
            rows.append(values)
    return rows


def identity(cell: str) -> str:
    match = re.fullmatch(r"`([A-Z][0-9]+(?:\.[0-9]+)?)`", cell)
    if match is None:
        raise AssertionError(f"not an exact identity cell: {cell!r}")
    return match.group(1)


def roadmap_rows(header: tuple[str, ...]) -> list[tuple[str, ...]]:
    return table_rows(read_text(ROADMAP), header)


def roadmap_child_rows() -> list[tuple[str, ...]]:
    lines = read_text(ROADMAP).splitlines()
    rows: list[tuple[str, ...]] = []
    index = 0
    while index < len(lines):
        cells = tuple(cell.strip() for cell in lines[index].strip().strip("|").split("|"))
        if cells not in {CHILD_HEADER, STANDARDS_HEADER}:
            index += 1
            continue
        index += 2
        while index < len(lines) and lines[index].startswith("|"):
            values = tuple(cell.strip() for cell in lines[index].strip().strip("|").split("|"))
            rows.append(values)
            index += 1
    return rows


class RoadmapAuthorityTests(unittest.TestCase):
    def test_node_kinds_are_explicit_complete_and_nonoverlapping(self) -> None:
        milestones = [identity(row[0]) for row in roadmap_rows(MILESTONE_HEADER)]
        children = [identity(row[0]) for row in roadmap_child_rows()]
        gates = [identity(row[0]) for row in roadmap_rows(GATE_HEADER)]
        boundaries = [identity(row[0]) for row in roadmap_rows(BOUNDARY_HEADER)]

        self.assertEqual(["M0"], milestones)
        self.assertEqual(["G1"], gates)
        self.assertEqual(["I1.1", "I1.2", "I2.1", "F1.1", "F2.1"], boundaries)
        self.assertEqual(54, len(children))
        self.assertEqual(54, len(set(children)))
        kinds = [set(milestones), set(children), set(gates), set(boundaries)]
        for index, current in enumerate(kinds):
            for other in kinds[index + 1 :]:
                self.assertFalse(current & other)

    def test_authoritative_dependency_cells_use_exact_identities(self) -> None:
        rows = roadmap_child_rows()
        for row in rows:
            dependency_cell = row[2]
            self.assertNotRegex(dependency_cell, r"[–—-]`[A-Z]")
            for dependency in dependency_cell.split(", "):
                self.assertRegex(dependency, r"^`(?:M0|[A-Z][0-9]+\.[0-9]+)`$")

        by_child = {identity(row[0]): row[2] for row in rows}
        self.assertEqual("`C1.3`, `C1.4`, `C1.5`, `C2.4`", by_child["C3.1"])
        self.assertEqual("`A1.4`, `A1.5`, `A1.6`, `A1.7`, `A1.8`", by_child["A1.9"])
        self.assertEqual("`P1.2`, `P1.3`, `P1.4`", by_child["P1.5"])

    def test_roadmap_has_no_mutable_child_status_column(self) -> None:
        roadmap = read_text(ROADMAP)
        self.assertNotIn("| Child | Outcome | Status |", roadmap)
        self.assertIn("`BACKLOG.md` is the durable Superpowers entry point", roadmap)


if __name__ == "__main__":
    unittest.main()
