"""Deterministic and durable version 4 FDR serialization."""

from __future__ import annotations

from datetime import datetime
import math
import os
from pathlib import Path
import re
import secrets
from typing import NoReturn, TextIO, cast

from .errors import FDROutputError, FDRRecordingStateError, FDRValidationError
from .models import FDRHeader, FDRNormalizationResult, FDRRecording, FDRSample


_METADATA_PATTERN = re.compile(r"^[A-Z0-9]{4}$")
_RESERVED_METADATA_KEYS = frozenset({"COMM", "DREF"})
_DATE_FORMATS = (
    (re.compile(r"^[0-9]{2}/[0-9]{2}/[0-9]{4}$"), "%m/%d/%Y"),
    (re.compile(r"^[0-9]{2}/[0-9]{2}/[0-9]{2}$"), "%m/%d/%y"),
    (re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"), "%Y-%m-%d"),
)


def _single_line(value: str, name: str) -> str:
    if "\n" in value or "\r" in value:
        raise FDRValidationError(f"{name} must not contain a line separator")
    return value


def _render_number(value: int | float) -> str:
    if type(value) is int:
        return str(value)
    if type(value) is not float or not math.isfinite(value):
        raise FDRValidationError("FDR numbers must be finite int or float values")
    return repr(value)


def _validate_date(value: str) -> None:
    for pattern, date_format in _DATE_FORMATS:
        if pattern.fullmatch(value) is None:
            continue
        try:
            datetime.strptime(value, date_format)
        except ValueError:
            break
        return
    raise FDRValidationError("DATE must be MM/DD/YYYY, MM/DD/YY, or YYYY-MM-DD")


def _render_header(header: FDRHeader) -> str:
    if not isinstance(header, FDRHeader):
        raise FDRValidationError("header must be an FDRHeader")
    if header.source_version != 4:
        raise FDRValidationError("writer supports version 4 headers only")

    lines = ["A", "4"]
    lines.extend(f"COMM, {_single_line(comment, 'comment')}" for comment in header.comments)
    for item in header.metadata:
        if _METADATA_PATTERN.fullmatch(item.key) is None or item.key in _RESERVED_METADATA_KEYS:
            raise FDRValidationError("metadata key must be four-character uppercase text")
        value = _single_line(item.value, "metadata value")
        if item.key == "DATE":
            _validate_date(value)
        lines.append(f"{item.key}, {value}")
    for dataref in header.datarefs:
        path = _single_line(dataref.path, "DataRef path")
        if any(character.isspace() for character in path) or "//" in path:
            raise FDRValidationError("DataRef path must not contain whitespace or double slashes")
        declaration = f"DREF, {path} {_render_number(dataref.scale)}"
        if dataref.comment is not None:
            declaration += f" // {_single_line(dataref.comment, 'DataRef comment')}" if dataref.comment else " //"
        lines.append(declaration)
    return "\n".join(lines) + "\n"


def _render_sample(sample: FDRSample, dataref_count: int) -> str:
    if not isinstance(sample, FDRSample):
        raise FDRValidationError("sample must be an FDRSample")
    if len(sample.additional_values) != dataref_count:
        raise FDRValidationError("sample additional values do not match declared DataRefs")
    if sample.legacy_values:
        raise FDRValidationError("version 4 samples must not contain legacy values")
    fields = (
        sample.time_utc.isoformat(),
        _render_number(sample.longitude),
        _render_number(sample.latitude),
        _render_number(sample.altitude_msl_ft),
        _render_number(sample.heading_magnetic_deg),
        _render_number(sample.pitch_deg),
        _render_number(sample.roll_deg),
        *(_render_number(value) for value in sample.additional_values),
    )
    return ", ".join(fields) + "\n"


def _create_partial(destination: Path) -> tuple[Path, TextIO]:
    for _attempt in range(100):
        partial_path = destination.with_name(f".{destination.name}.{secrets.token_hex(8)}.partial")
        try:
            return partial_path, partial_path.open("x", encoding="utf-8", newline="\n")
        except FileExistsError:
            continue
    raise FileExistsError(f"could not create a unique partial file beside {destination}")


def _wrapped_output_error(error: OSError, artifact_path: Path | None) -> FDROutputError:
    try:
        raise FDROutputError("FDR output operation failed", artifact_path=artifact_path) from error
    except FDROutputError as wrapped:
        return wrapped


def _published_cleanup_error(error: OSError, partial_path: Path) -> FDROutputError:
    try:
        raise FDROutputError(
            f"FDR publication succeeded but partial cleanup failed: {error}",
            artifact_path=partial_path,
        ) from error
    except FDROutputError as wrapped:
        return wrapped


class FDRStreamWriter:
    """Incrementally write validated samples and explicitly commit or abort."""

    def __init__(
        self,
        header: FDRHeader,
        stream: TextIO,
        *,
        destination: Path | None,
        partial_path: Path | None,
        overwrite: bool,
        header_text: str,
    ) -> None:
        self._header = header
        self._stream = stream
        self._destination = destination
        self._partial_path = partial_path
        self._overwrite = overwrite
        self._sample_count = 0
        self._state = "active"
        try:
            self._write_text(header_text)
        except BaseException as primary:
            self._abort_after(primary)

    @property
    def partial_path(self) -> Path | None:
        """Return the diagnostic partial path for path-based output."""
        return self._partial_path

    @property
    def destination_path(self) -> Path | None:
        """Return the requested final path for path-based output."""
        return self._destination

    @property
    def sample_count(self) -> int:
        """Return the number of successfully written samples."""
        return self._sample_count

    def write_sample(self, sample: FDRSample) -> None:
        """Append one sample matching the header's declared DataRef width."""
        self._require_active()
        try:
            line = _render_sample(sample, len(self._header.datarefs))
            self._write_text(line)
        except BaseException as primary:
            self._abort_after(primary)
        self._sample_count += 1

    def commit(self) -> None:
        """Synchronize output and publish a path after at least one sample."""
        self._require_active()
        if self._sample_count == 0:
            self._abort_after(FDRRecordingStateError("cannot commit an FDR recording without samples"))

        if self._destination is None:
            try:
                self._stream.flush()
            except BaseException as primary:
                self._abort_after(primary)
            self._state = "committed"
            return

        partial_path = cast(Path, self._partial_path)
        try:
            self._stream.flush()
            os.fsync(self._stream.fileno())
            self._stream.close()
        except BaseException as primary:
            self._abort_after(primary)
        if self._overwrite:
            try:
                os.replace(partial_path, self._destination)
            except BaseException as primary:
                self._abort_after(primary)
            self._state = "committed"
            return
        try:
            os.link(partial_path, self._destination)
        except BaseException as primary:
            self._abort_after(primary)
        self._state = "committed"
        try:
            os.unlink(partial_path)
        except FileNotFoundError:
            return
        except OSError as cleanup:
            raise _published_cleanup_error(cleanup, partial_path)

    def abort(self) -> None:
        """Stop writing while preserving any path partial for diagnosis."""
        if self._state != "active":
            return
        self._state = "aborted"
        try:
            if self._destination is None:
                self._stream.flush()
            else:
                self._stream.close()
        except OSError as error:
            raise _wrapped_output_error(error, self._artifact_path())

    def _write_text(self, value: str) -> None:
        try:
            written = self._stream.write(value)
        except OSError as error:
            raise _wrapped_output_error(error, self._artifact_path())
        if written != len(value):
            raise FDROutputError("FDR output stream performed a short write", artifact_path=self._artifact_path())

    def _artifact_path(self) -> Path | None:
        return self._partial_path if self._partial_path is not None else self._destination

    def _require_active(self) -> None:
        if self._state != "active":
            raise FDRRecordingStateError(f"writer is already {self._state}")

    def _abort_after(self, primary: BaseException) -> NoReturn:
        wrapped_primary = _wrapped_output_error(primary, self._artifact_path()) if isinstance(primary, OSError) else primary
        try:
            self.abort()
        except BaseException as cleanup:
            raise BaseExceptionGroup("FDR writer operation and cleanup failed", [wrapped_primary, cleanup]) from None
        raise wrapped_primary.with_traceback(wrapped_primary.__traceback__)

    def __enter__(self) -> FDRStreamWriter:
        """Return this active writer for explicit-commit context use."""
        self._require_active()
        return self

    def __exit__(self, _exc_type: object, exc_value: BaseException | None, _traceback: object) -> None:
        """Abort an uncommitted writer without hiding a body failure."""
        if self._state != "active":
            return
        if exc_value is None:
            self.abort()
            return
        try:
            self.abort()
        except BaseException as cleanup:
            raise BaseExceptionGroup("FDR context body and cleanup failed", [exc_value, cleanup]) from None


class FDRWriter:
    """Write complete or incremental canonical version 4 recordings."""

    def open(
        self,
        header: FDRHeader,
        destination: str | os.PathLike[str] | TextIO,
        *,
        overwrite: bool = False,
    ) -> FDRStreamWriter:
        """Open a stream writer for a path or caller-owned text stream."""
        header_text = _render_header(header)
        if isinstance(destination, (str, os.PathLike)):
            path = Path(cast(str | os.PathLike[str], destination))
            try:
                partial_path, stream = _create_partial(path)
            except OSError as error:
                raise _wrapped_output_error(error, path)
            return FDRStreamWriter(
                header,
                stream,
                destination=path,
                partial_path=partial_path,
                overwrite=overwrite,
                header_text=header_text,
            )
        return FDRStreamWriter(
            header,
            cast(TextIO, destination),
            destination=None,
            partial_path=None,
            overwrite=overwrite,
            header_text=header_text,
        )

    def write(
        self,
        recording: FDRRecording,
        destination: str | os.PathLike[str] | TextIO,
        *,
        overwrite: bool = False,
        allow_lossy_legacy: bool = False,
    ) -> FDRNormalizationResult:
        """Write a complete recording and report any omitted legacy fields."""
        if not isinstance(recording, FDRRecording):
            raise FDRValidationError("recording must be an FDRRecording")
        result = recording.normalized_v4(allow_lossy_legacy=allow_lossy_legacy)
        with self.open(result.recording.header, destination, overwrite=overwrite) as stream_writer:
            for sample in result.recording.samples:
                stream_writer.write_sample(sample)
            stream_writer.commit()
        return result
