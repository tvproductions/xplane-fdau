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
from .models import (
    FDRDataref,
    FDRHeader,
    FDRLegacyColumn,
    FDRMetadata,
    FDRNormalizationResult,
    FDRRecording,
    FDRSample,
)
from .reader import FDRReader, FDRSampleStream
from .recording import (
    FDRRecordingDefinition,
    FDRRecordingSession,
    FDRSampleSink,
    FDRSampleSource,
    FDRSamplingPolicy,
    FDRStoragePolicy,
)
from .profiles import (
    FDRRecordingProfile,
    FDRTrajectorySource,
    compose_profiles,
    get_profile,
    list_profiles,
    mandatory_trajectory_sources,
)
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
    "FDRRecording",
    "FDRRecordingDefinition",
    "FDRRecordingProfile",
    "FDRRecordingSession",
    "FDRRecordingStateError",
    "FDRRecordConfig",
    "FDRReader",
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
    "__version__",
    "compose_profiles",
    "get_profile",
    "list_profiles",
    "load_record_config",
    "mandatory_trajectory_sources",
    "resolve_recording_definition",
]

__version__ = "0.1.0"
