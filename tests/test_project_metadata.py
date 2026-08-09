from pathlib import Path
import tomllib
import unittest


class ProjectMetadataTests(unittest.TestCase):
    def test_distribution_contract_is_dependency_free(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual("xplane-fdr", project["name"])
        self.assertEqual("0.1.0", project["version"])
        self.assertEqual(">=3.12", project["requires-python"])
        self.assertEqual([], project["dependencies"])

    def test_runtime_package_exposes_matching_version(self) -> None:
        import xplane_fdr

        self.assertEqual("0.1.0", xplane_fdr.__version__)
