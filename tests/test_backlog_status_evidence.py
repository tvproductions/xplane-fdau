from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys
import tempfile
import unittest
from typing import override
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex/skills/backlog-status/scripts"))

from tests.backlog_audit_support import initialize_git, run_git, write_evidence  # noqa: E402
from backlog.policy import allowed_kinds  # noqa: E402  # ty: ignore[unresolved-import]


class EvidenceTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.assertIsNotNone(__import__("importlib.util").util.find_spec("backlog.evidence"), "evidence rule module must exist")
        self.validate = import_module("backlog.evidence").evidence_findings
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = "evidence space/naïve verification.md"
        write_evidence(self.root, self.path)
        initialize_git(self.root)

    def codes(
        self, *, head: bool = True, child: str = "T1.1", gate: int | None = 1, kinds: frozenset[str] = frozenset({"verification"}), path: str | None = None
    ) -> set[str]:
        findings = self.validate(self.root, path or self.path, child, gate, kinds=kinds, require_head=head)
        for item in findings:
            self.assertEqual(child, item.node)
            self.assertEqual(gate, item.gate)
        return {item.code for item in findings}

    def test_committed_bytes_and_stage_only_distinction(self) -> None:
        self.assertEqual(set(), self.codes())
        new = "new.md"
        write_evidence(self.root, new)
        self.assertIn("evidence.untracked", self.codes(path=new))
        run_git(self.root, "add", "--", new)
        self.assertEqual(set(), self.codes(path=new, head=False))
        self.assertIn("evidence.not-in-head", self.codes(path=new))

    def test_absent_deleted_ignored_and_nonregular(self) -> None:
        self.assertIn("evidence.path", self.codes(path="absent.md"))
        (self.root / self.path).unlink()
        self.assertIn("evidence.path", self.codes())
        (self.root / "directory.md").mkdir()
        self.assertIn("evidence.path", self.codes(path="directory.md"))
        (self.root / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
        write_evidence(self.root, "ignored.md")
        self.assertIn("evidence.untracked", self.codes(path="ignored.md"))
        for path in ("../outside.md", "/absolute.md", "C:/absolute.md", "bad\\path.md", "x.txt"):
            self.assertIn("evidence.path", self.codes(path=path))

    def test_unstaged_staged_and_crlf_raw_changes(self) -> None:
        write_evidence(self.root, self.path, newline="\r\n")
        self.assertIn("evidence.dirty", self.codes(head=False))
        run_git(self.root, "add", "--", self.path)
        self.assertEqual(set(), self.codes(head=False))
        self.assertIn("evidence.not-in-head", self.codes())
        run_git(self.root, "commit", "-qam", "CRLF bytes")
        self.assertEqual(set(), self.codes())

    def test_conflict_index_and_symlink_mode_are_ineligible(self) -> None:
        blob = run_git(self.root, "rev-parse", f"HEAD:{self.path}").strip()
        run_git(self.root, "update-index", "--force-remove", "--", self.path)
        records = b"".join(b"100644 " + blob + b" " + str(stage).encode() + b"\t" + self.path.encode() + b"\0" for stage in (1, 2, 3))
        run_git(self.root, "update-index", "-z", "--index-info", data=records)
        self.assertIn("evidence.dirty", self.codes())
        run_git(self.root, "reset", "-q", "HEAD", "--", self.path)
        run_git(self.root, "update-index", "--cacheinfo", "120000", blob.decode(), self.path)
        self.assertIn("evidence.path", self.codes())

    def test_path_resolving_outside_is_rejected(self) -> None:
        outside = Path(self.enterContext(tempfile.TemporaryDirectory())) / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        original = Path.resolve

        def resolve(path: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
            return outside if path == self.root / self.path else original(path, *args, **kwargs)

        with patch.object(Path, "resolve", resolve):
            self.assertIn("evidence.path", self.codes())

    def test_git_failures_close_eligibility(self) -> None:
        with patch("backlog.evidence.subprocess.run", side_effect=OSError("Git unavailable")):
            self.assertIn("evidence.git", self.codes())
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        write_evidence(root, self.path)
        self.root = root
        self.assertIn("evidence.git", self.codes())

    def test_slot_kind_result_matrix_and_identity(self) -> None:
        for slot in ("gate", "review", "completion", "release"):
            child = "G1" if slot == "release" else "T1.1"
            gate = 1 if slot == "gate" else None
            for kind in ("verification", "artifact", "review", "approval"):
                for result in ("passed", "accepted"):
                    with self.subTest(slot=slot, kind=kind, result=result):
                        write_evidence(self.root, self.path, child=child, gate=gate, kind=kind, result=result)
                        run_git(self.root, "add", "--", self.path)
                        codes = self.codes(head=False, child=child, gate=gate, kinds=allowed_kinds(slot))
                        self.assertEqual(kind not in allowed_kinds(slot), "evidence.kind" in codes)
                        self.assertEqual(result != ("accepted" if kind in {"review", "approval"} else "passed"), "evidence.result" in codes)
                        self.assertNotIn("evidence.child-mismatch", codes)
                        self.assertNotIn("evidence.gate-mismatch", codes)
            self.assertIn("evidence.child-mismatch", self.codes(head=False, child="T1.9", gate=gate))
            self.assertIn("evidence.gate-mismatch", self.codes(head=False, child=child, gate=2 if gate is None else None))

    def test_exact_metadata_order_date_subject_and_gate(self) -> None:
        original = (self.root / self.path).read_text(encoding="utf-8")
        mutations = (
            ("- **Gate:** `1`", "- **Gate:** `0`", "evidence.gate-mismatch"),
            ("- **Gate:** `1`", "- **Gate:** `-1`", "evidence.gate-mismatch"),
            ("2026-09-05", "2026-02-30", "evidence.metadata"),
            ("Verified fixture contract", "", "evidence.metadata"),
            ("- **Kind:** verification\n- **Result:** passed", "- **Result:** passed\n- **Kind:** verification", "evidence.metadata"),
            ("- **Kind:** verification", "- **Kind:** unknown", "evidence.kind"),
        )
        for old, new, code in mutations:
            with self.subTest(new=new):
                (self.root / self.path).write_text(original.replace(old, new), encoding="utf-8", newline="\n")
                run_git(self.root, "add", "--", self.path)
                self.assertIn(code, self.codes(head=False))


if __name__ == "__main__":
    unittest.main()
