from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from io import StringIO
import json
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

from backlog.model import GitState  # noqa: E402  # ty: ignore[unresolved-import]


@dataclass(frozen=True, slots=True)
class CliResult:
    code: int
    stdout: str
    stderr: str


def load_cli() -> object:
    path = SCRIPTS / "backlog_status.py"
    specification = importlib.util.spec_from_file_location("backlog_status_cli", path)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load backlog status CLI")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class BacklogStatusCliTests(unittest.TestCase):
    def malformed_fixture(self) -> Path:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        shutil.copytree(FIXTURE, temporary, dirs_exist_ok=True)
        backlog = temporary / "BACKLOG.md"
        backlog.write_text(backlog.read_text(encoding="utf-8").replace("0/1", "0/x", 1), encoding="utf-8")
        return temporary

    def run_cli(self, argv: list[str], *, root: Path) -> CliResult:
        module = load_cli()
        output = StringIO()
        errors = StringIO()
        with patch.object(module, "observe_git", return_value=GitState("main", False, ())):
            code = module.main(  # ty: ignore[unresolved-attribute]
                argv, root=root, stdout=output, stderr=errors
            )
        return CliResult(code, output.getvalue(), errors.getvalue())

    def test_status_writes_human_report_to_stdout(self) -> None:
        status = self.run_cli(["status"], root=FIXTURE)

        self.assertEqual(0, status.code)
        self.assertIn("Repository: xplane-fdau", status.stdout)
        self.assertEqual("", status.stderr)

    def test_status_json_writes_schema_version_one_in_source_order(self) -> None:
        status = self.run_cli(["status", "--json"], root=FIXTURE)

        self.assertEqual(0, status.code)
        self.assertEqual("", status.stderr)
        payload = json.loads(status.stdout)
        self.assertEqual(1, payload["schema_version"])
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["findings"])
        self.assertIsNone(payload["recommendation"])
        self.assertNotIn("timestamp", payload)
        self.assertEqual(["T1.1", "T1.2"], [child["id"] for child in payload["roadmap"]["local_children"]])
        self.assertEqual(["T1.1", "T1.2"], [child["id"] for child in payload["backlog"]["children"]])

    def test_current_repository_status_reports_human_and_json(self) -> None:
        human = self.run_cli(["status"], root=ROOT)

        self.assertEqual(0, human.code, human.stderr)
        self.assertIn("64 local children", human.stdout)
        for line in (
            "D1.1  specified  dependency-ready=no  gates=0/4",
            "D1.2  specified  dependency-ready=no  gates=0/4",
            "D1.3  specified  dependency-ready=no  gates=0/4",
            "statement=successful D1.3 verification makes the statusless `I1.0` "
            "handoff condition eligible to be reported as the next action without "
            "changing `I1.1`, `I1.2`, G1, release, push, tag, or publication authorization.",
        ):
            self.assertIn(line, human.stdout)

        machine = self.run_cli(["status", "--json"], root=ROOT)

        self.assertEqual(0, machine.code, machine.stderr)
        payload = json.loads(machine.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["findings"])
        self.assertIsNone(payload["recommendation"])
        self.assertEqual(64, len(payload["roadmap"]["local_children"]))
        self.assertEqual(64, len(payload["backlog"]["children"]))
        d1_children = {child["id"]: child for child in payload["backlog"]["children"] if child["id"].startswith("D1.")}
        self.assertEqual(["D1.1", "D1.2", "D1.3"], list(d1_children))
        expected_dependencies = {"D1.1": ["T1.2"], "D1.2": ["D1.1"], "D1.3": ["D1.2"]}
        expected_statements = {
            "D1.1": [
                "the canonical design has approved governance metadata and no unresolved "
                "placeholder, contradiction, ambiguity, or load-bearing review finding;",
                "canonical JSON, hashing, identity, provenance, measurement, binding, raw "
                "observation, sample, frame, clock/timing, validity, quality, schema, fixture, "
                "and Python/native conformance decisions are exact and versioned;",
                "ownership and dependency direction remain consistent with the approved "
                "scope amendment and distinguish FDAU acquisition quality from q4xpcc "
                "operational policy and findings; and",
                "the approved design is linked from `C1.1` through `C4.4`, and those "
                "children advance only to `specified`, with zero delivery gates satisfied "
                "and no implementation-plan, review, artifact, or release evidence.",
            ],
            "D1.2": [
                "one approved design fixes every A1/R1/P1 contract shape and policy needed by the four q4xpcc Phase 24A Slice 2 plans;",
                "every family has an exact identity/version boundary, owned fields, "
                "invariants, references, error outcomes, and intended future schema/fixture "
                "path;",
                "deployment, revision pinning, release-artifact hashes, delivered-file "
                "hashes, conformance, and no-divergent-subset proof are explicit without "
                "requiring a current release artifact; and",
                "independent review finds no unresolved load-bearing ambiguity, the "
                "approved contract-only design is recorded as binding architecture input "
                "for future A1, R1, and P1 specifications, and those implementation "
                "children remain `queued` with zero delivery gates satisfied and no "
                "implementation, artifact, or release claim.",
            ],
            "D1.3": [
                "D1.1 and D1.2 are verified with committed review evidence and no unresolved load-bearing finding;",
                "`HANDOFF.md` and the concise q4xpcc brief agree with the approved designs and distinguish design readiness from implementation and adoption;",
                "the brief is emitted from a clean committed state and identifies its exact local HEAD revision; and",
                "successful D1.3 verification makes the statusless `I1.0` handoff "
                "condition eligible to be reported as the next action without changing "
                "`I1.1`, `I1.2`, G1, release, push, tag, or publication authorization.",
            ],
        }
        for child_id, child in d1_children.items():
            self.assertEqual("specified", child["status"])
            self.assertEqual(expected_dependencies[child_id], child["dependencies"])
            self.assertEqual(
                "docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md",
                child["specification"],
            )
            self.assertIsNone(child["plan"])
            self.assertEqual(0, child["gates"]["satisfied"])
            self.assertEqual(4, child["gates"]["total"])
            self.assertEqual(expected_statements[child_id], [gate["statement"] for gate in child["gates"]["items"]])
            self.assertEqual([False, False, False, False], [gate["satisfied"] for gate in child["gates"]["items"]])
            self.assertTrue(all(gate["evidence"] == [] for gate in child["gates"]["items"]))
            self.assertIsNone(child["review_evidence"])
            self.assertIsNone(child["resume_state"])
            self.assertIsNone(child["reason"])
            self.assertFalse(child["dependency_ready"])

        roadmap_ids = [child["id"] for child in payload["roadmap"]["local_children"]]
        backlog_ids = [child["id"] for child in payload["backlog"]["children"]]
        boundaries = {boundary["id"]: boundary for boundary in payload["roadmap"]["external_boundaries"]}
        self.assertNotIn("I1.0", roadmap_ids)
        self.assertNotIn("I1.0", backlog_ids)
        self.assertEqual(
            {
                "id": "I1.0",
                "kind": "external_boundary",
                "title": "q4xpcc Phase 24A specification and plan reconciliation",
                "owner": "q4xpcc",
                "handoff_condition": "Phase 24A specification and plan reconciliation may begin after `D1.3`.",
            },
            boundaries["I1.0"],
        )

    def test_unknown_command_is_invalid_usage(self) -> None:
        invalid = self.run_cli(["audit"], root=FIXTURE)

        self.assertEqual(2, invalid.code)
        self.assertIn("invalid choice", invalid.stderr)

    def test_malformed_repository_writes_parse_context_to_stderr(self) -> None:
        malformed = self.run_cli(["status"], root=self.malformed_fixture())

        self.assertEqual(1, malformed.code)
        self.assertEqual("", malformed.stdout)
        self.assertRegex(malformed.stderr, r"BACKLOG.md:[0-9]+:")


if __name__ == "__main__":
    unittest.main()
