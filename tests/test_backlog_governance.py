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
HANDOFF = ROOT / "HANDOFF.md"
D1_DESIGN = ROOT / "docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md"

MILESTONE_HEADER = ("Milestone", "Outcome")
CHILD_HEADER = ("Child", "Outcome", "Depends on")
STANDARDS_HEADER = ("Child", "Outcome", "Depends on", "External prerequisite")
GATE_HEADER = ("Gate", "Outcome", "Depends on")
BACKLOG_GATE_HEADER = ("Gate", "Outcome", "Gate state", "Prerequisites", "Evidence")
BOUNDARY_HEADER = ("Boundary", "Outcome", "Owner", "xplane-fdau handoff condition")
BACKLOG_BOUNDARY_HEADER = ("Boundary", "Owner", "xplane-fdau handoff condition")
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
EXPECTED_EPIC_MEMBERS = {
    "B1": ("B1.1",),
    "D1": ("D1.1", "D1.2", "D1.3"),
    "C1": ("C1.1", "C1.2", "C1.3", "C1.4", "C1.5"),
    "C2": ("C2.1", "C2.2", "C2.3", "C2.4"),
    "C3": ("C3.1", "C3.2", "C3.3", "C3.4", "C3.5"),
    "C4": ("C4.1", "C4.2", "C4.3", "C4.4"),
    "A1": ("A1.1", "A1.2", "A1.3", "A1.4", "A1.5", "A1.6", "A1.7", "A1.8", "A1.9"),
    "R1": ("R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7"),
    "P1": ("P1.1", "P1.2", "P1.3", "P1.4", "P1.5", "P1.6"),
    "S": ("S1.1", "S2.1", "S2.2", "S3.1", "S4.1"),
    "F1": ("F1.1", "F1.2", "F1.3", "F1.4", "F1.5", "F1.6"),
    "T1": ("T1.1", "T1.2", "T1.3", "T1.4", "T1.5", "T1.6"),
    "T2": ("T2.1", "T2.2"),
    "T3": ("T3.1",),
}
D1_SPECIFICATION = "[design](docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md)"
D1_OUTCOMES = {
    "D1.1": "Canonical C1–C4 design approval",
    "D1.2": "Acquisition, recording, projection, and pinning contract design",
    "D1.3": "Reviewed q4xpcc Phase 24A handoff",
}
D1_INVENTORY_ROWS = (
    (
        "`D1.1`",
        "Canonical C1–C4 design approval",
        "`specified`",
        "`T1.2`",
        D1_SPECIFICATION,
        "—",
        "0/4",
        "—",
        "—",
        "—",
    ),
    (
        "`D1.2`",
        "Acquisition, recording, projection, and pinning contract design",
        "`specified`",
        "`D1.1`",
        D1_SPECIFICATION,
        "—",
        "0/4",
        "—",
        "—",
        "—",
    ),
    (
        "`D1.3`",
        "Reviewed q4xpcc Phase 24A handoff",
        "`specified`",
        "`D1.2`",
        D1_SPECIFICATION,
        "—",
        "0/4",
        "—",
        "—",
        "—",
    ),
)
D1_GATE_STATEMENTS = {
    "D1.1": (
        "the canonical design has approved governance metadata and no unresolved placeholder, contradiction, ambiguity, or load-bearing review finding;",
        "canonical JSON, hashing, identity, provenance, measurement, binding, raw "
        "observation, sample, frame, clock/timing, validity, quality, schema, fixture, "
        "and Python/native conformance decisions are exact and versioned;",
        "ownership and dependency direction remain consistent with the approved scope "
        "amendment and distinguish FDAU acquisition quality from q4xpcc operational "
        "policy and findings; and",
        "the approved design is linked from `C1.1` through `C4.4`, and those children "
        "advance only to `specified`, with zero delivery gates satisfied and no "
        "implementation-plan, review, artifact, or release evidence.",
    ),
    "D1.2": (
        "one approved design fixes every A1/R1/P1 contract shape and policy needed by the four q4xpcc Phase 24A Slice 2 plans;",
        "every family has an exact identity/version boundary, owned fields, invariants, references, error outcomes, and intended future schema/fixture path;",
        "deployment, revision pinning, release-artifact hashes, delivered-file hashes, "
        "conformance, and no-divergent-subset proof are explicit without requiring a "
        "current release artifact; and",
        "independent review finds no unresolved load-bearing ambiguity, the approved "
        "contract-only design is recorded as binding architecture input for future A1, "
        "R1, and P1 specifications, and those implementation children remain `queued` "
        "with zero delivery gates satisfied and no implementation, artifact, or release "
        "claim.",
    ),
    "D1.3": (
        "D1.1 and D1.2 are verified with committed review evidence and no unresolved load-bearing finding;",
        "`HANDOFF.md` and the concise q4xpcc brief agree with the approved designs and distinguish design readiness from implementation and adoption;",
        "the brief is emitted from a clean committed state and identifies its exact local HEAD revision; and",
        "successful D1.3 verification makes the statusless `I1.0` handoff condition "
        "eligible to be reported as the next action without changing `I1.1`, `I1.2`, "
        "G1, release, push, tag, or publication authorization.",
    ),
}


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


