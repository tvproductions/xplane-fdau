"""User-documentation contracts for the published toolkit."""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    """Protect the stable promises a user needs to choose and operate the library."""

    def test_mkdocs_navigation_names_every_published_page(self) -> None:
        """A missing navigation entry makes a complete page undiscoverable."""
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

        for page in ("index.md", "usage/fdr-toolkit.md", "reference/fdr.md"):
            self.assertIn(page, config)
        self.assertIn("validation:", config)
        self.assertIn("links:", config)

    def test_documentation_states_the_supported_format_and_capture_boundary(self) -> None:
        """Users must not infer a v3 writer or bundled simulator integration."""
        text = self._published_text()

        for required in (
            "FDR v3 and v4",
            "canonical v4",
            "lossy",
            "explicit opt-in",
            "standard library",
            "push-first",
            "session.record(sample)",
            "capture adapters are not bundled",
            "cadence scheduling",
            "connections",
            "plugin lifecycle",
            "does not include a live-record command",
            "ARINC",
            "FOQA",
        ):
            self.assertIn(required, text)

    def test_documentation_covers_storage_config_geojson_and_xppython3(self) -> None:
        """The operational information must be present where an adopter can find it."""
        text = self._published_text()

        for required in (
            "Output/FDR files",
            "xplane-fdr-YYYYMMDDTHHMMSSffffffZ.fdr",
            "fdr-record-config-v1.schema.json",
            "custom DataRefs",
            "[longitude, latitude]",
            "MSL",
            "2D",
            "partial",
            "overwrite",
            "XPPython3",
            "released wheel",
            "inspect",
            "validate",
            "to-geojson",
        ):
            self.assertIn(required, text)

    def test_recording_examples_construct_semantic_inputs(self) -> None:
        """Callback examples need runnable models, not undefined placeholders."""
        guide = (ROOT / "docs/usage/fdr-toolkit.md").read_text(encoding="utf-8")

        for required in (
            "FDRRecordingDefinition(",
            "FDRSample(time(12), -87.9, 41.9, 700, 270, 2, -1, (), ())",
            "session.record_from((sample,))",
        ):
            self.assertIn(required, guide)

    def test_partial_recovery_distinguishes_publication_from_cleanup_failure(self) -> None:
        """Callers must not retry publication after the final artifact was linked."""
        guide = (ROOT / "docs/usage/fdr-toolkit.md").read_text(encoding="utf-8")
        prose = " ".join(guide.split())

        for required in (
            "Before publication",
            "never creates the requested final artifact",
            "After publication",
            "cleanup-specific `FDROutputError`",
            "retains both the final artifact and the partial artifact",
            "must not blindly retry publication",
        ):
            self.assertIn(required, prose)

    def test_documented_schema_url_has_a_published_schema_artifact(self) -> None:
        """The schema URL in a user configuration must not lead to a Pages 404."""
        published = ROOT / "docs/schemas/fdr-record-config-v1.schema.json"
        packaged = ROOT / "xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json"

        self.assertTrue(published.is_file())
        self.assertEqual(packaged.read_bytes(), published.read_bytes())

    def _published_text(self) -> str:
        paths = (
            ROOT / "README.md",
            ROOT / "docs/index.md",
            ROOT / "docs/usage/fdr-toolkit.md",
            ROOT / "docs/reference/fdr.md",
        )
        return "\n".join(path.read_text(encoding="utf-8") for path in paths)
