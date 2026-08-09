"""Strict adapter-neutral JSON configuration for FDR recording."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import json
import math
import os
from pathlib import Path, PureWindowsPath
from typing import Literal, NoReturn, Protocol, cast

from .errors import FDRConfigError
from .models import FDRDataref, FDRHeader, FDRMetadata
from .profiles import compose_profiles, list_profiles
from .recording import FDRRecordingDefinition, FDRSamplingPolicy, FDRStoragePolicy


_DEFAULT_STORAGE_DIRECTORY = Path("Output/FDR files")
_ROOT_PROPERTIES = frozenset({"$schema", "schema_version", "profiles", "sampling", "metadata", "datarefs", "storage"})
_SAMPLING_PROPERTIES = frozenset({"interval_seconds", "duration_seconds"})
_METADATA_PROPERTIES = frozenset(
    {
        "aircraft_path",
        "tail_number",
        "local_date",
        "pressure_in_hg",
        "isa_offset_c",
        "wind_direction_deg",
        "wind_speed_kt",
        "comments",
    }
)
_DATAREF_PROPERTIES = frozenset({"path", "scale", "comment"})
_STORAGE_PROPERTIES = frozenset({"directory", "filename"})
_PROFILE_NAMES = frozenset(profile.name for profile in list_profiles())


class _ReadableText(Protocol):
    """Structural type accepted by :func:`json.load`."""

    def read(self, size: int = -1, /) -> str: ...


class _JSONObject(list[tuple[str, object]]):
    """Object-pairs marker retaining duplicate JSON properties."""


class _LocatedConfigError(FDRConfigError):
    """Configuration error carrying source and optional JSON syntax location."""

    def __init__(
        self,
        message: str,
        *,
        source: str,
        property_path: str | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        self.source = source
        self.line = line
        self.column = column
        super().__init__(message, property_path=property_path)
        if line is not None:
            location = f"{source}:{line}"
            if column is not None:
                location += f":{column}"
            ValueError.__init__(self, f"{location}: {message}")
        else:
            ValueError.__init__(self, f"{source}: {self}")


def _config_error(
    message: str,
    *,
    source: str,
    property_path: str | None = None,
    line: int | None = None,
    column: int | None = None,
) -> NoReturn:
    raise _LocatedConfigError(
        message,
        source=source,
        property_path=property_path,
        line=line,
        column=column,
    )


def _property_path(parent: str, name: str) -> str:
    return f"{parent}.{name}"


def _convert_json_tree(value: object, path: str, source: str) -> object:
    if isinstance(value, _JSONObject):
        result: dict[str, object] = {}
        for key, child in value:
            child_path = _property_path(path, key)
            if key in result:
                _config_error("duplicate property", source=source, property_path=child_path)
            result[key] = _convert_json_tree(child, child_path, source)
        return result
    if isinstance(value, list):
        return [_convert_json_tree(child, f"{path}[{index}]", source) for index, child in enumerate(value)]
    return value


def _source_name(path_or_stream: str | os.PathLike[str] | _ReadableText) -> str:
    if isinstance(path_or_stream, (str, os.PathLike)):
        return os.fspath(path_or_stream)
    return str(getattr(path_or_stream, "name", "<stream>"))


def _load_json(stream: _ReadableText, source: str) -> object:
    try:
        value = json.load(stream, object_pairs_hook=_JSONObject)
    except json.JSONDecodeError as error:
        _config_error(error.msg, source=source, line=error.lineno, column=error.colno)
    return _convert_json_tree(value, "$", source)


def _require_object(value: object, path: str, source: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _config_error("must be an object", source=source, property_path=path)
    return cast(dict[str, object], value)


def _reject_unknown(value: dict[str, object], allowed: frozenset[str], path: str, source: str) -> None:
    for name in value:
        if name not in allowed:
            _config_error("unknown property", source=source, property_path=_property_path(path, name))


def _require_array(value: object, path: str, source: str) -> list[object]:
    if not isinstance(value, list):
        _config_error("must be an array", source=source, property_path=path)
    return value


def _require_string(
    value: object,
    path: str,
    source: str,
    *,
    allow_empty: bool = True,
    single_line: bool = False,
) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        qualifier = "non-empty " if not allow_empty else ""
        _config_error(f"must be a {qualifier}string", source=source, property_path=path)
    if "\x00" in value:
        _config_error("must not contain NUL", source=source, property_path=path)
    if single_line and ("\r" in value or "\n" in value):
        _config_error("must be a single-line string", source=source, property_path=path)
    return value


def _require_number(
    value: object,
    path: str,
    source: str,
    *,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
    exclusive_minimum: bool = False,
) -> int | float:
    if type(value) not in (int, float):
        _config_error("must be a finite number", source=source, property_path=path)
    number = cast(int | float, value)
    if not math.isfinite(number):
        _config_error("must be a finite number", source=source, property_path=path)
    if minimum is not None and (number < minimum or (exclusive_minimum and number == minimum)):
        comparison = "greater than" if exclusive_minimum else "at least"
        _config_error(f"must be {comparison} {minimum}", source=source, property_path=path)
    if maximum is not None and number > maximum:
        _config_error(f"must be at most {maximum}", source=source, property_path=path)
    return number


def _optional_string(
    value: dict[str, object],
    name: str,
    path: str,
    source: str,
    *,
    allow_empty: bool = False,
) -> str | None:
    if name not in value:
        return None
    return _require_string(
        value[name],
        _property_path(path, name),
        source,
        allow_empty=allow_empty,
        single_line=True,
    )


def _optional_number(
    value: dict[str, object],
    name: str,
    path: str,
    source: str,
    *,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
) -> int | float | None:
    if name not in value:
        return None
    return _require_number(value[name], _property_path(path, name), source, minimum=minimum, maximum=maximum)


def _programmatic_error(message: str, property_path: str) -> NoReturn:
    raise FDRConfigError(message, property_path=property_path)


def _validate_programmatic_text(
    value: object,
    property_path: str,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, str) or (not allow_empty and not value):
        _programmatic_error("must be a string", property_path)
    if "\x00" in value or "\r" in value or "\n" in value:
        _programmatic_error("must be a single-line string without NUL", property_path)


def _validate_programmatic_number(
    value: object,
    property_path: str,
    *,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
) -> None:
    if type(value) not in (int, float):
        _programmatic_error("must be a finite number", property_path)
    number = cast(int | float, value)
    if not math.isfinite(number):
        _programmatic_error("must be a finite number", property_path)
    if minimum is not None and number < minimum:
        _programmatic_error(f"must be at least {minimum}", property_path)
    if maximum is not None and number > maximum:
        _programmatic_error(f"must be at most {maximum}", property_path)


@dataclass(frozen=True, slots=True)
class FDRMetadataConfig:
    """Optional typed metadata used to construct an FDR v4 header."""

    aircraft_path: str | None = None
    tail_number: str | None = None
    local_date: date | None = None
    pressure_in_hg: int | float | None = None
    isa_offset_c: int | float | None = None
    wind_direction_deg: int | float | None = None
    wind_speed_kt: int | float | None = None
    comments: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("aircraft_path", "tail_number"):
            value = getattr(self, name)
            if value is not None:
                _validate_programmatic_text(value, f"$.metadata.{name}")
        if self.local_date is not None and type(self.local_date) is not date:
            _programmatic_error("must be a date", "$.metadata.local_date")
        for name in ("pressure_in_hg", "isa_offset_c"):
            value = getattr(self, name)
            if value is not None:
                _validate_programmatic_number(value, f"$.metadata.{name}")
        if self.wind_direction_deg is not None:
            _validate_programmatic_number(self.wind_direction_deg, "$.metadata.wind_direction_deg", minimum=0, maximum=360)
        if self.wind_speed_kt is not None:
            _validate_programmatic_number(self.wind_speed_kt, "$.metadata.wind_speed_kt", minimum=0)
        if type(self.comments) is not tuple:
            _programmatic_error("must be a tuple", "$.metadata.comments")
        for index, comment in enumerate(self.comments):
            _validate_programmatic_text(comment, f"$.metadata.comments[{index}]", allow_empty=True)


@dataclass(frozen=True, slots=True)
class FDRDatarefConfig:
    """One ordered custom DataRef with optional override properties."""

    path: str
    scale: int | float | None = None
    comment: str | None = None

    def __post_init__(self) -> None:
        _validate_programmatic_text(self.path, "$.datarefs[].path")
        if self.scale is not None:
            _validate_programmatic_number(self.scale, "$.datarefs[].scale")
        if self.comment is not None:
            _validate_programmatic_text(self.comment, "$.datarefs[].comment", allow_empty=True)


@dataclass(frozen=True, slots=True)
class FDRRecordConfig:
    """Immutable semantic representation of version 1 recording JSON."""

    schema_version: Literal[1]
    profiles: tuple[str, ...] = ("standard",)
    sampling: FDRSamplingPolicy = field(default_factory=FDRSamplingPolicy)
    metadata: FDRMetadataConfig = field(default_factory=FDRMetadataConfig)
    datarefs: tuple[FDRDatarefConfig, ...] = ()
    storage: FDRStoragePolicy = field(default_factory=FDRStoragePolicy)

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            _programmatic_error("must be the integer 1", "$.schema_version")
        if type(self.profiles) is not tuple:
            _programmatic_error("must be a tuple", "$.profiles")
        for index, profile in enumerate(self.profiles):
            if not isinstance(profile, str) or profile not in _PROFILE_NAMES:
                _programmatic_error("must name a built-in profile", f"$.profiles[{index}]")
        if not isinstance(self.sampling, FDRSamplingPolicy):
            _programmatic_error("must be an FDRSamplingPolicy", "$.sampling")
        if not isinstance(self.metadata, FDRMetadataConfig):
            _programmatic_error("must be an FDRMetadataConfig", "$.metadata")
        if type(self.datarefs) is not tuple:
            _programmatic_error("must be a tuple", "$.datarefs")
        seen: set[str] = set()
        for index, dataref in enumerate(self.datarefs):
            if not isinstance(dataref, FDRDatarefConfig):
                _programmatic_error("must be an FDRDatarefConfig", f"$.datarefs[{index}]")
            if dataref.path in seen:
                _programmatic_error("duplicate DataRef path", f"$.datarefs[{index}].path")
            seen.add(dataref.path)
        if not isinstance(self.storage, FDRStoragePolicy):
            _programmatic_error("must be an FDRStoragePolicy", "$.storage")


def _parse_profiles(root: dict[str, object], source: str) -> tuple[str, ...]:
    if "profiles" not in root:
        return ("standard",)
    values = _require_array(root["profiles"], "$.profiles", source)
    profiles: list[str] = []
    for index, value in enumerate(values):
        path = f"$.profiles[{index}]"
        name = _require_string(value, path, source, allow_empty=False)
        if name not in _PROFILE_NAMES:
            _config_error(f'unknown profile "{name}"', source=source, property_path=path)
        profiles.append(name)
    return tuple(profiles)


def _parse_sampling(root: dict[str, object], source: str) -> FDRSamplingPolicy:
    value = _require_object(root.get("sampling", {}), "$.sampling", source)
    _reject_unknown(value, _SAMPLING_PROPERTIES, "$.sampling", source)
    interval = _require_number(value.get("interval_seconds", 0.1), "$.sampling.interval_seconds", source, minimum=0, exclusive_minimum=True)
    duration = None
    if "duration_seconds" in value:
        duration = _require_number(value["duration_seconds"], "$.sampling.duration_seconds", source, minimum=0, exclusive_minimum=True)
    return FDRSamplingPolicy(float(interval), None if duration is None else float(duration))


def _parse_metadata(root: dict[str, object], source: str) -> FDRMetadataConfig:
    value = _require_object(root.get("metadata", {}), "$.metadata", source)
    _reject_unknown(value, _METADATA_PROPERTIES, "$.metadata", source)
    local_date = None
    if "local_date" in value:
        raw_date = _require_string(value["local_date"], "$.metadata.local_date", source, allow_empty=False)
        try:
            local_date = date.fromisoformat(raw_date)
        except ValueError:
            _config_error("must be an ISO YYYY-MM-DD date", source=source, property_path="$.metadata.local_date")
        if raw_date != local_date.isoformat():
            _config_error("must be an ISO YYYY-MM-DD date", source=source, property_path="$.metadata.local_date")

    comments: tuple[str, ...] = ()
    if "comments" in value:
        comment_values = _require_array(value["comments"], "$.metadata.comments", source)
        comments = tuple(_require_string(comment, f"$.metadata.comments[{index}]", source, single_line=True) for index, comment in enumerate(comment_values))
    return FDRMetadataConfig(
        aircraft_path=_optional_string(value, "aircraft_path", "$.metadata", source),
        tail_number=_optional_string(value, "tail_number", "$.metadata", source),
        local_date=local_date,
        pressure_in_hg=_optional_number(value, "pressure_in_hg", "$.metadata", source),
        isa_offset_c=_optional_number(value, "isa_offset_c", "$.metadata", source),
        wind_direction_deg=_optional_number(value, "wind_direction_deg", "$.metadata", source, minimum=0, maximum=360),
        wind_speed_kt=_optional_number(value, "wind_speed_kt", "$.metadata", source, minimum=0),
        comments=comments,
    )


def _parse_datarefs(root: dict[str, object], source: str) -> tuple[FDRDatarefConfig, ...]:
    if "datarefs" not in root:
        return ()
    values = _require_array(root["datarefs"], "$.datarefs", source)
    datarefs: list[FDRDatarefConfig] = []
    seen: set[str] = set()
    for index, entry in enumerate(values):
        item_path = f"$.datarefs[{index}]"
        value = _require_object(entry, item_path, source)
        _reject_unknown(value, _DATAREF_PROPERTIES, item_path, source)
        path_property = f"{item_path}.path"
        if "path" not in value:
            _config_error("is required", source=source, property_path=path_property)
        path = _require_string(value["path"], path_property, source, allow_empty=False, single_line=True)
        if path in seen:
            _config_error("duplicate DataRef path", source=source, property_path=path_property)
        seen.add(path)
        scale = None if "scale" not in value else _require_number(value["scale"], f"{item_path}.scale", source)
        comment = _optional_string(value, "comment", item_path, source, allow_empty=True)
        datarefs.append(FDRDatarefConfig(path, scale, comment))
    return tuple(datarefs)


def _valid_storage_filename(value: str, path: str, source: str) -> str:
    if not value.endswith(".fdr"):
        _config_error("must be a basename ending in .fdr", source=source, property_path=path)
    if "/" in value or "\\" in value or PureWindowsPath(value).drive:
        _config_error("must not contain a drive or directory separator", source=source, property_path=path)
    return value


def _parse_storage(root: dict[str, object], source: str) -> FDRStoragePolicy:
    value = _require_object(root.get("storage", {}), "$.storage", source)
    _reject_unknown(value, _STORAGE_PROPERTIES, "$.storage", source)
    raw_directory = value.get("directory", str(_DEFAULT_STORAGE_DIRECTORY))
    directory = Path(_require_string(raw_directory, "$.storage.directory", source, allow_empty=False))
    filename = None
    if "filename" in value:
        filename = _valid_storage_filename(
            _require_string(value["filename"], "$.storage.filename", source, allow_empty=False, single_line=True),
            "$.storage.filename",
            source,
        )
    return FDRStoragePolicy(directory, filename)


def _parse_config(value: object, source: str) -> FDRRecordConfig:
    root = _require_object(value, "$", source)
    _reject_unknown(root, _ROOT_PROPERTIES, "$", source)
    if "schema_version" not in root:
        _config_error("is required", source=source, property_path="$.schema_version")
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        _config_error("must be the integer 1", source=source, property_path="$.schema_version")
    if "$schema" in root:
        _require_string(root["$schema"], "$.$schema", source)
    return FDRRecordConfig(
        schema_version=1,
        profiles=_parse_profiles(root, source),
        sampling=_parse_sampling(root, source),
        metadata=_parse_metadata(root, source),
        datarefs=_parse_datarefs(root, source),
        storage=_parse_storage(root, source),
    )


def load_record_config(path_or_stream: str | os.PathLike[str] | _ReadableText) -> FDRRecordConfig:
    """Load and strictly validate one UTF-8 JSON recording configuration."""
    source = _source_name(path_or_stream)
    if isinstance(path_or_stream, (str, os.PathLike)):
        try:
            with open(path_or_stream, encoding="utf-8") as stream:
                value = _load_json(stream, source)
        except (OSError, UnicodeError) as error:
            _config_error(str(error), source=source)
    else:
        value = _load_json(path_or_stream, source)
    return _parse_config(value, source)


def _metadata_entries(config: FDRMetadataConfig) -> tuple[FDRMetadata, ...]:
    values: list[tuple[str, str]] = []
    if config.aircraft_path is not None:
        values.append(("ACFT", config.aircraft_path))
    if config.tail_number is not None:
        values.append(("TAIL", config.tail_number))
    if config.local_date is not None:
        values.append(("DATE", config.local_date.isoformat()))
    if config.pressure_in_hg is not None:
        values.append(("PRES", str(config.pressure_in_hg)))
    if config.isa_offset_c is not None:
        values.append(("DISA", str(config.isa_offset_c)))
    if config.wind_direction_deg is not None or config.wind_speed_kt is not None:
        direction = "" if config.wind_direction_deg is None else str(config.wind_direction_deg)
        speed = "" if config.wind_speed_kt is None else str(config.wind_speed_kt)
        values.append(("WIND", f"{direction},{speed}"))
    return tuple(FDRMetadata(key, value) for key, value in values)


def _resolved_datarefs(config: FDRRecordConfig) -> tuple[FDRDataref, ...]:
    resolved = list(compose_profiles(config.profiles))
    positions = {dataref.path: index for index, dataref in enumerate(resolved)}
    for custom in config.datarefs:
        position = positions.get(custom.path)
        if position is None:
            positions[custom.path] = len(resolved)
            resolved.append(FDRDataref(custom.path, 1.0 if custom.scale is None else custom.scale, custom.comment))
            continue
        earlier = resolved[position]
        resolved[position] = FDRDataref(
            custom.path,
            earlier.scale if custom.scale is None else custom.scale,
            earlier.comment if custom.comment is None else custom.comment,
        )
    return tuple(resolved)


def resolve_recording_definition(config: FDRRecordConfig) -> FDRRecordingDefinition:
    """Resolve profiles, custom declarations, metadata, and policies."""
    if not isinstance(config, FDRRecordConfig):
        raise FDRConfigError("config must be an FDRRecordConfig", property_path="$")
    header = FDRHeader(
        source_version=4,
        source_origin="A",
        comments=config.metadata.comments,
        metadata=_metadata_entries(config.metadata),
        datarefs=_resolved_datarefs(config),
        legacy_columns=(),
        local_date=config.metadata.local_date,
    )
    return FDRRecordingDefinition(header, config.sampling, config.storage)
