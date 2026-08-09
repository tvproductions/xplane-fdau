"""User-documentation contracts for the published toolkit."""

from __future__ import annotations

import hashlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    """Protect the active FDAU and native-FDR documentation contract."""

    def test_superseded_core_plan_cannot_be_mistaken_for_active_work(self) -> None:
        """Agents must reach current authority before historical execution steps."""
        plan = self._read_required_text(ROOT / "docs/superpowers/plans/2026-08-08-xplane-fdr-core.md")

        notice = "**Superseded — non-executable:**"
        self.assertIn(notice, plan)
        self.assertLess(plan.index(notice), plan.index("**For agentic workers:**"))
        self.assertIn(
            "../../architecture/xplane12_virtual_fdau_ecosystem_design.md",
            plan,
        )
        self.assertIn(
            "../specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md",
            plan,
        )

    def test_migration_spec_records_approved_unreleased_implementation_status(self) -> None:
        """The governing migration spec must no longer invite draft review."""
        specification = self._read_required_text(ROOT / "docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md")

        self.assertIn("**Status:** Approved / implemented but unreleased", specification)
        self.assertNotIn("**Status:** Draft", specification)

    def test_mkdocs_navigation_names_every_published_page(self) -> None:
        """A missing navigation entry makes a complete page undiscoverable."""
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

        for page in ("index.md", "usage/native-fdr.md", "reference/native-fdr.md"):
            self.assertIn(page, config)
        self.assertIn("validation:", config)
        self.assertIn("links:", config)

    def test_documentation_states_the_supported_format_and_capture_boundary(self) -> None:
        """Users must not infer a v3 writer or bundled simulator integration."""
        text = self._published_text()

        for required in (
            "FDR v3 and v4",
            "canonical v4",
            "lossy projection",
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
            "xplane-fdau-YYYYMMDDTHHMMSSffffffZ.fdr",
            "fdr-record-config-v1.schema.json",
            "custom DataRefs",
            "[longitude, latitude]",
            "MSL",
            "2D",
            "partial",
            "overwrite",
            "XPPython3",
            "unreleased",
            "inspect",
            "validate",
            "to-geojson",
        ):
            self.assertIn(required, text)

    def test_recording_examples_construct_semantic_inputs(self) -> None:
        """Callback examples need runnable models, not undefined placeholders."""
        guide = self._read_required_text(ROOT / "docs/usage/native-fdr.md")

        for required in (
            "FDRRecordingDefinition(",
            "FDRSample(time(12), -87.9, 41.9, 700, 270, 2, -1, (), ())",
            "session.record_from((sample,))",
        ):
            self.assertIn(required, guide)

    def test_partial_recovery_distinguishes_publication_from_cleanup_failure(self) -> None:
        """Callers must not retry publication after the final artifact was linked."""
        guide = self._read_required_text(ROOT / "docs/usage/native-fdr.md")
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

    def test_active_documentation_uses_the_fdau_native_projection_boundary(self) -> None:
        """Users need the nested native-format and sink entry points."""
        text = self._published_text()

        for required in (
            "xplane-fdau",
            "xplane_fdau.formats.xplane_fdr",
            "xplane_fdau.sinks.xplane_fdr",
            "xplane-fdau fdr inspect",
            "xplane-fdau fdr validate",
            "xplane-fdau fdr to-geojson",
            "lossy projection",
            "canonical FDAU archive",
            "standard library",
        ):
            self.assertIn(required, text)

    def test_imported_architecture_documents_retain_their_recorded_bytes(self) -> None:
        """The copied q4xpcc architecture references are immutable provenance."""
        expected_hashes = {
            "xplane12_virtual_fdau_ecosystem_design.md": "fc0fe7c0c6c37e51f52dec2781ce840dec729365754f9afce3b308306ae54480",
            "xplane12_foqa_fdr_addon_design_spec_v2.md": "9333d74bdb2ffeb9a8d21fdf508393289bf1e230f775f55cd36a5ae01dbd23ad",
        }

        for filename, expected_hash in expected_hashes.items():
            document = ROOT / "docs/architecture" / filename
            self.assertTrue(document.is_file())
            self.assertEqual(expected_hash, hashlib.sha256(document.read_bytes()).hexdigest())

    def test_active_surfaces_do_not_promise_the_unreleased_fdr_identity(self) -> None:
        """The former identity remains historical material, not an active contract."""
        active_paths = [
            ROOT / "README.md",
            ROOT / "mkdocs.yml",
            ROOT / "pyproject.toml",
            ROOT / ".pre-commit-config.yaml",
            ROOT / "AGENTS.md",
            ROOT / "BACKLOG.md",
            ROOT / "CHANGELOG.md",
            ROOT / "HANDOFF.md",
            ROOT / "docs/index.md",
            ROOT / "docs/usage/native-fdr.md",
            ROOT / "docs/reference/native-fdr.md",
            ROOT / "docs/schemas/fdr-record-config-v1.schema.json",
        ]
        active_paths.extend((ROOT / ".codex/skills").glob("*/SKILL.md"))
        active_paths.extend((ROOT / ".github/workflows").glob("*.yml"))
        active_paths.extend((ROOT / "tools").glob("*.py"))

        active_text = "\n".join(self._read_required_text(path) for path in active_paths)
        for required in (
            "https://github.com/tvproductions/xplane-fdau",
            "xplane-fdau",
            "xplane_fdau",
        ):
            self.assertIn(required, active_text)

        for path in active_paths:
            text = self._read_required_text(path)
            self.assertNotIn("https://github.com/tvproductions/xplane-fdr", text, path)
            self.assertNotIn("xplane-fdr =", text, path)
            self.assertNotIn("xplane-fdr inspect", text, path)
            self.assertNotIn("xplane-fdr validate", text, path)
            self.assertNotIn("xplane-fdr to-geojson", text, path)

    def test_active_plugin_guidance_and_runtime_docstrings_use_fdau_identity(self) -> None:
        """Current agent guidance and shipped help must name the installed project."""
        plugin_guidance = self._read_required_text(ROOT / ".codex/plugins/superpowers/PROJECT-INSTALL.md")
        runtime_paths = tuple(sorted((ROOT / "xplane_fdau").rglob("*.py")))
        runtime_text = "\n".join(self._read_required_text(path) for path in runtime_paths)

        self.assertIn("Project-specific operational skills are maintained for `xplane-fdau`", plugin_guidance)
        self.assertNotIn("will be designed for `xplane-fdr`", plugin_guidance)
        self.assertIn(":mod:`xplane_fdau.formats.xplane_fdr`", runtime_text)
        self.assertNotIn(":mod:`xplane_fdr`", runtime_text)

    def test_migration_closeout_preserves_the_unreleased_next_contract_boundary(self) -> None:
        """The next agent must not release or skip the canonical contract sequence."""
        handoff = self._read_required_text(ROOT / "HANDOFF.md")
        changelog = self._read_required_text(ROOT / "CHANGELOG.md")
        backlog = self._read_required_text(ROOT / "BACKLOG.md")
        backlog_prose = " ".join(backlog.split())

        for required in (
            "Identity and native-FDR-kernel migration: implemented and verified, but unreleased.",
            "Completed implementation plan",
            "measurement, binding, observation, sample, frame, timing, and quality contracts",
            "ARINC",
            "FDM/FOQA",
        ):
            self.assertIn(required, handoff)
        self.assertIn("## 0.1.0 (Unreleased)", changelog)
        self.assertNotIn("## 0.1.0 (Released)", changelog)
        for required in (
            "measurement, binding, observation, sample, frame, timing, and quality contracts",
            "acquisition profiles, demand resolution, continuity, and generic fan-out",
            "canonical archive, manifest, recovery, and deterministic replay",
            "canonical samples to the native FDR sink with explicit loss reporting",
            "ARINC",
            "FDM/FOQA",
        ):
            self.assertIn(required, backlog_prose)

    def _published_text(self) -> str:
        paths = (
            ROOT / "README.md",
            ROOT / "docs/index.md",
            ROOT / "docs/usage/native-fdr.md",
            ROOT / "docs/reference/native-fdr.md",
        )
        return "\n".join(self._read_required_text(path) for path in paths)

    def _read_required_text(self, path: Path) -> str:
        self.assertTrue(path.is_file(), path)
        return path.read_text(encoding="utf-8")
