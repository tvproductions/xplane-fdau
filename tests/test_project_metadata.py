from pathlib import Path
import importlib.util
import tomllib
import unittest


class ProjectMetadataTests(unittest.TestCase):
    def test_distribution_contract_is_dependency_free_fdau(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual("xplane-fdau", project["name"])
        self.assertEqual("0.1.0", project["version"])
        self.assertEqual(">=3.12", project["requires-python"])
        self.assertEqual([], project["dependencies"])
        self.assertEqual({"xplane-fdau": "xplane_fdau.cli:main"}, project["scripts"])

    def test_runtime_root_exposes_only_matching_version(self) -> None:
        import xplane_fdau

        self.assertEqual("0.1.0", xplane_fdau.__version__)
        self.assertEqual(["__version__"], xplane_fdau.__all__)

    def test_unreleased_legacy_namespace_is_absent(self) -> None:
        self.assertIsNone(importlib.util.find_spec("xplane_fdr"))
