"""Public exceptions for Flight Data Recorder processing."""

from __future__ import annotations

from os import PathLike


class FDRError(ValueError):
    """Base class for errors raised by :mod:`xplane_fdau.formats.xplane_fdr`."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class _FDRSourceError(FDRError):
    """Base for errors that can identify a source and line."""

    def __init__(self, message: str, *, source: str | None = None, line: int | None = None) -> None:
        self.source = source
        self.line = line
        location = ":".join(str(part) for part in (source, line) if part is not None)
        super().__init__(f"{location}: {message}" if location else message)
        self.message = message


class FDRParseError(_FDRSourceError):
    """Raised when FDR source text cannot be parsed."""


class FDRValidationError(_FDRSourceError):
    """Raised when FDR data violates the domain model."""


class FDRConfigError(FDRError):
    """Raised when recording configuration is invalid."""

    def __init__(self, message: str, *, property_path: str | None = None) -> None:
        self.property_path = property_path
        super().__init__(f"{property_path}: {message}" if property_path is not None else message)
        self.message = message


class FDRRecordingStateError(FDRError):
    """Raised for an invalid recording-session state transition."""


class FDROutputError(FDRError):
    """Raised when an FDR artifact cannot be created or published."""

    def __init__(self, message: str, *, artifact_path: str | PathLike[str] | None = None) -> None:
        self.artifact_path = artifact_path
        super().__init__(f"{artifact_path}: {message}" if artifact_path is not None else message)
        self.message = message
