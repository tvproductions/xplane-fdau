from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

from tests.backlog_audit_support import copy_fixture, replace_text


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
sys.path.insert(0, str(SCRIPTS))

from backlog.audit import load_audit  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.rules import structural_findings  # noqa: E402  # ty: ignore[unresolved-import]


T11 = "| `T1.1` | Markdown authority contract and explicit inventory normalization |"
T12 = "| `T1.2` | Typed parser, status report, and versioned JSON |"
T12_ROADMAP = f"{T12} `T1.1` |"
T12_BACKLOG = (
    "| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | [design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — | — | — |"
)
T11_BACKLOG = (
    "| `T1.1` | Markdown authority contract and explicit inventory normalization | `verified` | `M0` | "
    "[design](docs/superpowers/specs/t1-design.md) | [plan](docs/superpowers/plans/t1-1.md) | 1/1 | "
    "[review](.superpowers/sdd/t1-1/review.md) | — | — |"
)


class StructuralRulesTests(unittest.TestCase):
    def fixture_root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        copy_fixture(root)
        return root

    def finding(self, root: Path, code: str):
        findings = structural_findings(load_audit(root))
        return next(item for item in findings if item.code == code)

    def assert_finding(self, root: Path, code: str, path: str, node: str | None, *, line_known: bool = True) -> None:
        finding = self.finding(root, code)
        self.assertEqual(path, finding.path)
        self.assertEqual(node, finding.node)
        if line_known:
            self.assertIsNotNone(finding.line)
        else:
            self.assertIsNone(finding.line)
        self.assertIsNone(finding.gate)

    def test_valid_fixture_has_no_structural_findings(self) -> None:
        self.assertEqual((), structural_findings(load_audit(self.fixture_root())))

    def test_roadmap_identity_epic_dependency_and_cycle_rules(self) -> None:
        cases = (
            (
                "duplicate same kind",
                "ROADMAP.md",
                T12_ROADMAP,
                T12_ROADMAP.replace("`T1.2`", "`T1.1`", 1),
                "roadmap.duplicate-id",
                "T1.1",
            ),
            (
                "cross kind reuse",
                "ROADMAP.md",
                "| `I1.1` | Fixture contract adoption | Fixture consumer | Adoption begins after `T1.2`. |",
                "| `T1.1` | Fixture contract adoption | Fixture consumer | Adoption begins after `T1.2`. |",
                "roadmap.kind-conflict",
                "T1.1",
            ),
            (
                "unknown dependency",
                "ROADMAP.md",
                T12_ROADMAP,
                T12_ROADMAP.replace("`T1.1`", "`T9.9`"),
                "roadmap.unknown-dependency",
                "T1.2",
            ),
            (
                "duplicate dependency",
                "ROADMAP.md",
                T12_ROADMAP,
                T12_ROADMAP.replace("`T1.1`", "`T1.1`, `T1.1`"),
                "roadmap.duplicate-dependency",
                "T1.2",
            ),
            (
                "nonlocal dependency",
                "ROADMAP.md",
                T12_ROADMAP,
                T12_ROADMAP.replace("`T1.1`", "`G1`"),
                "roadmap.dependency-kind",
                "T1.2",
            ),
            (
                "self cycle",
                "ROADMAP.md",
                T12_ROADMAP,
                T12_ROADMAP.replace("`T1.1`", "`T1.2`"),
                "roadmap.dependency-cycle",
                "T1.2",
            ),
        )
        for name, path, old, new, code, node in cases:
            with self.subTest(name=name):
                root = self.fixture_root()
                replace_text(root, path, old, new)
                self.assert_finding(root, code, "ROADMAP.md", node)

        loaded = load_audit(self.fixture_root())
        first_child, *remaining_children = loaded.snapshot.roadmap.local_children
        roadmap = replace(
            loaded.snapshot.roadmap,
            local_children=(replace(first_child, epic="T2"), *remaining_children),
        )
        changed = replace(loaded, snapshot=replace(loaded.snapshot, roadmap=roadmap))
        finding = next(item for item in structural_findings(changed) if item.code == "roadmap.epic-mismatch")
        self.assertEqual(("ROADMAP.md", "T1.1", None), (finding.path, finding.node, finding.gate))
        self.assertIsNotNone(finding.line)

        root = self.fixture_root()
        replace_text(root, "ROADMAP.md", T11 + " `M0` |", T11 + " `T1.2` |")
        self.assert_finding(root, "roadmap.dependency-cycle", "ROADMAP.md", "T1.2")

    def test_standards_epic_owns_canonical_s_children(self) -> None:
        root = self.fixture_root()
        standards = """## S — Standards epic

| Child | Outcome | Depends on | External prerequisite |
| --- | --- | --- | --- |
| `S1.1` | First standards outcome | `M0` | — |
| `S2.1` | Second standards outcome | `M0` | — |
| `S2.2` | Third standards outcome | `M0` | — |
| `S3.1` | Fourth standards outcome | `M0` | — |
| `S4.1` | Fifth standards outcome | `M0` | — |

"""
        replace_text(root, "ROADMAP.md", "## Release gates", standards + "## Release gates")

        mismatches = [item.node for item in structural_findings(load_audit(root)) if item.code == "roadmap.epic-mismatch"]

        self.assertEqual([], mismatches)

    def test_cycle_retains_valid_edge_when_a_sibling_dependency_is_invalid(self) -> None:
        root = self.fixture_root()
        replace_text(root, "ROADMAP.md", T11 + " `M0` |", T11 + " `T1.2` |")
        replace_text(root, "ROADMAP.md", T12_ROADMAP, T12_ROADMAP.replace("`T1.1`", "`T1.1`, `T9.9`"))

        codes = {item.code for item in structural_findings(load_audit(root))}

        self.assertTrue({"roadmap.dependency-cycle", "roadmap.unknown-dependency"} <= codes)

    def test_combined_identity_collision_retains_same_kind_and_cross_kind_codes(self) -> None:
        root = self.fixture_root()
        duplicate = "| `T1.1` | Alternate same-kind outcome | `M0` |"
        replace_text(root, "ROADMAP.md", T11 + " `M0` |", T11 + " `M0` |\n" + duplicate)
        replace_text(
            root,
            "ROADMAP.md",
            "| `I1.1` | Fixture contract adoption | Fixture consumer | Adoption begins after `T1.2`. |",
            "| `T1.1` | Fixture contract adoption | Fixture consumer | Adoption begins after `T1.2`. |",
        )

        codes = {item.code for item in structural_findings(load_audit(root))}

        self.assertTrue({"roadmap.duplicate-id", "roadmap.kind-conflict"} <= codes)

    def test_invalid_or_ambiguous_roadmap_does_not_cascade_cross_file_findings(self) -> None:
        invalid_root = self.fixture_root()
        replace_text(
            invalid_root,
            "ROADMAP.md",
            "| --- | --- |\n| `M0` | Frozen migration baseline |",
            "| --- | invalid |\n| `M0` | Frozen migration baseline |",
        )
        replace_text(invalid_root, "BACKLOG.md", "- Active child: —.", "- Active child: `T1.2`.")
        replace_text(invalid_root, "BACKLOG.md", "1/1", "0/1")

        invalid_codes = {item.code for item in structural_findings(load_audit(invalid_root))}

        self.assertEqual({"backlog.gate-count"}, invalid_codes)

        ambiguous_root = self.fixture_root()
        duplicate = "| `T1.1` | Alternate same-kind outcome | `M0` |"
        replace_text(ambiguous_root, "ROADMAP.md", T11 + " `M0` |", T11 + " `M0` |\n" + duplicate)

        ambiguous_codes = {item.code for item in structural_findings(load_audit(ambiguous_root))}

        self.assertNotIn("backlog.outcome-drift", ambiguous_codes)
        self.assertNotIn("backlog.dependency-drift", ambiguous_codes)
        self.assertNotIn("backlog.child-order", ambiguous_codes)

        release_root = self.fixture_root()
        roadmap_gate = "| `G1` | Canonical vertical-slice reconciliation | `T1.2` |"
        replace_text(
            release_root,
            "ROADMAP.md",
            roadmap_gate,
            roadmap_gate + "\n| `G1` | Alternate release outcome | `T1.2` |",
        )
        replace_text(
            release_root,
            "BACKLOG.md",
            "Canonical vertical-slice reconciliation",
            "Changed release definition",
        )

        release_codes = {item.code for item in structural_findings(load_audit(release_root))}

        self.assertNotIn("release.definition-drift", release_codes)

    def test_backlog_inventory_and_selection_rules(self) -> None:
        cases = (
            (
                "missing child",
                T12_BACKLOG + "\n",
                "",
                "backlog.missing-child",
                "T1.2",
            ),
            (
                "duplicate child",
                T12_BACKLOG,
                T12_BACKLOG + "\n" + T12_BACKLOG,
                "backlog.duplicate-child",
                "T1.2",
            ),
            (
                "outcome drift",
                T12_BACKLOG,
                T12_BACKLOG.replace("Typed parser, status report, and versioned JSON", "Different outcome"),
                "backlog.outcome-drift",
                "T1.2",
            ),
            (
                "dependency drift",
                T12_BACKLOG,
                T12_BACKLOG.replace("`T1.1`", "`M0`", 1),
                "backlog.dependency-drift",
                "T1.2",
            ),
            (
                "unknown selection",
                "- Active child: —.",
                "- Active child: `T9.9`.",
                "backlog.invalid-selection",
                "T9.9",
            ),
        )
        for name, old, new, code, node in cases:
            with self.subTest(name=name):
                root = self.fixture_root()
                replace_text(root, "BACKLOG.md", old, new)
                self.assert_finding(root, code, "BACKLOG.md", node, line_known=code != "backlog.missing-child")

        root = self.fixture_root()
        replace_text(root, "BACKLOG.md", T12_BACKLOG, T12_BACKLOG.replace("`T1.2`", "`T9.9`", 1))
        replace_text(
            root,
            "BACKLOG.md",
            "### T1.2 — Typed parser, status report, and versioned JSON",
            "### T9.9 — Typed parser, status report, and versioned JSON",
        )
        self.assert_finding(root, "backlog.unknown-child", "BACKLOG.md", "T9.9")

        root = self.fixture_root()
        replace_text(root, "BACKLOG.md", T11_BACKLOG + "\n" + T12_BACKLOG, T12_BACKLOG + "\n" + T11_BACKLOG)
        self.assert_finding(root, "backlog.child-order", "BACKLOG.md", "T1.2")

    def test_backlog_child_kind_and_nonlocal_selection(self) -> None:
        loaded = load_audit(self.fixture_root())
        child = loaded.snapshot.backlog.children[1]
        nonlocal_child = replace(child, id="G1")
        backlog = replace(loaded.snapshot.backlog, children=(loaded.snapshot.backlog.children[0], nonlocal_child))
        changed = replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))
        finding = next(item for item in structural_findings(changed) if item.code == "backlog.child-kind")
        self.assertEqual(("BACKLOG.md", "G1", None), (finding.path, finding.node, finding.gate))
        self.assertIsNotNone(finding.line)

        backlog = replace(loaded.snapshot.backlog, active_child="M0")
        changed = replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))
        finding = next(item for item in structural_findings(changed) if item.code == "backlog.invalid-selection")
        self.assertEqual(("BACKLOG.md", "M0", None), (finding.path, finding.node, finding.gate))
        self.assertIsNotNone(finding.line)

    def test_gate_heading_and_count_rules(self) -> None:
        cases = (
            (
                "gate count",
                "1/1",
                "0/1",
                "backlog.gate-count",
                "T1.1",
            ),
            (
                "gate title",
                "### T1.2 — Typed parser, status report, and versioned JSON",
                "### T1.2 — Different title",
                "backlog.gate-title",
                "T1.2",
            ),
        )
        for name, old, new, code, node in cases:
            with self.subTest(name=name):
                root = self.fixture_root()
                replace_text(root, "BACKLOG.md", old, new)
                self.assert_finding(root, code, "BACKLOG.md", node)

        root = self.fixture_root()
        replace_text(
            root,
            "BACKLOG.md",
            "\n## Release-gate dashboard",
            "\n### T9.9 — Orphan gates\n\n- [ ] Still visible.\n\n## Release-gate dashboard",
        )
        self.assert_finding(root, "backlog.orphan-gates", "BACKLOG.md", "T9.9")

    def test_release_dashboard_rules(self) -> None:
        dashboard = "| `G1` | Canonical vertical-slice reconciliation | `waiting` | `T1.2` | — |"
        cases = (
            ("missing row", dashboard + "\n", "", "release.inventory", "G1"),
            ("duplicate row", dashboard, dashboard + "\n" + dashboard, "release.inventory", "G1"),
            ("unknown row", dashboard, dashboard.replace("`G1`", "`G9`", 1), "release.inventory", "G9"),
            (
                "title drift",
                dashboard,
                dashboard.replace("Canonical vertical-slice reconciliation", "Different definition"),
                "release.definition-drift",
                "G1",
            ),
            (
                "prerequisite drift",
                dashboard,
                dashboard.replace("`T1.2`", "`M0`", 1),
                "release.definition-drift",
                "G1",
            ),
        )
        for name, old, new, code, node in cases:
            with self.subTest(name=name):
                root = self.fixture_root()
                replace_text(root, "BACKLOG.md", old, new)
                self.assert_finding(root, code, "BACKLOG.md", node, line_known=name != "missing row")

        root = self.fixture_root()
        replace_text(root, "BACKLOG.md", dashboard, dashboard.replace("`G1`", "`T1.1`", 1))
        wrong_kind = [item for item in structural_findings(load_audit(root)) if item.code == "release.inventory"]
        self.assertEqual({"G1", "T1.1"}, {item.node for item in wrong_kind})
        self.assertTrue(all(item.gate is None for item in wrong_kind))
        self.assertIsNotNone(next(item.line for item in wrong_kind if item.node == "T1.1"))


if __name__ == "__main__":
    unittest.main()
