"""Tests for the installed-wheel smoke-test command."""

from __future__ import annotations

import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import installed_smoke
from xplane_fdau.formats.xplane_fdr import FDRReader


class InstalledSmokeTests(unittest.TestCase):
    def test_checkout_path_detection_rejects_checkout_import(self) -> None:
        checkout = Path("C:/work/xplane-fdr").resolve()
        with self.assertRaisesRegex(installed_smoke.SmokeError, "checkout"):
            installed_smoke.ensure_outside_checkout(checkout / "xplane_fdau/__init__.py", checkout)

    def test_symlinked_venv_interpreter_keeps_scripts_directory_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            scripts = root / "venv" / "bin"
            target = root / "base" / "python"
            scripts.mkdir(parents=True)
            target.parent.mkdir()
            target.write_text("target", encoding="utf-8")
            interpreter = scripts / "python"
            command = scripts / "xplane-fdau"
            command.write_text("command", encoding="utf-8")
            try:
                os.symlink(target, interpreter)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            self.assertEqual(command.absolute(), installed_smoke.validate_command_path(command, interpreter))
            with self.assertRaisesRegex(installed_smoke.SmokeError, "scripts directory"):
                installed_smoke.validate_command_path(root / "outside" / "xplane-fdau", interpreter)

    def test_minimal_fixtures_are_self_contained_and_parseable(self) -> None:
        self.assertTrue(installed_smoke.MINIMAL_V3.startswith(b"A\n3\n"))
        self.assertTrue(installed_smoke.MINIMAL_V4.startswith(b"A\n4\n"))
        self.assertEqual(1, len(FDRReader().read(io.StringIO(installed_smoke.MINIMAL_V3.decode("utf-8"))).samples))
        self.assertEqual(1, len(FDRReader().read(io.StringIO(installed_smoke.MINIMAL_V4.decode("utf-8"))).samples))

    def test_version_parser_requires_release_version(self) -> None:
        self.assertEqual("0.1.0", installed_smoke.parse_version(["0.1.0"]))
        with self.assertRaisesRegex(installed_smoke.SmokeError, "usage"):
            installed_smoke.parse_version([])

    def test_smoke_uses_the_nested_native_fdr_cli(self) -> None:
        commands: list[list[str]] = []

        with (
            mock.patch.object(installed_smoke, "ensure_outside_checkout"),
            mock.patch.object(installed_smoke, "_command_path", return_value=Path("xplane-fdau")),
            mock.patch.object(installed_smoke, "_run", side_effect=commands.append),
        ):
            installed_smoke.smoke("0.1.0", checkout=Path("checkout"))

        self.assertEqual("fdr", commands[0][1])
        self.assertEqual("validate", commands[0][2])
        self.assertEqual("fdr", commands[-1][1])
        self.assertEqual("to-geojson", commands[-1][2])


if __name__ == "__main__":
    unittest.main()
