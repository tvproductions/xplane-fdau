"""Tests for the installed-wheel smoke-test command."""

from __future__ import annotations

from pathlib import Path
import unittest

from tools import installed_smoke


class InstalledSmokeTests(unittest.TestCase):
    def test_checkout_path_detection_rejects_checkout_import(self) -> None:
        checkout = Path("C:/work/xplane-fdr").resolve()
        imported = checkout / "xplane_fdr" / "__init__.py"

        with self.assertRaisesRegex(installed_smoke.SmokeError, "checkout"):
            installed_smoke.ensure_outside_checkout(imported, checkout)

    def test_checkout_path_detection_accepts_site_packages_import(self) -> None:
        checkout = Path("C:/work/xplane-fdr").resolve()
        imported = Path("C:/venv/Lib/site-packages/xplane_fdr/__init__.py").resolve()

        installed_smoke.ensure_outside_checkout(imported, checkout)

    def test_version_parser_requires_release_version(self) -> None:
        self.assertEqual("0.1.0", installed_smoke.parse_version(["0.1.0"]))
        with self.assertRaisesRegex(installed_smoke.SmokeError, "usage"):
            installed_smoke.parse_version([])


if __name__ == "__main__":
    unittest.main()
