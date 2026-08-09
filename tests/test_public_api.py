"""Contracts for the stable :mod:`xplane_fdr` import surface."""

from __future__ import annotations

import unittest

import xplane_fdr


class PublicAPITests(unittest.TestCase):
    """Keep documented imports deliberate and importable."""

    def test_documented_stable_imports_are_exported(self) -> None:
        """A removed public name must fail before it reaches the documentation."""
        required = {
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
            "FDRRecordingDefinition",
            "FDRRecordingProfile",
            "FDRRecordingSession",
            "FDRRecordingStateError",
            "FDRSample",
            "FDRSampleSink",
            "FDRSampleSource",
            "FDRSampleStream",
            "FDRSamplingPolicy",
            "FDRStoragePolicy",
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

        self.assertTrue(required.issubset(set(xplane_fdr.__all__)))
        for name in required:
            self.assertIsNotNone(getattr(xplane_fdr, name))
