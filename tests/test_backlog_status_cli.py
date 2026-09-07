from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, replace
import importlib.util
import hashlib
from io import BytesIO, StringIO, TextIOWrapper
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

from tests.backlog_audit_support import audit_fixture, replace_text, reviewed_gate_fixture, run_git, write_active_plan, write_evidence  # noqa: E402
from backlog.audit import audit_repository, load_audit  # noqa: E402  # ty: ignore[unresolved-import]
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

    def test_all_mutation_dry_runs_render_candidate_and_preserve_every_file(self) -> None:
        cases = (
            ["select", "T1.2", "--expect-current", "none"],
            ["transition", "T1.2", "planned", "--expect", "specified", "--plan", "docs/superpowers/plans/t1-2.md"],
            [
                "record-gate",
                "T1.2",
                "1",
                "--expect-open",
                "--evidence",
                ".superpowers/sdd/t1-2/gate-1.md",
                "--evidence",
                ".superpowers/sdd/t1-2/gate-1-artifact.md",
            ],
            ["reopen-gate", "T1.2", "1", "--expect-closed", "--reason", "Evidence contract changed"],
            ["suspend", "T1.2", "blocked", "--expect", "specified", "--reason", "Named prerequisite unavailable"],
            ["resume", "T1.2", "--expect", "blocked", "--resume", "specified", "--reason", "Prerequisite restored"],
        )
        for args in cases:
            with self.subTest(command=args[0]):
                root = self.fixture_root()
                if args[0] == "transition":
                    write_active_plan(root, "docs/superpowers/plans/t1-2.md")
                elif args[0] in {"record-gate", "reopen-gate"}:
                    reviewed_gate_fixture(root)
                    for path in (".superpowers/sdd/t1-2/gate-1.md", ".superpowers/sdd/t1-2/gate-1-artifact.md"):
                        write_evidence(root, path, child="T1.2")
                    run_git(root, "add", "--", ".superpowers")
                    if args[0] == "reopen-gate":
                        replace_text(root, "BACKLOG.md", "| 0/1 |", "| 1/1 |")
                        replace_text(
                            root,
                            "BACKLOG.md",
                            "- [ ] Frozen parser remains open.",
                            "- [x] Frozen parser remains open. — Evidence: [verification](.superpowers/sdd/t1-2/gate-1.md)",
                        )
                elif args[0] == "resume":
                    replace_text(root, "BACKLOG.md", "`specified`", "`blocked`")
                    replace_text(root, "BACKLOG.md", "| 0/1 | — | — | — |", "| 0/1 | — | `specified` | Named prerequisite unavailable |")
                before = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
                digest = hashlib.sha256((root / "BACKLOG.md").read_bytes()).hexdigest()
                result = self.run_cli([*args, "--target-sha256", digest], root=root, mock_git=False)
                self.assertEqual(0, result.code, result.stdout + result.stderr)
                self.assertEqual("", result.stderr)
                for marker in (
                    "Mutation:",
                    "Mode: dry-run",
                    "Target: BACKLOG.md",
                    "Original SHA-256:",
                    "Candidate SHA-256:",
                    "Rationale:",
                    "Diff:",
                    "--- a/BACKLOG.md",
                    "+++ b/BACKLOG.md",
                    "Post-change audit:",
                    "Repository: xplane-fdau",
                ):
                    self.assertIn(marker, result.stdout)
                self.assertNotIn("\r", result.stdout)
                self.assertEqual(before, {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()})
                if args[0] == "select":
                    self.assertIn("dependency-ready=yes", result.stdout)

    def test_mutation_output_is_lf_even_when_backlog_uses_crlf(self) -> None:
        root = self.fixture_root()
        target = root / "BACKLOG.md"
        original = target.read_bytes().replace(b"\n", b"\r\n")
        target.write_bytes(original)
        result = self.run_cli(["select", "T1.2", "--expect-current", "none"], root=root)
        self.assertEqual(0, result.code, result.stdout + result.stderr)
        self.assertNotIn("\r", result.stdout)
        self.assertEqual(original, target.read_bytes())

    def test_apply_changes_only_backlog_and_returns_ordinary_valid_audit(self) -> None:
        root = self.fixture_root()
        before = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
        result = self.run_cli(["select", "T1.2", "--expect-current", "none", "--apply"], root=root, mock_git=False)
        self.assertEqual(0, result.code, result.stdout + result.stderr)
        self.assertIn("Mode: applied", result.stdout)
        after = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
        self.assertEqual(before.keys(), after.keys())
        self.assertEqual([Path("BACKLOG.md")], [path for path in before if before[path] != after[path]])
        self.assertEqual(0, self.run_cli(["audit"], root=root, mock_git=False).code)

    def test_postpublication_reporting_failures_retain_audit_and_warn_against_retry(self) -> None:
        for seam in ("observe_git", "with_dependency_readiness", "build_report", "render_human", "_mutation_heading"):
            with self.subTest(seam=seam):
                root = self.fixture_root()
                module = load_cli()
                output, errors = StringIO(), StringIO()
                original = (root / "BACKLOG.md").read_bytes()
                with patch.object(module, seam, side_effect=OSError(f"{seam} failed after publication")):
                    code = module.main(["select", "T1.2", "--expect-current", "none", "--apply"], root=root, stdout=output, stderr=errors)
                self.assertEqual(1, code)
                self.assertEqual("", errors.getvalue())
                self.assertIn("mutation.published", output.getvalue())
                self.assertIn("do not retry", output.getvalue().lower())
                self.assertIn(f"{seam} failed after publication", output.getvalue())
                self.assertIn("Post-change audit:", output.getvalue())
                self.assertIn("Active child: T1.2", output.getvalue())
                self.assertNotIn("Traceback", output.getvalue())
                self.assertNotEqual(original, (root / "BACKLOG.md").read_bytes())
                self.assertEqual(0, self.run_cli(["audit"], root=root, mock_git=False).code)

    def test_postpublication_broken_stdout_reports_published_state_on_stderr(self) -> None:
        root = self.fixture_root()
        module = load_cli()
        output, errors = StringIO(), StringIO()
        with patch.object(output, "write", side_effect=BrokenPipeError("stdout closed after publication")):
            code = module.main(["select", "T1.2", "--expect-current", "none", "--apply"], root=root, stdout=output, stderr=errors)
        self.assertEqual(1, code)
        self.assertIn("mutation.published", errors.getvalue())
        self.assertIn("do not retry", errors.getvalue())
        self.assertIn("Active child: T1.2", errors.getvalue())
        self.assertIn(b"- Active child: `T1.2`.", (root / "BACKLOG.md").read_bytes())

    def test_published_final_audit_refusal_survives_broken_stdout(self) -> None:
        root = self.fixture_root()
        module = load_cli()
        output, errors = StringIO(), StringIO()
        original = (root / "BACKLOG.md").read_bytes()

        def failed_final_audit(root, *, backlog_text=None):
            if backlog_text is None:
                raise OSError("final audit failed after replacement")
            return audit_repository(root, backlog_text=backlog_text)

        with patch("backlog.edit.audit_repository", side_effect=failed_final_audit):
            with patch.object(output, "write", side_effect=BrokenPipeError("stdout unavailable")):
                code = module.main(["select", "T1.2", "--expect-current", "none", "--apply"], root=root, stdout=output, stderr=errors)
        self.assertEqual(1, code)
        self.assertIn("mutation.published", errors.getvalue())
        self.assertIn("do not retry", errors.getvalue())
        self.assertIn("final audit failed after replacement", errors.getvalue())
        self.assertEqual(original.replace("- Active child: —.".encode(), b"- Active child: `T1.2`."), (root / "BACKLOG.md").read_bytes())

    def test_applied_buffered_stdout_flush_failure_reports_published_state(self) -> None:
        root = self.fixture_root()
        module = load_cli()
        raw = BytesIO()
        output = TextIOWrapper(raw, encoding="utf-8", newline="\n")
        self.addCleanup(output.close)
        errors = StringIO()
        original = (root / "BACKLOG.md").read_bytes()
        with patch.object(raw, "write", side_effect=BrokenPipeError("buffered stdout flush failed")):
            code = module.main(["select", "T1.2", "--expect-current", "none", "--apply"], root=root, stdout=output, stderr=errors)
        self.assertEqual(1, code, "main returned success before buffered output was flushed")
        self.assertIn("mutation.published", errors.getvalue())
        self.assertIn("do not retry", errors.getvalue())
        self.assertIn("buffered stdout flush failed", errors.getvalue())
        self.assertEqual(original.replace("- Active child: —.".encode(), b"- Active child: `T1.2`."), (root / "BACKLOG.md").read_bytes())

    def test_mutation_domain_refusals_use_stdout_and_status_one(self) -> None:
        root = self.fixture_root()
        for args in (
            ["select", "T1.2", "--expect-current", "T1.1"],
            ["select", "T1.2", "--expect-current", "none", "--target-sha256", "0" * 64],
            ["record-gate", "T1.2", "1", "--expect-open", "--evidence", "a.md", "--evidence", "a.md"],
        ):
            result = self.run_cli(args, root=root)
            self.assertEqual(1, result.code, result.stderr)
            self.assertEqual("", result.stderr)
            self.assertIn("mutation.", result.stdout)
            self.assertNotIn("Traceback", result.stdout)

    def test_mutation_invalid_grammar_is_usage_error(self) -> None:
        root = self.fixture_root()
        valid = ["select", "T1.2", "--expect-current", "none"]
        cases = (
            ["select", "T1.2"],
            ["transition", "T1.2", "planned"],
            ["transition", "T1.2", "released", "--expect", "verified"],
            ["transition", "T1.2", "unknown", "--expect", "specified"],
            ["record-gate", "T1.2", "1", "--expect-open"],
            ["record-gate", "T1.2", "1", "--expect-open=false", "--evidence", "a.md"],
            ["reopen-gate", "T1.2", "1", "--expect-closed=false", "--reason", "reason"],
            ["record-gate", "T1.2", "0", "--expect-open", "--evidence", "a.md"],
            ["record-gate", "T1.2", "x", "--expect-open", "--evidence", "a.md"],
            ["suspend", "T1.2", "blocked", "--reason", "reason"],
            ["resume", "T1.2", "--resume", "specified", "--reason", "reason"],
            [*valid, "--json"],
            [*valid, "--target-sha256", "A" * 64],
            ["audit", "--target-sha256", "0" * 64],
        )
        for args in cases:
            with self.subTest(args=args):
                result = self.run_cli(args, root=root)
                self.assertEqual(2, result.code)
                self.assertEqual("", result.stdout)
                self.assertIn("usage:", result.stderr)

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
        self.assertIsNone(payload["backlog"]["active_child"])
        self.assertEqual("write_plan", payload["recommendation"]["action"])
        self.assertEqual("T1.6", payload["recommendation"]["child"])
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
