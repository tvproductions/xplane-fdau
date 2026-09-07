from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass, replace
import hashlib
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.backlog_audit_support import audit_fixture, replace_bytes, replace_text, run_git, write_active_design, write_active_plan, write_evidence

SCRIPTS = Path(__file__).resolve().parents[1] / ".codex" / "skills" / "backlog-status" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from backlog.audit import audit_repository  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.edit import (  # noqa: E402  # ty: ignore[unresolved-import]
    MutationPlan,
    MutationRefusal,
    plan_resume,
    plan_selection,
    plan_suspend,
    plan_transition,
    _NONSUSPENDED,
    _TRANSITIONS,
)
from backlog.model import Finding  # noqa: E402  # ty: ignore[unresolved-import]


class SelectionPlanningTests(unittest.TestCase):
    def copy_fixture_root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory())) / "repository"
        audit_fixture(root)
        return root

    def assert_refusal(self, code: str, *args: object, **kwargs: object) -> None:
        with self.assertRaises(MutationRefusal) as raised:
            plan_selection(*args, **kwargs)
        self.assertEqual(code, raised.exception.code)

    def test_plan_is_frozen_and_selects_one_local_child_without_writing(self) -> None:
        root = self.copy_fixture_root()
        original = (root / "BACKLOG.md").read_bytes()

        plan = plan_selection(root, "T1.2", expect_current=None)

        self.assertIsInstance(plan, MutationPlan)
        self.assertTrue(is_dataclass(plan))
        with self.assertRaises(FrozenInstanceError):
            plan.summary = "changed"  # type: ignore[misc]
        self.assertEqual(root.resolve(), plan.root)
        self.assertEqual(root.resolve() / "BACKLOG.md", plan.target)
        self.assertEqual(original, plan.original)
        self.assertEqual(hashlib.sha256(original).hexdigest(), plan.original_sha256)
        self.assertEqual(hashlib.sha256(plan.candidate).hexdigest(), plan.candidate_sha256)
        self.assertIn("- Active child: `T1.2`.", plan.candidate.decode("utf-8"))
        self.assertIn("--- a/BACKLOG.md", plan.diff)
        self.assertIn("+++ b/BACKLOG.md", plan.diff)
        self.assertEqual((), plan.audit.findings)
        self.assertEqual(original, (root / "BACKLOG.md").read_bytes())

    def test_plan_deselects_the_current_child(self) -> None:
        root = self.copy_fixture_root()
        replace_bytes(root, "BACKLOG.md", b"- Active child: \xe2\x80\x94.", b"- Active child: `T1.2`.")

        plan = plan_selection(root, None, expect_current="T1.2")

        self.assertIn(b"- Active child: \xe2\x80\x94.", plan.candidate)
        self.assertEqual(None, plan.audit.snapshot.backlog.active_child)

    def test_plan_refuses_a_no_op_selection(self) -> None:
        root = self.copy_fixture_root()

        self.assert_refusal("mutation.target", root, None, expect_current=None)

    def test_plan_refuses_unknown_or_nonlocal_children(self) -> None:
        root = self.copy_fixture_root()

        self.assert_refusal("mutation.target", root, "T9.9", expect_current=None)
        self.assert_refusal("mutation.target", root, "I1.1", expect_current=None)

    def test_plan_refuses_a_mismatched_expected_selection(self) -> None:
        root = self.copy_fixture_root()

        self.assert_refusal("mutation.expected-selection", root, "T1.2", expect_current="T1.1")

    def test_plan_refuses_malformed_or_uppercase_target_hashes(self) -> None:
        root = self.copy_fixture_root()

        self.assert_refusal("mutation.target-sha256", root, "T1.2", expect_current=None, target_sha256="wrong")
        self.assert_refusal("mutation.target-sha256", root, "T1.2", expect_current=None, target_sha256="A" * 64)

    def test_plan_refuses_a_stale_well_formed_target_hash(self) -> None:
        root = self.copy_fixture_root()

        self.assert_refusal("mutation.stale", root, "T1.2", expect_current=None, target_sha256="0" * 64)

    def test_plan_refuses_when_the_existing_audit_has_errors(self) -> None:
        root = self.copy_fixture_root()
        replace_bytes(root, "BACKLOG.md", b"`specified`", b"`not-a-state`")

        self.assert_refusal("mutation.audit", root, "T1.2", expect_current=None)

    def test_warning_only_audit_remains_actionable_and_survives_candidate_audit(self) -> None:
        root = self.copy_fixture_root()
        warning = Finding("fixture.warning", "warning", "BACKLOG.md", 5, None, None, "fixture warning")
        original_audit = audit_repository
        audit_texts: list[str | None] = []

        def warning_audit(path: Path, *, backlog_text: str | None = None):
            audited = original_audit(path, backlog_text=backlog_text)
            audit_texts.append(backlog_text)
            return replace(audited, findings=(*audited.findings, warning))

        with patch("backlog.edit.audit_repository", side_effect=warning_audit):
            plan = plan_selection(root, "T1.2", expect_current=None)

        self.assertEqual((warning,), plan.audit.findings)
        self.assertEqual(2, len(audit_texts))
        self.assertEqual(plan.original.decode("utf-8"), audit_texts[0])
        self.assertEqual(plan.candidate.decode("utf-8"), audit_texts[1])
        self.assertEqual("T1.2", plan.audit.snapshot.backlog.active_child)