def roadmap_epics() -> dict[str, tuple[str, ...]]:
    lines = read_text(ROADMAP).splitlines()
    epics: dict[str, tuple[str, ...]] = {}
    for index, line in enumerate(lines):
        match = re.fullmatch(r"#{2,3} ([A-Z][0-9]*) — .+ epic", line)
        if match is None:
            continue
        epic = match.group(1)
        table_start = next(
            candidate
            for candidate in range(index + 1, len(lines))
            if tuple(cell.strip() for cell in lines[candidate].strip().strip("|").split("|")) in {CHILD_HEADER, STANDARDS_HEADER}
        )
        members: list[str] = []
        for row in lines[table_start + 2 :]:
            if not row.startswith("|"):
                break
            members.append(identity(row.strip().strip("|").split("|")[0].strip()))
        epics[epic] = tuple(members)
    return epics


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


def acceptance_headings(path: Path) -> list[str]:
    lines = read_text(path).splitlines()
    starts = [lines.index(heading) + 1 for heading in ("## Acceptance criteria", "## Local-child acceptance gates") if heading in lines]
    if not starts:
        return []
    index = starts[0]
    headings: list[str] = []
    for line in lines[index:]:
        if line.startswith("## "):
            break
        if line.startswith("### "):
            headings.append(line.removeprefix("### "))
    return headings


def section_body(path: Path, heading: str, *, level: int) -> str:
    text = read_text(path)
    prefix = "#" * level
    heading_line = f"{prefix} {heading}\n"
    start = text.index(heading_line)
    body_start = start + len(heading_line)
    match = re.search(rf"^#{{1,{level}}} ", text[body_start:], re.MULTILINE)
    if match is None:
        return text[start:]
    return text[start : body_start + match.start()]


def normalized_list_items(body: str, marker: str) -> tuple[str, ...]:
    pattern = rf"^{re.escape(marker)}(.*?)(?=^{re.escape(marker)}|\Z)"
    return tuple(re.sub(r"\s+", " ", match).strip() for match in re.findall(pattern, body, re.MULTILINE | re.DOTALL))


def normalized_numbered_items(body: str) -> tuple[str, ...]:
    lead_in = "Its acceptance gates are:\n\n"
    numbered_block = body[body.index(lead_in) + len(lead_in) :].split("\n\n", 1)[0]
    return tuple(
        re.sub(r"\s+", " ", match).strip()
        for match in re.findall(
            r"^[0-9]+\. (.*?)(?=^[0-9]+\. |\Z)",
            numbered_block,
            re.MULTILINE | re.DOTALL,
        )
    )


