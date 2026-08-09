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

    def test_release_validates_then_uses_protected_trusted_publish_job(self) -> None:
        workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("actions/download-artifact@v4", workflow)
        self.assertIn("publish-pypi:", workflow)
        self.assertIn("needs: [validate-release, installed-wheel]", workflow)
        self.assertIn("environment: pypi", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("github.ref_type == 'tag'", workflow)
        self.assertIn("uv publish dist/*", workflow)


if __name__ == "__main__":
    unittest.main()