class SelectionBytePreservationTests(unittest.TestCase):
    def copy_fixture_root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory())) / "repository"
        audit_fixture(root)
        return root

    def assert_refusal(self, code: str, *args: object, **kwargs: object) -> None:
        with self.assertRaises(MutationRefusal) as raised:
            plan_selection(*args, **kwargs)
        self.assertEqual(code, raised.exception.code)

    def test_selection_edit_preserves_all_unmanaged_bytes_for_lf_crlf_and_no_final_newline(self) -> None:
        for newline, final_newline in ((b"\n", True), (b"\r\n", True), (b"\n", False)):
            with self.subTest(newline=newline, final_newline=final_newline):
                root = self.copy_fixture_root()
                target = root / "BACKLOG.md"
                original = target.read_bytes().replace(b"\n", newline)
                if not final_newline:
                    original = original.rstrip(b"\n\r")
                original = original.replace(b"# Fixture Backlog", b"# Fixture Backlog \xe2\x80\x94 caf\xc3\xa9", 1)
                target.write_bytes(original)

                plan = plan_selection(root, "T1.2", expect_current=None)

                original_lines = original.splitlines(keepends=True)
                candidate_lines = plan.candidate.splitlines(keepends=True)
                changed = [index for index, (before, after) in enumerate(zip(original_lines, candidate_lines)) if before != after]
                self.assertEqual([4], changed)
                self.assertEqual(len(original_lines), len(candidate_lines))
                self.assertTrue(candidate_lines[4].endswith(newline))
                self.assertEqual(original_lines[:4], candidate_lines[:4])
                self.assertEqual(original_lines[5:], candidate_lines[5:])
                self.assertEqual(b"- Active child: `T1.2`." + newline, candidate_lines[4])

    def test_plan_refuses_invalid_utf8_before_a_plan_exists(self) -> None:
        root = self.copy_fixture_root()
        target = root / "BACKLOG.md"
        target.write_bytes(target.read_bytes().replace(b"Fixture", b"\xffixture", 1))

        self.assert_refusal("mutation.target", root, "T1.2", expect_current=None)

    def test_plan_refuses_a_nonregular_or_symlink_backlog(self) -> None:
        root = self.copy_fixture_root()
        target = root / "BACKLOG.md"
        target.unlink()
        target.mkdir()

        self.assert_refusal("mutation.target", root, "T1.2", expect_current=None)

        target.rmdir()
        source = root / "alternate.md"
        source.write_text("not a backlog", encoding="utf-8")
        try:
            os.symlink(source, target)
        except OSError as error:
            self.fail(f"the test environment must permit a symlink fixture: {error}")

        self.assert_refusal("mutation.target", root, "T1.2", expect_current=None)


if __name__ == "__main__":
    unittest.main()


