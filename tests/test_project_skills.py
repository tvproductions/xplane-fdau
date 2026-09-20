"""Tests for the project's locally defined workflow skills."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest

from pre_commit.clientlib import load_config
import yaml


PROJECT_SKILL_DIRECTORIES = {
    "backlog-status",
    "code-quality",
    "documentation",
    "hygiene",
    "release",
}
DISCOVERABLE_PROJECT_SKILLS = PROJECT_SKILL_DIRECTORIES


class ProjectSkillTests(unittest.TestCase):
    def test_repository_governance_is_excluded_from_source_builds(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        excluded = set(project["tool"]["uv"]["build-backend"]["source-exclude"])
        self.assertTrue({".codex/**", ".git/**", ".superpowers/**", "docs/superpowers/**"}.issubset(excluded))

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

        instructions = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(".agents/superpowers", instructions)
        self.assertIn(".agents/skills/superpowers", instructions)
        self.assertIn("merge back to `main`", instructions)
        self.assertIn("remove the worktree", instructions)

        workflow_steps = (
            "brainstorming",
            "using-git-worktrees",
            "writing-plans",
            "subagent-driven-development",
            "test-driven-development",
            "requesting-code-review",
            "finishing-a-development-branch",
        )
        positions = [instructions.index(f"`superpowers:{name}`") for name in workflow_steps]
        self.assertEqual(sorted(positions), positions)

    def test_release_skill_stops_after_local_readiness(self) -> None:
        text = Path(".codex/skills/release/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("publication is not authorized", text)
        self.assertIn("xplane_fdau-0.1.0-py3-none-any.whl", text)
        self.assertNotIn("check-tag", text)

    def test_plugin_only_gz_skills_authority(self) -> None:
        config = tomllib.loads(Path(".codex/config.toml").read_text(encoding="utf-8"))
        marketplace = config["marketplaces"]["gz-skills"]
        self.assertEqual(
            {
                "source_type": "git",
                "source": "https://github.com/tvproductions/gz-skills.git",
                "ref": "v0.3.2",
            },
            marketplace,
        )
        self.assertEqual(
            1,
            sum(entry.get("source") == marketplace["source"] for entry in config["marketplaces"].values()),
        )
        self.assertEqual({"enabled": True}, config["plugins"]["gz-skills@gz-skills"])
        self.assertEqual(
            ["gz-skills@gz-skills"],
            sorted(name for name in config["plugins"] if name.startswith("gz-skills@")),
        )
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
        instructions = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("sole portable workflow authority", instructions)
        self.assertIn("gz-skills@gz-skills", instructions)
        self.assertIn(".codex/config.toml", instructions)
        self.assertIn("full `gzs-update-dependencies`", instructions)
        self.assertNotIn("snapshot under `.agents/skills/gzs-*`", instructions)

        design = Path("docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md").read_text(encoding="utf-8")
        self.assertIn("gz_skills_plugin_only_specification.md", design)

        draft = Path("docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md").read_text(encoding="utf-8")
        self.assertIn(".codex/config.toml", draft)
        self.assertIn("Codex marketplace", draft)

        attributes = Path(".gitattributes").read_text(encoding="utf-8")
        self.assertNotIn(".agents/skills/gzs-*/**", attributes)
        baseline = json.loads(Path(".secrets.baseline").read_text(encoding="utf-8"))
        self.assertNotIn("gz-skills.lock.json", baseline["results"])

    def test_hygiene_audits_backlog_then_runs_one_quality_gate_through_pre_commit(self) -> None:
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
                ("uv", "run", "--offline", "--frozen", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit"),
                ("uv", "run", "--offline", "--frozen", "mkdocs", "build", "--strict"),
                ("uv", "run", "--offline", "--frozen", "python", "tools/quality.py", "pre-commit"),
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

        audit_command = ("uv", "run", "--offline", "--frozen", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit")
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

    def test_hygiene_guidance_names_full_offline_project_adapter(self) -> None:
        command = "uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py"
        skill = Path(".codex/skills/hygiene/SKILL.md").read_text(encoding="utf-8")
        instructions = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(command, skill)
        self.assertIn(command, instructions)
        for required in (
            "gzs-repository-hygiene",
            "mkdocs build --strict",
            "quality-check",
            "twine check --strict",
            "tools/release.py check-dist",
            "temporary",
            "preserved",
            "cleanup",
            "offline",
            "3.12",
            "3.13",
            "3.14",
            "code-quality",
            "documentation",
            "release",
        ):
            with self.subTest(required=required):
                self.assertIn(required, skill)
        self.assertIn("--dependencies", skill)
        self.assertIn("gzs-update-dependencies", skill)
        self.assertNotIn("git push", skill)
        self.assertNotIn("Git sync is authorized", skill)
        self.assertNotIn("release is authorized", skill)

    def test_pre_commit_runs_quality_check_and_other_repository_hooks(self) -> None:
        config = load_config(".pre-commit-config.yaml")
        hooks = [hook for repo in config["repos"] for hook in repo["hooks"]]
        self.assertEqual(
            {"quality-check", "detect-secrets-baseline", "lizard-report", "cohesion-report"},
            {hook["id"] for hook in hooks},
        )
        quality_hooks = [hook for hook in hooks if hook["id"] == "quality-check"]
        self.assertEqual(1, len(quality_hooks))
        self.assertEqual("uv run python tools/quality.py check", quality_hooks[0]["entry"])
        self.assertFalse(quality_hooks[0]["pass_filenames"])
        raw_config = yaml.safe_load(Path(".pre-commit-config.yaml").read_text(encoding="utf-8"))
        raw_repos = raw_config["repos"]
        raw_hooks = [hook for repo in raw_repos for hook in repo["hooks"]]
        self.assertTrue(all(repo["repo"] == "local" for repo in raw_repos))
        self.assertTrue(all(hook["language"] == "system" for hook in raw_hooks))
        self.assertTrue(all(hook["entry"].startswith("uv run ") for hook in raw_hooks))
