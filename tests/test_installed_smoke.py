"""Tests for the installed-wheel smoke-test command."""

from __future__ import annotations

import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import xplane_fdau
from tools import installed_smoke
from xplane_fdau.formats.xplane_fdr import FDRReader


class InstalledSmokeTests(unittest.TestCase):
    def test_measurement_definition_smoke_passes(self) -> None:
        self.assertTrue(hasattr(installed_smoke, "_measurement_definition_smoke"), "measurement definition smoke is absent")
        installed_smoke._measurement_definition_smoke()

    def test_measurement_definition_smoke_detects_ineffective_entry_rejections(self) -> None:
        from xplane_fdau.measurements import _definition_io

        self.assertTrue(hasattr(installed_smoke, "_measurement_definition_smoke"), "measurement definition smoke is absent")
        original = _definition_io._measurement_definition_from_wire
        for tamper, message in (("numeric", "irrelevant numeric"), ("title", "stale hash")):

            def accept_tampered(raw: object, *, path: str = "", source: str = "<memory>", selected: str = tamper) -> object:
                if isinstance(raw, dict) and ("numeric" in raw if selected == "numeric" else raw.get("title") == "Tampered"):
                    return object()
                return original(raw, path=path, source=source)

            with (
                self.subTest(tamper=tamper),
                mock.patch.object(_definition_io, "_measurement_definition_from_wire", side_effect=accept_tampered),
                self.assertRaisesRegex(installed_smoke.SmokeError, message),
            ):
                installed_smoke._measurement_definition_smoke()

    def test_measurement_definition_smoke_detects_wrong_ownership_bytes_and_hash(self) -> None:
        import xplane_fdau.measurements as measurements
        from xplane_fdau.measurements import _definition_io, models

        self.assertTrue(hasattr(installed_smoke, "_measurement_definition_smoke"), "measurement definition smoke is absent")
        with mock.patch.object(measurements, "MeasurementDefinition", object()), self.assertRaises(installed_smoke.SmokeError):
            installed_smoke._measurement_definition_smoke()
        with mock.patch.object(_definition_io, "_measurement_definition_bytes", return_value=b"incorrect\n"), self.assertRaises(installed_smoke.SmokeError):
            installed_smoke._measurement_definition_smoke()
        with mock.patch.object(models, "_definition_content_hash", return_value="0" * 64), self.assertRaisesRegex(installed_smoke.SmokeError, "hash differs"):
            installed_smoke._measurement_definition_smoke()

    def test_measurement_definition_smoke_is_called_by_the_installed_flow(self) -> None:
        self.assertTrue(hasattr(installed_smoke, "_measurement_definition_smoke"), "measurement definition smoke is absent")
        with (
            mock.patch.object(installed_smoke, "ensure_outside_checkout"),
            mock.patch.object(installed_smoke, "_command_path", return_value=Path("xplane-fdau")),
            mock.patch.object(installed_smoke, "_run"),
            mock.patch.object(installed_smoke, "_measurement_definition_smoke") as check,
        ):
            installed_smoke.smoke("0.1.0", checkout=Path("checkout"))
        check.assert_called_once_with()

    def test_measurement_definition_guide_examples_execute(self) -> None:
        from dataclasses import replace

        from xplane_fdau.contracts import ContractValidationError
        from xplane_fdau.measurements import MeasurementDefinition, NumericSpec, ValidityState

        page = Path(__file__).resolve().parents[1] / "docs/reference/measurement-definitions.md"
        self.assertTrue(page.is_file(), "measurement definition guide is absent")
        examples = re.findall(r"```python\n(.*?)```", page.read_text(encoding="utf-8"), re.DOTALL)
        self.assertTrue(examples)
        namespace: dict[str, object] = {}
        for example in examples:
            exec(compile(example, str(page), "exec"), namespace)
        value = namespace["definition"]
        self.assertIsInstance(value, MeasurementDefinition)
        if not isinstance(value, MeasurementDefinition):
            self.fail("guide did not construct a measurement definition")
        self.assertEqual((ValidityState.UNKNOWN,), value.allowed_validity)
        self.assertEqual((), value.allowed_quality)
        self.assertEqual(namespace["identity_hash"], value.content_hash)
        self.assertEqual(64, len(value.content_hash))
        self.assertNotEqual(value.content_hash, replace(value, definition_revision=2).content_hash)
        with self.assertRaises(ContractValidationError) as rejected:
            replace(value, numeric=NumericSpec(storage_precision_bits=1, resolution=1))
        self.assertEqual("/numeric", rejected.exception.path)

    def test_measurement_quality_smoke_detects_reordered_acceptance(self) -> None:
        from xplane_fdau.measurements import QualityFlag, _quality

        original = _quality._quality_flags

        def accept_reversed(value: object, *, path: str = "/quality") -> tuple[QualityFlag, ...]:
            if value == ("stale", "rounded"):
                return (QualityFlag.STALE, QualityFlag.ROUNDED)
            return original(value, path=path)

        with mock.patch.object(_quality, "_quality_flags", side_effect=accept_reversed), self.assertRaisesRegex(installed_smoke.SmokeError, "noncanonical"):
            installed_smoke._measurement_quality_smoke()

    def test_measurement_quality_smoke_detects_duplicate_acceptance(self) -> None:
        from xplane_fdau.measurements import QualityFlag, _quality

        original = _quality._quality_flags

        def accept_duplicate(value: object, *, path: str = "/quality") -> tuple[QualityFlag, ...]:
            if value == ("stale", "stale"):
                return (QualityFlag.STALE, QualityFlag.STALE)
            return original(value, path=path)

        with mock.patch.object(_quality, "_quality_flags", side_effect=accept_duplicate), self.assertRaisesRegex(installed_smoke.SmokeError, "noncanonical"):
            installed_smoke._measurement_quality_smoke()

    def test_measurement_quality_smoke_passes(self) -> None:
        installed_smoke._measurement_quality_smoke()

    def test_timing_smoke_detects_incorrect_difference(self) -> None:
        import xplane_fdau.contracts as contracts

        with mock.patch.object(contracts, "difference_clock_readings_ns", return_value=99), self.assertRaises(installed_smoke.SmokeError):
            installed_smoke._canonical_timing_smoke()

    def test_timing_smoke_detects_altered_utc_digits(self) -> None:
        import xplane_fdau.contracts as contracts

        original = contracts.canonical_bytes

        def broken(value: object) -> bytes:
            if type(value) is contracts.UtcInstant:
                return b'"2026-10-26T12:34:56.123456788Z"\n'
            return original(value)

        with mock.patch.object(contracts, "canonical_bytes", side_effect=broken), self.assertRaises(installed_smoke.SmokeError):
            installed_smoke._canonical_timing_smoke()

    def test_timing_smoke_passes_against_the_real_public_contracts(self) -> None:
        installed_smoke._canonical_timing_smoke()

    def test_console_child_runs_through_uv_in_the_installed_environment(self) -> None:
        command = [str(Path(sys.executable).parent / "xplane-fdau"), "fdr", "validate", "flight.fdr"]
        with mock.patch.object(installed_smoke.subprocess, "run", return_value=subprocess.CompletedProcess(command, 0)) as run:
            installed_smoke._run(command)
        self.assertEqual(
            ["uv", "run", "--offline", "--no-project", "--python", sys.executable, *command],
            run.call_args.args[0],
        )

    def test_value_smoke_rejects_incorrect_canonical_projection(self) -> None:
        import xplane_fdau.contracts as contracts

        original = contracts.canonical_bytes

        def broken(value: object) -> bytes:
            if type(value) is contracts.InlineValue:
                return b'{"element_representation":"real","representation":"fixed_array","value":[1.0,2.0]}\n'
            return original(value)

        with mock.patch.object(contracts, "canonical_bytes", side_effect=broken), self.assertRaises(installed_smoke.SmokeError):
            installed_smoke._canonical_values_smoke()

    def test_value_smoke_rejects_altered_payload_metadata(self) -> None:
        from xplane_fdau.contracts import values

        original = values._payload_reference_wire

        def broken(value: values.PayloadReference) -> dict[str, object]:
            return original(value) | {"byte_length": 999}

        with mock.patch("xplane_fdau.contracts.canonical_json._payload_reference_wire", side_effect=broken), self.assertRaises(installed_smoke.SmokeError):
            installed_smoke._canonical_values_smoke()

    def test_value_smoke_runs_without_payload_storage_access(self) -> None:
        with (
            mock.patch("builtins.open", side_effect=AssertionError("unexpected payload access")),
            mock.patch("pathlib.Path.open", side_effect=AssertionError("unexpected payload access")),
            mock.patch("pathlib.Path.read_bytes", side_effect=AssertionError("unexpected payload access")),
        ):
            installed_smoke._canonical_values_smoke()

    def test_all_installed_runtime_modules_are_discovered_and_imported(self) -> None:
        expected = {
            "xplane_fdau",
            "xplane_fdau.cli",
            "xplane_fdau.contracts",
            "xplane_fdau.contracts.errors",
            "xplane_fdau.contracts._json_parse",
            "xplane_fdau.contracts._binary64",
            "xplane_fdau.contracts._identity_validation",
            "xplane_fdau.contracts._content_hash",
            "xplane_fdau.contracts.identity",
            "xplane_fdau.contracts.provenance",
            "xplane_fdau.contracts.canonical_json",
            "xplane_fdau.contracts.values",
            "xplane_fdau.contracts._value_io",
            "xplane_fdau.contracts.timing",
            "xplane_fdau.contracts._timing_validation",
            "xplane_fdau.contracts._timing_io",
            "xplane_fdau.measurements",
            "xplane_fdau.measurements.models",
            "xplane_fdau.measurements._quality",
            "xplane_fdau.measurements._definition_validation",
            "xplane_fdau.measurements._definition_io",
            "xplane_fdau.formats",
            "xplane_fdau.formats.xplane_fdr",
            "xplane_fdau.formats.xplane_fdr.config",
            "xplane_fdau.formats.xplane_fdr.definition",
            "xplane_fdau.formats.xplane_fdr.errors",
            "xplane_fdau.formats.xplane_fdr.geojson",
            "xplane_fdau.formats.xplane_fdr.models",
            "xplane_fdau.formats.xplane_fdr.profiles",
            "xplane_fdau.formats.xplane_fdr.reader",
            "xplane_fdau.formats.xplane_fdr.schemas",
            "xplane_fdau.formats.xplane_fdr.writer",
            "xplane_fdau.sinks",
            "xplane_fdau.sinks.xplane_fdr",
        }

        imported = installed_smoke.import_all_modules(xplane_fdau)

        self.assertEqual(expected, set(imported))
        for name in imported:
            self.assertIn(name, sys.modules)

    def test_checkout_path_detection_rejects_checkout_import(self) -> None:
        checkout = Path("C:/work/xplane-fdr").resolve()
        with self.assertRaisesRegex(installed_smoke.SmokeError, "checkout"):
            installed_smoke.ensure_outside_checkout(checkout / "src/xplane_fdau/__init__.py", checkout)

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

    def test_legacy_package_presence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            legacy = Path(raw) / "xplane_fdr"
            legacy.mkdir()
            (legacy / "__init__.py").write_text("", encoding="utf-8")
            sys.path.insert(0, raw)
            importlib.invalidate_caches()
            try:
                with self.assertRaisesRegex(installed_smoke.SmokeError, "xplane_fdr"):
                    installed_smoke.ensure_legacy_package_absent()
            finally:
                sys.path.remove(raw)
                importlib.invalidate_caches()

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

    def test_smoke_rejects_wrong_installed_canonical_bytes(self) -> None:
        with (
            mock.patch.object(installed_smoke, "ensure_outside_checkout"),
            mock.patch.object(installed_smoke, "_command_path", return_value=Path("xplane-fdau")),
            mock.patch.object(installed_smoke, "_run"),
            mock.patch("xplane_fdau.contracts.canonical_bytes", return_value=b"incorrect\n"),
            self.assertRaises(installed_smoke.SmokeError),
        ):
            installed_smoke.smoke("0.1.0", checkout=Path("checkout"))

    def test_smoke_rejects_wrong_installed_reference_or_hash(self) -> None:
        for target, wrong in (
            ("xplane_fdau.contracts.identity._definition_ref_wire", {"definition_id": "wrong.id"}),
            ("xplane_fdau.contracts._content_hash._record_content_hash", "0" * 64),
            ("xplane_fdau.contracts._content_hash._definition_preimage", b"incorrect\n"),
        ):
            with (
                self.subTest(target=target),
                mock.patch.object(installed_smoke, "ensure_outside_checkout"),
                mock.patch.object(installed_smoke, "_command_path", return_value=Path("xplane-fdau")),
                mock.patch.object(installed_smoke, "_run"),
                mock.patch(target, return_value=wrong),
                self.assertRaises(installed_smoke.SmokeError),
            ):
                installed_smoke.smoke("0.1.0", checkout=Path("checkout"))


if __name__ == "__main__":
    unittest.main()