class RoadmapAuthorityTests(unittest.TestCase):
    def test_epic_identities_and_membership_are_exact(self) -> None:
        self.assertEqual(EXPECTED_EPIC_MEMBERS, roadmap_epics())

    def test_node_kinds_are_explicit_complete_and_nonoverlapping(self) -> None:
        milestones = [identity(row[0]) for row in roadmap_rows(MILESTONE_HEADER)]
        epics = list(roadmap_epics())
        children = [identity(row[0]) for row in roadmap_child_rows()]
        gates = [identity(row[0]) for row in roadmap_rows(GATE_HEADER)]
        boundaries = [identity(row[0]) for row in roadmap_rows(BOUNDARY_HEADER)]

        self.assertEqual(["M0"], milestones)
        self.assertEqual(["G1"], gates)
        self.assertEqual(["I1.0", "I1.1", "I1.2", "I2.1", "F2.1"], boundaries)
        self.assertEqual(
            [
                "q4xpcc Phase 24A specification and plan reconciliation",
                "q4xpcc contract-model and fixture adoption",
                "q4xpcc live XPLM acquisition adoption",
                "Development/corroboration adapter adoption",
                "Approved FOQA program governance and claims",
            ],
            [row[1] for row in roadmap_rows(BOUNDARY_HEADER)],
        )
        self.assertEqual(64, len(children))
        self.assertEqual(64, len(set(children)))
        kinds = [set(milestones), set(epics), set(children), set(gates), set(boundaries)]
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
        self.assertEqual("`C4.4`, `R1.7`", by_child["F1.1"])
        self.assertEqual("`T2.1`", by_child["T2.2"])
        self.assertEqual("`T2.2`, `T3.1`", by_child["B1.1"])
        self.assertEqual("`T1.2`", by_child.get("D1.1"))
        self.assertEqual("`D1.1`", by_child.get("D1.2"))
        self.assertEqual("`D1.2`", by_child.get("D1.3"))

    def test_q4xpcc_readiness_boundaries_are_exact_and_distinct(self) -> None:
        roadmap_boundaries = {identity(row[0]): (row[2], row[3]) for row in roadmap_rows(BOUNDARY_HEADER)}
        self.assertEqual(
            {
                "I1.0": (
                    "q4xpcc",
                    "Phase 24A specification and plan reconciliation may begin after `D1.3`.",
                ),
                "I1.1": (
                    "q4xpcc",
                    "Contract-model and fixture adoption may begin after `C4.4`.",
                ),
                "I1.2": (
                    "q4xpcc",
                    "Live XPLM acquisition adoption may begin after `A1.9`.",
                ),
            },
            {boundary: roadmap_boundaries.get(boundary) for boundary in ("I1.0", "I1.1", "I1.2")},
        )

        backlog_boundaries = {identity(row[0]): (row[1], row[2]) for row in table_rows(read_text(BACKLOG), BACKLOG_BOUNDARY_HEADER)}
        self.assertEqual(
            {
                "I1.0": (
                    "q4xpcc",
                    "Phase 24A specification and plan reconciliation may begin after `D1.3`.",
                ),
                "I1.1": ("q4xpcc", "Contract/fixture adoption may begin after `C4.4`."),
                "I1.2": ("q4xpcc", "Live XPLM acquisition adoption may begin after `A1.9`."),
            },
            {boundary: backlog_boundaries.get(boundary) for boundary in ("I1.0", "I1.1", "I1.2")},
        )

    def test_roadmap_has_no_mutable_child_status_column(self) -> None:
        roadmap = read_text(ROADMAP)
        self.assertNotIn("| Child | Outcome | Status |", roadmap)
        self.assertIn("`BACKLOG.md` is the durable Superpowers entry point", roadmap)


