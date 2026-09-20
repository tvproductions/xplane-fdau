"""Read-only dependency refresh status contracts."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any, override
from unittest.mock import patch
from urllib.request import Request
from urllib.parse import urlparse

from tools import dependency_refresh as refresh
from tools.dependency_matrix import MatrixResult
from tools.dependency_refresh import canonical_json, collect_status, main


def _index(name: str, versions: tuple[str, ...], *, yanked: bool = False, requires_python: str = ">=3.12") -> dict[str, object]:
    files = []
    for version in versions:
        files.append(
            {
                "filename": f"{name.replace(chr(45), chr(95))}-{version}-py3-none-any.whl",
                "hashes": {"sha256": hashlib.sha256(f"{name}-{version}".encode()).hexdigest()},
                "requires-python": requires_python,
                "yanked": yanked and version == versions[0],
            }
        )
    return {"name": name, "versions": list(versions), "files": files}


class StatusFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        (root / ".github/workflows").mkdir(parents=True)
        (root / "pyproject.toml").write_text(
            '[project]\nname = "xplane-fdau"\nversion = "0.1.0"\nrequires-python = ">=3.12"\ndependencies = []\n'
            '[dependency-groups]\ndev = ["foo>=1"]\ntest = ["universal-only>=1"]\n'
            '[build-system]\nrequires = ["uv_build>=0.12,<0.13"]\nbuild-backend = "uv_build"\n'
            '[tool.uv]\nrequired-version = "==0.12.16"\n',
            encoding="utf-8",
        )
        (root / ".python-version").write_text("3.12\n", encoding="utf-8")
        (root / ".github/workflows/ci.yml").write_text('- uses: astral-sh/setup-uv@v10.1.0\n  with:\n    version: "0.12.16"\n', encoding="utf-8")
        (root / ".github/workflows/release-readiness.yml").write_text('- uses: astral-sh/setup-uv@v10.1.0\n  with:\n    version: "0.12.16"\n', encoding="utf-8")
        packages: list[dict[str, Any]] = []
        for name, version in (("foo", "1.0"), ("universal-only", "1.0")):
            digest = hashlib.sha256(f"{name}-{version}".encode()).hexdigest()
            packages.append(
                {
                    "name": name,
                    "version": version,
                    "source": {"registry": "https://pypi.org/simple"},
                    "wheels": [
                        {"url": f"https://files.pythonhosted.org/{name.replace(chr(45), chr(95))}-{version}-py3-none-any.whl", "hash": f"sha256:{digest}"}
                    ],
                }
            )
        packages.append({"name": "xplane-fdau", "version": "0.1.0", "source": {"editable": "."}})
        (root / "uv.lock").write_text(
            'version = 1\nrevision = 3\nrequires-python = ">=3.12"\n' + "".join(self._lock_package(p) for p in packages), encoding="utf-8"
        )
        self.tree = self._graph(include_universal=True)
        self.metadata = {
            "schema": {"version": "preview"},
            "workspace_root": "ROOT",
            "environment": {"root": "ROOT/.venv", "python": {"path": "ROOT/.venv/python", "version": "3.12.13", "implementation": "cpython"}},
            "workspace": {"path": "ROOT", "id": "workspace+ROOT"},
            "requires_python": ">=3.12",
            "conflicts": {"sets": []},
            "module_owners": {},
            "members": [],
            "resolution": self._graph(include_universal=True)["resolution"],
        }
        self.audit: dict[str, Any] = {
            "schema": {"version": "preview"},
            "summary": {"audited_packages": 2, "vulnerabilities": 0, "adverse_statuses": 0},
            "vulnerabilities": [],
            "adverse_statuses": [],
        }
        self.audit_exit = 0
        self.indexes: dict[str, dict[str, Any]] = {
            "foo": _index("foo", ("1.0", "2.0")),
            "universal-only": _index("universal-only", ("1.0", "2.0")),
            "uv": _index("uv", ("0.12.16", "0.12.17")),
            "uv-build": _index("uv-build", ("0.12.16", "0.12.17")),
        }
        self.calls: list[tuple[str, ...]] = []

    @staticmethod
    def _lock_package(package: dict[str, Any]) -> str:
        name, version = package["name"], package["version"]
        if name == "xplane-fdau":
            return f'\n[[package]]\nname = "{name}"\nversion = "{version}"\nsource = {{ editable = "." }}\n'
        digest = hashlib.sha256(f"{name}-{version}".encode()).hexdigest()
        filename = f"{name.replace(chr(45), chr(95))}-{version}-py3-none-any.whl"
        return (
            f'\n[[package]]\nname = "{name}"\nversion = "{version}"\n'
            f'source = {{ registry = "https://pypi.org/simple" }}\n'
            f'wheels = [{{ url = "https://files.pythonhosted.org/{filename}", hash = "sha256:{digest}" }}]\n'
        )

    @staticmethod
    def _graph(*, include_universal: bool) -> dict[str, object]:
        resolution = {
            "foo==1.0@registry+https://pypi.org/simple": {
                "name": "foo",
                "version": "1.0",
                "source": {"registry": {"url": "https://pypi.org/simple"}},
                "kind": "package",
                "dependencies": [],
                "latest_version": "2.0",
                "wheels": [],
            },
            "xplane-fdau==0.1.0@editable+ROOT/": {
                "name": "xplane-fdau",
                "version": "0.1.0",
                "source": {"editable": "ROOT/"},
                "kind": "package",
                "dependencies": [],
                "dependency_groups": [],
            },
        }
        if include_universal:
            resolution["universal-only==1.0@registry+https://pypi.org/simple"] = {
                "name": "universal-only",
                "version": "1.0",
                "source": {"registry": {"url": "https://pypi.org/simple"}},
                "kind": "package",
                "dependencies": [],
                "latest_version": "2.0",
                "wheels": [],
            }
        return {
            "schema": {"version": "preview"},
            "workspace_root": "ROOT",
            "workspace": {"path": "ROOT", "id": "workspace+ROOT"},
            "roots": [],
            "inverted": False,
            "members": [],
            "resolution": resolution,
        }

    def runner(self, args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
        self.calls.append(args)
        if args == ("uv", "--version"):
            return 0, "uv 0.12.17 (test)\n", ""
        if args[:3] == ("uv", "--no-config", "tree"):
            return 0, json.dumps(self.tree), ""
        if args[:4] == ("uv", "--no-config", "workspace", "metadata"):
            metadata = dict(self.metadata)
            metadata["requires_python"] = ">=3.12"
            return 0, json.dumps(metadata), ""
        if args[:3] == ("uv", "--no-config", "audit"):
            return self.audit_exit, json.dumps(self.audit), ""
        if args == ("git", "branch", "--show-current"):
            return 0, "feature\n", ""
        if args == ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"):
            return 0, "", ""
        if args == ("git", "ls-files", "-s", "-z"):
            return 0, "", ""
        raise AssertionError(args)

    def opener(self, request: Request, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
        url = request.full_url
        name = urlparse(url).path.strip("/").split("/")[-1]
        return json.dumps(self.indexes[name]).encode(), url, "application/vnd.pypi.simple.v1+json"


class DependencyStatusTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.fixture = StatusFixture(Path(self.temporary.name))

    def test_status_enumerates_universal_lock_and_uses_no_config_after_uv_mismatch(self) -> None:
        report = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        self.assertEqual(
            set(report),
            {
                "schema_version",
                "uv",
                "python",
                "dependencies",
                "current_findings",
                "pre_apply_blockers",
                "proposed_files",
                "proposed_commands",
                "reviewed_paths",
                "plan_sha256",
            },
        )
        self.assertEqual({item["name"] for item in report["dependencies"]}, {"foo", "universal-only"})
        self.assertEqual({item["name"] for item in report["dependencies"] if item["outdated"]}, {"foo", "universal-only"})
        self.assertEqual(report["uv"]["installed"], "0.12.17")
        self.assertEqual(report["uv"]["required"], "==0.12.16")
        self.assertIn(("uv", "--no-config", "tree", "--outdated", "--all-groups", "--universal", "--locked", "--format", "json"), self.fixture.calls)
        self.assertTrue(all(isinstance(command, list) for command in report["proposed_commands"]))

    def test_current_advisory_and_yank_are_remediation_findings(self) -> None:
        self.fixture.indexes["foo"]["files"][0]["yanked"] = True
        self.fixture.audit = {
            "schema": {"version": "preview"},
            "summary": {"audited_packages": 2, "vulnerabilities": 1, "adverse_statuses": 0},
            "vulnerabilities": [{"name": "universal-only", "version": "1.0", "id": "GHSA-test", "fixed_version": "2.0"}],
            "adverse_statuses": [],
        }
        self.fixture.audit_exit = 1
        report = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        self.assertEqual({item["kind"] for item in report["current_findings"]}, {"advisory", "yanked"})
        self.assertEqual(report["pre_apply_blockers"], [])

    def test_malformed_advisory_is_source_blocker(self) -> None:
        self.fixture.audit = {"bad": []}
        report = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        self.assertIn("source", {item["kind"] for item in report["pre_apply_blockers"]})

    def test_incompatible_uv_release_is_blocker_and_retains_installed_version(self) -> None:
        self.fixture.indexes["uv"]["files"][1]["requires-python"] = ">=3.12,<3.14"
        report = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        self.assertEqual(report["uv"]["candidate"], "0.12.17")
        self.assertIn("incompatible-uv", {item["kind"] for item in report["pre_apply_blockers"]})

    def test_report_digest_and_json_ignore_absolute_root(self) -> None:
        first = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        with tempfile.TemporaryDirectory() as second_root:
            second_fixture = StatusFixture(Path(second_root))
            second = collect_status(second_fixture.root, second_fixture.runner, second_fixture.opener)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(first["plan_sha256"], second["plan_sha256"])
        self.assertTrue(canonical_json(first).endswith("\n"))
        self.assertFalse(canonical_json(first).endswith("\n\n"))
        self.assertNotIn(str(self.fixture.root), canonical_json(first))

    def test_error_report_json_is_ascii_safe_on_windows_console(self) -> None:
        output = canonical_json({"warning": "\u26a0"})
        self.assertIn("\\u26a0", output)
        output.encode("cp1252")

    def test_status_cli_json_and_human_render_same_report(self) -> None:
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch

        with patch(
            "tools.dependency_refresh.collect_status",
            return_value={"schema_version": 1, "uv": {}, "pre_apply_blockers": [], "current_findings": [], "dependencies": [], "plan_sha256": "abc"},
        ):
            json_output = StringIO()
            with redirect_stdout(json_output):
                self.assertEqual(main(["status", "--json"]), 0)
            human_output = StringIO()
            with redirect_stdout(human_output):
                self.assertEqual(main(["status"]), 0)
        self.assertEqual(json.loads(json_output.getvalue())["plan_sha256"], "abc")
        self.assertIn("abc", human_output.getvalue())

    def test_unknown_preview_root_blocks_status(self) -> None:
        self.fixture.tree["unexpected"] = "drift"
        report = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        self.assertIn("unknown uv preview schema", {item.get("reason") for item in report["pre_apply_blockers"]})


class DependencyApplyTests(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.fixture = StatusFixture(Path(self.temporary.name))

    def test_rejects_stale_source_lock_branch_and_unreviewed_paths_before_mutation(self) -> None:
        original = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        with self.assertRaisesRegex(refresh.ScopeError, "digest changed"):
            refresh.apply_status(self.fixture.root, "0" * 64, (), self.fixture.runner, self.fixture.opener, uv_owner="winget")
        self.fixture.indexes["uv"]["versions"].append("0.12.18")
        with self.assertRaisesRegex(refresh.ScopeError, "digest changed"):
            refresh.apply_status(self.fixture.root, original["plan_sha256"], (), self.fixture.runner, self.fixture.opener, uv_owner="winget")
        self.fixture.indexes["uv"] = _index("uv", ("0.12.16", "0.12.17"))
        (self.fixture.root / "uv.lock").write_text((self.fixture.root / "uv.lock").read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(refresh.ScopeError, "digest changed"):
            refresh.apply_status(self.fixture.root, original["plan_sha256"], (), self.fixture.runner, self.fixture.opener, uv_owner="winget")
        self.assertNotIn(("uv", "lock", "--upgrade"), self.fixture.calls)

    def test_rejects_unreviewed_dirty_path_and_accepts_exact_untracked_scope(self) -> None:
        source = self.fixture.root / "tools/dependency_sources.py"
        source.parent.mkdir()
        source.write_text("source", encoding="utf-8")
        scoped_runner = self._runner_with_scope("?? tools/dependency_sources.py\0")

        def older_uv(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            if args == ("uv", "--version"):
                return 0, "uv 0.12.16 (test)\n", ""
            return scoped_runner(args, cwd)

        report = collect_status(self.fixture.root, older_uv, self.fixture.opener)
        with self.assertRaisesRegex(refresh.ScopeError, "review scope"):
            refresh.apply_status(self.fixture.root, report["plan_sha256"], (), older_uv, self.fixture.opener, uv_owner="winget:astral-sh.uv")
        with self.assertRaisesRegex(refresh.ScopeError, "owner action required"):
            refresh.apply_status(
                self.fixture.root, report["plan_sha256"], ("tools/dependency_sources.py",), older_uv, self.fixture.opener, uv_owner="winget:astral-sh.uv"
            )
        self.assertNotIn(("uv", "lock", "--upgrade"), self.fixture.calls)

    def _runner_with_scope(self, status: str) -> Callable[[tuple[str, ...], Path], tuple[int, str, str]]:
        original_runner = self.fixture.runner

        def runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            if args == ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"):
                return 0, status, ""
            return original_runner(args, cwd)

        return runner

    def test_rejects_branch_or_staged_blob_change_with_unchanged_working_bytes(self) -> None:
        source = self.fixture.root / "tools/dependency_sources.py"
        source.parent.mkdir()
        source.write_text("stable", encoding="utf-8")
        base_runner = self.fixture.runner
        staged_blob = "a" * 40
        branch = "feature"

        def runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            if args == ("git", "branch", "--show-current"):
                return 0, branch + "\n", ""
            if args == ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"):
                return 0, "A  tools/dependency_sources.py\0", ""
            if args == ("git", "ls-files", "-s", "-z"):
                return 0, f"100644 {staged_blob} 0\ttools/dependency_sources.py\0", ""
            return base_runner(args, cwd)

        before = collect_status(self.fixture.root, runner, self.fixture.opener)
        self.assertEqual(before["reviewed_paths"][0]["index_blob"], "a" * 40)
        staged_blob = "b" * 40
        with self.assertRaisesRegex(refresh.ScopeError, "digest changed"):
            refresh.apply_status(self.fixture.root, before["plan_sha256"], ("tools/dependency_sources.py",), runner, self.fixture.opener, uv_owner="unknown")
        staged_blob = "a" * 40
        branch = "other"
        with self.assertRaisesRegex(refresh.ScopeError, "digest changed"):
            refresh.apply_status(self.fixture.root, before["plan_sha256"], ("tools/dependency_sources.py",), runner, self.fixture.opener, uv_owner="unknown")
        self.assertNotIn(("uv", "lock", "--upgrade"), self.fixture.calls)

    def test_new_untracked_path_after_status_invalidates_review(self) -> None:
        status = "?? tools/dependency_sources.py\0"
        source = self.fixture.root / "tools/dependency_sources.py"
        source.parent.mkdir()
        source.write_text("stable", encoding="utf-8")
        base_runner = self.fixture.runner

        def runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            if args == ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"):
                return 0, status, ""
            return base_runner(args, cwd)

        before = collect_status(self.fixture.root, runner, self.fixture.opener)
        (self.fixture.root / "tools/dependency_refresh.py").write_text("new", encoding="utf-8")
        status += "?? tools/dependency_refresh.py\0"
        with self.assertRaisesRegex(refresh.ScopeError, "digest changed"):
            refresh.apply_status(self.fixture.root, before["plan_sha256"], ("tools/dependency_sources.py",), runner, self.fixture.opener, uv_owner="unknown")

    def test_preflight_rejects_duplicate_python_or_workflow_anchor(self) -> None:
        project = self.fixture.root / "pyproject.toml"
        project.write_text(project.read_text(encoding="utf-8") + 'requires-python = ">=3.12"\n', encoding="utf-8")
        report = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        with self.assertRaises(refresh.ScopeError):
            refresh.apply_status(self.fixture.root, report["plan_sha256"], (), self.fixture.runner, self.fixture.opener, uv_owner="standalone")
        self.assertNotIn(("uv", "self", "update", "--dry-run", "0.12.17"), self.fixture.calls)

    def test_hygiene_runner_allows_full_quality_suite_duration(self) -> None:
        command = ("uv", "run", "--offline", "--frozen", "python", ".codex/skills/hygiene/scripts/hygiene.py")
        with patch.object(refresh.subprocess, "run") as subprocess_run:
            subprocess_run.return_value.returncode = 0
            subprocess_run.return_value.stdout = ""
            subprocess_run.return_value.stderr = ""
            self.assertEqual(refresh._run(command, self.fixture.root)[0], 0)
        self.assertGreaterEqual(subprocess_run.call_args.kwargs["timeout"], 900)

    def test_unknown_owner_blocks_before_file_writes(self) -> None:
        project = self.fixture.root / "pyproject.toml"
        initial = project.read_bytes()
        report = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        with self.assertRaisesRegex(refresh.ScopeError, "owner"):
            refresh.apply_status(self.fixture.root, report["plan_sha256"], (), self.fixture.runner, self.fixture.opener, uv_owner="unknown")
        self.assertEqual(initial, project.read_bytes())
        self.assertNotIn(("uv", "lock", "--upgrade"), self.fixture.calls)

    def test_transitive_constraint_uses_exact_official_parent_release(self) -> None:
        after = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        lock = self.fixture.root / "uv.lock"
        lock.write_text(
            lock.read_text(encoding="utf-8")
            + '\n[[package]]\nname = "wily"\nversion = "1.25.0"\nsource = { registry = "https://pypi.org/simple" }\ndependencies = [{ name = "foo" }]\n',
            encoding="utf-8",
        )
        after["dependencies"] = [item for item in after["dependencies"] if item["name"] == "foo"]
        requirement = "foo>=1,<2"

        def opener(request: Request, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
            payload = {"info": {"name": "wily", "version": "1.25.0", "requires_dist": [requirement]}}
            return json.dumps(payload).encode(), request.full_url, "application/json"

        remaining = refresh._remaining_constraints(self.fixture.root, after, opener)
        self.assertEqual(len(remaining), 1)
        self.assertTrue(remaining[0]["explained"])
        constraints = remaining[0]["constraints"]
        assert isinstance(constraints, list) and isinstance(constraints[0], dict)
        self.assertEqual(constraints[0]["requirement"], "foo>=1,<2")
        self.assertEqual(constraints[0]["source"], "https://pypi.org/pypi/wily/1.25.0/json")
        requirement = "foo>=1"
        remaining = refresh._remaining_constraints(self.fixture.root, after, opener)
        self.assertFalse(remaining[0]["explained"])

    def _clean_after(self, before: dict[str, Any]) -> dict[str, Any]:
        after = copy.deepcopy(before)
        after["current_findings"] = []
        after["pre_apply_blockers"] = []
        after["python"]["declared"] = ">=3.12,<3.15"
        after["uv"]["required"] = "==0.12.17"
        for dependency in after["dependencies"]:
            dependency["outdated"] = False
            dependency["newest_stable"] = dependency["version"]
            dependency["resolver_candidate"] = None
        return after

    def test_already_current_uv_edits_only_anchors_and_runs_ordered_gates(self) -> None:
        before = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        after = self._clean_after(before)
        project = self.fixture.root / "pyproject.toml"
        original = project.read_text(encoding="utf-8")
        calls: list[tuple[str, ...]] = []

        def runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            calls.append(args)
            return 0, "", ""

        matrix_calls: list[Path] = []

        def matrix(root: Path) -> MatrixResult:
            matrix_calls.append(root)
            return MatrixResult(True, (), {"wheel": "a" * 64}, ())

        with patch.object(refresh, "collect_status", side_effect=[before, after]):
            result = refresh.apply_status(
                self.fixture.root, before["plan_sha256"], (), runner, self.fixture.opener, uv_owner="standalone", matrix_runner=matrix
            )
        self.assertEqual(result["status"], "passed")
        self.assertEqual(calls[:3], [("uv", "lock", "--upgrade"), ("uv", "sync", "--all-groups", "--locked"), ("uv", "lock", "--check")])
        self.assertEqual(matrix_calls, [self.fixture.root])
        self.assertNotIn(("uv", "self", "update", "0.12.17"), calls)
        updated = project.read_text(encoding="utf-8")
        self.assertEqual(
            updated,
            original.replace('requires-python = ">=3.12"', 'requires-python = ">=3.12,<3.15"').replace(
                'required-version = "==0.12.16"', 'required-version = "==0.12.17"'
            ),
        )
        for relative in ("ci.yml", "release-readiness.yml"):
            workflow = (self.fixture.root / ".github/workflows" / relative).read_text(encoding="utf-8")
            self.assertIn('version: "0.12.17"', workflow)

    def test_standalone_update_probes_then_verifies_before_edit(self) -> None:
        base_runner = self.fixture.runner

        def old_runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            if args == ("uv", "--version"):
                return 0, "uv 0.12.16 (test)\n", ""
            return base_runner(args, cwd)

        before = collect_status(self.fixture.root, old_runner, self.fixture.opener)
        after = self._clean_after(before)
        calls: list[tuple[str, ...]] = []

        def runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            calls.append(args)
            return (0, "uv 0.12.17 (test)\n", "") if args == ("uv", "--version") else (0, "", "")

        with patch.object(refresh, "collect_status", side_effect=[before, after]):
            refresh.apply_status(
                self.fixture.root,
                before["plan_sha256"],
                (),
                runner,
                self.fixture.opener,
                uv_owner="standalone",
                matrix_runner=lambda root: MatrixResult(True, (), {}, ()),
            )
        self.assertEqual(calls[:3], [("uv", "self", "update", "--dry-run", "0.12.17"), ("uv", "self", "update", "0.12.17"), ("uv", "--version")])

    def test_resolver_failure_preserves_original_report_and_failed_command(self) -> None:
        before = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)

        def runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            return (7, "", "resolver failed") if args == ("uv", "lock", "--upgrade") else (0, "", "")

        with patch.object(refresh, "collect_status", return_value=before):
            with self.assertRaises(refresh.UpdateError) as caught:
                refresh.apply_status(self.fixture.root, before["plan_sha256"], (), runner, self.fixture.opener, uv_owner="standalone")
        self.assertEqual(caught.exception.report["before"]["plan_sha256"], before["plan_sha256"])
        self.assertEqual(caught.exception.report["commands"][-1]["command"], ["uv", "lock", "--upgrade"])
        self.assertEqual(caught.exception.report["commands"][-1]["exit_code"], 7)

    def test_remaining_advisory_fails_before_verification_gates(self) -> None:
        before = collect_status(self.fixture.root, self.fixture.runner, self.fixture.opener)
        after = self._clean_after(before)
        after["current_findings"] = [{"kind": "advisory", "name": "foo", "version": "1.0", "id": "GHSA-still"}]
        calls: list[tuple[str, ...]] = []

        def runner(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
            calls.append(args)
            return 0, "", ""

        with patch.object(refresh, "collect_status", side_effect=[before, after]):
            with self.assertRaises(refresh.UpdateError) as caught:
                refresh.apply_status(self.fixture.root, before["plan_sha256"], (), runner, self.fixture.opener, uv_owner="standalone")
        self.assertIn("GHSA-still", str(caught.exception))
        self.assertEqual(calls, [("uv", "lock", "--upgrade"), ("uv", "sync", "--all-groups", "--locked"), ("uv", "lock", "--check")])
        self.assertEqual(caught.exception.report["after"]["current_findings"], after["current_findings"])
