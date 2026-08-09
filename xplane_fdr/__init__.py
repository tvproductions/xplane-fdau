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
    "FDRSample",
    "FDRValidationError",
    "__version__",
]

__version__ = "0.1.0"
