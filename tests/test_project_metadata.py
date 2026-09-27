from pathlib import Path
import importlib.util
import subprocess
import sys
import tomllib
import unittest


class ProjectMetadataTests(unittest.TestCase):
    def test_distribution_contract_is_dependency_free_fdau(self) -> None:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual("xplane-fdau", project["name"])
        self.assertEqual("0.1.0", project["version"])
        self.assertEqual(">=3.12,<3.13", project["requires-python"])
        self.assertEqual(
            {"Programming Language :: Python :: 3.12"},
            {item for item in project["classifiers"] if item.startswith("Programming Language :: Python :: 3.")},
        )
        self.assertEqual([], project["dependencies"])
        self.assertEqual({"xplane-fdau": "xplane_fdau.cli:main"}, project["scripts"])

    def test_runtime_package_uses_only_installed_src_layout(self) -> None:
        root = Path(__file__).resolve().parents[1]
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual("src", project["tool"]["uv"]["build-backend"]["module-root"])
        self.assertTrue((root / "src/xplane_fdau/__init__.py").is_file())
        self.assertFalse((root / "xplane_fdau").exists())
        result = subprocess.run(
            [sys.executable, "-c", "from pathlib import Path; import xplane_fdau; print(Path(xplane_fdau.__file__).resolve())"],
            cwd=root,
            capture_output=True,
            text=True,
            errors="replace",
            check=True,
        )
        self.assertTrue(Path(result.stdout.strip()).is_relative_to((root / "src/xplane_fdau").resolve()))

    def test_runtime_root_exposes_only_matching_version(self) -> None:
        import xplane_fdau

        self.assertEqual("0.1.0", xplane_fdau.__version__)
        self.assertEqual(["__version__"], xplane_fdau.__all__)

    def test_unreleased_legacy_namespace_is_absent(self) -> None:
        self.assertFalse(Path("xplane_fdr").exists())
        self.assertIsNone(importlib.util.find_spec("xplane_fdr"))
