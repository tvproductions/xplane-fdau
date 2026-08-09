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
    "FDRValidationError",
    "FDRWriter",
    "__version__",
]

__version__ = "0.1.0"
