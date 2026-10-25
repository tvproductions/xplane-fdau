"""Verify the real CI command graph against the project execution contract."""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

import yaml


class ReleaseWorkflowTests(unittest.TestCase):
    def workflows(self):
        return [
            yaml.safe_load(path.read_text(encoding="utf-8")) for path in (Path(".github/workflows/ci.yml"), Path(".github/workflows/release-readiness.yml"))
        ]

    def test_ci_builds_uploads_and_smokes_one_artifact_pair(self) -> None:
        workflow = self.workflows()[0]
        jobs = workflow["jobs"]
        self.assertEqual("quality", jobs["artifacts"]["needs"])
        self.assertEqual("artifacts", jobs["installed-wheel"]["needs"])
        installed = jobs["installed-wheel"]["steps"]
        self.assertFalse(any("uv build" in step.get("run", "") for step in installed))
        self.assertTrue(any("tools/installed_smoke.py" in step.get("run", "") for step in installed))
        self.assertTrue(any(step.get("with", {}).get("name") == "distribution" for step in installed))

    def test_release_readiness_is_manual_and_non_publishing(self) -> None:
        self.assertFalse(Path(".github/workflows/release.yml").exists())
        workflow = self.workflows()[1]
        triggers = workflow.get("on", workflow.get(True, {}))
        self.assertEqual({"workflow_dispatch"}, set(triggers))
        self.assertEqual({"contents": "read"}, workflow["permissions"])
        text = Path(".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        for forbidden in ("uv publish", "id-token: write", "publish-pypi:", "check-tag"):
            self.assertNotIn(forbidden, text)

    def test_setup_uv_inputs_match_exact_project_pin_and_actions_are_immutable(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        required_uv = project["tool"]["uv"]["required-version"]
        python_pin = Path(".python-version").read_text(encoding="utf-8").strip()
        self.assertRegex(required_uv, r"^==\d+\.\d+\.\d+$")
        for workflow in self.workflows():
            setups = []
            for job in workflow["jobs"].values():
                for step in job["steps"]:
                    uses = step.get("uses")
                    if uses:
                        self.assertRegex(uses, r"^[\w-]+/[\w-]+@[0-9a-f]{40}$")
                    if uses and uses.startswith("astral-sh/setup-uv@"):
                        setups.append(step)
                        self.assertEqual(required_uv[2:], step.get("with", {}).get("version"))
                        self.assertEqual(python_pin, step.get("with", {}).get("python-version"))
                    run = step.get("run", "")
                    self.assertIsNone(re.search(r"--python 3\.12(?:\s|$)", run))
                    self.assertNotIn("uv sync --frozen", run)
            self.assertTrue(setups)

    def test_each_workflow_runs_one_four_check_aggregate(self) -> None:
        for workflow in self.workflows():
            quality_steps = [step for job in workflow["jobs"].values() for step in job["steps"] if "tools/quality.py check" in step.get("run", "")]
            self.assertEqual(1, len(quality_steps))
            self.assertIn("--locked", quality_steps[0]["run"])
            self.assertFalse(any("python -m unittest discover" in step.get("run", "") for job in workflow["jobs"].values() for step in job["steps"]))
