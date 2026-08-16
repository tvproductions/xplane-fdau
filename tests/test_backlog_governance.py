"""Contract tests for the hand-authored roadmap and backlog authorities."""

from __future__ import annotations

from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch


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


def metadata(path: Path) -> dict[str, str]:
    lines = read_text(path).splitlines()
    result: dict[str, str] = {}
    started = False
    for line in lines[1:]:
        if not started and not line:
            continue
        match = re.fullmatch(r"- \*\*([^*]+):\*\* (.+)", line)
        if match is None:
            if started:
                break
            continue
        started = True
        key, value = match.groups()
        result[key] = value
    return result


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


class BacklogAuthorityTests(unittest.TestCase):
    def test_current_position_has_one_exact_selection_line(self) -> None:
        backlog = read_text(BACKLOG)
        selection_lines = [line for line in backlog.splitlines() if line.startswith("- Active child:")]
        self.assertEqual(["- Active child: `T1.1`."], selection_lines)
        self.assertNotIn("Active child slice:", backlog)

    def test_inventory_matches_every_roadmap_child_once_in_order(self) -> None:
        roadmap = roadmap_child_rows()
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        self.assertEqual(54, len(inventory))
        self.assertEqual(
            [(identity(row[0]), row[1], row[2]) for row in roadmap],
            [(identity(row[0]), row[1], row[3]) for row in inventory],
        )

    def test_inventory_excludes_nonchildren_and_range_rows(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        inventory_ids = [identity(row[0]) for row in inventory]
        excluded = {"M0", "G1", "I1.1", "I1.2", "I2.1", "F1.1", "F2.1"}
        self.assertFalse(set(inventory_ids) & excluded)
        self.assertEqual(len(inventory_ids), len(set(inventory_ids)))
        self.assertNotRegex("\n".join(row[0] for row in inventory), r"[–—]")

    def test_inventory_owns_complete_mutable_state_cells(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        allowed_statuses = {
            "`queued`",
            "`designing`",
            "`specified`",
            "`planned`",
            "`in_progress`",
            "`implemented`",
            "`reviewed`",
            "`verified`",
            "`blocked`",
            "`deferred`",
            "`released`",
        }
        for row in inventory:
            child, _outcome, status, dependencies, spec, plan, gates, review, resume, reason = row
            self.assertIn(status, allowed_statuses, child)
            self.assertRegex(dependencies, r"^`(?:M0|[A-Z][0-9]+\.[0-9]+)`(?:, `(?:M0|[A-Z][0-9]+\.[0-9]+)`)*$")
            self.assertTrue(spec == "—" or spec.startswith("[design](docs/superpowers/specs/"), child)
            self.assertTrue(
                plan == "—" or plan.startswith("[draft plan](docs/superpowers/plans/") or plan.startswith("[plan](docs/superpowers/plans/"),
                child,
            )
            self.assertRegex(gates, r"^(?:—|[0-9]+/[0-9]+)$")
            self.assertEqual("—", review)
            if status == "`blocked`":
                self.assertEqual("`queued`", resume)
                self.assertNotEqual("—", reason)
            else:
                self.assertEqual("—", resume)
                self.assertEqual("—", reason)

    def test_no_second_child_status_dashboard_remains(self) -> None:
        backlog = read_text(BACKLOG)
        self.assertEqual(1, backlog.count("| Child | Outcome | Status |"))
        for obsolete_heading in (
            "## Build-foundation child dashboard",
            "## Canonical-contract child dashboard",
            "## Future release-path child dashboard",
            "## Standards child dashboard",
            "## Repository governance tooling",
        ):
            self.assertNotIn(obsolete_heading, backlog)
        self.assertIn("## Release-gate dashboard", backlog)
        self.assertIn("## External consumer and downstream boundaries", backlog)

    def test_all_child_gate_headings_are_within_the_unified_section(self) -> None:
        backlog = read_text(BACKLOG)
        section_start = backlog.index("## Local-child acceptance gates")
        section_end = backlog.index("\n## Release-gate dashboard", section_start)
        for heading in re.finditer(r"^### [A-Z][0-9]+\.[0-9]+ — ", backlog, re.MULTILINE):
            self.assertGreater(heading.start(), section_start)
            self.assertLess(heading.start(), section_end)


class GovernanceArtifactTests(unittest.TestCase):
    def test_every_spec_uses_one_complete_governance_family(self) -> None:
        for path in sorted((ROOT / "docs/superpowers/specs").glob("*.md")):
            values = metadata(path)
            self.assertIn(values.get("Governance"), {"active", "historical"}, path)
            if values["Governance"] == "active":
                self.assertEqual(
                    {
                        "Governance",
                        "Status",
                        "Date",
                        "Decision owner",
                        "Roadmap epic",
                        "Roadmap children",
                        "Approval",
                    },
                    set(values),
                    path,
                )
                self.assertIn(values["Status"], {"draft", "approved", "implemented", "superseded"}, path)
            else:
                self.assertEqual({"Governance", "Status", "Disposition"}, set(values), path)
                self.assertIn(values["Status"], {"completed", "superseded"}, path)

    def test_every_plan_uses_one_complete_governance_family(self) -> None:
        for path in sorted((ROOT / "docs/superpowers/plans").glob("*.md")):
            values = metadata(path)
            self.assertIn(values.get("Governance"), {"active", "historical"}, path)
            if values["Governance"] == "active":
                self.assertEqual(
                    {
                        "Governance",
                        "Status",
                        "Date",
                        "Roadmap child",
                        "Source specification",
                        "Approval",
                        "Completion evidence",
                    },
                    set(values),
                    path,
                )
                self.assertIn(
                    values["Status"],
                    {"draft", "approved", "in_progress", "completed", "superseded"},
                    path,
                )
            else:
                self.assertEqual({"Governance", "Status", "Disposition"}, set(values), path)
                self.assertIn(values["Status"], {"completed", "superseded"}, path)

    def test_completed_active_plan_completion_evidence_is_inline_repo_relative_file(self) -> None:
        root = ROOT.resolve()
        for path in sorted((ROOT / "docs/superpowers/plans").glob("*.md")):
            values = metadata(path)
            if values.get("Governance") != "active" or values.get("Status") != "completed":
                continue
            evidence = values["Completion evidence"]
            self.assertNotEqual("—", evidence, path)
            inline_match = re.fullmatch(r"`([^`]+)`", evidence)
            link_match = re.fullmatch(r"\[[^]]+\]\(([^)]+)\)", evidence)
            self.assertTrue(inline_match is not None or link_match is not None, path)
            if inline_match is not None:
                evidence_path = inline_match.group(1)
            elif link_match is not None:
                evidence_path = link_match.group(1)
            else:
                continue
            candidate = Path(evidence_path)
            self.assertFalse(candidate.is_absolute(), path)
            resolved = (ROOT / candidate).resolve()
            self.assertTrue(resolved.is_relative_to(root), path)
            self.assertEqual(resolved.relative_to(root).as_posix(), evidence_path, path)
            self.assertTrue(resolved.is_file(), path)
            if not resolved.is_relative_to((ROOT / "docs").resolve()):
                self.assertIsNotNone(inline_match, path)

    def test_completion_evidence_rejects_absolute_and_noncanonical_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            plan_directory = root / "docs/superpowers/plans"
            plan_directory.mkdir(parents=True)
            evidence = root / ".superpowers/sdd/example/completion.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("evidence\n", encoding="utf-8")
            plan = plan_directory / "completed.md"
            for value in (
                str(evidence),
                ".superpowers/sdd/example/../example/completion.md",
            ):
                plan.write_text(
                    "# Test Plan\n\n"
                    "- **Governance:** active\n"
                    "- **Status:** completed\n"
                    "- **Date:** 2026-08-15\n"
                    "- **Roadmap child:** `T1.1`\n"
                    "- **Source specification:** `docs/superpowers/specs/example.md`\n"
                    "- **Approval:** 2026-08-15 — Jeff / tvproductions\n"
                    f"- **Completion evidence:** `{value}`\n",
                    encoding="utf-8",
                )
                with patch(__name__ + ".ROOT", root):
                    with self.assertRaises(AssertionError):
                        self.test_completed_active_plan_completion_evidence_is_inline_repo_relative_file()

    def test_completion_evidence_permits_markdown_link_inside_docs_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            plan_directory = root / "docs/superpowers/plans"
            plan_directory.mkdir(parents=True)
            evidence = root / "docs/evidence/completion.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("evidence\n", encoding="utf-8")
            (plan_directory / "completed.md").write_text(
                "# Test Plan\n\n"
                "- **Governance:** active\n"
                "- **Status:** completed\n"
                "- **Date:** 2026-08-15\n"
                "- **Roadmap child:** `T1.1`\n"
                "- **Source specification:** `docs/superpowers/specs/example.md`\n"
                "- **Approval:** 2026-08-15 — Jeff / tvproductions\n"
                "- **Completion evidence:** [completion](docs/evidence/completion.md)\n",
                encoding="utf-8",
            )
            with patch(__name__ + ".ROOT", root):
                self.test_completed_active_plan_completion_evidence_is_inline_repo_relative_file()

    def test_active_artifact_assignments_match_current_roadmap_children(self) -> None:
        active_specs = {
            path.name: metadata(path) for path in sorted((ROOT / "docs/superpowers/specs").glob("*.md")) if metadata(path).get("Governance") == "active"
        }
        active_plans = {
            path.name: metadata(path) for path in sorted((ROOT / "docs/superpowers/plans").glob("*.md")) if metadata(path).get("Governance") == "active"
        }
        self.assertEqual(
            {
                "2026-08-09-src-layout-migration-design.md",
                "2026-08-09-xplane-fdau-backlog-status-skill-design.md",
                "2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md",
                "2026-08-15-xplane-fdau-local-workflow-skills-design.md",
            },
            set(active_specs),
        )
        self.assertEqual(
            {
                "2026-08-09-src-layout-migration.md",
                "2026-08-15-xplane-fdau-backlog-authority-normalization.md",
            },
            set(active_plans),
        )
        self.assertEqual("`T1.1`", active_plans["2026-08-15-xplane-fdau-backlog-authority-normalization.md"]["Roadmap child"])

    def test_historical_artifacts_name_their_disposition(self) -> None:
        historical_paths = (
            ROOT / "docs/superpowers/specs/2026-08-08-xplane-fdr-core-design.md",
            ROOT / "docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md",
            ROOT / "docs/superpowers/plans/2026-08-08-xplane-fdr-core.md",
            ROOT / "docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md",
        )
        for path in historical_paths:
            self.assertIn(metadata(path)["Status"], {"completed", "superseded"})
            self.assertNotEqual("—", metadata(path)["Disposition"])


if __name__ == "__main__":
    unittest.main()
