"""Push-first recording sessions and configurable artifact resolution."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import math
import os
from pathlib import Path
from typing import NoReturn, Protocol, TextIO, cast

from .errors import FDRRecordingStateError, FDRValidationError
from .models import FDRHeader, FDRRecording, FDRSample
from .writer import FDRStreamWriter, FDRWriter


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
    if "/" in value or "\\" in value:
        raise FDRValidationError(f"{name} must not contain a directory separator")
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


class FDRSampleSource(Protocol):
    """Iterable source of semantic FDR samples."""

    def __iter__(self) -> Iterator[FDRSample]: ...


class FDRSampleSink(Protocol):
    """Lifecycle-managed destination accepting semantic FDR samples."""

    @property
    def destination_path(self) -> Path | None: ...

    @property
    def partial_path(self) -> Path | None: ...

    def write_sample(self, sample: FDRSample) -> None: ...

    def commit(self) -> None: ...

    def abort(self) -> None: ...


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
        resolved_filename = f"xplane-fdr-{started:%Y%m%dT%H%M%S}{started.microsecond:06d}Z.fdr"
    return directory / resolved_filename


class FDRRecordingSession:
    """Prepared push-first session that publishes only committed recordings."""

    def __init__(
        self,
        destination: str | os.PathLike[str] | TextIO,
        definition: FDRRecordingDefinition,
        *,
        destination_path: Path | None,
        overwrite: bool,
    ) -> None:
        self._destination = destination
        self._definition = definition
        self._destination_path = destination_path
        self._overwrite = overwrite
        self._sink: FDRStreamWriter | None = None
        self._sample_count = 0
        self._state = "prepared"

    @classmethod
    def open(
        cls,
        destination: str | os.PathLike[str] | TextIO | None,
        definition: FDRRecordingDefinition,
        *,
        xplane_root: str | os.PathLike[str] | None = None,
        filename: str | None = None,
        started_at_utc: datetime | None = None,
        overwrite: bool = False,
        utc_clock: Callable[[], datetime] = utc_now,
    ) -> FDRRecordingSession:
        """Prepare a session without creating or writing its destination."""
        if not isinstance(definition, FDRRecordingDefinition):
            raise FDRValidationError("definition must be an FDRRecordingDefinition")
        if isinstance(destination, (str, os.PathLike)):
            path = Path(cast(str | os.PathLike[str], destination))
            target: str | os.PathLike[str] | TextIO = path
            destination_path: Path | None = path
        elif destination is not None:
            target = destination
            destination_path = None
        else:
            path = _resolved_destination(
                definition,
                xplane_root=xplane_root,
                filename=filename,
                started_at_utc=started_at_utc,
                utc_clock=utc_clock,
            )
            target = path
            destination_path = path
        return cls(
            target,
            definition,
            destination_path=destination_path,
            overwrite=overwrite,
        )

    @property
    def destination_path(self) -> Path | None:
        """Return the resolved path, or ``None`` for a caller stream."""
        return self._destination_path

    @property
    def partial_path(self) -> Path | None:
        """Return the path writer's diagnostic partial once active."""
        return None if self._sink is None else self._sink.partial_path

    def _require_active(self) -> FDRStreamWriter:
        if self._state != "active" or self._sink is None:
            raise FDRRecordingStateError(f"recording session is {self._state}")
        return self._sink

    def record(self, sample: FDRSample) -> None:
        """Validate and append exactly one semantic sample."""
        sink = self._require_active()
        FDRRecording(self._definition.header, (sample,))
        try:
            sink.write_sample(sample)
        except BaseException:
            self._state = "aborted"
            raise
        self._sample_count += 1

    def record_from(self, source: FDRSampleSource) -> int:
        """Record each sample from an iterable source and return its count."""
        count = 0
        for sample in source:
            self.record(sample)
            count += 1
        return count

    def commit(self) -> Path | None:
        """Publish an active recording and return its resolved destination."""
        sink = self._require_active()
        if self._sample_count == 0:
            primary = FDRRecordingStateError("cannot commit an FDR recording without samples")
            self._abort_after(primary)
        try:
            sink.commit()
        except BaseException:
            self._state = "aborted"
            raise
        self._state = "committed"
        return self._destination_path

    def abort(self) -> None:
        """Abort an active session while retaining a path-based partial."""
        sink = self._require_active()
        self._state = "aborted"
        sink.abort()

    def _abort_after(self, primary: BaseException) -> NoReturn:
        sink = cast(FDRStreamWriter, self._sink)
        self._state = "aborted"
        try:
            sink.abort()
        except BaseException as cleanup:
            raise BaseExceptionGroup("FDR recording and cleanup failed", [primary, cleanup]) from None
        raise primary.with_traceback(primary.__traceback__)

    def __enter__(self) -> FDRRecordingSession:
        """Activate this prepared session and create its stream writer."""
        if self._state != "prepared":
            raise FDRRecordingStateError(f"recording session is {self._state}")
        try:
            self._sink = FDRWriter().open(
                self._definition.header,
                self._destination,
                overwrite=self._overwrite,
            )
        except BaseException:
            self._state = "aborted"
            raise
        self._state = "active"
        return self

    def __exit__(self, _exc_type: object, exc_value: BaseException | None, _traceback: object) -> None:
        """Commit a successful non-empty body, otherwise abort."""
        if self._state != "active":
            return
        if exc_value is None:
            self.commit()
            return
        self._abort_after(exc_value)
