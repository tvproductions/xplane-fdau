"""X-Plane Flight Data Recorder toolkit."""

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
    "FDRError",
    "FDRHeader",
    "FDRLegacyColumn",
    "FDRMetadata",
    "FDRNormalizationResult",
    "FDROutputError",
    "FDRParseError",
    "FDRRecording",
    "FDRRecordingDefinition",
    "FDRRecordingProfile",
    "FDRRecordingSession",
    "FDRRecordingStateError",
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
    "mandatory_trajectory_sources",
]

__version__ = "0.1.0"
