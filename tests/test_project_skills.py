"""Tests for the project's locally defined workflow skills."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


class ProjectSkillTests(unittest.TestCase):
    def test_project_skills_are_scoped_to_unreleased_xplane_fdau(self) -> None:
        for name in ("code-quality", "documentation", "hygiene", "git-sync", "release"):
            path = Path(".codex/skills") / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            self.assertIn("name:", text)
            self.assertIn("xplane-fdau", text)
            self.assertNotIn("xpwebapi", text.lower())

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
