from __future__ import annotations

from dataclasses import replace
from importlib import import_module
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from typing import override

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex/skills/backlog-status/scripts"))

from backlog.audit import load_audit  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.model import AuditPolicy, HistoricalAdmission  # noqa: E402  # ty: ignore[unresolved-import]
from tests.backlog_audit_support import evidence_fixture, initialize_git, replace_text, run_git, write_evidence  # noqa: E402


class LifecycleTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertIsNotNone(__import__("importlib.util").util.find_spec("backlog.lifecycle"), "lifecycle rule module must exist")
        self.rules = import_module("backlog.lifecycle")
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        evidence_fixture(self.root)

    def loaded(self):  # type: ignore[no-untyped-def]
        return load_audit(self.root)

    def codes(self, loaded=None) -> set[str]:  # type: ignore[no-untyped-def]
        return {item.code for item in self.rules.lifecycle_findings(loaded or self.loaded())}

    def state(
        self,
        status: str,
        *,
        resume: str | None = None,
        reason: str | None = None,
        selected: bool = False,
        plan_status: str | None = None,
        design_status: str | None = None,
    ):  # type: ignore[no-untyped-def]
        loaded = self.loaded()
        snapshot = loaded.snapshot
        child = replace(snapshot.backlog.children[0], status=status, resume_state=resume, reason=reason)
        backlog = replace(snapshot.backlog, children=(child, *snapshot.backlog.children[1:]), active_child=child.id if selected else None)
        artifacts = snapshot.artifacts
        if plan_status:
            artifacts = replace(artifacts, plans=tuple(replace(plan, status=plan_status) for plan in artifacts.plans))
        if design_status:
            artifacts = replace(artifacts, specifications=tuple(replace(spec, status=design_status) for spec in artifacts.specifications))
            if design_status == "draft":
                backlog = replace(backlog, children=(child, replace(backlog.children[1], status="queued")))
        return replace(loaded, snapshot=replace(snapshot, backlog=backlog, artifacts=artifacts))

    def test_stage_specific_positive_controls(self) -> None:
        cases = (
            ("queued", None, None),
            ("designing", None, "draft"),
            ("specified", None, None),
            ("planned", "approved", None),
            ("in_progress", "in_progress", None),
            ("implemented", "completed", None),
            ("reviewed", "completed", None),
            ("verified", "completed", None),
        )
        for status, plan, design in cases:
            with self.subTest(status=status):
                loaded = self.state(status, selected=status == "in_progress", plan_status=plan, design_status=design)
                # These controls test lifecycle requirements; adherence separately rejects queued checked gates.
                self.assertEqual(set(), self.codes(loaded))

    def test_suspension_metadata_and_resume_requirements(self) -> None:
        for suspended in ("blocked", "deferred"):
            for resume in ("queued", "designing", "specified", "planned", "in_progress", "implemented", "reviewed", "verified"):
                with self.subTest(suspended=suspended, resume=resume):
                    plan = "in_progress" if resume == "in_progress" else "approved" if resume == "planned" else "completed"
                    design = "draft" if resume == "designing" else None
                    self.assertEqual(set(), self.codes(self.state(suspended, resume=resume, reason="Waiting", plan_status=plan, design_status=design)))
            for resume, reason in ((None, "Waiting"), ("verified", None), ("blocked", "Waiting"), ("deferred", "Waiting"), ("released", "Waiting")):
                self.assertIn("lifecycle.suspension", self.codes(self.state(suspended, resume=resume, reason=reason)))
        for resume, reason in (("verified", None), (None, "Stale")):
            self.assertIn("lifecycle.suspension", self.codes(self.state("verified", resume=resume, reason=reason)))

    def test_ordinary_requirements_and_dependency_timing(self) -> None:
        self.assertIn("lifecycle.selection", self.codes(self.state("in_progress", plan_status="in_progress")))
        self.assertIn("lifecycle.plan", self.codes(self.state("implemented", plan_status="approved")))
        self.assertIn("lifecycle.specification", self.codes(self.state("specified", design_status="draft")))
        for changes, expected in (({"approval": None}, "lifecycle.plan"), ({"completion_evidence": None}, "lifecycle.completion")):
            loaded = self.loaded()
            artifacts = replace(loaded.snapshot.artifacts, plans=tuple(replace(plan, **changes) for plan in loaded.snapshot.artifacts.plans))
            self.assertIn(expected, self.codes(replace(loaded, snapshot=replace(loaded.snapshot, artifacts=artifacts))))
        loaded = self.state("queued")
        second = loaded.snapshot.backlog.children[1]
        self.assertEqual(set(), self.codes(loaded))  # specified may await T1.1 implementation
        backlog = replace(loaded.snapshot.backlog, children=(loaded.snapshot.backlog.children[0], replace(second, status="in_progress")))
        self.assertIn("lifecycle.dependencies", self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))
        (self.root / ".superpowers/sdd/t1-1/completion.md").unlink()
        self.assertIn("evidence.path", self.codes())

    def test_review_gates_order_duplicates_and_head(self) -> None:
        loaded = self.loaded()
        child = loaded.snapshot.backlog.children[0]
        for changes, expected in (
            ({"review_evidence": None}, "lifecycle.review"),
            ({"gates": replace(child.gates, items=(replace(child.gates.items[0], satisfied=False),))}, "lifecycle.gates"),
        ):
            backlog = replace(loaded.snapshot.backlog, children=(replace(child, **changes), loaded.snapshot.backlog.children[1]))
            self.assertIn(expected, self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))
        evidence = child.gates.items[0].evidence[0]
        item = replace(child.gates.items[0], evidence=(evidence, "a.md", evidence))
        backlog = replace(loaded.snapshot.backlog, children=(replace(child, gates=replace(child.gates, items=(item,))), loaded.snapshot.backlog.children[1]))
        codes = self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog)))
        self.assertTrue({"evidence.order", "evidence.duplicate", "evidence.path"} <= codes)
        with (self.root / evidence).open("a", encoding="utf-8") as stream:
            stream.write("Edited\n")
        self.assertIn("evidence.dirty", self.codes())

    def test_unlinked_active_completion_slots_validate_declared_child_and_index_bytes(self) -> None:
        plan_path = "docs/superpowers/plans/unlinked-completed.md"
        evidence = ".superpowers/sdd/t1-2/unlinked-completion.md"
        source = (self.root / "docs/superpowers/plans/t1-1.md").read_text(encoding="utf-8")
        (self.root / plan_path).write_text(
            source.replace("**Roadmap child:** `T1.1`", "**Roadmap child:** `T1.2`").replace(".superpowers/sdd/t1-1/completion.md", evidence),
            encoding="utf-8",
            newline="\n",
        )
        write_evidence(self.root, evidence, child="T1.2", gate=None)
        run_git(self.root, "add", "--", plan_path, evidence)
        run_git(self.root, "commit", "-qm", "Unlinked completion control")
        original = (self.root / evidence).read_bytes()
        loaded = self.loaded()
        for status in ("draft", "approved", "in_progress", "completed", "superseded"):
            artifacts = replace(
                loaded.snapshot.artifacts,
                plans=tuple(replace(plan, status=status) if plan.path == plan_path else plan for plan in loaded.snapshot.artifacts.plans),
            )
            self.assertEqual(set(), self.codes(replace(loaded, snapshot=replace(loaded.snapshot, artifacts=artifacts))))
        for content, stage, expected in (
            (b"Malformed evidence\n", True, "evidence.metadata"),
            (original.replace(b"Kind:** verification", b"Kind:** review").replace(b"Result:** passed", b"Result:** accepted"), True, "evidence.kind"),
            (original.replace(b"Child:** `T1.2`", b"Child:** `T1.1`"), True, "evidence.child-mismatch"),
            (original.replace("Gate:** —".encode(), b"Gate:** `1`"), True, "evidence.gate-mismatch"),
            (original + b"Unstaged bytes\n", False, "evidence.dirty"),
        ):
            with self.subTest(expected=expected):
                (self.root / evidence).write_bytes(content)
                if stage:
                    run_git(self.root, "add", "--", evidence)
                findings = [item for item in self.rules.lifecycle_findings(self.loaded()) if item.path == evidence]
                self.assertEqual([expected], [item.code for item in findings])
                self.assertEqual(("T1.2", None), (findings[0].node, findings[0].gate))
                (self.root / evidence).write_bytes(original)
                run_git(self.root, "add", "--", evidence)
        (self.root / evidence).write_bytes(original + b"Staged completion update\n")
        run_git(self.root, "add", "--", evidence)
        self.assertEqual(set(), self.codes())  # unlinked slots require index eligibility, not HEAD.
        (self.root / evidence).unlink()
        self.assertIn("evidence.path", self.codes())
        invalid = replace(self.loaded(), invalid_paths=frozenset({"BACKLOG.md"}))
        self.assertEqual({"evidence.path"}, self.codes(invalid))

    def test_linked_completion_keeps_head_requirement_without_duplicate_findings(self) -> None:
        evidence = ".superpowers/sdd/t1-1/completion.md"
        with (self.root / evidence).open("ab") as stream:
            stream.write(b"Completion update\n")
        run_git(self.root, "add", "--", evidence)
        self.assertEqual(set(), self.codes(self.state("implemented")))
        for status, resume in (("verified", None), ("blocked", "verified"), ("deferred", "verified")):
            with self.subTest(status=status):
                loaded = self.state(status, resume=resume, reason="Waiting" if resume else None)
                findings = [item for item in self.rules.lifecycle_findings(loaded) if item.path == evidence]
                self.assertEqual(["evidence.not-in-head"], [item.code for item in findings])

    def historical(self):  # type: ignore[no-untyped-def]
        plan = "docs/superpowers/plans/t1-1.md"
        (self.root / plan).write_text(
            "# Historical\n\n- **Governance:** historical\n- **Status:** completed\n- **Disposition:** Completed `T1.1`.\n", encoding="utf-8", newline="\n"
        )
        run_git(self.root, "add", "--", plan)
        run_git(self.root, "commit", "-qm", "Historical baseline")
        digest = __import__("hashlib").sha256((self.root / plan).read_bytes()).hexdigest()
        return replace(self.loaded(), policy=AuditPolicy((HistoricalAdmission("T1.1", plan, digest),)))

    def test_historical_pinned_admission_and_suspended_verified(self) -> None:
        loaded = self.historical()
        self.assertEqual(set(), self.codes(loaded))
        for status in ("blocked", "deferred"):
            child = replace(loaded.snapshot.backlog.children[0], status=status, resume_state="verified", reason="Awaiting governance")
            backlog = replace(loaded.snapshot.backlog, children=(child, loaded.snapshot.backlog.children[1]))
            self.assertEqual(set(), self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))
            self.assertEqual(status, child.status)

    def test_historical_rejects_pin_identity_state_and_evidence_mutations(self) -> None:
        loaded = self.historical()
        pin = loaded.policy.historical[0]
        for changed in (replace(pin, child="T1.2"), replace(pin, plan="docs/superpowers/plans/other.md"), replace(pin, sha256="0" * 64)):
            self.assertIn("lifecycle.historical-plan", self.codes(replace(loaded, policy=AuditPolicy((changed,)))))
        self.assertIn("lifecycle.historical-plan", self.codes(replace(loaded, policy=None)))
        for change in ({"status": "superseded"}, {"disposition": "Completed `T1.10`."}):
            artifacts = replace(
                loaded.snapshot.artifacts,
                historical=tuple(replace(plan, **change) if plan.path == pin.plan else plan for plan in loaded.snapshot.artifacts.historical),
            )
            self.assertIn("lifecycle.historical-plan", self.codes(replace(loaded, snapshot=replace(loaded.snapshot, artifacts=artifacts))))
        child = replace(loaded.snapshot.backlog.children[0], plan="docs/superpowers/plans/historical-plan.md")
        backlog = replace(loaded.snapshot.backlog, children=(child, loaded.snapshot.backlog.children[1]))
        self.assertIn("lifecycle.historical-plan", self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))
        for state in ("queued", "in_progress", "implemented", "reviewed"):
            child = replace(loaded.snapshot.backlog.children[0], status=state)
            backlog = replace(loaded.snapshot.backlog, children=(child, loaded.snapshot.backlog.children[1]))
            self.assertIn("lifecycle.historical-plan", self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))
        for path in (".superpowers/sdd/t1-1/review.md", ".superpowers/sdd/t1-1/gate-1.md", pin.plan):
            original = (self.root / path).read_bytes()
            (self.root / path).write_bytes(original + b"\nEdited\n")
            self.assertIn("lifecycle.historical-plan", self.codes(loaded))
            (self.root / path).unlink()
            self.assertIn("lifecycle.historical-plan", self.codes(loaded))
            (self.root / path).write_bytes(original)

    def test_real_d1_historical_controls(self) -> None:
        # The real D1.2 backlog wording awaits Task 5's reviewed reconciliation.
        # Normalize only this isolated copy to the approved design statements;
        # policy, historical plans, and all evidence retain their exact bytes.
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        shutil.copytree(ROOT / "docs", root / "docs")
        for name in ("BACKLOG.md", "ROADMAP.md"):
            shutil.copyfile(ROOT / name, root / name)
        original = load_audit(ROOT)
        paths = {path for child in original.snapshot.backlog.children for item in child.gates.items for path in item.evidence}
        paths.update(child.review_evidence for child in original.snapshot.backlog.children if child.review_evidence)
        paths.update(plan.completion_evidence for plan in original.snapshot.artifacts.plans if plan.completion_evidence)
        for path in paths:
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, root / path)
        child = next(child for child in original.snapshot.backlog.children if child.id == "D1.2")
        acceptance = next(item for item in original.sources.design_acceptance if item.child == child.id and item.path == child.specification)
        lines = (root / "BACKLOG.md").read_text(encoding="utf-8").splitlines()
        for gate, statement in reversed(tuple(zip(child.gates.items, acceptance.statements, strict=True))):
            start = gate.source.line - 1
            end = start + 1
            while end < len(lines) and lines[end][:1].isspace():
                end += 1
            links = " ".join(f"[verification]({path})" for path in gate.evidence)
            lines[start:end] = [f"- [x] {statement.value} — Evidence: {links}"]
        (root / "BACKLOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        initialize_git(root)
        loaded = load_audit(root)
        self.assertEqual((), loaded.findings)
        for identity in ("D1.1", "D1.2", "D1.3"):
            child = next(child for child in loaded.snapshot.backlog.children if child.id == identity)
            self.assertEqual((), self.rules.historical_plan_findings(loaded, child))

    def test_historical_requires_structural_and_governing_acceptance_match(self) -> None:
        loaded = self.historical()
        child = loaded.snapshot.backlog.children[0]
        changed = replace(child.gates.items[0], statement="Different acceptance contract")
        child = replace(child, gates=replace(child.gates, items=(changed,)))
        backlog = replace(loaded.snapshot.backlog, children=(child, loaded.snapshot.backlog.children[1]))
        self.assertIn("lifecycle.historical-plan", self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))

    def test_multiple_unselected_verified_and_four_suspended_standards(self) -> None:
        loaded = self.loaded()
        first, second = loaded.snapshot.backlog.children
        plan = loaded.snapshot.artifacts.plans[0]
        for name, kind, result, gate in (
            ("completion", "verification", "passed", None),
            ("review", "review", "accepted", None),
            ("gate", "verification", "passed", 1),
        ):
            write_evidence(self.root, f"second/{name}.md", child="T1.2", gate=gate, kind=kind, result=result)
        run_git(self.root, "add", "--", "second")
        run_git(self.root, "commit", "-qm", "Second verified evidence")
        plan = replace(plan, path="docs/superpowers/plans/t1-2.md", child="T1.2", completion_evidence="second/completion.md")
        gate = replace(second.gates.items[0], satisfied=True, evidence=("second/gate.md",))
        second = replace(second, status="verified", plan=plan.path, review_evidence="second/review.md", gates=replace(second.gates, satisfied=1, items=(gate,)))
        backlog = replace(loaded.snapshot.backlog, children=(first, second), release_gates=(replace(loaded.snapshot.backlog.release_gates[0], state="ready"),))
        artifacts = replace(loaded.snapshot.artifacts, plans=(*loaded.snapshot.artifacts.plans, plan))
        self.assertEqual(set(), self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog, artifacts=artifacts))))
        actual = load_audit(ROOT)
        standards = [child for child in actual.snapshot.backlog.children if child.status == "blocked" and child.resume_state == "queued"]
        self.assertEqual(4, len(standards))
        self.assertFalse([finding for finding in self.rules.lifecycle_findings(actual) if finding.node in {child.id for child in standards}])

    def test_missing_release_sections_and_unrelated_prose(self) -> None:
        for path, heading in (("ROADMAP.md", "## Version 0.1.0 release gates"), ("BACKLOG.md", "## Current position")):
            original = (self.root / path).read_bytes()
            replace_text(self.root, path, heading, "## Unmanaged section")
            self.assertTrue(any(item.code == "markdown.heading" and item.path == path for item in self.loaded().findings))
            (self.root / path).write_bytes(original)
        with (self.root / "BACKLOG.md").open("a", encoding="utf-8") as stream:
            stream.write("\nAn explicitly requested ordinary Git sync is authorized.\n")
        self.assertEqual((), import_module("backlog.rules").release_authorization_findings(self.loaded()))

    def test_release_state_and_authorization_forms(self) -> None:
        rule = import_module("backlog.rules").release_authorization_findings
        self.assertEqual((), rule(self.loaded()))
        self.assertIn("release.prohibited-state", {item.code for item in rule(self.state("released"))})
        cases = (
            ("BACKLOG.md", "prohibited pending their separate gates and authorization.", "authorized."),
            ("ROADMAP.md", "- [ ] A separate release review authorizes publication.", "- [x] A separate release review authorizes publication."),
            ("ROADMAP.md", "- [ ] A separate release review authorizes publication.", "- [ ] A changed release review authorizes publication."),
        )
        for path, old, new in cases:
            original = (self.root / path).read_bytes()
            replace_text(self.root, path, old, new)
            self.assertIn("release.authorization", {item.code for item in rule(self.loaded())})
            (self.root / path).write_bytes(original)
        for path, form in (
            ("BACKLOG.md", "- Release, tag, and package publication: prohibited pending their separate gates and authorization."),
            ("ROADMAP.md", "- [ ] A separate release review authorizes publication."),
        ):
            original = (self.root / path).read_bytes()
            for replacement in ("", form + "\n" + form):
                replace_text(self.root, path, form, replacement)
                finding = next(item for item in rule(self.loaded()) if item.code == "release.authorization")
                self.assertEqual(path, finding.path)
                self.assertIsNotNone(finding.line)
                (self.root / path).write_bytes(original)

    def test_release_readiness_and_satisfied_evidence(self) -> None:
        loaded = self.loaded()
        gate = loaded.snapshot.backlog.release_gates[0]
        backlog = replace(loaded.snapshot.backlog, release_gates=(replace(gate, state="ready"),))
        self.assertIn("release.prerequisites", self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))
        second = replace(loaded.snapshot.backlog.children[1], status="verified")
        backlog = replace(backlog, children=(*backlog.children[:1], second))
        ready = replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))
        self.assertNotIn("release.prerequisites", self.codes(ready))
        backlog = replace(backlog, release_gates=(replace(gate, state="satisfied"),))
        self.assertIn("release.evidence", self.codes(replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))))
        path = "release.md"
        write_evidence(self.root, path, child="G1", gate=None)
        run_git(self.root, "add", "--", path)
        backlog = replace(backlog, release_gates=(replace(gate, state="satisfied", evidence=(path,)),))
        satisfied = replace(loaded, snapshot=replace(loaded.snapshot, backlog=backlog))
        self.assertIn("evidence.not-in-head", self.codes(satisfied))
        run_git(self.root, "commit", "-qm", "Release evidence")
        self.assertNotIn("evidence.not-in-head", self.codes(satisfied))
        replace_text(self.root, "ROADMAP.md", "- [ ] A separate release", "- [x] A separate release")
        fresh = self.loaded()
        satisfied = replace(satisfied, sources=fresh.sources)
        self.assertIn("release.authorization", {item.code for item in import_module("backlog.rules").release_authorization_findings(satisfied)})

    def test_oversized_evidence_gate_preserves_independent_findings(self) -> None:
        path = ".superpowers/sdd/t1-1/gate-1.md"
        replace_text(self.root, path, "- **Gate:** `1`", "- **Gate:** `" + "9" * 4301 + "`")
        run_git(self.root, "add", "--", path)
        run_git(self.root, "commit", "-qm", "Oversized ordinal fixture")
        (self.root / ".superpowers/sdd/t1-1/review.md").unlink()
        findings = self.rules.lifecycle_findings(self.loaded())
        mismatch = next(item for item in findings if item.code == "evidence.gate-mismatch")
        self.assertEqual((path, 4, "T1.1", 1), (mismatch.path, mismatch.line, mismatch.node, mismatch.gate))
        independent = next(item for item in findings if item.code == "evidence.path")
        self.assertEqual((".superpowers/sdd/t1-1/review.md", "T1.1", None), (independent.path, independent.node, independent.gate))

    def test_release_prefix_normalization_precedes_discovery(self) -> None:
        rule = import_module("backlog.rules").release_authorization_findings
        canonical = "- Release, tag, and package publication: prohibited pending their separate gates and authorization."
        variants = (
            canonical,
            canonical.replace("Release,", "Release, "),
            canonical.replace("package publication:", "package\n  publication:"),
            canonical.replace("- Release,", "-  Release,\t"),
        )
        original = (self.root / "BACKLOG.md").read_bytes()
        for variant in variants:
            with self.subTest(variant=variant):
                (self.root / "BACKLOG.md").write_bytes(original)
                replace_text(self.root, "BACKLOG.md", canonical, variant)
                loaded = self.loaded()
                self.assertEqual((), rule(loaded))
                source = loaded.sources.backlog_release_statements[0]
                self.assertEqual((canonical, 6), (source.value, source.source.line))
                # An equivalent statement in a later section is outside the managed surface.
                with (self.root / "BACKLOG.md").open("a", encoding="utf-8", newline="\n") as stream:
                    stream.write("\n" + variant + "\n")
                self.assertEqual((), rule(self.loaded()))
                (self.root / "BACKLOG.md").write_bytes(original)
        for first in variants:
            for second in variants:
                with self.subTest(first=first, second=second):
                    (self.root / "BACKLOG.md").write_bytes(original)
                    replace_text(self.root, "BACKLOG.md", canonical, first + "\n" + second)
                    loaded = self.loaded()
                    findings = [item for item in rule(loaded) if item.code == "release.authorization"]
                    self.assertEqual(1, len(findings))
                    finding = findings[0]
                    second_line = 7 + first.count("\n")
                    self.assertEqual(("BACKLOG.md", second_line), (finding.path, finding.line))
                    self.assertEqual((6, second_line), tuple(item.source.line for item in loaded.sources.backlog_release_statements))
                    (self.root / "BACKLOG.md").write_bytes(original)


if __name__ == "__main__":
    unittest.main()
