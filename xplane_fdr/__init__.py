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
    "FDRRecordingStateError",
    "FDRReader",
    "FDRSample",
    "FDRSampleStream",
    "FDRValidationError",
    "__version__",
]

__version__ = "0.1.0"
