"""Tests for the project's locally defined workflow skills."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import unittest


PROJECT_SKILL_DIRECTORIES = {
    "backlog-status",
    "code-quality",
    "documentation",
    "hygiene",
    "release",
}
DISCOVERABLE_PROJECT_SKILLS = PROJECT_SKILL_DIRECTORIES - {"backlog-status"}
GZ_SKILLS = {
    "gzs-agent-context-diet",
    "gzs-cross-platform-python",
    "gzs-git-sync",
    "gzs-intent-audit",
    "gzs-plan-audit",
    "gzs-quality-gate",
    "gzs-repository-hygiene",
    "gzs-router",
    "gzs-session-handoff",
    "gzs-tech-debt-review",
    "gzs-update-dependencies",
}
GZ_SKILLS_REPOSITORY = "https://github.com/tvproductions/gz-skills.git"
GZ_SKILLS_REVISION = "e925081362eec2517ab429517e250ecca6877cdc"  # pragma: allowlist secret
TRANSIENT_SKILL_DIRECTORIES = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}


def _skill_tree_sha256(skill_root: Path) -> str:
    digest = hashlib.sha256()
    files = []
    for path in skill_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_root)
        if any(part in TRANSIENT_SKILL_DIRECTORIES for part in relative.parts):
            continue
        files.append((relative.as_posix(), path))

    for relative, path in sorted(files, key=lambda item: item[0].encode("utf-8")):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


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

    def test_canonical_gz_skills_installation_matches_locked_catalog(self) -> None:
        lock_path = Path("gz-skills.lock.json")
        self.assertTrue(lock_path.is_file(), "canonical gz-skills lock must exist")
        document = json.loads(lock_path.read_text(encoding="utf-8"))

        self.assertEqual(1, document["schema_version"])
        entries = document["skills"]
        self.assertEqual(GZ_SKILLS, {entry["name"] for entry in entries})

        discovery_root = Path(".agents/skills")
        discovered = {path.name for path in discovery_root.glob("gzs-*") if path.is_dir() and (path / "SKILL.md").is_file()}
        self.assertEqual(GZ_SKILLS, discovered)

        for entry in entries:
            name = entry["name"]
            expected_installed_path = f".agents/skills/{name}"
            self.assertEqual(expected_installed_path, entry["installed_path"])
            self.assertFalse(Path(entry["installed_path"]).is_absolute())
            installed_path = (lock_path.parent / entry["installed_path"]).resolve()
            self.assertEqual(
                (discovery_root / name).resolve(),
                installed_path,
            )
            self.assertEqual(
                {
                    "repository": GZ_SKILLS_REPOSITORY,
                    "revision": GZ_SKILLS_REVISION,
                    "path": f"skills/{name}",
                },
                entry["source"],
            )
            self.assertEqual(entry["sha256"], _skill_tree_sha256(installed_path))

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
