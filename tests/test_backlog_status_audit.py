from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
FIXTURE = ROOT / "tests/fixtures/backlog_status/valid"
sys.path.insert(0, str(SCRIPTS))

from backlog.audit import finding_key, load_audit  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.model import Finding  # noqa: E402  # ty: ignore[unresolved-import]


class AuditLoadingTests(unittest.TestCase):
    def copy_fixture_root(self) -> Path:
        temporary = Path(self.enterContext(tempfile.TemporaryDirectory()))
        shutil.copytree(FIXTURE, temporary, dirs_exist_ok=True)
        return temporary

    def test_retains_all_audit_source_facts_with_wrapped_lf_and_crlf_statements(self) -> None:
        root = self.copy_fixture_root()
        backlog_path = root / "BACKLOG.md"
        backlog = backlog_path.read_text(encoding="utf-8")
        backlog = backlog.replace("- Active child: —.", "- Active child: `T1.2`.", 1)
        backlog = backlog.replace(
            "### T1.2 — Typed parser, status report, and versioned JSON\n\n- [ ] Frozen parser remains open.",
            "### T1.2 — Typed parser, status report, and versioned JSON\n\n"
            "- [ ] Frozen parser remains\n      open.\n\n"
            "### T9.9 — Orphan criterion, retained!\n\n- [ ] Unknown child remains visible.",
            1,
        )
        backlog_path.write_text(backlog, encoding="utf-8", newline="\r\n")
        design_path = root / "docs/superpowers/specs/t1-design.md"
        design = design_path.read_text(encoding="utf-8") + (
            "\n## Acceptance criteria\n\n"
            "### T1.1 — Markdown authority contract and explicit inventory normalization\n\n"
            "- Frozen contract is verified and\n  remains explicit.\n\n"
            "### T1.2 — Typed parser, status report, and versioned JSON\n\n"
            "- Frozen parser remains\n  open.\n"
        )
        design_path.write_text(design, encoding="utf-8", newline="\n")

        result = load_audit(root)

        self.assertEqual(
            (
                "Markdown authority contract and explicit inventory normalization",
                "Typed parser, status report, and versioned JSON",
            ),
            tuple(fact.outcome for fact in result.sources.inventory_rows),
        )
        self.assertEqual("T1.2", result.sources.selection.child)
        self.assertEqual(5, result.sources.selection.source.line)
        dashboard = result.sources.release_dashboard[0]
        self.assertEqual("Canonical vertical-slice reconciliation", dashboard.outcome)
        self.assertEqual(("T1.2",), dashboard.dependencies)
        self.assertEqual(
            (
                ("T1.1", "Markdown authority contract and explicit inventory normalization", 16),
                ("T1.2", "Typed parser, status report, and versioned JSON", 21),
                ("T9.9", "Orphan criterion, retained!", 26),
            ),
            tuple((fact.child, fact.title, fact.source.line) for fact in result.sources.gate_headings),
        )
        metadata = next(fact for fact in result.sources.artifact_metadata if fact.path.endswith("t1-design.md"))
        self.assertEqual((5, 9), (metadata.date.source.line, metadata.approval.source.line))
        criteria = result.sources.design_acceptance
        self.assertEqual(
            (
                (
                    "T1.1",
                    "Markdown authority contract and explicit inventory normalization",
                    15,
                    (("Frozen contract is verified and remains explicit.", 17),),
                ),
                (
                    "T1.2",
                    "Typed parser, status report, and versioned JSON",
                    20,
                    (("Frozen parser remains open.", 22),),
                ),
            ),
            tuple(
                (
                    section.child,
                    section.title,
                    section.source.line,
                    tuple((statement.value, statement.source.line) for statement in section.statements),
                )
                for section in criteria
            ),
        )

    def test_independent_authority_and_artifact_parse_failures_survive(self) -> None:
        root = self.copy_fixture_root()
        roadmap_path = root / "ROADMAP.md"
        roadmap_path.write_text(
            roadmap_path.read_text(encoding="utf-8").replace("| --- | --- |", "| --- | invalid |", 1),
            encoding="utf-8",
        )
        plan_path = root / "docs/superpowers/plans/t1-1.md"
        plan_path.write_text(
            plan_path.read_text(encoding="utf-8").replace("- **Status:** completed", "- **Status:** unknown", 1),
            encoding="utf-8",
        )

        result = load_audit(root)

        paths = {finding.path for finding in result.findings}
        self.assertIn("ROADMAP.md", paths)
        self.assertIn("docs/superpowers/plans/t1-1.md", paths)
        self.assertIn("ROADMAP.md", result.invalid_paths)
        self.assertTrue(all(finding.line is not None for finding in result.findings))
        self.assertEqual(6, next(finding.line for finding in result.findings if finding.path == "ROADMAP.md"))
        self.assertEqual(4, next(finding.line for finding in result.findings if finding.path.endswith("t1-1.md")))
        self.assertEqual((), result.snapshot.roadmap.local_children)
        self.assertEqual(("T1.1", "T1.2"), tuple(child.id for child in result.snapshot.backlog.children))
        self.assertIsNone(result.policy)
        self.assertFalse(any(finding.code == "backlog.missing-child" for finding in result.findings))

    def test_unreadable_authority_uses_stable_code_and_empty_report_shape(self) -> None:
        root = self.copy_fixture_root()
        (root / "ROADMAP.md").unlink()

        result = load_audit(root)

        finding = next(item for item in result.findings if item.path == "ROADMAP.md")
        self.assertEqual("input.unreadable", finding.code)
        self.assertEqual((), result.snapshot.roadmap.milestones)
        self.assertIn("ROADMAP.md", result.invalid_paths)

    def test_git_launch_failure_is_an_independent_policy_finding(self) -> None:
        with patch("backlog.policy.subprocess.run", side_effect=OSError("git unavailable")):
            result = load_audit(ROOT)

        finding = next(item for item in result.findings if item.code == "policy.unavailable")
        self.assertEqual(
            "docs/superpowers/specs/2026-09-05-t1-3-audit-policy-supplement-design.md",
            finding.path,
        )
        self.assertIsNone(result.policy)
        self.assertEqual(64, len(result.snapshot.roadmap.local_children))
        self.assertEqual(64, len(result.snapshot.backlog.children))

    def test_finding_key_orders_missing_context_last(self) -> None:
        findings = (
            Finding("z.last", "warning", "B.md", None, None, None, "last"),
            Finding("b.second", "error", "A.md", 2, "T1.2", 2, "second"),
            Finding("a.first", "error", "A.md", 2, "T1.1", 1, "first"),
        )

        ordered = tuple(sorted(findings, key=finding_key))

        self.assertEqual(("a.first", "b.second", "z.last"), tuple(item.code for item in ordered))


if __name__ == "__main__":
    unittest.main()
