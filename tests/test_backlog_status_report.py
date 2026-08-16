from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
from unittest.mock import patch
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
FIXTURE = ROOT / "tests/fixtures/backlog_status/valid"
sys.path.insert(0, str(SCRIPTS))

from backlog.model import Finding, GitState, RecentCommit, Recommendation  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.parse import parse_repository  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.report import (  # noqa: E402  # ty: ignore[unresolved-import]
    build_report,
    observe_git,
    render_json,
    render_human,
    with_dependency_readiness,
)


class HumanStatusReportTests(unittest.TestCase):
    def test_dependency_readiness_uses_only_verified_dependencies(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))

        children = {child.id: child for child in snapshot.backlog.children}

        self.assertTrue(children["T1.2"].dependency_ready)

    def test_dependency_readiness_rejects_unverified_child_states(self) -> None:
        snapshot = parse_repository(FIXTURE)
        first, second = snapshot.backlog.children
        for status in ("reviewed", "implemented", "planned"):
            with self.subTest(status=status):
                backlog = replace(snapshot.backlog, children=(replace(first, status=status), second))
                updated = with_dependency_readiness(replace(snapshot, backlog=backlog))
                children = {child.id: child for child in updated.backlog.children}
                self.assertFalse(children["T1.2"].dependency_ready)

    def test_milestone_dependency_is_ready_without_git_history(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))

        children = {child.id: child for child in snapshot.backlog.children}

        self.assertTrue(children["T1.1"].dependency_ready)

    def test_human_status_contains_every_node_child_artifact_gate_and_git_fact(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        git = GitState("main", False, (RecentCommit("abc1234", "fixture commit"),))

        output = render_human(build_report(snapshot, git))

        for value in ("M0", "T1", "T1.1", "T1.2", "G1", "I1.1"):
            self.assertIn(value, output)
        self.assertIn("Authority: roadmap=ROADMAP.md backlog=BACKLOG.md", output)
        self.assertIn("Active child: —", output)
        self.assertIn("T1.2  specified  dependency-ready=yes  gates=0/1", output)
        self.assertIn("title=Fixture contract adoption", output)
        self.assertIn("docs/superpowers/specs/t1-design.md", output)
        self.assertIn("Git: branch=main dirty=no", output)
        self.assertIn("Findings: none", output)
        self.assertIn("Recommendation: unavailable until T1.4", output)
        self.assertTrue(output.endswith("\n"))
        self.assertFalse(output.endswith("\n\n"))

    def test_observe_git_uses_only_read_only_commands(self) -> None:
        responses = iter(("main\n", " M BACKLOG.md\n", "abcdef\x00first\n012345\x00second\n"))

        with patch("backlog.report.subprocess.run") as run:
            run.side_effect = [type("Completed", (), {"stdout": response})() for response in responses]
            state = observe_git(FIXTURE, limit=2)

        self.assertEqual("main", state.branch)
        self.assertTrue(state.dirty)
        self.assertEqual(
            (RecentCommit("abcdef", "first"), RecentCommit("012345", "second")),
            state.recent_commits,
        )
        self.assertEqual(
            [
                (("git", "-C", str(FIXTURE), "branch", "--show-current"),),
                (("git", "-C", str(FIXTURE), "status", "--porcelain"),),
                (("git", "-C", str(FIXTURE), "log", "-2", "--format=%H%x00%s"),),
            ],
            [call.args for call in run.call_args_list],
        )

    def test_observe_git_leaves_the_current_checkout_unchanged(self) -> None:
        def repository_state() -> tuple[str, str]:
            head = subprocess.run(
                ("git", "-C", str(ROOT), "rev-parse", "HEAD"),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            ).stdout
            status = subprocess.run(
                ("git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=all"),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            ).stdout
            return head, status

        before = repository_state()

        observed = observe_git(ROOT)

        self.assertEqual(before, repository_state())
        self.assertEqual(before[0].strip(), observed.recent_commits[0].sha)


class JsonStatusReportTests(unittest.TestCase):
    def test_json_serializes_populated_finding_and_recommendation_with_null_optionals(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        report = replace(
            build_report(snapshot, GitState("main", False, ())),
            findings=(
                Finding(
                    code="MISSING_EVIDENCE",
                    severity="warning",
                    path="BACKLOG.md",
                    line=None,
                    node=None,
                    gate=None,
                    message="A synthetic warning.",
                ),
            ),
            recommendation=Recommendation(
                action="wait",
                child=None,
                reason="A synthetic recommendation.",
                command=None,
            ),
        )

        payload = json.loads(render_json(report), object_pairs_hook=dict)

        self.assertEqual(["code", "severity", "path", "line", "node", "gate", "message"], list(payload["findings"][0]))
        self.assertEqual(
            {
                "code": "MISSING_EVIDENCE",
                "severity": "warning",
                "path": "BACKLOG.md",
                "line": None,
                "node": None,
                "gate": None,
                "message": "A synthetic warning.",
            },
            payload["findings"][0],
        )
        self.assertEqual(["action", "child", "reason", "command"], list(payload["recommendation"]))
        self.assertEqual(
            {
                "action": "wait",
                "child": None,
                "reason": "A synthetic recommendation.",
                "command": None,
            },
            payload["recommendation"],
        )

    def test_json_schema_version_one_is_exact_and_excludes_source_locations(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        report = build_report(snapshot, GitState("main", False, (RecentCommit("abc1234", "fixture commit"),)))

        rendered = render_json(report)
        payload = json.loads(rendered, object_pairs_hook=dict)

        self.assertEqual(
            [
                "schema_version",
                "repository",
                "valid",
                "roadmap",
                "backlog",
                "artifacts",
                "findings",
                "recommendation",
                "git",
            ],
            list(payload),
        )
        self.assertEqual(1, payload["schema_version"])
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["findings"])
        self.assertIsNone(payload["recommendation"])
        self.assertTrue(rendered.endswith("\n"))
        self.assertFalse(rendered.endswith("\n\n"))
        self.assertEqual(["id", "kind", "title"], list(payload["roadmap"]["milestones"][0]))
        self.assertEqual(["id", "kind", "title", "children"], list(payload["roadmap"]["epics"][0]))
        self.assertEqual(
            ["id", "kind", "epic", "title", "dependencies", "external_prerequisite"],
            list(payload["roadmap"]["local_children"][0]),
        )
        self.assertEqual(["id", "kind", "title", "dependencies"], list(payload["roadmap"]["release_gates"][0]))
        self.assertEqual(
            ["id", "kind", "title", "owner", "handoff_condition"],
            list(payload["roadmap"]["external_boundaries"][0]),
        )
        self.assertEqual(["active_child", "children", "release_gates"], list(payload["backlog"]))
        self.assertEqual(
            ["id", "status", "dependencies", "specification", "plan", "gates", "review_evidence", "resume_state", "reason", "dependency_ready"],
            list(payload["backlog"]["children"][0]),
        )
        self.assertEqual(["satisfied", "total", "items"], list(payload["backlog"]["children"][0]["gates"]))
        self.assertEqual(["ordinal", "statement", "satisfied", "evidence"], list(payload["backlog"]["children"][0]["gates"]["items"][0]))
        self.assertEqual(["id", "state", "evidence"], list(payload["backlog"]["release_gates"][0]))
        self.assertEqual(["specifications", "plans", "historical"], list(payload["artifacts"]))
        self.assertEqual(["path", "governance", "status", "epic", "children", "approval"], list(payload["artifacts"]["specifications"][0]))
        self.assertEqual(
            ["path", "governance", "status", "child", "source_specification", "approval", "completion_evidence"],
            list(payload["artifacts"]["plans"][0]),
        )
        self.assertEqual(["path", "governance", "status", "disposition"], list(payload["artifacts"]["historical"][0]))
        self.assertEqual(["branch", "dirty", "recent_commits"], list(payload["git"]))
        self.assertEqual(["sha", "subject"], list(payload["git"]["recent_commits"][0]))
        self.assertNotIn('"source":', rendered)
        self.assertEqual(
            """{
  "schema_version": 1,
  "repository": "xplane-fdau",
  "valid": true,
  "roadmap": {
    "milestones": [
      {
        "id": "M0",
        "kind": "milestone",
        "title": "Frozen migration baseline"
      }
    ],
    "epics": [
      {
        "id": "T1",
        "kind": "epic",
        "title": "Repository governance tooling",
        "children": [
          "T1.1",
          "T1.2"
        ]
      }
    ],
    "local_children": [
      {
        "id": "T1.1",
        "kind": "local_child",
        "epic": "T1",
        "title": "Markdown authority contract and explicit inventory normalization",
        "dependencies": [
          "M0"
        ],
        "external_prerequisite": null
      },
      {
        "id": "T1.2",
        "kind": "local_child",
        "epic": "T1",
        "title": "Typed parser, status report, and versioned JSON",
        "dependencies": [
          "T1.1"
        ],
        "external_prerequisite": null
      }
    ],
    "release_gates": [
      {
        "id": "G1",
        "kind": "release_gate",
        "title": "Canonical vertical-slice reconciliation",
        "dependencies": [
          "T1.2"
        ]
      }
    ],
    "external_boundaries": [
      {
        "id": "I1.1",
        "kind": "external_boundary",
        "title": "Fixture contract adoption",
        "owner": "Fixture consumer",
        "handoff_condition": "Adoption begins after `T1.2`."
      }
    ]
  },
  "backlog": {
    "active_child": null,
    "children": [
      {
        "id": "T1.1",
        "status": "verified",
        "dependencies": [
          "M0"
        ],
        "specification": "docs/superpowers/specs/t1-design.md",
        "plan": "docs/superpowers/plans/t1-1.md",
        "gates": {
          "satisfied": 1,
          "total": 1,
          "items": [
            {
              "ordinal": 1,
              "statement": "Frozen contract is verified and remains explicit.",
              "satisfied": true,
              "evidence": [
                ".superpowers/sdd/t1-1/gate-1.md"
              ]
            }
          ]
        },
        "review_evidence": ".superpowers/sdd/t1-1/review.md",
        "resume_state": null,
        "reason": null,
        "dependency_ready": true
      },
      {
        "id": "T1.2",
        "status": "specified",
        "dependencies": [
          "T1.1"
        ],
        "specification": "docs/superpowers/specs/t1-design.md",
        "plan": null,
        "gates": {
          "satisfied": 0,
          "total": 1,
          "items": [
            {
              "ordinal": 1,
              "statement": "Frozen parser remains open.",
              "satisfied": false,
              "evidence": []
            }
          ]
        },
        "review_evidence": null,
        "resume_state": null,
        "reason": null,
        "dependency_ready": true
      }
    ],
    "release_gates": [
      {
        "id": "G1",
        "state": "waiting",
        "evidence": []
      }
    ]
  },
  "artifacts": {
    "specifications": [
      {
        "path": "docs/superpowers/specs/t1-design.md",
        "governance": "active",
        "status": "approved",
        "epic": "T1",
        "children": [
          "T1.1",
          "T1.2"
        ],
        "approval": "2026-08-15 — Fixture owner"
      }
    ],
    "plans": [
      {
        "path": "docs/superpowers/plans/t1-1.md",
        "governance": "active",
        "status": "completed",
        "child": "T1.1",
        "source_specification": "docs/superpowers/specs/t1-design.md",
        "approval": "2026-08-15 — Fixture owner",
        "completion_evidence": ".superpowers/sdd/t1-1/completion.md"
      }
    ],
    "historical": [
      {
        "path": "docs/superpowers/plans/historical-plan.md",
        "governance": "historical",
        "status": "completed",
        "disposition": "Completed fixture plan."
      },
      {
        "path": "docs/superpowers/specs/historical-design.md",
        "governance": "historical",
        "status": "superseded",
        "disposition": "Superseded fixture design."
      }
    ]
  },
  "findings": [],
  "recommendation": null,
  "git": {
    "branch": "main",
    "dirty": false,
    "recent_commits": [
      {
        "sha": "abc1234",
        "subject": "fixture commit"
      }
    ]
  }
}\n""",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
