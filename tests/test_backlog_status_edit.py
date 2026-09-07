from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass, replace
import hashlib
from pathlib import Path
import os
import stat
import sys
import tempfile
from typing import override
import unittest
from unittest.mock import patch

from tests.backlog_audit_support import (
    audit_fixture,
    replace_bytes,
    replace_text,
    reviewed_gate_fixture,
    run_git,
    write_active_design,
    write_active_plan,
    write_evidence,
)

SCRIPTS = Path(__file__).resolve().parents[1] / ".codex" / "skills" / "backlog-status" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from backlog.audit import audit_repository  # noqa: E402  # ty: ignore[unresolved-import]
from backlog.edit import (  # noqa: E402  # ty: ignore[unresolved-import]
    MutationPlan,
    MutationRefusal,
    plan_resume,
    plan_record_gate,
    plan_reopen_gate,
    plan_selection,
    plan_suspend,
    plan_transition,
    _NONSUSPENDED,
    _TRANSITIONS,
)
from backlog.model import Finding  # noqa: E402  # ty: ignore[unresolved-import]
from backlog import edit  # noqa: E402  # ty: ignore[unresolved-import]


class PublicationTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        audit_fixture(self.root)
        self.plan = plan_selection(self.root, "T1.2", expect_current=None)

    def publish(self):
        self.assertTrue(callable(getattr(edit, "publish_mutation", None)), "publication boundary is absent")
        return edit.publish_mutation(self.plan)

    def assert_unpublished(self) -> None:
        self.assertEqual(self.plan.original, self.plan.target.read_bytes())
        self.assertEqual([], list(self.root.glob(".BACKLOG.md.*.tmp")))

    def test_success_publishes_exact_bytes_preserves_mode_and_closes_before_replace(self) -> None:
        mode = stat.S_IMODE(self.plan.target.stat().st_mode)
        original_replace = os.replace
        partials: list[Path] = []

        def replace_closed(source, target):
            partial = Path(source)
            partials.append(partial)
            self.assertEqual(self.root, partial.parent)
            self.assertRegex(partial.name, r"^\.BACKLOG\.md\..+\.tmp$")
            self.assertEqual(mode, stat.S_IMODE(partial.stat().st_mode))
            self.assertEqual(self.plan.candidate, partial.read_bytes())
            # Windows refuses this rename if the writer is still open.
            return original_replace(source, target)

        with patch("os.replace", side_effect=replace_closed):
            loaded = self.publish()
        self.assertEqual((), loaded.findings)
        self.assertEqual(self.plan.candidate, self.plan.target.read_bytes())
        self.assertEqual(1, len(partials))
        self.assertFalse(partials[0].exists())

    def test_initial_stale_target_refuses_before_creating_a_partial(self) -> None:
        changed = self.plan.original + b"\n"
        self.plan.target.write_bytes(changed)
        with patch("tempfile.mkstemp", side_effect=AssertionError("stale plan created a partial")):
            with self.assertRaises(MutationRefusal) as raised:
                self.publish()
        self.assertEqual("mutation.stale", raised.exception.code)
        self.assertEqual(changed, self.plan.target.read_bytes())

    def test_fresh_candidate_audit_refuses_changed_non_target_authority(self) -> None:
        evidence = self.root / ".superpowers/sdd/t1-1/gate-1.md"
        evidence.write_bytes(evidence.read_bytes() + b"Changed after planning.\n")
        with self.assertRaises(MutationRefusal) as raised:
            self.publish()
        self.assertEqual("mutation.audit", raised.exception.code)
        self.assert_unpublished()

    def test_prepublication_io_failures_preserve_original_and_remove_partial(self) -> None:
        for seam in ("mkstemp", "fsync", "chmod", "replace"):
            with self.subTest(seam=seam):
                module = "tempfile" if seam == "mkstemp" else "os"
                with patch(f"{module}.{seam}", side_effect=OSError(f"{seam} failed")):
                    with self.assertRaises(MutationRefusal) as raised:
                        self.publish()
                self.assertEqual("mutation.publish", raised.exception.code)
                self.assertIn(f"{seam} failed", str(raised.exception))
                self.assert_unpublished()

    def test_target_stat_failure_is_a_domain_refusal_without_publication(self) -> None:
        original_stat = Path.stat

        def failing_stat(path, *args, **kwargs):
            if path == self.plan.target:
                raise OSError("target stat failed")
            return original_stat(path, *args, **kwargs)

        with patch.object(Path, "stat", failing_stat):
            with self.assertRaises(MutationRefusal) as raised:
                self.publish()
        self.assertIn("target stat failed", str(raised.exception))
        self.assert_unpublished()

    def test_cleanup_failure_keeps_primary_first_and_names_owned_partial(self) -> None:
        with patch("os.replace", side_effect=OSError("primary replace failed")):
            with patch.object(Path, "unlink", side_effect=OSError("cleanup failed")):
                with self.assertRaises(MutationRefusal) as raised:
                    self.publish()
        partials = list(self.root.glob(".BACKLOG.md.*.tmp"))
        self.assertEqual(1, len(partials))
        message = str(raised.exception)
        self.assertLess(message.index("primary replace failed"), message.index("cleanup failed"))
        self.assertIn(str(partials[0]), message)
        self.assertEqual(self.plan.original, self.plan.target.read_bytes())

    def test_descriptor_cleanup_failure_keeps_open_failure_first(self) -> None:
        real_close = os.close

        def close_then_fail(fd):
            real_close(fd)
            raise OSError("descriptor cleanup failed")

        with patch("os.fdopen", side_effect=OSError("opening partial failed")), patch("os.close", side_effect=close_then_fail):
            with self.assertRaises(MutationRefusal) as raised:
                self.publish()
        message = str(raised.exception)
        self.assertIn("opening partial failed", message)
        self.assertLess(message.index("opening partial failed"), message.index("descriptor cleanup failed"))
        self.assert_unpublished()

    def test_failure_cleans_only_owned_partial_and_leaves_other_siblings(self) -> None:
        other = self.root / ".BACKLOG.md.other-owner.tmp"
        other.write_bytes(b"another writer")
        with patch("os.fsync", side_effect=OSError("fsync failed")):
            with self.assertRaises(MutationRefusal):
                self.publish()
        self.assertEqual(b"another writer", other.read_bytes())
        self.assertEqual([other], list(self.root.glob(".BACKLOG.md.*.tmp")))
        self.assertEqual(self.plan.original, self.plan.target.read_bytes())

    def test_final_audit_failure_reports_published_state_and_no_retry(self) -> None:
        def fail_final(root, *, backlog_text=None):
            if backlog_text is None:
                raise OSError("final audit failed")
            return audit_repository(root, backlog_text=backlog_text)

        with patch("backlog.edit.audit_repository", side_effect=fail_final):
            with self.assertRaises(MutationRefusal) as raised:
                self.publish()
        self.assertEqual("mutation.published", raised.exception.code)
        self.assertIn("do not retry", str(raised.exception).lower())
        self.assertEqual(self.plan.candidate, self.plan.target.read_bytes())
        self.assertEqual([], list(self.root.glob(".BACKLOG.md.*.tmp")))

    def test_write_flush_close_failures_and_short_write_do_not_publish(self) -> None:
        real_fdopen = os.fdopen
        for stage in ("write", "short-write", "flush", "close"):
            with self.subTest(stage=stage):

                class FaultyStream:
                    def __init__(self, fd, mode):
                        self.stream = real_fdopen(fd, mode)

                    def write(self, data):
                        if stage == "write":
                            raise OSError("write failed")
                        if stage == "short-write":
                            return self.stream.write(data[:-1])
                        return self.stream.write(data)

                    def flush(self):
                        if stage == "flush":
                            raise OSError("flush failed")
                        return self.stream.flush()

                    def fileno(self):
                        return self.stream.fileno()

                    def close(self):
                        self.stream.close()
                        if stage == "close":
                            raise OSError("close failed")

                    def __enter__(self):
                        return self

                    def __exit__(self, *args):
                        self.close()

                with patch("os.fdopen", side_effect=FaultyStream):
                    with self.assertRaises(MutationRefusal) as raised:
                        self.publish()
                self.assertEqual("mutation.publish", raised.exception.code)
                self.assert_unpublished()

    def test_publication_orders_durability_stale_checks_and_fresh_audits(self) -> None:
        events: list[str] = []
        real_stat, real_read = Path.stat, Path.read_bytes
        real_create, real_fdopen = tempfile.mkstemp, os.fdopen
        real_fsync, real_chmod, real_replace = os.fsync, os.chmod, os.replace

        def observed_stat(path, *args, **kwargs):
            if path == self.plan.target and kwargs.get("follow_symlinks") is False:
                events.append("mode")
            return real_stat(path, *args, **kwargs)

        def observed_read(path):
            if path == self.plan.target and "final-audit" not in events:
                events.append("recheck")
            return real_read(path)

        def create(**kwargs):
            events.append("create")
            return real_create(**kwargs)

        class ObservedStream:
            def __init__(self, fd, mode):
                self.stream = real_fdopen(fd, mode)

            def write(self, data):
                events.append("write")
                return self.stream.write(data)

            def flush(self):
                events.append("flush")
                return self.stream.flush()

            def fileno(self):
                return self.stream.fileno()

            def close(self):
                events.append("close")
                self.stream.close()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()

        def fsync(fd):
            events.append("fsync")
            return real_fsync(fd)

        def chmod(path, mode):
            events.append("chmod")
            return real_chmod(path, mode)

        def audit(root, *, backlog_text=None):
            events.append("final-audit" if backlog_text is None else "candidate-audit")
            return audit_repository(root, backlog_text=backlog_text)

        def publish_replace(source, target):
            events.append("replace")
            return real_replace(source, target)

        with patch.object(Path, "stat", observed_stat), patch.object(Path, "read_bytes", observed_read):
            with patch("tempfile.mkstemp", side_effect=create), patch("os.fdopen", side_effect=ObservedStream):
                with patch("os.fsync", side_effect=fsync), patch("os.chmod", side_effect=chmod), patch("os.replace", side_effect=publish_replace):
                    with patch("backlog.edit.audit_repository", side_effect=audit):
                        loaded = self.publish()
        self.assertEqual((), loaded.findings)
        self.assertEqual(
            ["mode", "recheck", "create", "write", "flush", "fsync", "close", "chmod", "recheck", "candidate-audit", "replace", "final-audit"], events
        )
        self.assertEqual(self.plan.candidate, self.plan.target.read_bytes())

    def test_final_stale_recheck_failure_cleans_partial(self) -> None:
        original_read = Path.read_bytes
        reads = 0

        def fail_second_read(path):
            nonlocal reads
            if path == self.plan.target:
                reads += 1
                if reads == 2:
                    return self.plan.original + b"changed"
            return original_read(path)

        with patch.object(Path, "read_bytes", fail_second_read):
            with self.assertRaises(MutationRefusal) as raised:
                self.publish()
        self.assertEqual("mutation.stale", raised.exception.code)
        self.assert_unpublished()

    def test_final_audit_error_finding_is_a_published_state_refusal(self) -> None:
        failure = Finding("fixture.error", "error", "BACKLOG.md", 1, None, None, "final audit invalid")

        def audit(root, *, backlog_text=None):
            loaded = audit_repository(root, backlog_text=backlog_text)
            return replace(loaded, findings=(failure,)) if backlog_text is None else loaded

        with patch("backlog.edit.audit_repository", side_effect=audit):
            with self.assertRaises(MutationRefusal) as raised:
                self.publish()
        self.assertEqual("mutation.published", raised.exception.code)
        self.assertIn("do not retry", str(raised.exception).lower())
        self.assertEqual(self.plan.candidate, self.plan.target.read_bytes())


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
            ("queued", "designing"),
            ("designing", "specified"),
            ("specified", "planned"),
            ("planned", "in_progress"),
            ("in_progress", "implemented"),
            ("implemented", "reviewed"),
            ("reviewed", "verified"),
            ("specified", "designing"),
            ("planned", "specified"),
            ("in_progress", "planned"),
            ("implemented", "in_progress"),
            ("reviewed", "implemented"),
            ("verified", "reviewed"),
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


