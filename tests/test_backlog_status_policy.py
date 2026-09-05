from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
POLICY_PATH = "docs/superpowers/specs/2026-09-05-t1-3-audit-policy-supplement-design.md"
sys.path.insert(0, str(SCRIPTS))

from backlog.policy import PolicyError, allowed_kinds, load_policy  # noqa: E402  # ty: ignore[unresolved-import]


class AuditPolicyTests(unittest.TestCase):
    def remove_repository(self, root: Path) -> None:
        def make_writable(function: Callable[[str], object], path: str, _error: BaseException) -> None:
            os.chmod(path, 0o700)
            function(path)

        shutil.rmtree(root, onexc=make_writable)

    def make_repository(self, transform: Callable[[str], str] | None = None) -> Path:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(self.remove_repository, temporary)
        target = temporary / POLICY_PATH
        target.parent.mkdir(parents=True)
        text = (ROOT / POLICY_PATH).read_text(encoding="utf-8")
        if transform is not None:
            text = transform(text)
        target.write_text(text, encoding="utf-8", newline="\n")
        self.run_git(temporary, "init", "-q")
        self.run_git(temporary, "config", "core.autocrlf", "false")
        self.run_git(temporary, "add", POLICY_PATH)
        self.run_git(
            temporary,
            "-c",
            "user.name=Fixture Owner",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture policy",
        )
        return temporary

    def run_git(self, root: Path, *arguments: str) -> None:
        subprocess.run(
            ("git", "-C", str(root), *arguments),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_approved_committed_policy_loads_exact_historical_pins(self) -> None:
        policy = load_policy(ROOT)

        self.assertEqual(("D1.1", "D1.2", "D1.3"), tuple(item.child for item in policy.historical))
        expected = {
            "D1.1": "c4869782b22736cf5372d93b21b330e85657bcc4c832f041f088bd79caa4780e",  # pragma: allowlist secret
            "D1.2": "9b3c3a2c984f4536730c72c3479577b86707b03e50fca8d3e13f5a50ed80343f",  # pragma: allowlist secret
            "D1.3": "ec5a0c559ae3d49d412446c538eeb7b4fc34069f9030e973473e8f7e6d08c3b0",  # pragma: allowlist secret
        }
        self.assertEqual(expected, {item.child: item.sha256 for item in policy.historical})
        for admission in policy.historical:
            digest = __import__("hashlib").sha256((ROOT / admission.plan).read_bytes()).hexdigest()
            self.assertEqual(admission.sha256, digest)

    def test_slot_kind_matrix_is_fixed(self) -> None:
        self.assertEqual(frozenset({"verification", "artifact"}), allowed_kinds("gate"))
        self.assertEqual(frozenset({"review"}), allowed_kinds("review"))
        self.assertEqual(frozenset({"verification", "artifact"}), allowed_kinds("completion"))
        self.assertEqual(frozenset({"verification", "artifact"}), allowed_kinds("release"))

    def test_missing_policy_is_unavailable(self) -> None:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)

        with self.assertRaises(PolicyError) as raised:
            load_policy(temporary)

        self.assertEqual("policy.unavailable", raised.exception.code)
        self.assertEqual(POLICY_PATH, raised.exception.path)

    def test_draft_or_missing_approval_policy_is_unapproved(self) -> None:
        mutations = (
            lambda text: text.replace("- **Status:** approved", "- **Status:** draft", 1),
            lambda text: text.replace("- **Approval:** 2026-09-05 — Jeff / tvproductions", "- **Approval:** —", 1),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                root = self.make_repository(mutation)
                with self.assertRaises(PolicyError) as raised:
                    load_policy(root)
                self.assertEqual("policy.unapproved", raised.exception.code)

    def test_unstaged_or_index_only_policy_edit_is_unavailable(self) -> None:
        for staged in (False, True):
            with self.subTest(staged=staged):
                root = self.make_repository()
                target = root / POLICY_PATH
                target.write_text(target.read_text(encoding="utf-8") + "\nEdited.\n", encoding="utf-8")
                if staged:
                    self.run_git(root, "add", POLICY_PATH)
                with self.assertRaises(PolicyError) as raised:
                    load_policy(root)
                self.assertEqual("policy.unavailable", raised.exception.code)

    def test_duplicate_admission_rows_are_invalid(self) -> None:
        row = (
            "| `D1.1` | `docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md` | "
            "`c4869782b22736cf5372d93b21b330e85657bcc4c832f041f088bd79caa4780e` |"
        )
        root = self.make_repository(lambda text: text.replace(row, f"{row}\n{row}", 1))

        with self.assertRaises(PolicyError) as raised:
            load_policy(root)

        self.assertEqual("policy.invalid", raised.exception.code)

    def test_invalid_digest_and_malformed_plan_paths_are_invalid(self) -> None:
        mutations = (
            lambda text: text.replace("c4869782b22736cf5372d93b21b330e85657bcc4c832f041f088bd79caa4780e", "A" * 64, 1),
            lambda text: text.replace(
                "docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md",
                "../outside.md",
                1,
            ),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                root = self.make_repository(mutation)
                with self.assertRaises(PolicyError) as raised:
                    load_policy(root)
                self.assertEqual("policy.invalid", raised.exception.code)
                self.assertIsNotNone(raised.exception.line)


if __name__ == "__main__":
    unittest.main()
