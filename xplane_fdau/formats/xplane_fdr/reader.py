"""Incremental parser for X-Plane Flight Data Recorder text."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
import math
import os
from pathlib import Path
import re
from typing import Callable, NoReturn, override, Protocol, TypeVar, cast

from .errors import FDRParseError, FDRValidationError
from .models import FDRDataref, FDRHeader, FDRLegacyColumn, FDRMetadata, FDRRecording, FDRSample


_VERSION_PATTERN = re.compile(r"^([0-9]+)(?:\s+.*)?$")
_METADATA_PATTERN = re.compile(r"^[A-Z0-9]{4}$")
_TIMESTAMP_PATTERN = re.compile(r"^[0-9]{1,2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?$")
_INTEGER_PATTERN = re.compile(r"^[+-]?[0-9]+$")
_NUMBER_PATTERN = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
_NONFINITE_PATTERN = re.compile(r"^[+-]?(?:inf(?:inity)?|nan)$", re.IGNORECASE)
_DATE_FORMATS = (
    (re.compile(r"^[0-9]{2}/[0-9]{2}/[0-9]{4}$"), "%m/%d/%Y"),
    (re.compile(r"^[0-9]{2}/[0-9]{2}/[0-9]{2}$"), "%m/%d/%y"),
    (re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"), "%Y-%m-%d"),
)
_READ_SIZE = 8192
_T = TypeVar("_T")

_VERSION_3_SOURCE_LABELS = (
    "time",
    "Longitude",
    "Latitude",
    "Altitude",
    "HDG",
    "Pitch",
    "Roll",
    "BaroA",
    "AltMSL",
    "VSpd",
    "TAS",
    "IAS",
    "GndSpd",
    "Stall Warning",
    "flap",
    "flap",
    "OAT",
    "wind",
    "wind speed",
    "FQtyL",
    "FQtyR",
    "volt1",
    "amp1",
    "OilP",
    "OilT",
    "Eng1 Percent Power",
    "RPM",
    "MAP",
    "FFlow",
    "CHT-1",
    "CHT-2",
    "CHT-3",
    "CHT-4",
    "CHT-5",
    "CHT-6",
    "EGT-1",
    "EGT-2",
    "EGT-3",
    "EGT-4",
    "EGT-5",
    "EGT-6",
)
_VERSION_3_DUPLICATE_FIELD_IDS = {14: "flap[0]", 15: "flap[1]"}
_VERSION_3_LEGACY_COLUMNS = tuple(
    FDRLegacyColumn(_VERSION_3_DUPLICATE_FIELD_IDS.get(index, label), comment=label) for index, label in enumerate(_VERSION_3_SOURCE_LABELS)
)


@dataclass(slots=True)
class _HeaderState:
    """Mutable accumulator used while parsing a native FDR header."""

    comments: list[str] = field(default_factory=list)
    metadata: list[FDRMetadata] = field(default_factory=list)
    datarefs: list[FDRDataref] = field(default_factory=list)
    local_date: date | None = None
    last_line: int = 0


class _ReadableText(Protocol):
    """Minimal caller text-stream contract used by the reader."""

    def read(self, size: int = -1, /) -> str: ...

    def close(self) -> None: ...


class _NormalizedLines(Iterator[tuple[int, str]]):
    """Yield logical lines from bounded reads with universal newlines."""

    def __init__(self, source: _ReadableText) -> None:
        self._source = source
        self._buffer = ""
        self._eof = False
        self.line_number = 0

    @override
    def __iter__(self) -> _NormalizedLines:
        return self

    @override
    def __next__(self) -> tuple[int, str]:
        while True:
            for index, character in enumerate(self._buffer):
                if character not in "\r\n":
                    continue
                if character == "\r" and index + 1 == len(self._buffer) and not self._eof:
                    break
                separator_width = 2 if character == "\r" and self._buffer[index + 1 : index + 2] == "\n" else 1
                line, self._buffer = self._buffer[:index], self._buffer[index + separator_width :]
                self.line_number += 1
                return self.line_number, line
            if self._eof:
                if not self._buffer:
                    raise StopIteration
                line, self._buffer = self._buffer, ""
                self.line_number += 1
                return self.line_number, line
            chunk = self._source.read(_READ_SIZE)
            if not isinstance(chunk, str):
                raise TypeError("FDR source must be a text stream")
            if chunk:
                self._buffer += chunk
            else:
                self._eof = True


class FDRSampleStream(Iterator[FDRSample]):
    """Context-managed lazy samples with an eagerly parsed header."""

    def __init__(self, source: _ReadableText, *, source_name: str, owned: bool) -> None:
        self._source = source
        self._source_name = source_name
        self._owned = owned
        self._lines = _NormalizedLines(source)
        self._first_sample: tuple[int, str] | None = None
        self._v3_start_time: time | None = None
        self._v3_previous_elapsed: int | float | None = None
        self._closed = False
        self.header = self._parse_header()

    def __enter__(self) -> FDRSampleStream:
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        self.close()

    @override
    def __iter__(self) -> FDRSampleStream:
        return self

    @override
    def __next__(self) -> FDRSample:
        if self._closed:
            raise StopIteration
        try:
            return self._next_sample()
        except BaseException:
            self.close()
            raise

    def _next_sample(self) -> FDRSample:
        if self._first_sample is not None:
            line, text = self._first_sample
            self._first_sample = None
            return self._parse_sample(text, line)
        for line, text in self._lines:
            stripped = text.strip()
            if not stripped:
                continue
            kind = stripped.partition(",")[0].strip()
            if self.header.source_version == 3 and kind == "DATA":
                return self._parse_sample(stripped, line)
            if kind in {"COMM", "DREF"} or _METADATA_PATTERN.fullmatch(kind):
                self._parse_error(line, "header record after samples began")
            return self._parse_sample(stripped, line)
        raise StopIteration

    def close(self) -> None:
        """Close a path-owned source while leaving caller streams open."""
        if not self._closed and self._owned:
            self._source.close()
        self._closed = True

    def _parse_header(self) -> FDRHeader:
        origin = self._parse_origin()
        version_line, version = self._parse_version()
        state = _HeaderState(last_line=version_line)
        self._collect_header(version, origin, state)
        return self._build_header(version, origin, state)

    def _parse_origin(self) -> str:
        line, text = self._next_nonblank("missing origin marker")
        origin = text.strip()
        if origin not in {"A", "I"}:
            self._parse_error(line, "origin marker must be 'A' or 'I'")
        return origin

    def _parse_version(self) -> tuple[int, int]:
        line, text = self._next_nonblank("missing version line")
        match = _VERSION_PATTERN.fullmatch(text.strip())
        if match is None:
            self._parse_error(line, "version line must begin with an integer and optional suffix text")
        version = int(match.group(1))
        if version not in {3, 4}:
            self._parse_error(line, "reader supports versions 3 and 4 only")
        return line, version

    def _collect_header(self, version: int, origin: str, state: _HeaderState) -> None:
        for line, text in self._lines:
            stripped = text.strip()
            if not stripped:
                continue
            kind, separator, payload = stripped.partition(",")
            kind = kind.strip()
            if (version == 3 and kind == "DATA") or (version == 4 and ":" in kind):
                self._first_sample = (line, stripped)
                return
            if not separator:
                self._parse_error(line, "header record requires a comma")
            state.last_line = line
            self._append_header_record(version, origin, state, line, kind, payload.strip())

    def _append_header_record(self, version: int, origin: str, state: _HeaderState, line: int, kind: str, payload: str) -> None:
        if kind == "COMM":
            state.comments.append(payload)
            return
        if kind == "DREF" and version == 4:
            dataref = self._parse_dataref(payload, line)
            self._validate_dataref_append(origin, state.comments, state.metadata, state.datarefs, dataref, state.local_date, line)
            state.datarefs.append(dataref)
            return
        if _METADATA_PATTERN.fullmatch(kind):
            state.metadata.append(self._validated(FDRMetadata, line, kind, payload))
            if kind == "DATE":
                state.local_date = self._parse_date(payload, line)
            elif kind == "TIME" and version == 3:
                self._v3_start_time = self._parse_time(payload, line, name="TIME")
            return
        self._parse_error(line, "metadata key must be four-character uppercase text")

    def _build_header(self, version: int, origin: str, state: _HeaderState) -> FDRHeader:
        if version == 3 and self._v3_start_time is None:
            required_line = self._first_sample[0] if self._first_sample is not None else state.last_line
            self._parse_error(required_line, "version 3 requires a valid TIME header")
        return self._validated(
            FDRHeader,
            state.last_line,
            source_version=version,
            source_origin=origin,
            comments=tuple(state.comments),
            metadata=tuple(state.metadata),
            datarefs=tuple(state.datarefs) if version == 4 else (),
            legacy_columns=_VERSION_3_LEGACY_COLUMNS if version == 3 else (),
            local_date=state.local_date,
        )

    def _next_nonblank(self, missing_message: str) -> tuple[int, str]:
        for line, text in self._lines:
            if text.strip():
                return line, text
        self._parse_error(max(1, self._lines.line_number + 1), missing_message)

    def _parse_dataref(self, payload: str, line: int) -> FDRDataref:
        declaration, comment_marker, comment = payload.partition("//")
        fields = declaration.split()
        if len(fields) != 2:
            self._parse_error(line, "DataRef declaration requires a path and scale")
        scale = self._parse_number(fields[1], line, "DataRef scale")
        return self._validated(FDRDataref, line, fields[0], scale, comment.strip() if comment_marker else None)

    def _validate_dataref_append(
        self,
        origin: str,
        comments: list[str],
        metadata: list[FDRMetadata],
        datarefs: list[FDRDataref],
        dataref: FDRDataref,
        local_date: date | None,
        line: int,
    ) -> None:
        self._validated(
            FDRHeader,
            line,
            source_version=4,
            source_origin=origin,
            comments=tuple(comments),
            metadata=tuple(metadata),
            datarefs=tuple((*datarefs, dataref)),
            legacy_columns=(),
            local_date=local_date,
        )

    def _parse_date(self, value: str, line: int) -> date:
        for pattern, date_format in _DATE_FORMATS:
            if pattern.fullmatch(value) is None:
                continue
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                continue
        self._parse_error(line, "DATE must be MM/DD/YYYY, MM/DD/YY, or YYYY-MM-DD")

    def _parse_sample(self, text: str, line: int) -> FDRSample:
        if self.header.source_version == 3:
            return self._parse_v3_sample(text, line)
        return self._parse_v4_sample(text, line)

    def _parse_v4_sample(self, text: str, line: int) -> FDRSample:
        fields = tuple(field.strip() for field in text.split(","))
        expected = 7 + len(self.header.datarefs)
        if len(fields) != expected:
            self._parse_error(line, f"sample requires exactly {expected} columns")
        time_utc = self._parse_time(fields[0], line, name="UTC time")
        numbers = tuple(self._parse_number(value, line, "sample number") for value in fields[1:])
        return self._validated(
            FDRSample,
            line,
            time_utc=time_utc,
            longitude=numbers[0],
            latitude=numbers[1],
            altitude_msl_ft=numbers[2],
            heading_magnetic_deg=numbers[3],
            pitch_deg=numbers[4],
            roll_deg=numbers[5],
            additional_values=numbers[6:],
            legacy_values=(),
        )

    def _parse_v3_sample(self, text: str, line: int) -> FDRSample:
        fields = tuple(field.strip() for field in text.split(","))
        if not fields or fields[0] != "DATA":
            self._parse_error(line, "version 3 sample must begin with DATA")
        values = fields[1:]
        if len(values) != len(_VERSION_3_LEGACY_COLUMNS):
            self._parse_error(line, "version 3 DATA requires exactly 41 values")
        numbers = tuple(self._parse_number(value, line, "sample number") for value in values)
        elapsed = numbers[0]
        if elapsed < 0 or (type(elapsed) is float and not math.isfinite(elapsed)):
            raise FDRValidationError("elapsed seconds must be finite and non-negative", source=self._source_name, line=line)
        if self._v3_previous_elapsed is not None and elapsed < self._v3_previous_elapsed:
            raise FDRValidationError("elapsed seconds must be non-decreasing", source=self._source_name, line=line)
        if self._v3_start_time is None:  # pragma: no cover - protected by eager header parsing
            self._parse_error(line, "version 3 requires a valid TIME header")
        try:
            resolved = datetime.combine(date.min, self._v3_start_time) + timedelta(seconds=elapsed)
        except OverflowError as error:
            raise FDRValidationError("elapsed seconds are out of range", source=self._source_name, line=line) from error
        sample = self._validated(
            FDRSample,
            line,
            time_utc=resolved.time(),
            longitude=numbers[1],
            latitude=numbers[2],
            altitude_msl_ft=numbers[3],
            heading_magnetic_deg=numbers[4],
            pitch_deg=numbers[5],
            roll_deg=numbers[6],
            additional_values=(),
            legacy_values=numbers,
        )
        self._v3_previous_elapsed = elapsed
        return sample

    def _parse_time(self, value: str, line: int, *, name: str) -> time:
        if _TIMESTAMP_PATTERN.fullmatch(value) is None:
            self._parse_error(line, f"invalid {name}")
        hour, remainder = value.split(":", 1)
        try:
            return time.fromisoformat(f"{hour.zfill(2)}:{remainder}")
        except ValueError:
            self._parse_error(line, f"invalid {name}")

    def _parse_number(self, value: str, line: int, name: str) -> int | float:
        if _NUMBER_PATTERN.fullmatch(value) is None and _NONFINITE_PATTERN.fullmatch(value) is None:
            self._parse_error(line, f"invalid {name.lower()}")
        try:
            return int(value) if _INTEGER_PATTERN.fullmatch(value) is not None else float(value)
        except ValueError:
            self._parse_error(line, f"invalid {name.lower()}")

    def _validated(self, factory: Callable[..., _T], line: int, *args: object, **kwargs: object) -> _T:
        try:
            return factory(*args, **kwargs)
        except FDRValidationError as error:
            raise FDRValidationError(error.message, source=self._source_name, line=line) from error

    def _parse_error(self, line: int, message: str) -> NoReturn:
        raise FDRParseError(message, source=self._source_name, line=line)


class FDRReader:
    """Read version 3 or 4 FDR paths and caller-owned text streams."""

    def open(self, source: str | os.PathLike[str] | _ReadableText) -> FDRSampleStream:
        """Open a lazy sample stream and parse its header."""
        stream: _ReadableText
        source_name: str
        if isinstance(source, (str, os.PathLike)):
            path = Path(cast(str | os.PathLike[str], source))
            stream = path.open("r", encoding="utf-8", newline=None)
            source_name = str(path)
            owned = True
        else:
            stream = cast(_ReadableText, source)
            name = getattr(source, "name", None)
            source_name = name if isinstance(name, str) else "<stream>"
            owned = False
        try:
            return FDRSampleStream(stream, source_name=source_name, owned=owned)
        except BaseException:
            if owned:
                stream.close()
            raise

    def read(self, source: str | os.PathLike[str] | _ReadableText) -> FDRRecording:
        """Consume one source into a validated immutable recording."""
        with self.open(source) as stream:
            return FDRRecording(stream.header, tuple(stream))
