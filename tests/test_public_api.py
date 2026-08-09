"""Contracts for the stable native FDR import surface."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest

import xplane_fdau
import xplane_fdau.formats.xplane_fdr as native_fdr
import xplane_fdau.sinks.xplane_fdr as native_sink


FORMAT_NAMES = {
    "FDRConfigError",
    "FDRDataref",
    "FDRDatarefConfig",
    "FDRError",
    "FDRHeader",
    "FDRLegacyColumn",
    "FDRMetadata",
    "FDRMetadataConfig",
    "FDRNormalizationResult",
    "FDROutputError",
    "FDRParseError",
    "FDRRecordConfig",
    "FDRReader",
    "FDRRecording",
    "FDRRecordingProfile",
    "FDRRecordingStateError",
    "FDRSample",
    "FDRSampleStream",
    "FDRStreamWriter",
    "FDRTrajectorySource",
    "FDRValidationError",
    "FDRWriter",
    "compose_profiles",
    "get_profile",
    "list_profiles",
    "load_record_config",
    "mandatory_trajectory_sources",
    "recording_to_geojson",
    "resolve_recording_definition",
}
SINK_NAMES = {
    "FDRRecordingDefinition",
    "FDRRecordingSession",
    "FDRSampleSink",
    "FDRSampleSource",
    "FDRSamplingPolicy",
    "FDRStoragePolicy",
}


class PublicAPITests(unittest.TestCase):
    """Keep documented imports deliberate and importable."""

    def test_native_format_and_sink_export_exact_ownership_sets(self) -> None:
        """A misplaced public name must fail before it reaches the documentation."""
        self.assertEqual(["__version__"], xplane_fdau.__all__)
        self.assertEqual(FORMAT_NAMES, set(native_fdr.__all__))
        self.assertEqual(SINK_NAMES, set(native_sink.__all__))
        for name in FORMAT_NAMES:
            self.assertIsNotNone(getattr(native_fdr, name))
        for name in SINK_NAMES:
            self.assertIsNotNone(getattr(native_sink, name))

    def test_formats_do_not_depend_on_sinks_and_sink_imports_only_format_or_stdlib(self) -> None:
        """A format-to-sink edge would invert the native boundary."""
        project_root = Path(__file__).parents[1]
        formats_root = project_root / "xplane_fdau" / "formats"
        for path in formats_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(alias.name == "xplane_fdau.sinks" or alias.name.startswith("xplane_fdau.sinks."))
                if isinstance(node, ast.ImportFrom):
                    resolved = self._resolve_import(path, node)
                    self.assertFalse(resolved == "xplane_fdau.sinks" or resolved.startswith("xplane_fdau.sinks."))

        sink_path = project_root / "xplane_fdau" / "sinks" / "xplane_fdr.py"
        tree = ast.parse(sink_path.read_text(encoding="utf-8"), filename=str(sink_path))
        allowed_stdlib = set(__import__("sys").stdlib_module_names) | {"__future__"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertIn(alias.name.split(".", 1)[0], allowed_stdlib)
            if isinstance(node, ast.ImportFrom):
                self.assertEqual(0, node.level)
                module = node.module or ""
                if module.startswith("xplane_fdau"):
                    native_format = "xplane_fdau.formats.xplane_fdr"
                    self.assertTrue(module == native_format or module.startswith(f"{native_format}."))
                else:
                    self.assertIn(module.split(".", 1)[0], allowed_stdlib)

    @staticmethod
    def _resolve_import(path: Path, node: ast.ImportFrom) -> str:
        if node.level == 0:
            return node.module or ""
        project_root = Path(__file__).parents[1]
        module_parts = list(path.relative_to(project_root).with_suffix("").parts)
        if module_parts[-1] != "__init__":
            module_parts.pop()
        else:
            module_parts.pop()
        parent = module_parts[: len(module_parts) - node.level + 1]
        if node.module is not None:
            parent.extend(node.module.split("."))
        return ".".join(parent)
