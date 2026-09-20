"""Push-first publication lifecycle for native X-Plane FDR artifacts."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import datetime
import os
from pathlib import Path
from typing import NoReturn, Protocol, TextIO, cast

from xplane_fdau.formats.xplane_fdr.definition import (
    FDRRecordingDefinition,
    FDRSamplingPolicy,
    FDRStoragePolicy,
    _resolved_destination,
    utc_now,
)
from xplane_fdau.formats.xplane_fdr.errors import FDRRecordingStateError, FDRValidationError
from xplane_fdau.formats.xplane_fdr.models import FDRRecording, FDRSample
from xplane_fdau.formats.xplane_fdr.writer import FDRStreamWriter, FDRWriter

__all__ = [
    "FDRRecordingDefinition",
    "FDRRecordingSession",
    "FDRSampleSink",
    "FDRSampleSource",
    "FDRSamplingPolicy",
    "FDRStoragePolicy",
]


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
        return cls(target, definition, destination_path=destination_path, overwrite=overwrite)

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
