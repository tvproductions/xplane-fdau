from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
sys.path.insert(0, str(SCRIPTS))

from backlog.model import (  # noqa: E402  # ty: ignore[unresolved-import]
    AuditLoad,
    AuditPolicy,
    AuditSources,
    CHILD_STATUSES,
    GATE_STATES,
    NODE_KINDS,
    BacklogChild,
    GateSummary,
    HistoricalAdmission,
    RepositorySnapshot,
    Roadmap,
    Backlog,
    Artifacts,
    RoadmapChild,
    SourceLocation,
)


class BacklogStatusModelTests(unittest.TestCase):
    def test_controlled_vocabularies_are_exact(self) -> None:
        self.assertEqual(
            ("milestone", "epic", "local_child", "release_gate", "external_boundary"),
            NODE_KINDS,
        )
        self.assertEqual(
            (
                "queued",
                "designing",
                "specified",
                "planned",
                "in_progress",
                "implemented",
                "reviewed",
                "verified",
                "blocked",
                "deferred",
                "released",
            ),
            CHILD_STATUSES,
        )
        self.assertEqual(("waiting", "ready", "satisfied"), GATE_STATES)

    def test_models_are_frozen_and_preserve_tuple_order(self) -> None:
        location = SourceLocation("ROADMAP.md", 12)
        child = RoadmapChild(
            id="T1.2",
            kind="local_child",
            epic="T1",
            title="Typed parser, status report, and versioned JSON",
            dependencies=("T1.1",),
            external_prerequisite=None,
            source=location,
        )
        backlog_child = BacklogChild(
            id="T1.2",
            status="specified",
            dependencies=("T1.1",),
            specification="docs/superpowers/specs/t1.md",
            plan=None,
            gates=GateSummary(0, 4, ()),
            review_evidence=None,
            resume_state=None,
            reason=None,
            dependency_ready=True,
            source=SourceLocation("BACKLOG.md", 20),
        )
        self.assertEqual(("T1.1",), child.dependencies)
        self.assertTrue(backlog_child.dependency_ready)
        with self.assertRaises(FrozenInstanceError):
            child.title = "changed"  # type: ignore[misc]

    def test_audit_load_and_policy_models_are_frozen(self) -> None:
        root = Path("fixture").resolve()
        snapshot = RepositorySnapshot(
            root,
            Roadmap((), (), (), (), ()),
            Backlog(None, (), (), "BACKLOG.md"),
            Artifacts((), (), ()),
        )
        policy = AuditPolicy((HistoricalAdmission("D1.1", "docs/plan.md", "a" * 64),))
        load = AuditLoad(snapshot, (), frozenset(), AuditSources.empty(), policy)

        self.assertEqual("D1.1", load.policy.historical[0].child if load.policy else None)
        with self.assertRaises(FrozenInstanceError):
            load.policy = None  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