class BacklogAuthorityTests(unittest.TestCase):
    def test_acceptance_headings_match_exact_roadmap_outcomes(self) -> None:
        outcomes = {identity(row[0]): row[1] for row in roadmap_child_rows()}
        governed = [identity(row[0]) for row in table_rows(read_text(BACKLOG), INVENTORY_HEADER) if row[6] != "—"]
        self.assertEqual(
            [f"{child} — {outcomes[child]}" for child in governed],
            acceptance_headings(BACKLOG),
        )

    def test_current_position_has_one_exact_selection_line(self) -> None:
        backlog = read_text(BACKLOG)
        selection_lines = [line for line in backlog.splitlines() if line.startswith("- Active child:")]
        self.assertEqual(["- Active child: `D1.1`."], selection_lines)
        self.assertNotIn("Active child slice:", backlog)

    def test_inventory_matches_every_roadmap_child_once_in_order(self) -> None:
        roadmap = roadmap_child_rows()
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        self.assertEqual(64, len(inventory))
        self.assertEqual(
            [(identity(row[0]), row[1], row[2]) for row in roadmap],
            [(identity(row[0]), row[1], row[3]) for row in inventory],
        )

    def test_d1_inventory_rows_lock_complete_initial_lifecycle(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)

        self.assertEqual(
            D1_INVENTORY_ROWS,
            tuple(row for row in inventory if identity(row[0]).startswith("D1.")),
        )

    def test_d1_backlog_and_design_lock_all_four_acceptance_gates(self) -> None:
        for child, expected in D1_GATE_STATEMENTS.items():
            with self.subTest(child=child):
                heading = f"{child} — {D1_OUTCOMES[child]}"
                backlog_body = section_body(BACKLOG, heading, level=3)
                design_body = section_body(D1_DESIGN, heading, level=2)
                self.assertEqual(expected, normalized_list_items(backlog_body, "- [ ] "))
                self.assertEqual(expected, normalized_numbered_items(design_body))

    def test_handoff_orders_d1_verification_before_external_thresholds(self) -> None:
        handoff = re.sub(r"\s+", " ", read_text(HANDOFF))
        sequence = (
            "execute the selected `D1.1` canonical-design approval",
            "execute `D1.2` contract-only A1/R1/P1 design",
            "execute and verify `D1.3` reviewed consumer brief",
            "successful D1.3 verification makes `I1.0` eligible as the next reportable action",
        )
        for statement in sequence:
            self.assertIn(statement, handoff)
        positions = tuple(handoff.index(statement) for statement in sequence)
        self.assertEqual(tuple(sorted(positions)), positions)
        self.assertIn(
            "`I1.0` permits Phase 24A specification and plan reconciliation only after successful `D1.3` verification.",
            handoff,
        )
        self.assertIn(
            "`I1.1` permits delivered contract-model, schema, fixture, and runtime adoption only after `C4.4`.",
            handoff,
        )
        self.assertIn(
            "`I1.2` permits live XPLM acquisition adoption only after `A1.9`.",
            handoff,
        )

    def test_inventory_excludes_nonchildren_and_range_rows(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        inventory_ids = [identity(row[0]) for row in inventory]
        excluded = {"M0", "G1", "I1.0", "I1.1", "I1.2", "I2.1", "F2.1"}
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
            self.assertTrue(
                spec == "—"
                or spec.startswith("[design](docs/superpowers/specs/")
                or spec == "[architecture](docs/architecture/xplane_fdau_core_scope_amendment.md)",
                child,
            )
            self.assertTrue(
                plan == "—" or plan.startswith("[draft plan](docs/superpowers/plans/") or plan.startswith("[plan](docs/superpowers/plans/"),
                child,
            )
            self.assertRegex(gates, r"^(?:—|[0-9]+/[0-9]+)$")
            if status in {"`reviewed`", "`verified`"}:
                self.assertRegex(review, r"^\[review\]\(\.superpowers/sdd/.+/review\.md\)$", child)
            else:
                self.assertEqual("—", review)
            if status == "`blocked`":
                self.assertEqual("`queued`", resume)
                self.assertNotEqual("—", reason)
            else:
                self.assertEqual("—", resume)
                self.assertEqual("—", reason)

    def test_t1_1_is_verified_with_accepted_review_evidence(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        row = next(row for row in inventory if identity(row[0]) == "T1.1")
        review_link = "[review](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/review.md)"
        self.assertEqual("`verified`", row[2])
        self.assertEqual(review_link, row[7])

        evidence_path = ROOT / ".superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/review.md"
        self.assertTrue(evidence_path.is_file())
        self.assertEqual(
            {
                "Child": "`T1.1`",
                "Gate": "—",
                "Kind": "review",
                "Result": "accepted",
                "Date": "2026-08-16",
                "Subject": "Independent T1.1 implementation review",
            },
            metadata(evidence_path),
        )

    def test_t1_2_is_verified_with_accepted_review_evidence(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        row = next(row for row in inventory if identity(row[0]) == "T1.2")
        review_link = "[review](.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/review.md)"
        self.assertEqual("`verified`", row[2])
        self.assertEqual(review_link, row[7])

        evidence_path = ROOT / ".superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/review.md"
        self.assertTrue(evidence_path.is_file())
        self.assertEqual(
            {
                "Child": "`T1.2`",
                "Gate": "—",
                "Kind": "review",
                "Result": "accepted",
                "Date": "2026-08-23",
                "Subject": "Independent T1.2 implementation review",
            },
            metadata(evidence_path),
        )

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

    def test_release_gate_dashboard_matches_roadmap_outcomes_and_prerequisites(self) -> None:
        roadmap = roadmap_rows(GATE_HEADER)
        backlog = table_rows(read_text(BACKLOG), BACKLOG_GATE_HEADER)
        self.assertEqual(
            [(identity(row[0]), row[1], row[2]) for row in roadmap],
            [(identity(row[0]), row[1], row[3]) for row in backlog],
        )

    def test_all_child_gate_headings_are_within_the_unified_section(self) -> None:
        backlog = read_text(BACKLOG)
        section_start = backlog.index("## Local-child acceptance gates")
        section_end = backlog.index("\n## Release-gate dashboard", section_start)
        for heading in re.finditer(r"^### [A-Z][0-9]+\.[0-9]+ — ", backlog, re.MULTILINE):
            self.assertGreater(heading.start(), section_start)
            self.assertLess(heading.start(), section_end)


class GovernanceArtifactTests(unittest.TestCase):
    def test_active_design_acceptance_headings_match_exact_roadmap_outcomes(self) -> None:
        outcomes = {identity(row[0]): row[1] for row in roadmap_child_rows()}
        for path in sorted((ROOT / "docs/superpowers/specs").glob("*.md")):
            values = metadata(path)
            if values.get("Governance") != "active":
                continue
            children = re.findall(r"`([A-Z][0-9]+\.[0-9]+)`", values["Roadmap children"])
            self.assertTrue(
                all(child in outcomes for child in children),
                f"{path}: roadmap is missing an active design child",
            )
            self.assertEqual(
                [f"{child} — {outcomes[child]}" for child in children],
                acceptance_headings(path),
                path,
            )

    def test_active_design_epic_assignments_match_roadmap_contract(self) -> None:
        expected = {
            "2026-08-09-src-layout-migration-design.md": ("`B1`", ("B1.1",)),
            "2026-08-09-xplane-fdau-backlog-status-skill-design.md": (
                "`T1`",
                EXPECTED_EPIC_MEMBERS["T1"],
            ),
            "2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md": (
                "`C1`",
                EXPECTED_EPIC_MEMBERS["C1"] + EXPECTED_EPIC_MEMBERS["C2"] + EXPECTED_EPIC_MEMBERS["C3"] + EXPECTED_EPIC_MEMBERS["C4"],
            ),
            "2026-08-15-xplane-fdau-local-workflow-skills-design.md": (
                "`T2`",
                EXPECTED_EPIC_MEMBERS["T2"] + EXPECTED_EPIC_MEMBERS["T3"],
            ),
            "2026-08-22-q4xpcc-contract-handoff-readiness-design.md": (
                "`D1`",
                EXPECTED_EPIC_MEMBERS["D1"],
            ),
        }
        actual: dict[str, tuple[str, tuple[str, ...]]] = {}
        for path in sorted((ROOT / "docs/superpowers/specs").glob("*.md")):
            values = metadata(path)
            if values.get("Governance") != "active":
                continue
            children = tuple(re.findall(r"`([A-Z][0-9]+\.[0-9]+)`", values["Roadmap children"]))
            actual[path.name] = (values["Roadmap epic"], children)
        self.assertEqual(expected, actual)
        self.assertIn(
            "The canonical measurement-contract design is explicitly a cross-epic design "
            "spanning `C1`, `C2`, `C3`, and `C4`; its governance metadata is anchored by "
            "`Roadmap epic: C1`.",
            re.sub(r"\s+", " ", read_text(ROADMAP)),
        )

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
                "2026-08-22-q4xpcc-contract-handoff-readiness-design.md",
            },
            set(active_specs),
        )
        self.assertEqual(
            {
                "2026-08-09-src-layout-migration.md",
                "2026-08-15-xplane-fdau-backlog-authority-normalization.md",
                "2026-08-16-xplane-fdau-typed-backlog-status-reporting.md",
            },
            set(active_plans),
        )
        self.assertEqual("`T1.1`", active_plans["2026-08-15-xplane-fdau-backlog-authority-normalization.md"]["Roadmap child"])
        self.assertEqual("`T1.2`", active_plans["2026-08-16-xplane-fdau-typed-backlog-status-reporting.md"]["Roadmap child"])

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
