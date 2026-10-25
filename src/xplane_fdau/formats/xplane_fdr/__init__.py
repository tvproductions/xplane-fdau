"""X-Plane Flight Data Recorder toolkit."""

from .config import (
    FDRDatarefConfig,
    FDRMetadataConfig,
    FDRRecordConfig,
    load_record_config,
    resolve_recording_definition,
)
from .errors import (
    FDRConfigError,
    FDRError,
    FDROutputError,
    FDRParseError,
    FDRRecordingStateError,
    FDRValidationError,
)
from .geojson import recording_to_geojson
from .models import (
    FDRDataref,
    FDRHeader,
    FDRLegacyColumn,
    FDRMetadata,
    FDRNormalizationResult,
    FDRRecording,
    FDRSample,
)
from .profiles import (
    FDRRecordingProfile,
    FDRTrajectorySource,
    compose_profiles,
    get_profile,
    list_profiles,
    mandatory_trajectory_sources,
)
from .reader import FDRReader, FDRSampleStream
from .writer import FDRStreamWriter, FDRWriter

__all__ = [
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
    "FDRReader",
    "FDRRecordConfig",
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
]
