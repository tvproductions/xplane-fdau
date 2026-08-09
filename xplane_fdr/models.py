"""Immutable, validated Flight Data Recorder model types."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta
import math
import re
from typing import Literal

from .errors import FDRValidationError


_DATE_FORMATS = (
    (re.compile(r"^[0-9]{2}/[0-9]{2}/[0-9]{4}$"), "%m/%d/%Y"),
    (re.compile(r"^[0-9]{2}/[0-9]{2}/[0-9]{2}$"), "%m/%d/%y"),
    (re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"), "%Y-%m-%d"),
)


def _tuple[T](values: tuple[T, ...] | list[T], name: str) -> tuple[T, ...]:
    """Freeze a caller-provided sequence without changing its order."""
    if type(values) not in (tuple, list):
        raise FDRValidationError(f"{name} must be a tuple or list")
    return tuple(values)


def _require_text(value: object, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise FDRValidationError(f"{name} must be a non-empty string")
    return value


def _require_finite_number(value: object, name: str) -> int | float:
    if type(value) is int:
        return value
    if type(value) is not float or not math.isfinite(value):
        raise FDRValidationError(f"{name} must be a finite int or float")
    return value


def _validate_values(values: tuple[object, ...], name: str) -> tuple[int | float, ...]:
    return tuple(_require_finite_number(value, f"{name}[{index}]") for index, value in enumerate(values))


def _parse_local_date(value: str) -> date:
    for pattern, date_format in _DATE_FORMATS:
        if pattern.fullmatch(value) is None:
            continue
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            break
    raise FDRValidationError("DATE must be MM/DD/YYYY, MM/DD/YY, or YYYY-MM-DD")


@dataclass(frozen=True, slots=True)
class FDRMetadata:
    """An ordered FDR metadata entry."""

    key: str
    value: str

    def __post_init__(self) -> None:
        _require_text(self.key, "metadata key")
        _require_text(self.value, "metadata value", allow_empty=True)


def _resolve_local_date(metadata: tuple[FDRMetadata, ...], local_date: object) -> date | None:
    if local_date is not None and type(local_date) is not date:
        raise FDRValidationError("local date must be a date or None")
    declared_dates = tuple(_parse_local_date(item.value) for item in metadata if item.key == "DATE")
    if not declared_dates:
        if local_date is not None:
            raise FDRValidationError("local date requires effective DATE metadata")
        return None
    if local_date is None:
        return declared_dates[-1]
    if local_date != declared_dates[-1]:
        raise FDRValidationError("local date must match effective DATE metadata")
    return local_date


@dataclass(frozen=True, slots=True)
class FDRDataref:
    """An optional FDR DataRef declaration."""

    path: str
    scale: int | float
    comment: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.path, "DataRef path")
        _require_finite_number(self.scale, "DataRef scale")
        if self.comment is not None:
            _require_text(self.comment, "DataRef comment", allow_empty=True)


@dataclass(frozen=True, slots=True)
class FDRLegacyColumn:
    """A named position in a version 3 legacy fixed-width row."""

    identifier: str
    comment: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.identifier, "legacy column identifier")
        if self.comment is not None:
            _require_text(self.comment, "legacy column comment", allow_empty=True)

    @property
    def field_id(self) -> str:
        """Return the stable identifier used in normalization omissions."""
        return self.identifier


def _validate_header_schema(
    source_version: Literal[3, 4],
    datarefs: tuple[object, ...],
    legacy_columns: tuple[object, ...],
) -> None:
    if source_version == 3 and datarefs:
        raise FDRValidationError("version 3 headers must not declare DataRefs")
    if source_version == 4 and legacy_columns:
        raise FDRValidationError("version 4 headers must not declare legacy columns")


@dataclass(frozen=True, slots=True)
class FDRHeader:
    """The ordered header declarations shared by an FDR recording."""

    source_version: Literal[3, 4]
    source_origin: Literal["A", "I"]
    comments: tuple[str, ...]
    metadata: tuple[FDRMetadata, ...]
    datarefs: tuple[FDRDataref, ...]
    legacy_columns: tuple[FDRLegacyColumn, ...]
    local_date: date | None

    def __post_init__(self) -> None:
        if type(self.source_version) is not int or self.source_version not in {3, 4}:
            raise FDRValidationError("source version must be 3 or 4")
        if type(self.source_origin) is not str or self.source_origin not in {"A", "I"}:
            raise FDRValidationError("source origin must be 'A' or 'I'")
        comments = _tuple(self.comments, "comments")
        metadata = _tuple(self.metadata, "metadata")
        datarefs = _tuple(self.datarefs, "datarefs")
        legacy_columns = _tuple(self.legacy_columns, "legacy columns")
        if any(not isinstance(comment, str) for comment in comments):
            raise FDRValidationError("comments must contain only strings")
        if any(not isinstance(item, FDRMetadata) for item in metadata):
            raise FDRValidationError("metadata must contain FDRMetadata entries")
        if any(not isinstance(item, FDRDataref) for item in datarefs):
            raise FDRValidationError("datarefs must contain FDRDataref entries")
        if any(not isinstance(item, FDRLegacyColumn) for item in legacy_columns):
            raise FDRValidationError("legacy columns must contain FDRLegacyColumn entries")
        if len({item.path for item in datarefs}) != len(datarefs):
            raise FDRValidationError("DataRef paths must be unique")
        if len({item.identifier for item in legacy_columns}) != len(legacy_columns):
            raise FDRValidationError("legacy column identifiers must be unique")
        _validate_header_schema(self.source_version, datarefs, legacy_columns)
        object.__setattr__(
            self,
            "local_date",
            _resolve_local_date(metadata, self.local_date),
        )
        object.__setattr__(self, "comments", comments)
        object.__setattr__(self, "metadata", metadata)
        object.__setattr__(self, "datarefs", datarefs)
        object.__setattr__(self, "legacy_columns", legacy_columns)

    def metadata_value(self, key: str) -> str | None:
        """Return the effective last value for an ordered metadata key."""
        _require_text(key, "metadata key")
        for metadata in reversed(self.metadata):
            if metadata.key == key:
                return metadata.value
        return None


@dataclass(frozen=True, slots=True)
class FDRSample:
    """One timestamped position and attitude sample."""

    time_utc: time
    longitude: int | float
    latitude: int | float
    altitude_msl_ft: int | float
    heading_magnetic_deg: int | float
    pitch_deg: int | float
    roll_deg: int | float
    additional_values: tuple[int | float, ...]
    legacy_values: tuple[int | float, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.time_utc, time) or self.time_utc.tzinfo is not None:
            raise FDRValidationError("time_utc must be an unzoned time")
        longitude = _require_finite_number(self.longitude, "longitude")
        latitude = _require_finite_number(self.latitude, "latitude")
        if not -180 <= longitude <= 180:
            raise FDRValidationError("longitude must be between -180 and 180")
        if not -90 <= latitude <= 90:
            raise FDRValidationError("latitude must be between -90 and 90")
        object.__setattr__(self, "longitude", longitude)
        object.__setattr__(self, "latitude", latitude)
        for name in ("altitude_msl_ft", "heading_magnetic_deg", "pitch_deg", "roll_deg"):
            object.__setattr__(self, name, _require_finite_number(getattr(self, name), name))
        object.__setattr__(
            self,
            "additional_values",
            _validate_values(_tuple(self.additional_values, "additional values"), "additional values"),
        )
        object.__setattr__(
            self,
            "legacy_values",
            _validate_values(_tuple(self.legacy_values, "legacy values"), "legacy values"),
        )


@dataclass(frozen=True, slots=True)
class FDRRecording:
    """A fully validated, ordered FDR recording."""

    header: FDRHeader
    samples: tuple[FDRSample, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.header, FDRHeader):
            raise FDRValidationError("header must be an FDRHeader")
        samples = _tuple(self.samples, "samples")
        if any(not isinstance(sample, FDRSample) for sample in samples):
            raise FDRValidationError("samples must contain FDRSample entries")
        for index, sample in enumerate(samples):
            if len(sample.additional_values) != len(self.header.datarefs):
                raise FDRValidationError(f"sample {index} additional values do not match declared DataRefs")
            if len(sample.legacy_values) != len(self.header.legacy_columns):
                raise FDRValidationError(f"sample {index} legacy values do not match declared legacy columns")
        object.__setattr__(self, "samples", samples)

    @property
    def duration(self) -> timedelta:
        """Return elapsed time, treating each backward clock move as midnight."""
        resolved = self._resolved_datetimes(date.min)
        return resolved[-1] - resolved[0] if resolved else timedelta()

    def resolved_utc_datetimes(self, first_utc_date: date) -> tuple[datetime, ...]:
        """Resolve time-only samples against the caller's explicit first UTC date."""
        if type(first_utc_date) is not date:
            raise FDRValidationError("first_utc_date must be a date")
        return self._resolved_datetimes(first_utc_date)

    def _resolved_datetimes(self, first_utc_date: date) -> tuple[datetime, ...]:
        resolved: list[datetime] = []
        current_date = first_utc_date
        previous_time: time | None = None
        for sample in self.samples:
            if previous_time is not None and sample.time_utc < previous_time:
                current_date += timedelta(days=1)
            resolved.append(datetime.combine(current_date, sample.time_utc, tzinfo=UTC))
            previous_time = sample.time_utc
        return tuple(resolved)

    def normalized_v4(self, *, allow_lossy_legacy: bool = False) -> FDRNormalizationResult:
        """Return v4 data, requiring an explicit opt-in to omit legacy columns."""
        omitted = tuple(column.identifier for column in self.header.legacy_columns)
        if self.header.source_version == 3 and not allow_lossy_legacy:
            raise FDRValidationError("version 3 normalization requires allow_lossy_legacy=True")
        if not omitted and self.header.source_version == 4:
            return FDRNormalizationResult(self, ())
        normalized_header = replace(self.header, source_version=4, legacy_columns=())
        normalized_samples = tuple(replace(sample, legacy_values=()) for sample in self.samples)
        return FDRNormalizationResult(FDRRecording(normalized_header, normalized_samples), omitted)


@dataclass(frozen=True, slots=True)
class FDRNormalizationResult:
    """A canonical v4 recording and any legacy field identifiers omitted from it."""

    recording: FDRRecording
    omitted_legacy_field_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.recording, FDRRecording):
            raise FDRValidationError("recording must be an FDRRecording")
        if self.recording.header.source_version != 4:
            raise FDRValidationError("normalization results must contain a version 4 recording")
        omitted = _tuple(self.omitted_legacy_field_ids, "omitted legacy field ids")
        if any(not isinstance(identifier, str) for identifier in omitted):
            raise FDRValidationError("omitted legacy field ids must contain only strings")
        object.__setattr__(self, "omitted_legacy_field_ids", omitted)
