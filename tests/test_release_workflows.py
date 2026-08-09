"""Contract tests for release artifact hand-off in GitHub Actions workflows."""

from __future__ import annotations

from pathlib import Path
import unittest


class ReleaseWorkflowTests(unittest.TestCase):
    def test_ci_builds_uploads_and_smokes_one_artifact_pair(self) -> None:
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("name: distribution", workflow)
        self.assertIn("actions/download-artifact@v4", workflow)
        installed = workflow.split("installed-wheel:", 1)[1]
        self.assertNotIn("uv build", installed)
        self.assertIn('cd "$RUNNER_TEMP"', installed)

    def test_release_readiness_is_manual_and_non_publishing(self) -> None:
        self.assertFalse(Path(".github/workflows/release.yml").exists())
        workflow = Path(".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("actions/download-artifact@v4", workflow)
        self.assertIn("needs: validate-release", workflow)
        self.assertNotIn("uv publish", workflow)
        self.assertNotIn("id-token: write", workflow)
        self.assertNotIn("tags:", workflow)
        self.assertNotIn("publish-pypi:", workflow)
        self.assertNotIn("check-tag", workflow)


if __name__ == "__main__":
    unittest.main()