class LifecyclePlanningTests(unittest.TestCase):
    def copy_fixture_root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory())) / "repository"
        audit_fixture(root)
        return root

    def assert_refusal(self, code: str, planner, *args: object, **kwargs: object) -> None:  # type: ignore[no-untyped-def]
        with self.assertRaises(MutationRefusal) as raised:
            planner(*args, **kwargs)
        self.assertEqual(code, raised.exception.code)

    def test_transition_allows_exact_closed_graph_only(self) -> None:
        allowed = {
            ("queued", "designing"), ("designing", "specified"), ("specified", "planned"),
            ("planned", "in_progress"), ("in_progress", "implemented"),
            ("implemented", "reviewed"), ("reviewed", "verified"), ("specified", "designing"),
            ("planned", "specified"), ("in_progress", "planned"), ("implemented", "in_progress"),
            ("reviewed", "implemented"), ("verified", "reviewed"),
        }
        self.assertEqual(allowed, _TRANSITIONS)
        root = self.copy_fixture_root()
        for target in ("queued", "specified", "in_progress", "implemented", "reviewed", "verified"):
            with self.subTest(target=target):
                self.assert_refusal("mutation.transition", plan_transition, root, "T1.2", target, expect="specified")
        self.assert_refusal("mutation.transition", plan_transition, root, "T1.2", "released", expect="specified")

    def test_transition_refuses_stale_expected_status_before_candidate(self) -> None:
        root = self.copy_fixture_root()

        self.assert_refusal("mutation.expected-status", plan_transition, root, "T1.2", "planned", expect="queued")

    def test_transition_updates_only_the_allowed_link_cell_and_preserves_other_cells(self) -> None:
        root = self.copy_fixture_root()
        original = (root / "BACKLOG.md").read_bytes()
        write_active_plan(root, "docs/superpowers/plans/t1-2.md")

        plan = plan_transition(root, "T1.2", "planned", expect="specified", plan="docs/superpowers/plans/t1-2.md")

        before = next(line for line in original.decode("utf-8").splitlines() if line.startswith("| `T1.2` |"))
        after = next(line for line in plan.candidate.decode("utf-8").splitlines() if line.startswith("| `T1.2` |"))
        self.assertEqual(before.split("|")[1:3], after.split("|")[1:3])
        self.assertEqual(before.split("|")[4:5], after.split("|")[4:5])
        self.assertEqual(" `planned` ", after.split("|")[3])
        self.assertEqual(" [plan](docs/superpowers/plans/t1-2.md) ", after.split("|")[6])
        self.assertEqual(before.split("|")[7:], after.split("|")[7:])
        self.assertEqual("Requested lifecycle transition from `specified` to `planned`.", plan.rationale)

    def test_transition_accepts_stage_specific_specification_and_review_links(self) -> None:
        root = self.copy_fixture_root()
        write_active_design(root, "docs/superpowers/specs/t1-1-design.md", children=("T1.1",))
        write_active_design(root, "docs/superpowers/specs/t1-design.md", children=("T1.2",), status="draft")
        replace_text(
            root,
            "BACKLOG.md",
            "[design](docs/superpowers/specs/t1-design.md) | [plan](docs/superpowers/plans/t1-1.md)",
            "[design](docs/superpowers/specs/t1-1-design.md) | [plan](docs/superpowers/plans/t1-1.md)",
        )
        replace_text(root, "docs/superpowers/plans/t1-1.md", "`docs/superpowers/specs/t1-design.md`", "`docs/superpowers/specs/t1-1-design.md`")
        replace_text(
            root,
            "BACKLOG.md",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | [design](docs/superpowers/specs/t1-design.md)",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `queued` | `T1.1` | —",
        )
        self.assertEqual((), audit_repository(root).findings)

        designing = plan_transition(root, "T1.2", "designing", expect="queued", specification="docs/superpowers/specs/t1-design.md")

        self.assertIn("| `designing` | `T1.1` | [design](docs/superpowers/specs/t1-design.md)", designing.candidate.decode("utf-8"))

        root = self.copy_fixture_root()
        write_active_plan(root, "docs/superpowers/plans/t1-2.md", status="completed", completion_evidence=".superpowers/sdd/t1-2/completion.md")
        write_evidence(root, ".superpowers/sdd/t1-2/completion.md", child="T1.2", gate=None)
        write_evidence(root, ".superpowers/sdd/t1-2/review.md", child="T1.2", gate=None, kind="review", result="accepted")
        replace_text(
            root,
            "BACKLOG.md",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | [design](docs/superpowers/specs/t1-design.md) | — |",
            (
                "| `T1.2` | Typed parser, status report, and versioned JSON | `implemented` | `T1.1` | "
                "[design](docs/superpowers/specs/t1-design.md) | [plan](docs/superpowers/plans/t1-2.md) |"
            ),
        )
        run_git(root, "add", "--", "BACKLOG.md", "docs", ".superpowers")
        run_git(root, "commit", "-qm", "Implemented fixture")

        reviewed = plan_transition(root, "T1.2", "reviewed", expect="implemented", review=".superpowers/sdd/t1-2/review.md")

        self.assertIn("| 0/1 | [review](.superpowers/sdd/t1-2/review.md) |", reviewed.candidate.decode("utf-8"))

    def test_transition_rejects_links_outside_the_target_stage_or_with_table_delimiters(self) -> None:
        root = self.copy_fixture_root()
        self.assert_refusal("mutation.link", plan_transition, root, "T1.2", "planned", expect="specified", specification="docs/superpowers/specs/t1-design.md")
        self.assert_refusal("mutation.link", plan_transition, root, "T1.2", "planned", expect="specified", plan="bad|path")
        self.assert_refusal("mutation.link", plan_transition, root, "T1.2", "planned", expect="specified", plan="bad\npath")

    def test_reviewed_reopen_clears_only_review_and_records_rationale(self) -> None:
        root = self.copy_fixture_root()
        replace_text(
            root,
            "BACKLOG.md",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `specified` |",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `reviewed` |",
        )
        replace_text(
            root,
            "BACKLOG.md",
            "| `T1.2` | Typed parser, status report, and versioned JSON | `reviewed` | `T1.1` | [design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — |",
            (
                "| `T1.2` | Typed parser, status report, and versioned JSON | `reviewed` | `T1.1` | "
                "[design](docs/superpowers/specs/t1-design.md) | [plan](docs/superpowers/plans/t1-2.md) | "
                "0/1 | [review](.superpowers/sdd/t1-2/review.md) |"
            ),
        )
        write_active_plan(root, "docs/superpowers/plans/t1-2.md", status="completed", completion_evidence=".superpowers/sdd/t1-2/completion.md")
        write_evidence(root, ".superpowers/sdd/t1-2/completion.md", child="T1.2", gate=None)
        write_evidence(root, ".superpowers/sdd/t1-2/review.md", child="T1.2", gate=None, kind="review", result="accepted")
        run_git(root, "add", "--", "BACKLOG.md", "docs", ".superpowers")
        run_git(root, "commit", "-qm", "Reviewed fixture")

        plan = plan_transition(root, "T1.2", "implemented", expect="reviewed")

        self.assertIn("| `T1.2` | Typed parser, status report, and versioned JSON | `implemented` |", plan.candidate.decode("utf-8"))
        self.assertIn("| 0/1 | — | — | — |", plan.candidate.decode("utf-8"))
        self.assertEqual("Requested lifecycle transition from `reviewed` to `implemented`.", plan.rationale)

    def test_suspend_and_resume_round_trip_all_nonsuspended_states(self) -> None:
        root = self.copy_fixture_root()
        self.assertEqual(
            {"queued", "designing", "specified", "planned", "in_progress", "implemented", "reviewed", "verified"},
            _NONSUSPENDED,
        )
        for target in ("blocked", "deferred"):
            with self.subTest(target=target):
                suspended = plan_suspend(root, "T1.2", target, expect="specified", reason="Awaiting evidence")
                candidate = suspended.candidate.decode("utf-8")
                self.assertIn(f"| `{target}` |", candidate)
                self.assertIn("| `specified` | Awaiting evidence |", candidate)
                self.assertEqual(f"Suspended `specified` child as `{target}`: Awaiting evidence", suspended.rationale)
                (root / "BACKLOG.md").write_bytes(suspended.candidate)
                resumed = plan_resume(root, "T1.2", expect=target, resume="specified", reason="Evidence received")
                self.assertIn("| `specified` |", resumed.candidate.decode("utf-8"))
                self.assertIn("| — | — |", resumed.candidate.decode("utf-8"))
                self.assertNotIn("Evidence received", resumed.candidate.decode("utf-8"))
                self.assertEqual(f"Resumed `specified` child from `{target}`: Evidence received", resumed.rationale)
                (root / "BACKLOG.md").write_bytes(resumed.candidate)

    def test_suspend_and_resume_refuse_invalid_reasons_and_stale_resume(self) -> None:
        root = self.copy_fixture_root()
        for reason in ("", " reason", "reason ", "bad\nreason", "bad\rreason", "bad|reason"):
            with self.subTest(reason=reason):
                self.assert_refusal("mutation.reason", plan_suspend, root, "T1.2", "blocked", expect="specified", reason=reason)
        suspended = plan_suspend(root, "T1.2", "blocked", expect="specified", reason="Awaiting evidence")
        (root / "BACKLOG.md").write_bytes(suspended.candidate)
        self.assert_refusal("mutation.expected-status", plan_resume, root, "T1.2", expect="deferred", resume="specified", reason="Resume")
        self.assert_refusal("mutation.resume", plan_resume, root, "T1.2", expect="blocked", resume="planned", reason="Resume")
