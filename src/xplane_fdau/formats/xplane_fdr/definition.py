"""Immutable native FDR recording definitions and destination resolution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import math
import os
from pathlib import Path, PureWindowsPath

from .errors import FDRValidationError
from .models import FDRHeader


def utc_now() -> datetime:
    """Return the current aware UTC instant for generated artifact names."""
    return datetime.now(UTC)


def _positive_finite_float(value: object, name: str) -> float:
    if type(value) is not float or not math.isfinite(value) or value <= 0:
        raise FDRValidationError(f"{name} must be a positive finite float")
    return value


def _fdr_basename(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or not value.endswith(".fdr"):
        raise FDRValidationError(f"{name} must be a basename ending in .fdr")
    if "/" in value or "\\" in value or PureWindowsPath(value).drive:
        raise FDRValidationError(f"{name} must not contain a drive or directory separator")
    return value


def _utc_instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise FDRValidationError(f"{name} must be an aware UTC datetime")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class FDRSamplingPolicy:
    """Adapter-owned sampling cadence metadata for a recording definition."""

    interval_seconds: float = 0.1
    duration_seconds: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "interval_seconds",
            _positive_finite_float(self.interval_seconds, "interval_seconds"),
        )
        if self.duration_seconds is not None:
            object.__setattr__(
                self,
                "duration_seconds",
                _positive_finite_float(self.duration_seconds, "duration_seconds"),
            )


@dataclass(frozen=True, slots=True)
class FDRStoragePolicy:
    """Directory and optional literal filename used for artifact resolution."""

    directory: Path = Path("Output/FDR files")
    filename: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.directory, Path):
            raise FDRValidationError("storage directory must be a Path")
        if self.filename is not None:
            object.__setattr__(self, "filename", _fdr_basename(self.filename, "storage filename"))


@dataclass(frozen=True, slots=True)
class FDRRecordingDefinition:
    """Immutable header, sampling, and storage policy for one recording."""

    header: FDRHeader
    sampling: FDRSamplingPolicy
    storage: FDRStoragePolicy

    def __post_init__(self) -> None:
        if not isinstance(self.header, FDRHeader) or self.header.source_version != 4:
            raise FDRValidationError("recording definition requires a version 4 header")
        if not isinstance(self.sampling, FDRSamplingPolicy):
            raise FDRValidationError("recording definition sampling must be an FDRSamplingPolicy")
        if not isinstance(self.storage, FDRStoragePolicy):
            raise FDRValidationError("recording definition storage must be an FDRStoragePolicy")


def _resolved_destination(
    definition: FDRRecordingDefinition,
    *,
    xplane_root: str | os.PathLike[str] | None,
    filename: str | None,
    started_at_utc: datetime | None,
    utc_clock: Callable[[], datetime],
) -> Path:
    directory = definition.storage.directory
    if not directory.is_absolute():
        if xplane_root is None:
            raise FDRValidationError("relative storage directory requires xplane_root")
        directory = Path(xplane_root) / directory

    if filename is not None:
        resolved_filename = _fdr_basename(filename, "filename")
    elif definition.storage.filename is not None:
        resolved_filename = definition.storage.filename
    else:
        instant = started_at_utc if started_at_utc is not None else utc_clock()
        started = _utc_instant(instant, "recording start")
        resolved_filename = f"xplane-fdau-{started:%Y%m%dT%H%M%S}{started.microsecond:06d}Z.fdr"
    return directory / resolved_filename
