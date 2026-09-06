from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, replace
import importlib.util
from io import StringIO
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
FIXTURE = ROOT / "tests/fixtures/backlog_status/valid"
sys.path.insert(0, str(SCRIPTS))

from tests.backlog_audit_support import audit_fixture, replace_text, run_git, write_evidence  # noqa: E402
from backlog.audit import load_audit  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.model import Finding, GitState  # noqa: E402  # ty: ignore[unresolved-import]


@dataclass(frozen=True, slots=True)
class CliResult:
    code: int
    stdout: str
    stderr: str


def load_cli() -> ModuleType:
    path = SCRIPTS / "backlog_status.py"
    specification = importlib.util.spec_from_file_location("backlog_status_cli", path)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load backlog status CLI")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class BacklogStatusCliTests(unittest.TestCase):
    def fixture_root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        audit_fixture(root)
        return root

    def malformed_fixture(self) -> Path:
        root = self.fixture_root()
        replace_text(root, "BACKLOG.md", "0/1", "0/x")
        return root

    def run_cli(self, argv: list[str], *, root: Path, mock_git: bool = True) -> CliResult:
        module = load_cli()
        output = StringIO()
        errors = StringIO()
        git_context = patch.object(module, "observe_git", return_value=GitState("main", False, ())) if mock_git else nullcontext()
        with git_context:
            code = module.main(argv, root=root, stdout=output, stderr=errors)
        return CliResult(code, output.getvalue(), errors.getvalue())

    def test_status_writes_human_report_to_stdout(self) -> None:
        status = self.run_cli(["status"], root=self.fixture_root())

        self.assertEqual(0, status.code)
        self.assertIn("Repository: xplane-fdau", status.stdout)
        self.assertEqual("", status.stderr)

    def test_status_json_writes_schema_version_one_in_source_order(self) -> None:
        status = self.run_cli(["status", "--json"], root=self.fixture_root())

        self.assertEqual(0, status.code)
        self.assertEqual("", status.stderr)
        payload = json.loads(status.stdout)
        self.assertEqual(1, payload["schema_version"])
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["findings"])
        self.assertEqual("write_plan", payload["recommendation"]["action"])
        self.assertEqual("T1.2", payload["recommendation"]["child"])
        self.assertNotIn("timestamp", payload)
        self.assertEqual(["T1.1", "T1.2"], [child["id"] for child in payload["roadmap"]["local_children"]])
        self.assertEqual(["T1.1", "T1.2"], [child["id"] for child in payload["backlog"]["children"]])

    def test_current_repository_status_reports_human_and_json(self) -> None:
        human = self.run_cli(["status"], root=ROOT, mock_git=False)

        self.assertEqual(0, human.code, human.stderr)
        self.assertIn("64 local children", human.stdout)
        for line in (
            "D1.1  verified  dependency-ready=yes  gates=4/4",
            "D1.2  verified  dependency-ready=yes  gates=4/4",
            "D1.3  verified  dependency-ready=yes  gates=4/4",
            "statement=successful D1.3 verification makes the statusless `I1.0` "
            "handoff condition eligible to be reported as the next action without "
            "changing `I1.1`, `I1.2`, G1, release, push, tag, or publication authorization.",
        ):
            self.assertIn(line, human.stdout)

        machine = self.run_cli(["status", "--json"], root=ROOT, mock_git=False)

        self.assertEqual(0, machine.code, machine.stderr)
        payload = json.loads(machine.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["findings"])
        self.assertEqual("execute_plan", payload["recommendation"]["action"])
        self.assertEqual("T1.4", payload["recommendation"]["child"])
        self.assertEqual(64, len(payload["roadmap"]["local_children"]))
        self.assertEqual(64, len(payload["backlog"]["children"]))
        d1_children = {child["id"]: child for child in payload["backlog"]["children"] if child["id"].startswith("D1.")}
        self.assertEqual(["D1.1", "D1.2", "D1.3"], list(d1_children))
        expected_dependencies = {"D1.1": ["T1.2"], "D1.2": ["D1.1"], "D1.3": ["D1.2"]}
        expected_dependency_readiness = {"D1.1": True, "D1.2": True, "D1.3": True}
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
                "this one approved design fixes the A1/R1/P1 contract shapes and policies needed by all four q4xpcc Phase 24A "
                "Slice 2 plans, including acquisition, continuity, fan-out, recording, recovery, replay, native-FDR projection, "
                "deployment, and conformance planning surfaces;",
                "every family has an exact identity/version boundary, fields, invariants, references, runtime outcomes, error "
                "boundary, delivery ownership boundary, and future schema/conformance path, with closed failure codes and "
                "deterministic validation/causal precedence;",
                "installed-wheel and reproducibly bundled deployment, independently trusted expected "
                "version/revision/artifact/conformance pins, mode-specific metadata evidence, delivered-file hashes, "
                "conformance, and closed-world no-divergent-subset proof are explicit without requiring or fabricating a "
                "current release; and",
                "independent review reports no unresolved load-bearing ambiguity; native FDR, ARINC, FDM/FOQA, q4xpcc, and "
                "external-client boundaries remain consistent with the approved scope amendment; the approved contract-only "
                "design is recorded as binding input for later A1/R1/P1 specifications; and every implementation, schema, "
                "fixture, artifact, adoption, release, push, tag, and publication gate remains unsatisfied without advancing "
                "any A1, R1, P1, S, or F1 child.",
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
            self.assertEqual("verified", child["status"])
            self.assertEqual(expected_dependencies[child_id], child["dependencies"])
            expected_specification = {
                "D1.1": "docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md",
                "D1.2": "docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md",
                "D1.3": "docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md",
            }[child_id]
            self.assertEqual(expected_specification, child["specification"])
            expected_plan = {
                "D1.1": "docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md",
                "D1.2": "docs/superpowers/plans/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts.md",
                "D1.3": "docs/superpowers/plans/2026-09-05-d1-3-q4xpcc-handoff.md",
            }[child_id]
            self.assertEqual(expected_plan, child["plan"])
            self.assertEqual(4, child["gates"]["satisfied"])
            self.assertEqual(4, child["gates"]["total"])
            self.assertEqual(expected_statements[child_id], [gate["statement"] for gate in child["gates"]["items"]])
            self.assertEqual([True] * 4, [gate["satisfied"] for gate in child["gates"]["items"]])
            evidence_slug = {
                "D1.1": "2026-08-23-d1-1-canonical-design-approval",
                "D1.2": "2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts",
                "D1.3": "2026-09-05-d1-3-q4xpcc-handoff",
            }[child_id]
            self.assertEqual(
                [[f".superpowers/sdd/{evidence_slug}/gate-{ordinal}.md"] for ordinal in range(1, 5)],
                [gate["evidence"] for gate in child["gates"]["items"]],
            )
            self.assertEqual(
                f".superpowers/sdd/{evidence_slug}/review.md",
                child["review_evidence"],
            )
            self.assertIsNone(child["resume_state"])
            self.assertIsNone(child["reason"])
            self.assertEqual(expected_dependency_readiness[child_id], child["dependency_ready"])

        t1_3 = next(child for child in payload["backlog"]["children"] if child["id"] == "T1.3")
        self.assertIn(t1_3["status"], ("in_progress", "implemented", "reviewed", "verified"))
        self.assertEqual(sum(gate["satisfied"] for gate in t1_3["gates"]["items"]), t1_3["gates"]["satisfied"])
        self.assertEqual(4, t1_3["gates"]["total"])
        self.assertTrue(t1_3["dependency_ready"])

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

    def test_audit_is_the_same_human_report_as_status(self) -> None:
        root = self.fixture_root()
        audit = self.run_cli(["audit"], root=root, mock_git=False)
        self.assertEqual(0, audit.code, audit.stdout)
        self.assertEqual("", audit.stderr)
        self.assertEqual(self.run_cli(["status"], root=root, mock_git=False), audit)

    def test_next_is_the_same_read_only_human_report_with_an_action(self) -> None:
        root = self.fixture_root()

        result = self.run_cli(["next"], root=root, mock_git=False)

        self.assertEqual(0, result.code, result.stdout)
        self.assertEqual("", result.stderr)
        self.assertEqual(self.run_cli(["status"], root=root, mock_git=False), result)
        self.assertIn("action=write_plan child=T1.2", result.stdout)

    def test_executable_stdout_is_utf8_with_lf_even_under_legacy_pipe_encoding(self) -> None:
        for args in (["status", "--json"], ["audit"], ["next"]):
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "backlog_status.py"), *args],
                cwd=ROOT,
                env={**os.environ, "PYTHONIOENCODING": "cp1252"},
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            output = result.stdout.decode("utf-8")
            self.assertNotIn(b"\r", result.stdout)
            self.assertTrue(output.endswith("\n"))
            self.assertIn("—", output)

    def test_semantic_findings_block_both_commands_and_keep_context(self) -> None:
        root = self.fixture_root()
        replace_text(root, "BACKLOG.md", "| `specified` |", "| `planned` |")
        replace_text(root, "ROADMAP.md", "- [ ] A separate", "- [x] A separate")
        for args in (["audit"], ["status", "--json"], ["next"]):
            with self.subTest(args=args):
                result = self.run_cli(args, root=root, mock_git=False)
                self.assertEqual(1, result.code)
                self.assertEqual("", result.stderr)
                self.assertIn("release.authorization", result.stdout)
                self.assertIn("lifecycle.plan", result.stdout)
                if "--json" in args:
                    payload = json.loads(result.stdout)
                    self.assertFalse(payload["valid"])
                    self.assertEqual("wait", payload["recommendation"]["action"])
                    self.assertIn("backlog_status.py audit", payload["recommendation"]["command"])
                    self.assertTrue(all(item["line"] for item in payload["findings"]))
                elif args == ["next"]:
                    self.assertIn("action=wait", result.stdout)
                    self.assertIn("backlog_status.py audit", result.stdout)

    def test_every_managed_release_form_blocks_even_with_satisfied_prerequisites(self) -> None:
        root = self.fixture_root()
        # G1 depends only on the already verified fixture child in this scenario.
        replace_text(root, "ROADMAP.md", "reconciliation | `T1.2`", "reconciliation | `T1.1`")
        replace_text(root, "BACKLOG.md", "`waiting` | `T1.2` | —", "`satisfied` | `T1.1` | [verification](release.md)")
        write_evidence(root, "release.md", child="G1", gate=None)
        run_git(root, "add", "--", "ROADMAP.md", "BACKLOG.md", "release.md")
        run_git(root, "commit", "-qm", "Satisfied fixture release prerequisite and evidence")
        self.assertEqual(0, self.run_cli(["audit"], root=root, mock_git=False).code)
        forms = (
            ("BACKLOG.md", "- Release, tag, and package publication: prohibited pending their separate gates and authorization."),
            ("ROADMAP.md", "- [ ] A separate release review authorizes publication."),
        )
        for path, form in forms:
            original = (root / path).read_bytes()
            for replacement in ("", form + "\n" + form, form.replace("prohibited", "authorized").replace("[ ]", "[x]"), form + " Changed."):
                with self.subTest(path=path, replacement=replacement):
                    replace_text(root, path, form, replacement)
                    for args in (["audit"], ["status", "--json"]):
                        result = self.run_cli(args, root=root, mock_git=False)
                        self.assertEqual(1, result.code)
                        self.assertEqual("", result.stderr)
                        self.assertIn("release.authorization", result.stdout)
                        if "--json" in args:
                            payload = json.loads(result.stdout)
                            self.assertFalse(payload["valid"])
                            self.assertEqual("satisfied", payload["backlog"]["release_gates"][0]["state"])
                            self.assertEqual({"release.authorization"}, {item["code"] for item in payload["findings"]})
                    (root / path).write_bytes(original)

    def test_independent_parse_failures_keep_valid_authorities_and_json_shape(self) -> None:
        for count in ("0/x", "9" * 4301 + "/1"):
            with self.subTest(count_length=len(count)):
                root = self.fixture_root()
                replace_text(root, "BACKLOG.md", "1/1", count)
                replace_text(root, "docs/superpowers/plans/historical-plan.md", "**Governance:** historical", "**Governance:** invalid")
                for args in (["status", "--json"], ["audit"]):
                    result = self.run_cli(args, root=root, mock_git=False)
                    self.assertEqual(1, result.code)
                    self.assertEqual("", result.stderr)
                    self.assertIn("backlog.gate-count", result.stdout)
                    self.assertIn("artifact.governance", result.stdout)
                    if "--json" in args:
                        payload = json.loads(result.stdout)
                        self.assertFalse(payload["valid"])
                        self.assertEqual([], payload["backlog"]["children"])
                        self.assertEqual(2, len(payload["roadmap"]["local_children"]))
                        self.assertEqual(1, len(payload["artifacts"]["plans"]))
                        finding = next(item for item in payload["findings"] if item["code"] == "backlog.gate-count")
                        self.assertEqual("T1.1", finding["node"])
                        self.assertGreater(finding["line"], 0)

    def test_oversized_referenced_gate_ordinal_keeps_independent_contextual_reports(self) -> None:
        root = self.fixture_root()
        design = "docs/superpowers/specs/t1-design.md"
        earlier = (
            "## T1.2 — Detailed acceptance\n\nIts acceptance gates are:\n\n"
            "1. First exact gate.\n2. Second exact gate.\n3. Third exact gate.\n4. Fourth exact gate.\n\n"
        )
        replace_text(root, design, "## Acceptance criteria", earlier + "## Acceptance criteria")
        replace_text(root, design, "- Frozen parser remains open.", "`T1.2` is complete only when its four earlier acceptance gates pass.")
        replace_text(root, "BACKLOG.md", "— | 0/1 |", "— | 0/4 |")
        replace_text(
            root,
            "BACKLOG.md",
            "- [ ] Frozen parser remains open.",
            "- [ ] First exact gate.\n- [ ] Second exact gate.\n- [ ] Third exact gate.\n- [ ] Fourth exact gate.",
        )
        self.assertEqual(0, self.run_cli(["audit"], root=root, mock_git=False).code)
        ordinal_line = next(index for index, line in enumerate((root / design).read_text(encoding="utf-8").splitlines(), 1) if line == "1. First exact gate.")
        replace_text(root, design, "1. First exact gate.", "9" * 4301 + ". First exact gate.")
        replace_text(root, "docs/superpowers/plans/historical-plan.md", "**Governance:** historical", "**Governance:** invalid")
        for args in (["audit"], ["status", "--json"]):
            result = self.run_cli(args, root=root, mock_git=False)
            self.assertEqual(1, result.code)
            self.assertEqual("", result.stderr)
            self.assertIn("artifact.gate-drift", result.stdout)
            self.assertIn("artifact.governance", result.stdout)
            if "--json" in args:
                payload = json.loads(result.stdout)
                self.assertFalse(payload["valid"])
                finding = next(item for item in payload["findings"] if item["code"] == "artifact.gate-drift")
                self.assertEqual((design, ordinal_line, "T1.2", None), (finding["path"], finding["line"], finding["node"], finding["gate"]))
                self.assertIn("integer conversion limit", finding["message"])

    def test_unlinked_plan_completion_is_audited_by_both_commands(self) -> None:
        root = self.fixture_root()
        plan = "docs/superpowers/plans/unlinked-completed.md"
        (root / plan).write_bytes((root / "docs/superpowers/plans/t1-1.md").read_bytes())
        self.assertEqual(0, self.run_cli(["audit"], root=root, mock_git=False).code)
        replace_text(root, plan, ".superpowers/sdd/t1-1/completion.md", ".superpowers/sdd/absent-completion.md")
        for args in (["audit"], ["status", "--json"]):
            result = self.run_cli(args, root=root, mock_git=False)
            self.assertEqual(1, result.code)
            self.assertEqual("", result.stderr)
            self.assertIn("evidence.path", result.stdout)
            if "--json" in args:
                findings = json.loads(result.stdout)["findings"]
                self.assertEqual(1, len(findings))
                self.assertEqual("T1.1", findings[0]["node"])
                self.assertIsNone(findings[0]["gate"])

    def test_unavailable_git_is_blocking_and_has_empty_observation(self) -> None:
        root = self.fixture_root()
        module = load_cli()
        for error in (FileNotFoundError("Git unavailable"), subprocess.CalledProcessError(1, "git")):
            for args in (["audit"], ["status", "--json"]):
                output, errors = StringIO(), StringIO()
                with patch.object(module, "observe_git", side_effect=error):
                    code = module.main(args, root=root, stdout=output, stderr=errors)
                self.assertEqual(1, code)
                self.assertEqual("", errors.getvalue())
                self.assertIn("git.unavailable", output.getvalue())
                if "--json" in args:
                    payload = json.loads(output.getvalue())
                    self.assertEqual({"branch": "", "dirty": False, "recent_commits": []}, payload["git"])
                    self.assertFalse(payload["valid"])
                else:
                    self.assertIn("Git: unavailable", output.getvalue())

    def test_warnings_alone_allow_success(self) -> None:
        root = self.fixture_root()
        module = load_cli()
        loaded = replace(load_audit(root), findings=(Finding("fixture.warning", "warning", "BACKLOG.md", 1, None, None, "Synthetic warning."),))
        for args in (["audit"], ["status", "--json"]):
            output = StringIO()
            with patch.object(module, "audit_repository", return_value=loaded, create=True):
                code = module.main(args, root=root, stdout=output)
            self.assertEqual(0, code)
            self.assertIn("fixture.warning", output.getvalue())

    def test_commands_preserve_sources_index_and_head_after_mtime_only_change(self) -> None:
        root = self.fixture_root()

        def source_bytes() -> dict[Path, bytes]:
            return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file() and ".git" not in path.relative_to(root).parts}

        for args in (["status"], ["status", "--json"], ["audit"], ["next"]):
            with self.subTest(args=args):
                target = root / "BACKLOG.md"
                stat = target.stat()
                os.utime(target, ns=(stat.st_atime_ns, stat.st_mtime_ns + 5_000_000_000))
                before = source_bytes()
                index = (root / ".git/index").read_bytes()
                head = run_git(root, "rev-parse", "HEAD")
                result = self.run_cli(args, root=root, mock_git=False)
                self.assertEqual(0, result.code, result.stdout)
                self.assertEqual(index, (root / ".git/index").read_bytes())
                self.assertEqual(head, run_git(root, "rev-parse", "HEAD"))
                self.assertEqual(before, source_bytes())

    def test_command_specific_options_and_missing_command_are_invalid_usage(self) -> None:
        for args in (["audit", "--json"], ["next", "--json"], ["next", "--apply"], ["status", "--apply"], []):
            result = self.run_cli(args, root=ROOT)
            self.assertEqual(2, result.code)
            self.assertEqual("", result.stdout)
            self.assertIn("usage:", result.stderr)

    def test_unknown_command_is_invalid_usage(self) -> None:
        invalid = self.run_cli(["unknown"], root=self.fixture_root())

        self.assertEqual(2, invalid.code)
        self.assertIn("invalid choice", invalid.stderr)

    def test_malformed_repository_reports_parse_context_on_stdout(self) -> None:
        malformed = self.run_cli(["status"], root=self.malformed_fixture())

        self.assertEqual(1, malformed.code)
        self.assertEqual("", malformed.stderr)
        self.assertRegex(malformed.stdout, r"backlog.gate-count BACKLOG.md:[0-9]+")


if __name__ == "__main__":
    unittest.main()
