from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
from typing import cast
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
FIXTURE = ROOT / "tests/fixtures/backlog_status/valid"
sys.path.insert(0, str(SCRIPTS))

from backlog.model import ChildStatus, Finding  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.next_action import recommend_next  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.parse import parse_repository  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.report import with_dependency_readiness  # noqa: E402  # ty: ignore[unresolved-import]


class NextActionTests(unittest.TestCase):
    def selected_snapshot(
        self,
        status: str,
        *,
        resume_state: str | None = None,
        reason: str | None = None,
    ):
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        children = tuple(
            replace(
                child,
                status=cast(ChildStatus, status),
                resume_state=cast(ChildStatus | None, resume_state),
                reason=reason,
            )
            if child.id == "T1.2"
            else child
            for child in snapshot.backlog.children
        )
        backlog = replace(snapshot.backlog, active_child="T1.2", children=children)
        return replace(snapshot, backlog=backlog)

    def test_selected_child_maps_every_lifecycle_to_its_exact_action(self) -> None:
        cases = {
            "queued": ("refine_spec", "superpowers:brainstorming"),
            "designing": ("request_spec_review", "superpowers:requesting-code-review"),
            "specified": ("write_plan", "superpowers:writing-plans"),
            "planned": ("execute_plan", "superpowers:executing-plans"),
            "in_progress": ("execute_plan", "superpowers:executing-plans"),
            "implemented": ("request_review", "superpowers:requesting-code-review"),
            "reviewed": ("verify", "gzs-quality-gate"),
        }

        for status, (action, command_fragment) in cases.items():
            with self.subTest(status=status):
                recommendation = recommend_next(self.selected_snapshot(status), ())
                self.assertEqual(action, recommendation.action)
                self.assertEqual("T1.2", recommendation.child)
                self.assertTrue(recommendation.reason)
                self.assertIsNotNone(recommendation.command)
                self.assertIn(command_fragment, recommendation.command or "")

        for status in ("verified", "released"):
            with self.subTest(status=status):
                recommendation = recommend_next(self.selected_snapshot(status), ())
                self.assertEqual("wait", recommendation.action)
                self.assertEqual("T1.2", recommendation.child)
                self.assertTrue(recommendation.reason)
                self.assertIsNone(recommendation.command)

    def test_unselected_child_uses_roadmap_order_and_skips_terminal_children(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        snapshot = replace(snapshot, backlog=replace(snapshot.backlog, children=tuple(reversed(snapshot.backlog.children))))

        recommendation = recommend_next(snapshot, ())

        self.assertEqual("write_plan", recommendation.action)
        self.assertEqual("T1.2", recommendation.child)

    def test_unselected_child_skips_dependency_unready_work(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        children = tuple(replace(child, dependency_ready=False) if child.id == "T1.2" else child for child in snapshot.backlog.children)
        snapshot = replace(snapshot, backlog=replace(snapshot.backlog, children=children))

        recommendation = recommend_next(snapshot, ())

        self.assertEqual("wait", recommendation.action)
        self.assertIsNone(recommendation.child)
        self.assertIsNone(recommendation.command)

    def test_recommendation_never_selects_a_nonlocal_roadmap_node(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        children = tuple(replace(child, status="verified") for child in snapshot.backlog.children)
        snapshot = replace(snapshot, backlog=replace(snapshot.backlog, children=children))

        recommendation = recommend_next(snapshot, ())

        self.assertIsNone(recommendation.child)
        self.assertNotIn(recommendation.child, {"M0", "T1", "G1", "I1.1"})

    def test_audit_error_blocks_before_selected_or_unselected_work(self) -> None:
        finding = Finding("fixture.error", "error", "BACKLOG.md", 1, "T1.2", None, "Broken fixture")

        recommendation = recommend_next(self.selected_snapshot("specified"), (finding,))

        self.assertEqual("wait", recommendation.action)
        self.assertEqual("T1.2", recommendation.child)
        self.assertEqual(
            "uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit",
            recommendation.command,
        )

    def test_warning_does_not_block_actionable_work(self) -> None:
        finding = Finding("fixture.warning", "warning", "BACKLOG.md", 1, None, None, "Fixture warning")

        recommendation = recommend_next(self.selected_snapshot("specified"), (finding,))

        self.assertEqual(("write_plan", "T1.2"), (recommendation.action, recommendation.child))

    def test_selected_suspension_waits_with_exact_reason_without_substitution(self) -> None:
        for status in ("blocked", "deferred"):
            with self.subTest(status=status):
                reason = f"{status} fixture prerequisite"
                recommendation = recommend_next(
                    self.selected_snapshot(status, resume_state="specified", reason=reason),
                    (),
                )
                self.assertEqual("wait", recommendation.action)
                self.assertEqual("T1.2", recommendation.child)
                self.assertEqual(reason, recommendation.reason)
                self.assertIsNone(recommendation.command)


if __name__ == "__main__":
    unittest.main()