class GatePlanningTests(unittest.TestCase):
    def reviewed_root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory())) / "repository"
        audit_fixture(root)
        reviewed_gate_fixture(root)
        replace_text(
            root,
            "ROADMAP.md",
            "| `G1` | Canonical vertical-slice reconciliation | `T1.2` |",
            "| `G1` | Canonical vertical-slice reconciliation | `M0` |",
        )
        replace_text(
            root,
            "BACKLOG.md",
            "| `G1` | Canonical vertical-slice reconciliation | `waiting` | `T1.2` | — |",
            "| `G1` | Canonical vertical-slice reconciliation | `ready` | `M0` | — |",
        )
        return root

    def stage_gate_evidence(
        self,
        root: Path,
        path: str = ".superpowers/sdd/t1-2/gate-1.md",
        *,
        child: str = "T1.2",
        gate: int | None = 1,
        kind: str = "verification",
        result: str = "passed",
    ) -> str:
        write_evidence(root, path, child=child, gate=gate, kind=kind, result=result)
        run_git(root, "add", "--", path)
        return path

    def assert_refusal(self, code: str, planner, *args: object, **kwargs: object) -> None:  # type: ignore[no-untyped-def]
        with self.assertRaises(MutationRefusal) as raised:
            planner(*args, **kwargs)
        self.assertEqual(code, raised.exception.code)

    def test_record_gate_refuses_stale_gate_preconditions_and_invalid_ordinals(self) -> None:
        root = self.reviewed_root()
        evidence = self.stage_gate_evidence(root)

        self.assert_refusal("mutation.expected-gate", plan_record_gate, root, "T1.2", 1, expect_open=False, evidence=(evidence,))
        for ordinal in (0, 2):
            with self.subTest(ordinal=ordinal):
                self.assert_refusal("mutation.gate", plan_record_gate, root, "T1.2", ordinal, expect_open=True, evidence=(evidence,))

        closed = plan_record_gate(root, "T1.2", 1, expect_open=True, evidence=(evidence,))
        (root / "BACKLOG.md").write_bytes(closed.candidate)
        self.assert_refusal("mutation.expected-gate", plan_record_gate, root, "T1.2", 1, expect_open=True, evidence=(evidence,))

    def test_record_gate_delegates_evidence_eligibility_to_candidate_audit(self) -> None:
        cases = (
            ("missing", ".superpowers/sdd/t1-2/missing.md", "T1.2", 1, "verification", "passed", "evidence.path"),
            ("wrong-child", ".superpowers/sdd/t1-2/wrong-child.md", "T1.1", 1, "verification", "passed", "evidence.child-mismatch"),
            ("wrong-gate", ".superpowers/sdd/t1-2/wrong-gate.md", "T1.2", 2, "verification", "passed", "evidence.gate-mismatch"),
            ("wrong-kind", ".superpowers/sdd/t1-2/wrong-kind.md", "T1.2", 1, "review", "accepted", "evidence.kind"),
            ("wrong-result", ".superpowers/sdd/t1-2/wrong-result.md", "T1.2", 1, "verification", "failed", "evidence.result"),
        )
        for label, path, child, gate, kind, result, code in cases:
            with self.subTest(label=label):
                root = self.reviewed_root()
                if label != "missing":
                    self.stage_gate_evidence(root, path, child=child, gate=gate, kind=kind, result=result)
                self.assert_refusal(code, plan_record_gate, root, "T1.2", 1, expect_open=True, evidence=(path,))

        root = self.reviewed_root()
        untracked = self.stage_gate_evidence(root, ".superpowers/sdd/t1-2/untracked.md")
        run_git(root, "reset", "--", untracked)
        self.assert_refusal("evidence.untracked", plan_record_gate, root, "T1.2", 1, expect_open=True, evidence=(untracked,))

        root = self.reviewed_root()
        dirty = self.stage_gate_evidence(root, ".superpowers/sdd/t1-2/dirty.md")
        (root / dirty).write_text("changed", encoding="utf-8")
        self.assert_refusal("evidence.dirty", plan_record_gate, root, "T1.2", 1, expect_open=True, evidence=(dirty,))

    def test_record_gate_rejects_empty_duplicate_and_malformed_evidence_paths(self) -> None:
        root = self.reviewed_root()
        evidence = self.stage_gate_evidence(root)

        self.assert_refusal("mutation.evidence", plan_record_gate, root, "T1.2", 1, expect_open=True, evidence=())
        self.assert_refusal("mutation.evidence", plan_record_gate, root, "T1.2", 1, expect_open=True, evidence=(evidence, evidence))
        for path in ("bad|path.md", "bad\npath.md", "../outside.md", "bad\\path.md"):
            with self.subTest(path=path):
                self.assert_refusal("mutation.evidence", plan_record_gate, root, "T1.2", 1, expect_open=True, evidence=(path,))

    def test_record_and_reopen_gate_update_the_exact_marker_suffix_and_derived_count(self) -> None:
        root = self.reviewed_root()
        later = self.stage_gate_evidence(root, ".superpowers/sdd/t1-2/z-gate.md")
        earlier = self.stage_gate_evidence(root, ".superpowers/sdd/t1-2/a-gate.md")

        recorded = plan_record_gate(root, "T1.2", 1, expect_open=True, evidence=(later, earlier))

        candidate = recorded.candidate.decode("utf-8")
        self.assertIn("| 1/1 |", candidate)
        self.assertIn(
            "- [x] Frozen parser remains open. — Evidence: [verification](.superpowers/sdd/t1-2/a-gate.md) [verification](.superpowers/sdd/t1-2/z-gate.md)",
            candidate,
        )
        self.assertEqual((earlier, later), recorded.audit.snapshot.backlog.children[1].gates.items[0].evidence)
        (root / "BACKLOG.md").write_bytes(recorded.candidate)

        reopened = plan_reopen_gate(root, "T1.2", 1, expect_closed=True, reason="Evidence contract changed")

        reopened_text = reopened.candidate.decode("utf-8")
        self.assertIn("| 0/1 |", reopened_text)
        self.assertIn("- [ ] Frozen parser remains open.", reopened_text)
        self.assertNotIn("Evidence: [verification](.superpowers/sdd/t1-2/a-gate.md)", reopened_text)
        self.assertEqual("Reopened gate `1` for `T1.2`: Evidence contract changed", reopened.rationale)

    def test_gate_edit_preserves_wrapped_lf_crlf_and_no_final_newline_bytes(self) -> None:
        for newline, final_newline in ((b"\n", True), (b"\r\n", True), (b"\n", False)):
            with self.subTest(newline=newline, final_newline=final_newline):
                root = self.reviewed_root()
                evidence = self.stage_gate_evidence(root)
                target = root / "BACKLOG.md"
                original = target.read_bytes().replace(b"Frozen parser remains open.", b"Frozen parser remains\n      open.")
                original = original.replace(b"\n", newline)
                if not final_newline:
                    original = original.rstrip(b"\r\n")
                target.write_bytes(original)

                recorded = plan_record_gate(root, "T1.2", 1, expect_open=True, evidence=(evidence,))
                recorded_lines = recorded.candidate.splitlines(keepends=True)
                original_lines = original.splitlines(keepends=True)
                changed = [index for index, pair in enumerate(zip(original_lines, recorded_lines)) if pair[0] != pair[1]]
                self.assertEqual(3, len(changed))
                self.assertTrue(recorded_lines[changed[0]].endswith(newline) or not final_newline)
                self.assertEqual(original_lines[: changed[0]], recorded_lines[: changed[0]])
                self.assertEqual(original_lines[changed[-1] + 1 :], recorded_lines[changed[-1] + 1 :])

                (root / "BACKLOG.md").write_bytes(recorded.candidate)
                reopened = plan_reopen_gate(root, "T1.2", 1, expect_closed=True, reason="Recheck evidence")
                self.assertEqual(original, reopened.candidate)

    def test_reopen_gate_removes_source_wrapped_multi_whitespace_evidence(self) -> None:
        """A source-preserving reopen must not canonicalize a valid wrapped suffix."""
        root = self.reviewed_root()
        artifact = self.stage_gate_evidence(root, ".superpowers/sdd/t1-2/gate-artifact.md", kind="artifact")
        verification = self.stage_gate_evidence(root, ".superpowers/sdd/t1-2/gate-verification.md")
        replace_bytes(
            root,
            "BACKLOG.md",
            b"- [ ] Frozen parser remains open.\n",
            (
                b"- [x] Frozen parser remains\n"
                + f"      open. — Evidence: [artifact]({artifact})   \n".encode()
                + f"      [verification]({verification})\n".encode()
            ),
        )
        replace_bytes(root, "BACKLOG.md", b"| 0/1 | [review]", b"| 1/1 | [review]")

        reopened = plan_reopen_gate(root, "T1.2", 1, expect_closed=True, reason="Recheck source evidence")

        self.assertIn(b"- [ ] Frozen parser remains\n      open.\n", reopened.candidate)
        self.assertNotIn(b"open. \xe2\x80\x94 Evidence:", reopened.candidate)
        self.assertNotIn(artifact.encode(), reopened.candidate)
        self.assertNotIn(verification.encode(), reopened.candidate)

    def test_record_gate_appends_before_a_trailing_whitespace_only_continuation(self) -> None:
        """A record must append to the last meaningful line, not a blank continuation."""
        root = self.reviewed_root()
        evidence = self.stage_gate_evidence(root)
        replace_bytes(
            root,
            "BACKLOG.md",
            b"- [ ] Frozen parser remains open.\n",
            b"- [ ] Frozen parser remains open.\n      \t \n",
        )

        recorded = plan_record_gate(root, "T1.2", 1, expect_open=True, evidence=(evidence,))

        self.assertIn(
            "- [x] Frozen parser remains open. — Evidence: [verification](.superpowers/sdd/t1-2/gate-1.md)\n      \t \n".encode(),
            recorded.candidate,
        )

    def test_reopen_gate_requires_a_closed_gate_reviewed_child_and_reason(self) -> None:
        root = self.reviewed_root()
        evidence = self.stage_gate_evidence(root)
        recorded = plan_record_gate(root, "T1.2", 1, expect_open=True, evidence=(evidence,))
        (root / "BACKLOG.md").write_bytes(recorded.candidate)
        run_git(root, "add", "--", "BACKLOG.md", "docs", ".superpowers")
        run_git(root, "commit", "-qm", "Reviewed gate fixture")

        self.assert_refusal("mutation.expected-gate", plan_reopen_gate, root, "T1.2", 1, expect_closed=False, reason="Recheck")
        self.assert_refusal("mutation.gate", plan_reopen_gate, root, "T1.2", 2, expect_closed=True, reason="Recheck")
        self.assert_refusal("mutation.reason", plan_reopen_gate, root, "T1.2", 1, expect_closed=True, reason=" bad")

        verified = plan_transition(root, "T1.2", "verified", expect="reviewed")
        (root / "BACKLOG.md").write_bytes(verified.candidate)
        run_git(root, "add", "--", "BACKLOG.md", "docs", ".superpowers")
        run_git(root, "commit", "-qm", "Verified evidence fixture")
        self.assert_refusal("mutation.transition", plan_reopen_gate, root, "T1.2", 1, expect_closed=True, reason="Recheck")

        reviewed = plan_transition(root, "T1.2", "reviewed", expect="verified")
        (root / "BACKLOG.md").write_bytes(reviewed.candidate)
        reopened = plan_reopen_gate(root, "T1.2", 1, expect_closed=True, reason="Recheck")
        self.assertIn("| 0/1 |", reopened.candidate.decode("utf-8"))
