from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass, replace
import hashlib
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.backlog_audit_support import audit_fixture, replace_bytes

SCRIPTS = Path(__file__).resolve().parents[1] / ".codex" / "skills" / "backlog-status" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from backlog.audit import audit_repository  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.edit import MutationPlan, MutationRefusal, plan_selection  # noqa: E402  # ty: ignore[unresolved-import]
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

        def warning_audit(path: Path, *, backlog_text: str | None = None):
            return replace(original_audit(path, backlog_text=backlog_text), findings=(warning,))

        with patch("backlog.edit.audit_repository", side_effect=warning_audit):
            plan = plan_selection(root, "T1.2", expect_current=None)

        self.assertEqual((warning,), plan.audit.findings)


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
