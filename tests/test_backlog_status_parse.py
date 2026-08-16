from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
FIXTURE = ROOT / "tests/fixtures/backlog_status/valid"
sys.path.insert(0, str(SCRIPTS))

from backlog.parse import (  # noqa: E402  # ty: ignore[unresolved-import]
    MarkdownParseError,
    parse_artifacts,
    parse_backlog,
    parse_repository,
    parse_roadmap,
)


class ManagedMarkdownParseTests(unittest.TestCase):
    def copy_fixture_root(self) -> Path:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        shutil.copytree(FIXTURE, temporary, dirs_exist_ok=True)
        return temporary

    def copy_backlog(self, *, replace: tuple[str, str]) -> Path:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        path = temporary / "BACKLOG.md"
        original, replacement = replace
        path.write_text(
            (FIXTURE / "BACKLOG.md").read_text(encoding="utf-8").replace(original, replacement, 1),
            encoding="utf-8",
        )
        return path

    def copy_roadmap(self, *, replace: tuple[str, str]) -> Path:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        path = temporary / "ROADMAP.md"
        original, replacement = replace
        path.write_text(
            (FIXTURE / "ROADMAP.md").read_text(encoding="utf-8").replace(original, replacement, 1),
            encoding="utf-8",
        )
        return path

    def test_valid_fixture_parses_into_typed_roadmap_and_backlog(self) -> None:
        roadmap = parse_roadmap(FIXTURE / "ROADMAP.md")
        backlog = parse_backlog(FIXTURE / "BACKLOG.md")
        self.assertEqual(("M0",), tuple(node.id for node in roadmap.milestones))
        self.assertEqual(("T1",), tuple(node.id for node in roadmap.epics))
        self.assertEqual(("T1.1", "T1.2"), tuple(node.id for node in roadmap.local_children))
        self.assertEqual(("G1",), tuple(node.id for node in roadmap.release_gates))
        self.assertEqual(("I1.1",), tuple(node.id for node in roadmap.external_boundaries))
        self.assertEqual("Fixture contract adoption", roadmap.external_boundaries[0].title)
        self.assertEqual("Fixture consumer", roadmap.external_boundaries[0].owner)
        self.assertEqual("Adoption begins after `T1.2`.", roadmap.external_boundaries[0].handoff_condition)
        self.assertIsNone(backlog.active_child)
        self.assertEqual((1, 0), tuple(child.gates.satisfied for child in backlog.children))
        self.assertEqual((1, 1), tuple(child.gates.total for child in backlog.children))
        self.assertEqual("Frozen contract is verified and remains explicit.", backlog.children[0].gates.items[0].statement)
        self.assertEqual(("waiting",), tuple(gate.state for gate in backlog.release_gates))

    def test_malformed_selection_reports_exact_line(self) -> None:
        path = self.copy_backlog(replace=("- Active child: —.", "- Active child: T1.2."))
        with self.assertRaisesRegex(MarkdownParseError, r"BACKLOG.md:[0-9]+: active child"):
            parse_backlog(path)

    def test_malformed_inventory_cell_count_fails_closed(self) -> None:
        path = self.copy_backlog(
            replace=(
                "| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | "
                "`T1.1` | [design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — | — | — |",
                "| `T1.2` |",
            )
        )
        with self.assertRaisesRegex(MarkdownParseError, "inventory row requires 10 cells"):
            parse_backlog(path)

    def test_malformed_status_link_gate_and_identity_fail_with_context(self) -> None:
        replacements = (
            ("`specified`", "`unknown`", "invalid child status"),
            ("[design](docs/", "[design](../", "repository-relative link"),
            ("- [ ] Frozen", "- [?] Frozen", "gate task item"),
            ("`T1.2`", "T1.2", "identity cell"),
        )
        for old, new, message in replacements:
            with self.subTest(new=new):
                path = self.copy_backlog(replace=(old, new))
                with self.assertRaisesRegex(MarkdownParseError, message):
                    parse_backlog(path)

    def test_every_managed_repository_path_family_rejects_non_relative_targets(self) -> None:
        link_families = (
            ("specification link", "BACKLOG.md", "[design](docs/superpowers/specs/t1-design.md)", "design"),
            ("plan link", "BACKLOG.md", "[plan](docs/superpowers/plans/t1-1.md)", "plan"),
            ("review link", "BACKLOG.md", "[review](.superpowers/sdd/t1-1/review.md)", "review"),
            ("gate evidence link", "BACKLOG.md", "[verification](.superpowers/sdd/t1-1/gate-1.md)", "verification"),
            (
                "release evidence link",
                "BACKLOG.md",
                "| `G1` | Canonical vertical-slice reconciliation | `waiting` | `T1.2` | — |",
                "release-evidence",
            ),
        )
        metadata_families = (
            (
                "source specification value",
                "docs/superpowers/plans/t1-1.md",
                "`docs/superpowers/specs/t1-design.md`",
            ),
            (
                "completion evidence value",
                "docs/superpowers/plans/t1-1.md",
                "`.superpowers/sdd/t1-1/completion.md`",
            ),
        )
        invalid_targets = (
            "C:/absolute.md",
            "/absolute.md",
            "https://example.invalid/proof.md",
            "mailto:owner@example.invalid",
            "../proof.md",
            "docs/../proof.md",
            r"docs\proof.md",
            "docs//proof.md",
        )
        for label, relative, original, link_label in link_families:
            for target in invalid_targets:
                with self.subTest(family=label, target=target):
                    root = self.copy_fixture_root()
                    path = root / relative
                    text = path.read_text(encoding="utf-8")
                    if label == "release evidence link":
                        replacement = original[:-3] + f"[{link_label}]({target}) |"
                    else:
                        replacement = f"[{link_label}]({target})"
                    path.write_text(text.replace(original, replacement, 1), encoding="utf-8")
                    with self.assertRaisesRegex(MarkdownParseError, "repository-relative"):
                        parse_repository(root)
        for label, relative, original in metadata_families:
            for target in invalid_targets:
                with self.subTest(family=label, target=target):
                    root = self.copy_fixture_root()
                    path = root / relative
                    path.write_text(path.read_text(encoding="utf-8").replace(original, f"`{target}`", 1), encoding="utf-8")
                    with self.assertRaisesRegex(MarkdownParseError, "repository-relative"):
                        parse_repository(root)

    def test_duplicate_active_selection_is_a_syntax_ambiguity(self) -> None:
        path = self.copy_backlog(replace=("- Active child: —.", "- Active child: —.\n- Active child: —."))
        with self.assertRaisesRegex(MarkdownParseError, "exactly one managed active child"):
            parse_backlog(path)

    def test_invalid_gate_count_and_unchecked_evidence_fail_closed(self) -> None:
        for old, new, message in (
            ("0/1", "0/x", "invalid gate count"),
            ("- [ ] Frozen parser remains open.", "- [ ] Frozen parser remains open. — Evidence: [proof](proof.md)", "unchecked gate"),
        ):
            with self.subTest(new=new):
                path = self.copy_backlog(replace=(old, new))
                with self.assertRaisesRegex(MarkdownParseError, message):
                    parse_backlog(path)

    def test_displayed_gate_counts_are_independent_of_parsed_gate_items(self) -> None:
        path = self.copy_backlog(replace=("| — | 0/1 | — | — | — |", "| — | 7/9 | — | — | — |"))

        child = next(item for item in parse_backlog(path).children if item.id == "T1.2")

        self.assertEqual((7, 9), (child.gates.satisfied, child.gates.total))
        self.assertEqual(1, len(child.gates.items))
        self.assertFalse(child.gates.items[0].satisfied)

    def test_malformed_roadmap_separator_fails_closed(self) -> None:
        path = self.copy_roadmap(replace=("| --- | --- |", "| --- | text |"))
        with self.assertRaisesRegex(MarkdownParseError, "managed table separator"):
            parse_roadmap(path)

    def test_managed_table_separator_cell_count_matches_every_header_family(self) -> None:
        roadmap = (FIXTURE / "ROADMAP.md").read_text(encoding="utf-8")
        standards = (
            "## S — Standards implementation epic\n\n"
            "| Child | Outcome | Depends on | External prerequisite |\n"
            "| --- | --- | --- | --- |\n"
            "| `S1.1` | Standards baseline | `T1.2` | Licensed source |\n\n"
        )
        roadmap_with_standards = roadmap.replace("## Release gates", standards + "## Release gates", 1)
        cases = (
            ("milestone", roadmap, "| Milestone | Outcome |", "| --- | --- |", parse_roadmap),
            ("child", roadmap, "| Child | Outcome | Depends on |", "| --- | --- | --- |", parse_roadmap),
            (
                "standards",
                roadmap_with_standards,
                "| Child | Outcome | Depends on | External prerequisite |",
                "| --- | --- | --- | --- |",
                parse_roadmap,
            ),
            ("release gate", roadmap, "| Gate | Outcome | Depends on |", "| --- | --- | --- |", parse_roadmap),
            (
                "external boundary",
                roadmap,
                "| Boundary | Outcome | Owner | xplane-fdau handoff condition |",
                "| --- | --- | --- | --- |",
                parse_roadmap,
            ),
            (
                "inventory",
                (FIXTURE / "BACKLOG.md").read_text(encoding="utf-8"),
                "| Child | Outcome | Status | Depends on | Spec | Plan | Gates | Review | Resume | Reason |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                parse_backlog,
            ),
            (
                "release dashboard",
                (FIXTURE / "BACKLOG.md").read_text(encoding="utf-8"),
                "| Gate | Outcome | Gate state | Prerequisites | Evidence |",
                "| --- | --- | --- | --- | --- |",
                parse_backlog,
            ),
        )
        for label, document, header, delimiter, parser in cases:
            for malformed in (delimiter.replace(" | --- |", " |", 1), delimiter[:-1] + "| --- |"):
                with self.subTest(label=label, malformed=malformed):
                    temporary = Path(tempfile.mkdtemp())
                    self.addCleanup(shutil.rmtree, temporary)
                    filename = "BACKLOG.md" if parser is parse_backlog else "ROADMAP.md"
                    path = temporary / filename
                    path.write_text(document.replace(f"{header}\n{delimiter}", f"{header}\n{malformed}", 1), encoding="utf-8")
                    with self.assertRaisesRegex(MarkdownParseError, f"invalid managed table separator for {label}"):
                        parser(path)

    def test_managed_rows_reject_doubled_outer_delimiters(self) -> None:
        roadmap = (FIXTURE / "ROADMAP.md").read_text(encoding="utf-8")
        standards = (
            "## S — Standards implementation epic\n\n"
            "| Child | Outcome | Depends on | External prerequisite |\n"
            "| --- | --- | --- | --- |\n"
            "| `S1.1` | Standards baseline | `T1.2` | Licensed source |\n\n"
        )
        roadmap_with_standards = roadmap.replace("## Release gates", standards + "## Release gates", 1)
        backlog = (FIXTURE / "BACKLOG.md").read_text(encoding="utf-8")
        cases = (
            ("milestone", roadmap, "| `M0` | Frozen migration baseline |", parse_roadmap),
            (
                "child",
                roadmap,
                "| `T1.1` | Markdown authority contract and explicit inventory normalization | `M0` |",
                parse_roadmap,
            ),
            (
                "standards",
                roadmap_with_standards,
                "| `S1.1` | Standards baseline | `T1.2` | Licensed source |",
                parse_roadmap,
            ),
            (
                "release gate",
                roadmap,
                "| `G1` | Canonical vertical-slice reconciliation | `T1.2` |",
                parse_roadmap,
            ),
            (
                "external boundary",
                roadmap,
                "| `I1.1` | Fixture contract adoption | Fixture consumer | Adoption begins after `T1.2`. |",
                parse_roadmap,
            ),
            (
                "inventory",
                backlog,
                "| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | "
                "[design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — | — | — |",
                parse_backlog,
            ),
            (
                "release dashboard",
                backlog,
                "| `G1` | Canonical vertical-slice reconciliation | `waiting` | `T1.2` | — |",
                parse_backlog,
            ),
        )
        for label, document, row, parser in cases:
            for malformed in ("|" + row, row + "|", "|" + row + "|"):
                with self.subTest(label=label, malformed=malformed):
                    temporary = Path(tempfile.mkdtemp())
                    self.addCleanup(shutil.rmtree, temporary)
                    filename = "BACKLOG.md" if parser is parse_backlog else "ROADMAP.md"
                    path = temporary / filename
                    path.write_text(document.replace(row, malformed, 1), encoding="utf-8")
                    with self.assertRaisesRegex(MarkdownParseError, rf"{label} row requires [0-9]+ cells"):
                        parser(path)

    def test_table_without_separator_reports_parse_context(self) -> None:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        path = temporary / "ROADMAP.md"
        path.write_text("## Milestones\n| Milestone | Outcome |", encoding="utf-8")
        with self.assertRaisesRegex(MarkdownParseError, "invalid managed table separator"):
            parse_roadmap(path)

    def test_empty_markdown_reports_context_instead_of_index_error(self) -> None:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        path = temporary / "ROADMAP.md"
        path.write_text("", encoding="utf-8")
        with self.assertRaisesRegex(MarkdownParseError, r"ROADMAP.md:1: requires exactly one heading"):
            parse_roadmap(path)

    def test_truncated_heading_without_table_reports_context(self) -> None:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        path = temporary / "ROADMAP.md"
        path.write_text("## Milestones", encoding="utf-8")
        with self.assertRaisesRegex(MarkdownParseError, r"ROADMAP.md:1: requires exactly one milestone table header"):
            parse_roadmap(path)

    def test_single_hash_epic_heading_is_not_managed_syntax(self) -> None:
        path = self.copy_roadmap(replace=("## T1 — Repository governance tooling epic", "# T1 — Repository governance tooling epic"))
        with self.assertRaisesRegex(MarkdownParseError, "invalid managed epic heading"):
            parse_roadmap(path)

    def test_gate_heading_outside_managed_section_is_not_accepted(self) -> None:
        path = self.copy_backlog(replace=("## Local-child acceptance gates", "## Notes"))
        with self.assertRaisesRegex(MarkdownParseError, "requires exactly one heading: ## Local-child acceptance gates"):
            parse_backlog(path)

    def test_whitespace_only_gate_statement_fails_closed(self) -> None:
        path = self.copy_backlog(replace=("- [ ] Frozen parser remains open.", "- [ ] " + "   "))
        with self.assertRaisesRegex(MarkdownParseError, "gate task item requires a statement"):
            parse_backlog(path)

    def test_standards_row_requires_external_prerequisite_cell(self) -> None:
        path = self.copy_roadmap(
            replace=(
                "## Release gates",
                "## S — Standards implementation epic\n\n"
                "| Child | Outcome | Depends on | External prerequisite |\n"
                "| --- | --- | --- | --- |\n"
                "| `S1.1` | Standards baseline | `T1.2` |\n\n## Release gates",
            )
        )
        with self.assertRaisesRegex(MarkdownParseError, "standards row requires 4 cells"):
            parse_roadmap(path)

    def test_governance_artifacts(self) -> None:
        artifacts = parse_artifacts(FIXTURE)
        self.assertEqual(
            ("docs/superpowers/specs/t1-design.md",),
            tuple(artifact.path for artifact in artifacts.specifications),
        )
        specification = artifacts.specifications[0]
        self.assertEqual("approved", specification.status)
        self.assertEqual("T1", specification.epic)
        self.assertEqual(("T1.1", "T1.2"), specification.children)
        self.assertEqual("2026-08-15 — Fixture owner", specification.approval)
        self.assertEqual(
            ("docs/superpowers/plans/t1-1.md",),
            tuple(artifact.path for artifact in artifacts.plans),
        )
        plan = artifacts.plans[0]
        self.assertEqual("completed", plan.status)
        self.assertEqual("T1.1", plan.child)
        self.assertEqual("docs/superpowers/specs/t1-design.md", plan.source_specification)
        self.assertEqual(".superpowers/sdd/t1-1/completion.md", plan.completion_evidence)
        self.assertEqual(
            (
                "docs/superpowers/plans/historical-plan.md",
                "docs/superpowers/specs/historical-design.md",
            ),
            tuple(artifact.path for artifact in artifacts.historical),
        )
        self.assertEqual(
            ("Completed fixture plan.", "Superseded fixture design."),
            tuple(artifact.disposition for artifact in artifacts.historical),
        )
        snapshot = parse_repository(FIXTURE)
        self.assertEqual(FIXTURE.resolve(), snapshot.root)
        self.assertEqual(artifacts, snapshot.artifacts)

    def test_em_dash_approval_and_completion_evidence_parse_as_none(self) -> None:
        root = self.copy_fixture_root()
        design = root / "docs/superpowers/specs/t1-design.md"
        design.write_text(
            design.read_text(encoding="utf-8").replace("2026-08-15 — Fixture owner", "—", 1),
            encoding="utf-8",
        )
        plan = root / "docs/superpowers/plans/t1-1.md"
        text = plan.read_text(encoding="utf-8")
        text = text.replace("- **Approval:** 2026-08-15 — Fixture owner", "- **Approval:** —", 1)
        text = text.replace("- **Completion evidence:** `.superpowers/sdd/t1-1/completion.md`", "- **Completion evidence:** —", 1)
        plan.write_text(text, encoding="utf-8")

        artifacts = parse_artifacts(root)

        self.assertIsNone(artifacts.specifications[0].approval)
        self.assertIsNone(artifacts.plans[0].approval)
        self.assertIsNone(artifacts.plans[0].completion_evidence)

    def test_governance_artifact_accepts_one_blank_line_between_title_and_metadata(self) -> None:
        artifacts = parse_artifacts(FIXTURE)

        self.assertEqual("approved", artifacts.specifications[0].status)
        self.assertEqual("T1", artifacts.specifications[0].epic)
        self.assertEqual(("T1.1", "T1.2"), artifacts.specifications[0].children)

    def test_governance_artifact_requires_exactly_one_blank_before_metadata(self) -> None:
        mutations = (
            ("# Fixture T1 Design\n\n", "# Fixture T1 Design\n", 2),
            ("# Fixture T1 Design\n\n", "# Fixture T1 Design\n\n\n", 3),
            ("# Fixture T1 Design\n\n", "# Fixture T1 Design\n\nThis is not metadata.\n", 3),
        )
        for original, replacement, expected_line in mutations:
            with self.subTest(replacement=replacement):
                root = self.copy_fixture_root()
                design = root / "docs/superpowers/specs/t1-design.md"
                design.write_text(design.read_text(encoding="utf-8").replace(original, replacement, 1), encoding="utf-8")
                with self.assertRaisesRegex(MarkdownParseError, rf"t1-design.md:{expected_line}: missing Governance metadata"):
                    parse_artifacts(root)

    def test_governance_artifact_metadata_fails_closed(self) -> None:
        malformed = (
            ("missing-governance.md", "missing Governance metadata"),
            ("active-design-missing-owner.md", "active design metadata keys"),
            ("active-plan-multiple-child.md", "Roadmap child requires one identity"),
            ("historical-missing-disposition.md", "historical metadata keys"),
            ("active-design-invalid-status.md", "invalid active design status"),
            ("active-plan-invalid-status.md", "invalid active plan status"),
        )
        for filename, message in malformed:
            with self.subTest(filename=filename):
                root = self.copy_fixture_root()
                path = root / "docs/superpowers/specs" / filename
                if "plan" in filename:
                    path = root / "docs/superpowers/plans" / filename
                path.write_text("# Invalid\n\n", encoding="utf-8")
                if filename == "missing-governance.md":
                    path.write_text("# Invalid\n\n- **Status:** approved\n", encoding="utf-8")
                elif filename == "active-design-missing-owner.md":
                    path.write_text(
                        "# Invalid\n\n- **Governance:** active\n- **Status:** approved\n"
                        "- **Date:** 2026-08-16\n- **Roadmap epic:** `T1`\n"
                        "- **Roadmap children:** `T1.1`\n- **Approval:** —\n",
                        encoding="utf-8",
                    )
                elif filename == "active-plan-multiple-child.md":
                    path.write_text(
                        "# Invalid\n\n- **Governance:** active\n- **Status:** draft\n"
                        "- **Date:** 2026-08-16\n- **Roadmap child:** `T1.1`, `T1.2`\n"
                        "- **Source specification:** `docs/superpowers/specs/t1-design.md`\n"
                        "- **Approval:** —\n- **Completion evidence:** —\n",
                        encoding="utf-8",
                    )
                elif filename == "historical-missing-disposition.md":
                    path.write_text("# Invalid\n\n- **Governance:** historical\n- **Status:** completed\n", encoding="utf-8")
                elif filename == "active-design-invalid-status.md":
                    path.write_text(
                        "# Invalid\n\n- **Governance:** active\n- **Status:** unknown\n"
                        "- **Date:** 2026-08-16\n- **Decision owner:** Fixture owner\n"
                        "- **Roadmap epic:** `T1`\n- **Roadmap children:** `T1.1`\n- **Approval:** —\n",
                        encoding="utf-8",
                    )
                else:
                    path.write_text(
                        "# Invalid\n\n- **Governance:** active\n- **Status:** unknown\n"
                        "- **Date:** 2026-08-16\n- **Roadmap child:** `T1.1`\n"
                        "- **Source specification:** `docs/superpowers/specs/t1-design.md`\n"
                        "- **Approval:** —\n- **Completion evidence:** —\n",
                        encoding="utf-8",
                    )
                with self.assertRaisesRegex(MarkdownParseError, message):
                    parse_artifacts(root)

    def test_metadata_key_shape_reports_the_first_differing_field_line(self) -> None:
        mutations = (
            ("- **Decision owner:** Fixture owner\n", "- **Owner:** Fixture owner\n", 6),
            (
                "- **Status:** approved\n- **Date:** 2026-08-15\n",
                "- **Status:** approved\n- **Unexpected:** value\n- **Date:** 2026-08-15\n",
                5,
            ),
            ("- **Decision owner:** Fixture owner\n", "", 6),
            ("- **Approval:** 2026-08-15 — Fixture owner\n", "", 9),
        )
        for original, replacement, expected_line in mutations:
            with self.subTest(replacement=replacement):
                root = self.copy_fixture_root()
                design = root / "docs/superpowers/specs/t1-design.md"
                design.write_text(design.read_text(encoding="utf-8").replace(original, replacement, 1), encoding="utf-8")
                with self.assertRaises(MarkdownParseError) as raised:
                    parse_artifacts(root)
                self.assertEqual(expected_line, raised.exception.line)
                self.assertIn("active design metadata keys", raised.exception.message)

    def test_active_design_requires_epic_and_local_child_identity_families(self) -> None:
        malformed = (
            ("**Roadmap epic:** `T1`", "**Roadmap epic:** `T1.1`", "Roadmap epic requires one epic identity"),
            (
                "**Roadmap children:** `T1.1`, `T1.2`",
                "**Roadmap children:** `T1`",
                "Roadmap children requires local-child identities",
            ),
            (
                "**Roadmap children:** `T1.1`, `T1.2`",
                "**Roadmap children:** `T1.1`, `T1`",
                "Roadmap children requires local-child identities",
            ),
        )
        for old, new, message in malformed:
            with self.subTest(new=new):
                root = self.copy_fixture_root()
                design = root / "docs/superpowers/specs/t1-design.md"
                design.write_text(design.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
                with self.assertRaisesRegex(MarkdownParseError, message):
                    parse_artifacts(root)

    def test_active_design_accepts_letter_only_epic_with_dotted_children(self) -> None:
        root = self.copy_fixture_root()
        design = root / "docs/superpowers/specs/t1-design.md"
        text = design.read_text(encoding="utf-8")
        text = text.replace("**Roadmap epic:** `T1`", "**Roadmap epic:** `S`", 1)
        text = text.replace("**Roadmap children:** `T1.1`, `T1.2`", "**Roadmap children:** `S1.1`, `S1.2`", 1)
        design.write_text(text, encoding="utf-8")

        specification = next(item for item in parse_artifacts(root).specifications if item.path.endswith("t1-design.md"))

        self.assertEqual("S", specification.epic)
        self.assertEqual(("S1.1", "S1.2"), specification.children)


if __name__ == "__main__":
    unittest.main()
