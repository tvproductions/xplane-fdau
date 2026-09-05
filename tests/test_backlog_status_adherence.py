from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
sys.path.insert(0, str(SCRIPTS))

from backlog.audit import load_audit  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.adherence import adherence_findings  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.parse_sources import parse_roadmap_sources  # noqa: E402  # ty: ignore[unresolved-import]
from tests.backlog_audit_support import (  # noqa: E402
    AUDIT_VALID_DESIGN_ACCEPTANCE,
    copy_fixture,
    replace_text,
)


class AdherenceTests(unittest.TestCase):
    def fixture_root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        copy_fixture(root)
        return root

    def findings(self, root: Path):  # type: ignore[no-untyped-def]
        loaded = load_audit(root)
        return adherence_findings(loaded)

    def all_findings(self, root: Path):  # type: ignore[no-untyped-def]
        loaded = load_audit(root)
        return (*loaded.findings, *adherence_findings(loaded))

    def codes(self, root: Path) -> set[str]:
        return {finding.code for finding in self.findings(root)}

    def write_design(
        self,
        root: Path,
        name: str,
        *,
        status: str = "approved",
        epic: str = "T1",
        children: str = "`T1.1`, `T1.2`",
        approval: str = "2026-08-15 — Fixture owner",
        acceptance: str = AUDIT_VALID_DESIGN_ACCEPTANCE,
    ) -> str:
        relative = f"docs/superpowers/specs/{name}.md"
        (root / Path(relative)).write_text(
            "# Extra Design\n\n"
            "- **Governance:** active\n"
            f"- **Status:** {status}\n"
            "- **Date:** 2026-08-15\n"
            "- **Decision owner:** Fixture owner\n"
            f"- **Roadmap epic:** `{epic}`\n"
            f"- **Roadmap children:** {children}\n"
            f"- **Approval:** {approval}\n\n"
            f"{acceptance}",
            encoding="utf-8",
            newline="\n",
        )
        return relative

    def test_valid_fixture_has_no_adherence_findings(self) -> None:
        self.assertEqual((), self.findings(self.fixture_root()))

    def test_design_children_are_known_unique_and_in_roadmap_order(self) -> None:
        cases = (
            ("`T1.1`, `T1.2`", "`T1.1`, `T9.9`", "artifact.spec.unknown-child"),
            ("`T1.1`, `T1.2`", "`T1.1`, `T1.1`", "artifact.spec.duplicate-child"),
            ("`T1.1`, `T1.2`", "`T1.2`, `T1.1`", "artifact.spec.child-order"),
        )
        for old, new, expected in cases:
            with self.subTest(expected=expected):
                root = self.fixture_root()
                replace_text(root, "docs/superpowers/specs/t1-design.md", old, new)
                self.assertIn(expected, self.codes(root))

    def test_design_epic_must_be_known(self) -> None:
        root = self.fixture_root()
        replace_text(root, "docs/superpowers/specs/t1-design.md", "**Roadmap epic:** `T1`", "**Roadmap epic:** `T9`")
        self.assertIn("artifact.spec.unknown-epic", self.codes(root))

    def test_cross_epic_design_requires_a_recognized_roadmap_declaration(self) -> None:
        root = self.fixture_root()
        replace_text(
            root,
            "ROADMAP.md",
            "## Release gates",
            "## T2 — Second fixture epic\n\n"
            "| Child | Outcome | Depends on |\n| --- | --- | --- |\n"
            "| `T2.1` | Second fixture child | `T1.2` |\n\n## Release gates",
        )
        replace_text(root, "docs/superpowers/specs/t1-design.md", "`T1.1`, `T1.2`", "`T1.1`, `T1.2`, `T2.1`")

        self.assertIn("artifact.spec.cross-epic", self.codes(root))

        replace_text(
            root,
            "ROADMAP.md",
            "# Fixture Roadmap",
            "# Fixture Roadmap\n\nThe fixture design is explicitly a cross-epic design spanning `T1.1`, `T1.2`, and the peer `T2.1` child.",
        )
        self.assertNotIn("artifact.spec.cross-epic", self.codes(root))

    def test_real_roadmap_exposes_the_two_recognized_cross_epic_declarations(self) -> None:
        sources = parse_roadmap_sources(ROOT / "ROADMAP.md")
        self.assertEqual(
            (
                ("C1", ("C1", "C2", "C3", "C4"), 113),
                ("T2", ("T2.1", "T2.2", "T3.1"), 288),
            ),
            tuple((item.anchor_epic, item.members, item.source.line) for item in sources.cross_epic_designs),
        )

    def test_plan_rejects_zero_or_multiple_children_with_stable_codes(self) -> None:
        for replacement, expected in (
            ("**Roadmap child:** —", "artifact.plan.zero-children"),
            ("**Roadmap child:** `T1.1`, `T1.2`", "artifact.plan.multiple-children"),
        ):
            with self.subTest(expected=expected):
                root = self.fixture_root()
                replace_text(root, "docs/superpowers/plans/t1-1.md", "**Roadmap child:** `T1.1`", replacement)
                self.assertIn(expected, {finding.code for finding in self.all_findings(root)})

    def test_artifact_metadata_in_the_wrong_source_family_is_rejected(self) -> None:
        root = self.fixture_root()
        plan = root / "docs/superpowers/plans/t1-1.md"
        (root / "docs/superpowers/specs/wrong-family.md").write_bytes(plan.read_bytes())
        self.assertIn("artifact.plan.wrong-family", {finding.code for finding in self.all_findings(root)})

        root = self.fixture_root()
        design = root / "docs/superpowers/specs/t1-design.md"
        (root / "docs/superpowers/plans/wrong-family.md").write_bytes(design.read_bytes())
        self.assertIn("artifact.spec.wrong-family", {finding.code for finding in self.all_findings(root)})

    def test_active_artifact_dates_and_required_approvals_are_validated(self) -> None:
        cases = (
            ("**Date:** 2026-08-15", "**Date:** 2026-8-15", "artifact.spec.date"),
            ("**Date:** 2026-08-15", "**Date:** 2026-02-30", "artifact.spec.date"),
            ("**Approval:** 2026-08-15 — Fixture owner", "**Approval:** —", "artifact.approval"),
            ("**Approval:** 2026-08-15 — Fixture owner", "**Approval:** 2026-08-15 - Fixture owner", "artifact.approval"),
            ("**Approval:** 2026-08-15 — Fixture owner", "**Approval:** 2026-08-15 — ", "artifact.approval"),
        )
        for old, new, expected in cases:
            with self.subTest(new=new):
                root = self.fixture_root()
                replace_text(root, "docs/superpowers/specs/t1-design.md", old, new)
                self.assertIn(expected, self.codes(root))

    def test_historical_disposition_names_known_node_or_existing_replacement(self) -> None:
        root = self.fixture_root()
        replace_text(
            root,
            "docs/superpowers/plans/historical-plan.md",
            "Completed under `M0`.",
            "Completed somewhere else.",
        )
        finding = next(item for item in self.findings(root) if item.code == "artifact.historical.disposition")
        self.assertTrue(finding.path.endswith("historical-plan.md"))
        self.assertEqual(5, finding.line)

    def test_effective_lifecycle_requires_the_right_governing_design(self) -> None:
        cases = (
            ("`specified`", "[design](docs/superpowers/specs/t1-design.md)", "—", "artifact.spec.required"),
            ("`specified`", "[design](docs/superpowers/specs/t1-design.md)", "[design](docs/superpowers/specs/missing.md)", "artifact.spec.missing"),
        )
        for status, old_spec, new_spec, expected in cases:
            with self.subTest(expected=expected):
                root = self.fixture_root()
                self.assertIn(status, (root / "BACKLOG.md").read_text(encoding="utf-8"))
                replace_text(root, "BACKLOG.md", old_spec + " | — | 0/1", new_spec + " | — | 0/1")
                self.assertIn(expected, self.codes(root))

        for status in ("draft", "superseded"):
            with self.subTest(status=status):
                root = self.fixture_root()
                replace_text(root, "docs/superpowers/specs/t1-design.md", "**Status:** approved", f"**Status:** {status}")
                if status == "draft":
                    replace_text(root, "docs/superpowers/specs/t1-design.md", "**Approval:** 2026-08-15 — Fixture owner", "**Approval:** —")
                self.assertIn("artifact.spec.status", self.codes(root))

    def test_blocked_or_deferred_uses_resume_state_for_design_requirement(self) -> None:
        root = self.fixture_root()
        replace_text(
            root,
            "BACKLOG.md",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `specified`",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `blocked`",
        )
        replace_text(root, "BACKLOG.md", "| — | 0/1 | — | — | — |", "| — | 0/1 | — | `specified` | Waiting for fixture. |")
        self.assertNotIn("artifact.spec.required", self.codes(root))

    def test_queued_context_reference_is_valid_but_cannot_back_checked_gate_or_later_state(self) -> None:
        root = self.fixture_root()
        replace_text(
            root,
            "BACKLOG.md",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `specified`",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `queued`",
        )
        replace_text(root, "BACKLOG.md", "[design](docs/superpowers/specs/t1-design.md) | — | 0/1", "[context](ROADMAP.md) | — | 0/1")
        self.assertFalse({"artifact.spec.required", "artifact.spec.status", "artifact.gate-drift"} & self.codes(root))

        replace_text(root, "BACKLOG.md", "- [ ] Frozen parser remains open.", "- [x] Frozen parser remains open. — Evidence: [verification](docs/evidence.md)")
        self.assertIn("artifact.spec.context-gate", self.codes(root))

        for state in ("designing", "specified"):
            with self.subTest(state=state):
                changed = self.fixture_root()
                replace_text(
                    changed,
                    "BACKLOG.md",
                    "| `T1.2` | Typed parser, status report, and versioned JSON | `specified`",
                    f"| `T1.2` | Typed parser, status report, and versioned JSON | `{state}`",
                )
                replace_text(
                    changed,
                    "BACKLOG.md",
                    "[design](docs/superpowers/specs/t1-design.md) | — | 0/1",
                    "[context](ROADMAP.md) | — | 0/1",
                )
                self.assertIn("artifact.spec.governing", self.codes(changed))

    def test_suspended_queued_child_accepts_an_existing_context_reference(self) -> None:
        root = self.fixture_root()
        replace_text(
            root,
            "BACKLOG.md",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `specified`",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `deferred`",
        )
        replace_text(
            root,
            "BACKLOG.md",
            "[design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — | — | — |",
            "[context](ROADMAP.md) | — | 0/1 | — | `queued` | Deferred fixture. |",
        )
        self.assertFalse({code for code in self.codes(root) if code.startswith("artifact.spec.")})

    def test_plan_must_match_child_and_linked_governing_design(self) -> None:
        root = self.fixture_root()
        replace_text(root, "docs/superpowers/plans/t1-1.md", "**Roadmap child:** `T1.1`", "**Roadmap child:** `T1.2`")
        self.assertIn("artifact.plan.child", self.codes(root))

        root = self.fixture_root()
        self.write_design(root, "other", children="`T1.1`")
        replace_text(
            root,
            "docs/superpowers/plans/t1-1.md",
            "**Source specification:** `docs/superpowers/specs/t1-design.md`",
            "**Source specification:** `docs/superpowers/specs/other.md`",
        )
        self.assertIn("artifact.plan.source", self.codes(root))

    def test_linked_design_must_cover_the_backlog_child(self) -> None:
        root = self.fixture_root()
        replace_text(root, "docs/superpowers/specs/t1-design.md", "`T1.1`, `T1.2`", "`T1.1`")
        self.assertIn("artifact.spec.coverage", self.codes(root))

    def test_gate_matching_folds_whitespace_but_preserves_punctuation_order_count_and_title(self) -> None:
        root = self.fixture_root()
        replace_text(root, "docs/superpowers/specs/t1-design.md", "Frozen parser remains open.", "Frozen parser remains\n  open.")
        self.assertNotIn("artifact.gate-drift", self.codes(root))

        cases = (
            ("Frozen parser remains open.", "Changed parser condition.", 1),
            ("Frozen parser remains open.", "Frozen parser remains open!", 1),
            ("- Frozen parser remains open.", "- Extra criterion.\n\n- Frozen parser remains open.", 1),
            (
                "### T1.2 — Typed parser, status report, and versioned JSON",
                "### T1.2 — Changed subsection title",
                None,
            ),
        )
        for old, new, expected_gate in cases:
            with self.subTest(new=new):
                root = self.fixture_root()
                replace_text(root, "docs/superpowers/specs/t1-design.md", old, new)
                mismatch = next(
                    item for item in self.findings(root) if item.code == "artifact.gate-drift" and item.node == "T1.2" and item.gate == expected_gate
                )
                self.assertEqual(expected_gate, mismatch.gate)

        root = self.fixture_root()
        replace_text(root, "docs/superpowers/specs/t1-design.md", "- Frozen parser remains open.", "")
        mismatch = next(item for item in self.findings(root) if item.code == "artifact.gate-drift" and item.node == "T1.2")
        self.assertIsNone(mismatch.gate)

    def test_unlinked_approved_design_does_not_replace_the_explicit_link(self) -> None:
        root = self.fixture_root()
        acceptance = AUDIT_VALID_DESIGN_ACCEPTANCE.replace("Frozen parser remains open.", "Different unlinked criterion.")
        self.write_design(root, "unlinked", children="`T1.2`", acceptance=acceptance)
        self.assertNotIn("artifact.gate-drift", self.codes(root))

    def test_exact_four_gate_reference_resolves_a_unique_earlier_child_section(self) -> None:
        root = self.fixture_root()
        earlier = (
            "## T1.2 — Detailed acceptance\n\n"
            "Its acceptance gates are:\n\n"
            "1. First exact gate.\n"
            "2. Second exact gate.\n"
            "3. Third exact gate.\n"
            "4. Fourth exact gate.\n\n"
        )
        replace_text(root, "docs/superpowers/specs/t1-design.md", "## Acceptance criteria", earlier + "## Acceptance criteria")
        replace_text(
            root,
            "docs/superpowers/specs/t1-design.md",
            "- Frozen parser remains open.",
            "`T1.2` is complete only when its four earlier acceptance gates pass.",
        )
        replace_text(root, "BACKLOG.md", "— | 0/1 |", "— | 0/4 |")
        replace_text(
            root,
            "BACKLOG.md",
            "- [ ] Frozen parser remains open.",
            "- [ ] First exact gate.\n- [ ] Second exact gate.\n- [ ] Third exact gate.\n- [ ] Fourth exact gate.",
        )

        self.assertNotIn("artifact.gate-drift", self.codes(root))

        replace_text(root, "docs/superpowers/specs/t1-design.md", "Its acceptance gates are:", "Acceptance gates:")
        self.assertIn("artifact.gate-drift", self.codes(root))

        replace_text(
            root,
            "docs/superpowers/specs/t1-design.md",
            "## T1.2 — Detailed acceptance",
            "## T1.2 — Detailed acceptance\n\n"
            "Its acceptance gates are:\n\n"
            "1. First exact gate.\n2. Second exact gate.\n3. Third exact gate.\n4. Fourth exact gate.\n\n"
            "## T1.2 — Duplicate acceptance",
        )
        self.assertIn("artifact.gate-drift", self.codes(root))

    def test_unresolved_managed_reference_is_never_treated_as_literal_gate_text(self) -> None:
        exact_reference = "`T1.2` is complete only when its four earlier acceptance gates pass."
        valid_section = (
            "## T1.2 — Detailed acceptance\n\n"
            "Its acceptance gates are:\n\n"
            "1. First exact gate.\n"
            "2. Second exact gate.\n"
            "3. Third exact gate.\n"
            "4. Fourth exact gate.\n\n"
        )
        cases = (
            ("missing section", "", exact_reference),
            ("missing marker", valid_section.replace("Its acceptance gates are:", "Acceptance gates:"), exact_reference),
            ("wrong count", valid_section.replace("4. Fourth exact gate.\n", ""), exact_reference),
            ("ambiguous section", valid_section + valid_section.replace("Detailed acceptance", "Duplicate acceptance"), exact_reference),
            (
                "ambiguous marker",
                valid_section.replace("Its acceptance gates are:", "Its acceptance gates are:\n\nIts acceptance gates are:"),
                exact_reference,
            ),
            ("wrong referenced child", valid_section, exact_reference.replace("T1.2", "T1.1")),
        )
        for label, earlier, reference in cases:
            with self.subTest(label=label):
                root = self.fixture_root()
                replace_text(root, "docs/superpowers/specs/t1-design.md", "## Acceptance criteria", earlier + "## Acceptance criteria")
                replace_text(root, "docs/superpowers/specs/t1-design.md", "- Frozen parser remains open.", reference)
                replace_text(root, "BACKLOG.md", "- [ ] Frozen parser remains open.", f"- [ ] {reference}")

                loaded = load_audit(root)
                section = next(item for item in loaded.sources.design_acceptance if item.child == "T1.2")
                mismatches = [item for item in adherence_findings(loaded) if item.code == "artifact.gate-drift" and item.node == "T1.2"]

                self.assertEqual(1, len(mismatches))
                self.assertIsNone(mismatches[0].gate)
                self.assertIn("reference", mismatches[0].message)
                self.assertEqual(section.source.line + 2, mismatches[0].line)

    def test_managed_reference_must_be_the_only_acceptance_statement(self) -> None:
        root = self.fixture_root()
        reference = "`T1.2` is complete only when its four earlier acceptance gates pass."
        replace_text(
            root,
            "docs/superpowers/specs/t1-design.md",
            "## Acceptance criteria",
            "## T1.2 — Detailed acceptance\n\n"
            "Its acceptance gates are:\n\n"
            "1. First exact gate.\n"
            "2. Second exact gate.\n"
            "3. Third exact gate.\n"
            "4. Fourth exact gate.\n\n"
            "## Acceptance criteria",
        )
        replace_text(
            root,
            "docs/superpowers/specs/t1-design.md",
            "- Frozen parser remains open.",
            f"{reference}\n\nUnexpected sibling statement.",
        )
        replace_text(root, "BACKLOG.md", "— | 0/1 |", "— | 0/2 |")
        replace_text(
            root,
            "BACKLOG.md",
            "- [ ] Frozen parser remains open.",
            f"- [ ] {reference}\n- [ ] Unexpected sibling statement.",
        )

        loaded = load_audit(root)
        mismatch = next(item for item in adherence_findings(loaded) if item.code == "artifact.gate-drift" and item.node == "T1.2")

        self.assertIsNone(mismatch.gate)
        self.assertIn("reference", mismatch.message)

    def test_gate_drift_reports_title_each_ordinal_and_count_independently(self) -> None:
        root = self.fixture_root()
        replace_text(
            root,
            "docs/superpowers/specs/t1-design.md",
            "### T1.2 — Typed parser, status report, and versioned JSON",
            "### T1.2 — Changed title",
        )
        replace_text(
            root,
            "docs/superpowers/specs/t1-design.md",
            "- Frozen parser remains open.",
            "- Design first.\n\n- Design second.\n\n- Design third.",
        )
        replace_text(root, "BACKLOG.md", "— | 0/1 |", "— | 0/2 |")
        replace_text(root, "BACKLOG.md", "- [ ] Frozen parser remains open.", "- [ ] Backlog first.\n- [ ] Backlog second.")

        loaded = load_audit(root)
        section = next(item for item in loaded.sources.design_acceptance if item.child == "T1.2")
        mismatches = [item for item in adherence_findings(loaded) if item.code == "artifact.gate-drift" and item.node == "T1.2"]

        self.assertEqual(4, len(mismatches))
        self.assertEqual(2, sum(item.gate is None for item in mismatches))
        self.assertEqual({1, 2}, {item.gate for item in mismatches if item.gate is not None})
        title = next(item for item in mismatches if "title" in item.message)
        count = next(item for item in mismatches if "count" in item.message)
        self.assertEqual(section.source.line, title.line)
        self.assertEqual(section.source.line, count.line)
        for ordinal in (1, 2):
            mismatch = next(item for item in mismatches if item.gate == ordinal)
            self.assertEqual(section.statements[ordinal - 1].source.line, mismatch.line)

    def test_spec_link_must_remain_contained_and_resolve_to_regular_markdown(self) -> None:
        root = self.fixture_root()
        replace_text(root, "BACKLOG.md", "[design](docs/superpowers/specs/t1-design.md) | — | 0/1", "[design](../outside.md) | — | 0/1")
        self.assertIn("link.path", {finding.code for finding in self.all_findings(root)})

        root = self.fixture_root()
        replace_text(root, "BACKLOG.md", "[design](docs/superpowers/specs/t1-design.md) | — | 0/1", "[design](docs/superpowers/specs/missing.txt) | — | 0/1")
        self.assertIn("artifact.spec.path", self.codes(root))

    def test_real_f1_queued_architecture_links_remain_context_only(self) -> None:
        loaded = load_audit(ROOT)
        findings = adherence_findings(loaded)
        f1_children = {f"F1.{ordinal}" for ordinal in range(1, 7)}

        self.assertEqual(
            set(),
            {(finding.code, finding.node) for finding in findings if finding.node in f1_children},
        )

    def test_invalid_authority_or_linked_artifact_does_not_cascade_adherence(self) -> None:
        root = self.fixture_root()
        replace_text(
            root,
            "ROADMAP.md",
            "| Milestone | Outcome |\n| --- | --- |",
            "| Milestone | Outcome |\n| --- | invalid |",
        )
        loaded = load_audit(root)

        self.assertIn("ROADMAP.md", loaded.invalid_paths)
        self.assertFalse(
            {
                "artifact.spec.unknown-epic",
                "artifact.spec.unknown-child",
                "artifact.spec.epic",
                "artifact.gate-drift",
            }
            & {finding.code for finding in adherence_findings(loaded)}
        )

        root = self.fixture_root()
        replace_text(root, "docs/superpowers/specs/t1-design.md", "**Status:** approved", "**Status:** invalid")
        loaded = load_audit(root)

        self.assertIn("docs/superpowers/specs/t1-design.md", loaded.invalid_paths)
        self.assertFalse({"artifact.spec.governing", "artifact.plan.source", "artifact.gate-drift"} & {finding.code for finding in adherence_findings(loaded)})


if __name__ == "__main__":
    unittest.main()
