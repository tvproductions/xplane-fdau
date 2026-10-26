"""Tests for the project's locally defined workflow skills."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

import yaml
from pre_commit.clientlib import load_config

PROJECT_SKILL_DIRECTORIES = {
    "backlog-status",
    "code-quality",
    "documentation",
    "hygiene",
    "release",
}
DISCOVERABLE_PROJECT_SKILLS = PROJECT_SKILL_DIRECTORIES


class ProjectSkillTests(unittest.TestCase):
    def test_project_skills_are_scoped_to_unreleased_xplane_fdau(self) -> None:
        for name in DISCOVERABLE_PROJECT_SKILLS:
            path = Path(".codex/skills") / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            self.assertIn("name:", text)
            self.assertIn("xplane-fdau", text)
            self.assertNotIn("xpwebapi", text.lower())

    def test_superpowers_is_external_and_only_project_skills_are_tracked(self) -> None:
        skill_root = Path(".codex/skills")
        tracked_skill_directories = {path.name for path in skill_root.iterdir()}

        self.assertEqual(PROJECT_SKILL_DIRECTORIES, tracked_skill_directories)
        self.assertFalse(Path(".codex/plugins/superpowers").exists())

        ignore_lines = Path(".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".agents/superpowers/", ignore_lines)
        self.assertIn(".agents/skills/superpowers/", ignore_lines)
        self.assertNotIn(".agents/", ignore_lines)

        attributes = Path(".gitattributes").read_text(encoding="utf-8")
        self.assertNotIn(".codex/plugins/superpowers", attributes)

    def test_release_skill_stops_after_local_readiness(self) -> None:
        text = Path(".codex/skills/release/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("publication is not authorized", text)
        self.assertIn("xplane_fdau-0.1.0-py3-none-any.whl", text)
        self.assertNotIn("check-tag", text)

    def test_plugin_only_gz_skills_authority(self) -> None:
        config = tomllib.loads(Path(".codex/config.toml").read_text(encoding="utf-8"))
        lock = json.loads(Path(".skills-first/bundle.lock.json").read_text(encoding="utf-8"))
        marketplace = config["marketplaces"]["skills-first-starter"]
        self.assertEqual("git", marketplace["source_type"])
        self.assertEqual("https://github.com/tvproductions/gz-skills-first-starter.git", marketplace["source"])
        self.assertEqual(lock["starter"]["repository"], marketplace["source"])
        self.assertRegex(marketplace["ref"], r"^[a-f0-9]{40}$")
        self.assertEqual(lock["starter"]["revision"], marketplace["ref"])
        self.assertEqual(
            1,
            sum(entry.get("source") == marketplace["source"] for entry in config["marketplaces"].values()),
        )
        for component in lock["components"]:
            self.assertRegex(component["revision"], r"^[a-f0-9]{40}$")
            self.assertEqual({"enabled": component["enabled_by_default"]}, config["plugins"][f"{component['name']}@skills-first-starter"])
            enabled = [name for name, value in config["plugins"].items() if name.startswith(component["name"] + "@") and value["enabled"]]
            self.assertEqual([f"{component['name']}@skills-first-starter"] if component["enabled_by_default"] else [], enabled)
        self.assertFalse(Path("gz-skills.lock.json").exists())
        for root in (Path(".agents/skills"), Path(".codex/skills")):
            with self.subTest(root=root):
                self.assertEqual([], sorted(path.name for path in root.glob("gzs-*")))
        for path in (
            Path(".agents/gz-skills"),
            Path(".codex/plugins/gz-skills"),
            Path("gz-skills"),
        ):
            with self.subTest(path=path):
                self.assertFalse(path.exists() or path.is_symlink())

    def test_plugin_guidance_and_dependency_inventory(self) -> None:
        design = Path("docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md").read_text(encoding="utf-8")
        self.assertIn("gz_skills_plugin_only_specification.md", design)

        draft = Path("docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md").read_text(encoding="utf-8")
        self.assertIn(".codex/config.toml", draft)
        self.assertIn("independently of T2.2", draft)
        self.assertIn("None invokes Codex or manages the plugin cache.", draft)

        attributes = Path(".gitattributes").read_text(encoding="utf-8")
        self.assertNotIn(".agents/skills/gzs-*/**", attributes)
        baseline = json.loads(Path(".secrets.baseline").read_text(encoding="utf-8"))
        self.assertNotIn("gz-skills.lock.json", baseline["results"])

    def test_hygiene_audits_backlog_then_runs_one_quality_gate_directly(self) -> None:
        path = Path(".codex/skills/hygiene/scripts/hygiene.py")
        spec = importlib.util.spec_from_file_location("hygiene", path)
        if spec is None or spec.loader is None:
            self.fail("hygiene script must be importable")
        loader = spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)

        executed: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            executed.append(command)
            return subprocess.CompletedProcess(command, 0)

        self.assertEqual(0, module.run_local_hygiene(runner))
        self.assertEqual(
            [
                ("git", "status", "--short", "--branch"),
                ("git", "status", "--short", "--branch", "--ignored=matching"),
                ("uv", "lock", "--check", "--offline"),
                ("uv", "run", "--offline", "--frozen", "--all-groups", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit"),
                ("uv", "run", "--offline", "--frozen", "--all-groups", "mkdocs", "build", "--strict"),
                ("uv", "run", "--offline", "--frozen", "--all-groups", "python", "tools/quality.py", "pre-commit"),
            ],
            executed[:6],
        )

    def test_hygiene_stops_when_backlog_audit_fails(self) -> None:
        path = Path(".codex/skills/hygiene/scripts/hygiene.py")
        spec = importlib.util.spec_from_file_location("hygiene", path)
        if spec is None or spec.loader is None:
            self.fail("hygiene script must be importable")
        loader = spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)

        audit_command = ("uv", "run", "--offline", "--frozen", "--all-groups", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit")
        executed: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            executed.append(command)
            return subprocess.CompletedProcess(command, 7 if command == audit_command else 0)

        self.assertEqual(7, module.run_local_hygiene(runner))
        self.assertEqual(
            [
                ("git", "status", "--short", "--branch"),
                ("git", "status", "--short", "--branch", "--ignored=matching"),
                ("uv", "lock", "--check", "--offline"),
                audit_command,
            ],
            executed,
        )

    def test_hygiene_stops_after_offline_lock_failure(self) -> None:
        path = Path(".codex/skills/hygiene/scripts/hygiene.py")
        spec = importlib.util.spec_from_file_location("hygiene", path)
        if spec is None or spec.loader is None:
            self.fail("hygiene script must be importable")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)

        executed: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
            executed.append(command)
            return subprocess.CompletedProcess(command, 3 if command[0] == "uv" else 0)

        self.assertEqual(3, module.run_local_hygiene(runner))
        self.assertEqual(3, len(executed))

    def test_exact_fast_forward_uses_focused_main_checks(self) -> None:
        agents = Path("AGENTS.md").read_text(encoding="utf-8")
        quality = Path(".codex/skills/code-quality/SKILL.md").read_text(encoding="utf-8")
        hygiene = Path(".codex/skills/hygiene/SKILL.md").read_text(encoding="utf-8")
        for document in (agents, quality, hygiene):
            with self.subTest(document=document[:32]):
                self.assertIn("exact fast-forward", document)
                self.assertIn("focused", document)
                self.assertIn("complete gate", document)
        self.assertIn("uv sync --offline --frozen", hygiene)
        self.assertIn("uv lock --check --offline", hygiene)
        self.assertIn("backlog_status.py audit", hygiene)
        self.assertIn("test_current_repository_status_reports_human_and_json", hygiene)
        self.assertIn("test_runtime_package_uses_only_installed_src_layout", hygiene)
        self.assertIn("uv build --offline --no-sources", hygiene)
        self.assertIn("twine check --strict", hygiene)
        self.assertIn("tools/release.py check-dist", hygiene)
        self.assertIn("installed_smoke.py", hygiene)
        self.assertIn("git merge --ff-only", hygiene)
        self.assertIn("main HEAD", hygiene)

    def test_pre_commit_enforces_four_locked_routine_checks(self) -> None:
        config = load_config(".pre-commit-config.yaml")
        hooks = [hook for repo in config["repos"] for hook in repo["hooks"]]
        self.assertEqual(
            {"ruff-check", "ruff-format-check", "ty-check", "unittest"},
            {hook["id"] for hook in hooks},
        )
        by_id = {hook["id"]: hook for hook in hooks}
        self.assertEqual("uv run --locked --all-groups ruff check", by_id["ruff-check"]["entry"])
        self.assertEqual("uv run --locked --all-groups ruff format --check", by_id["ruff-format-check"]["entry"])
        self.assertEqual(["python"], by_id["ruff-check"]["types"])
        self.assertEqual(["python"], by_id["ruff-format-check"]["types"])
        for identity in ("ty-check", "unittest"):
            self.assertFalse(by_id[identity]["pass_filenames"])
            self.assertTrue(by_id[identity]["always_run"])
        self.assertEqual("uv run --locked --all-groups ty check", by_id["ty-check"]["entry"])
        self.assertEqual("uv run --locked --all-groups python -m unittest discover -q", by_id["unittest"]["entry"])
        self.assertNotIn("tools/quality.py check", " ".join(hook["entry"] for hook in hooks))
        raw_config = yaml.safe_load(Path(".pre-commit-config.yaml").read_text(encoding="utf-8"))
        raw_repos = raw_config["repos"]
        raw_hooks = [hook for repo in raw_repos for hook in repo["hooks"]]
        self.assertTrue(all(repo["repo"] == "local" for repo in raw_repos))
        self.assertTrue(all(hook["language"] == "system" for hook in raw_hooks))
        self.assertTrue(all(hook["entry"].startswith("uv run ") for hook in raw_hooks))
