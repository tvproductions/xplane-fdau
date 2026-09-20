"""Contract tests for release artifact hand-off in GitHub Actions workflows."""

from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


class ReleaseWorkflowTests(unittest.TestCase):
    def test_ci_builds_uploads_and_smokes_one_artifact_pair(self) -> None:
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("actions/checkout@v7.0.1", workflow)
        self.assertIn("astral-sh/setup-uv@v10.1.0", workflow)
        self.assertIn('version: "0.12.17"', workflow)
        self.assertIn("actions/upload-artifact@v7.0.1", workflow)
        self.assertIn("name: distribution", workflow)
        self.assertIn("actions/download-artifact@v8.0.1", workflow)
        self.assertIn("uv tool run twine@7.0.0 check --strict", workflow)
        installed = workflow.split("installed-wheel:", 1)[1]
        self.assertNotIn("uv build", installed)
        self.assertIn('cd "$RUNNER_TEMP"', installed)

    def test_release_readiness_is_manual_and_non_publishing(self) -> None:
        self.assertFalse(Path(".github/workflows/release.yml").exists())
        workflow = Path(".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("actions/checkout@v7.0.1", workflow)
        self.assertIn("astral-sh/setup-uv@v10.1.0", workflow)
        self.assertIn('version: "0.12.17"', workflow)
        self.assertIn("actions/upload-artifact@v7.0.1", workflow)
        self.assertIn("actions/download-artifact@v8.0.1", workflow)
        self.assertIn("uv tool run twine@7.0.0 check --strict", workflow)
        self.assertIn("needs: validate-release", workflow)
        self.assertNotIn("uv publish", workflow)
        self.assertNotIn("id-token: write", workflow)
        self.assertNotIn("tags:", workflow)
        self.assertNotIn("publish-pypi:", workflow)
        self.assertNotIn("check-tag", workflow)

    def test_every_setup_uv_step_matches_the_project_pin(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        required_uv = project.get("tool", {}).get("uv", {}).get("required-version")
        self.assertIsNotNone(required_uv, "project must pin the reviewed uv version")
        self.assertRegex(required_uv, r"^==\d+\.\d+\.\d+$")
        for path in (Path(".github/workflows/ci.yml"), Path(".github/workflows/release-readiness.yml")):
            with self.subTest(path=path):
                workflow = path.read_text(encoding="utf-8")
                setup_count = workflow.count("astral-sh/setup-uv@")
                self.assertGreater(setup_count, 0)
                self.assertEqual(setup_count, workflow.count(f'version: "{required_uv[2:]}"'))

    def test_release_readiness_runs_one_aggregate_source_suite(self) -> None:
        workflow = Path(".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        validation = workflow.split("  validate-release:", 1)[1].split("  installed-wheel:", 1)[0]
        self.assertEqual(1, validation.count("python tools/quality.py check"))
        self.assertNotIn("python -m unittest discover", validation)


if __name__ == "__main__":
    unittest.main()
