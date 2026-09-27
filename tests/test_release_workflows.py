"""Contract tests for release artifact hand-off in GitHub Actions workflows."""

from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


class ReleaseWorkflowTests(unittest.TestCase):
    def test_ci_builds_uploads_and_smokes_one_artifact_pair(self) -> None:
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertRegex(workflow, r"actions/checkout@v\d+")
        self.assertRegex(workflow, r"astral-sh/setup-uv@v\d+")
        self.assertRegex(workflow, r"actions/upload-artifact@v\d+")
        self.assertIn("name: distribution", workflow)
        self.assertRegex(workflow, r"actions/download-artifact@v\d+")
        self.assertIn("uv tool run twine@7.0.0 check --strict", workflow)
        installed = workflow.split("installed-wheel:", 1)[1]
        self.assertNotIn("uv build", installed)
        self.assertIn('cd "$RUNNER_TEMP"', installed)

    def test_release_readiness_is_manual_and_non_publishing(self) -> None:
        self.assertFalse(Path(".github/workflows/release.yml").exists())
        workflow = Path(".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertRegex(workflow, r"actions/checkout@v\d+")
        self.assertRegex(workflow, r"astral-sh/setup-uv@v\d+")
        self.assertRegex(workflow, r"actions/upload-artifact@v\d+")
        self.assertRegex(workflow, r"actions/download-artifact@v\d+")
        self.assertIn("uv tool run twine@7.0.0 check --strict", workflow)
        self.assertIn("needs: validate-release", workflow)
        self.assertNotIn("uv publish", workflow)
        self.assertNotIn("id-token: write", workflow)
        self.assertNotIn("tags:", workflow)
        self.assertNotIn("publish-pypi:", workflow)
        self.assertNotIn("check-tag", workflow)

    def test_setup_uv_has_no_exact_version_override(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        required_uv = project.get("tool", {}).get("uv", {}).get("required-version")
        self.assertIsNotNone(required_uv, "project must declare a supported uv floor")
        self.assertRegex(required_uv, r"^>=\d+\.\d+\.\d+$")
        for path in (Path(".github/workflows/ci.yml"), Path(".github/workflows/release-readiness.yml")):
            with self.subTest(path=path):
                workflow = path.read_text(encoding="utf-8")
                setup_count = workflow.count("astral-sh/setup-uv@")
                self.assertGreater(setup_count, 0)
                self.assertNotRegex(workflow, r"(?m)^\s+version: [\"'](?:\d+\.\d+\.\d+|latest)[\"']$")

    def test_release_readiness_runs_one_aggregate_source_suite(self) -> None:
        workflow = Path(".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        validation = workflow.split("  validate-release:", 1)[1].split("  installed-wheel:", 1)[0]
        self.assertEqual(1, validation.count("python tools/quality.py check"))
        self.assertNotIn("python -m unittest discover", validation)


if __name__ == "__main__":
    unittest.main()
