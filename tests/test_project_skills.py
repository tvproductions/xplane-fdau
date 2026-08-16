"""Tests for the project's locally defined workflow skills."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


PROJECT_SKILL_DIRECTORIES = {
    "backlog-status",
    "code-quality",
    "documentation",
    "git-sync",
    "hygiene",
    "release",
}
DISCOVERABLE_PROJECT_SKILLS = PROJECT_SKILL_DIRECTORIES - {"backlog-status"}


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

    def test_git_sync_skill_does_not_authorize_push_during_unreleased_increment(self) -> None:
        text = Path(".codex/skills/git-sync/SKILL.md").read_text(encoding="utf-8")

        self.assertNotIn("\ngit push ", text)
        self.assertIn("Do not push", text)
        self.assertIn("canonical vertical slice", text)
        self.assertIn("separately authorizes", text)

    def test_hygiene_script_runs_the_local_quality_gate(self) -> None:
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

        self.assertIn(("uv", "run", "python", "tools/quality.py", "check"), module.LOCAL_COMMANDS)
