"""Thin offline commands for inspecting, validating, and converting FDR files."""

from __future__ import annotations

import argparse
from datetime import date, datetime
import json
import os
from pathlib import Path
import secrets
import sys
from typing import cast, NoReturn, override, TextIO

from .errors import FDRError, FDROutputError
from .models import FDRRecording
from .reader import FDRReader
from .geojson import recording_to_geojson


_MANDATORY_FIELDS = (
    "time_utc",
    "longitude",
    "latitude",
    "altitude_msl_ft",
    "heading_magnetic_deg",
    "pitch_deg",
    "roll_deg",
)


class _ParserExit(Exception):
    """Carry an argparse exit status back to the callable entry point."""

    def __init__(self, status: int, message: str | None) -> None:
        self.status = status
        self.exit_message = message
        super().__init__(message)


class _ArgumentParser(argparse.ArgumentParser):
    """Return parser statuses instead of terminating an embedding process."""

    @override
    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        raise _ParserExit(status, message)


def _first_utc_date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError
        return parsed
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid date: {value!r}; expected YYYY-MM-DD") from error


def build_parser() -> argparse.ArgumentParser:
    """Build the documented offline command parser."""
    parser = _ArgumentParser(prog="xplane-fdr", description="Offline X-Plane FDR tools")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="strictly validate an FDR file")
    validate.add_argument("input", type=Path, metavar="INPUT")

    inspect = commands.add_parser("inspect", help="summarize an FDR file")
    inspect.add_argument("input", type=Path, metavar="INPUT")
    inspect.add_argument("--json", action="store_true", help="emit compact JSON")
    inspect.add_argument("--first-utc-date", type=_first_utc_date, metavar="YYYY-MM-DD")

    to_geojson = commands.add_parser("to-geojson", help="convert an FDR file to GeoJSON")
    to_geojson.add_argument("input", type=Path, metavar="INPUT")
    to_geojson.add_argument("output", type=Path, metavar="OUTPUT")
    to_geojson.add_argument("--first-utc-date", type=_first_utc_date, metavar="YYYY-MM-DD")
    to_geojson.add_argument("--overwrite", action="store_true", help="replace an existing output")
    return parser


def _utc_text(value: datetime) -> str:
    return f"{value.isoformat().removesuffix('+00:00')}Z"


def _inspection_summary(recording: FDRRecording, first_utc_date: date | None) -> dict[str, object]:
    header = recording.header
    samples = recording.samples
    if samples and first_utc_date is not None:
        resolved = recording.resolved_utc_datetimes(first_utc_date)
        start_utc: str | None = _utc_text(resolved[0])
        end_utc: str | None = _utc_text(resolved[-1])
    elif samples:
        start_utc = samples[0].time_utc.isoformat()
        end_utc = samples[-1].time_utc.isoformat()
    else:
        start_utc = None
        end_utc = None

    effective_metadata: dict[str, str] = {}
    for item in header.metadata:
        effective_metadata[item.key] = item.value
    if header.source_version == 4:
        fields = [*_MANDATORY_FIELDS, *(dataref.path for dataref in header.datarefs)]
    else:
        fields = [column.identifier for column in header.legacy_columns]
    return {
        "comments": list(header.comments),
        "datarefs": [{"comment": dataref.comment, "path": dataref.path, "scale": dataref.scale} for dataref in header.datarefs],
        "duration_seconds": recording.duration.total_seconds(),
        "effective_metadata": effective_metadata,
        "end_utc": end_utc,
        "fields": fields,
        "local_date": header.local_date.isoformat() if header.local_date is not None else None,
        "metadata": [{"key": item.key, "value": item.value} for item in header.metadata],
        "origin": header.source_origin,
        "sample_count": len(samples),
        "start_utc": start_utc,
        "version": header.source_version,
    }


def _strict_json(document: object) -> str:
    return json.dumps(document, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n"


def _write_stdout(value: str) -> None:
    buffer = getattr(sys.stdout, "buffer", None)
    if buffer is None:
        sys.stdout.write(value)
    else:
        buffer.write(value.encode("utf-8"))


def _human_summary(summary: dict[str, object]) -> str:
    local_date = summary["local_date"] if summary["local_date"] is not None else "not declared"
    start_utc = summary["start_utc"] if summary["start_utc"] is not None else "none"
    end_utc = summary["end_utc"] if summary["end_utc"] is not None else "none"
    lines = [
        f"Version: {summary['version']}",
        f"Origin: {summary['origin']}",
        f"Local date: {local_date}",
        f"Samples: {summary['sample_count']}",
        f"Start UTC: {start_utc}",
        f"End UTC: {end_utc}",
        f"Duration: {summary['duration_seconds']:.3f} seconds",
    ]
    comments = summary["comments"]
    if isinstance(comments, list) and comments:
        lines.append("Comments:")
        lines.extend(f"  {comment}" for comment in comments)
    metadata = summary["metadata"]
    if isinstance(metadata, list) and metadata:
        lines.append("Metadata:")
        lines.extend(f"  {item['key']}: {item['value']}" for item in metadata)
    datarefs = summary["datarefs"]
    if isinstance(datarefs, list) and datarefs:
        lines.append("DataRefs:")
        for item in datarefs:
            description = f"  {item['path']} (scale={item['scale']}"
            if item["comment"] is not None:
                description += f", comment={item['comment']}"
            lines.append(description + ")")
    lines.append("Fields: " + ", ".join(cast(list[str], summary["fields"])))
    return "\n".join(lines) + "\n"


def _create_partial(destination: Path) -> tuple[Path, TextIO]:
    for _attempt in range(100):
        partial = destination.with_name(f".{destination.name}.{secrets.token_hex(8)}.partial")
        try:
            return partial, partial.open("x", encoding="utf-8", newline="\n")
        except FileExistsError:
            continue
    raise FileExistsError(f"could not create a unique partial file beside {destination}")


def _output_error(error: OSError, artifact_path: Path) -> FDROutputError:
    try:
        raise FDROutputError(f"GeoJSON output operation failed: {error}", artifact_path=artifact_path) from error
    except FDROutputError as wrapped:
        return wrapped


def _published_cleanup_error(error: OSError, partial: Path) -> FDROutputError:
    try:
        raise FDROutputError(
            f"GeoJSON publication succeeded but partial cleanup failed: {error}",
            artifact_path=partial,
        ) from error
    except FDROutputError as wrapped:
        return wrapped


def _wrapped(error: BaseException, artifact_path: Path) -> BaseException:
    return _output_error(error, artifact_path) if isinstance(error, OSError) else error


def _raise_after_unpublished_cleanup(
    primary: BaseException,
    *,
    partial: Path,
    stream: TextIO,
) -> NoReturn:
    failures = [_wrapped(primary, partial)]
    try:
        stream.close()
    except BaseException as cleanup:
        failures.append(_wrapped(cleanup, partial))
    try:
        os.unlink(partial)
    except FileNotFoundError:
        pass
    except BaseException as cleanup:
        failures.append(_wrapped(cleanup, partial))
    if len(failures) > 1:
        raise BaseExceptionGroup("GeoJSON output and cleanup failed", failures) from None
    error = failures[0]
    raise error.with_traceback(error.__traceback__)


def _write_atomic_json(document: object, destination: Path, *, overwrite: bool) -> None:
    """Serialize and durably publish strict JSON through a sibling partial."""
    payload = _strict_json(document)
    try:
        partial, stream = _create_partial(destination)
    except OSError as error:
        raise _output_error(error, destination)
    try:
        written = stream.write(payload)
        if written != len(payload):
            raise FDROutputError("GeoJSON output stream performed a short write", artifact_path=partial)
        stream.flush()
        os.fsync(stream.fileno())
        stream.close()
    except BaseException as primary:
        _raise_after_unpublished_cleanup(primary, partial=partial, stream=stream)

    if overwrite:
        try:
            os.replace(partial, destination)
        except BaseException as primary:
            _raise_after_unpublished_cleanup(primary, partial=partial, stream=stream)
        return
    try:
        os.link(partial, destination)
    except BaseException as primary:
        _raise_after_unpublished_cleanup(primary, partial=partial, stream=stream)
    try:
        os.unlink(partial)
    except FileNotFoundError:
        return
    except OSError as cleanup:
        raise _published_cleanup_error(cleanup, partial)


def _format_error(error: BaseException) -> str:
    if isinstance(error, BaseExceptionGroup):
        rendered = "; ".join(_format_error(nested) for nested in error.exceptions)
    elif isinstance(error, OSError) and error.filename is not None:
        rendered = f"{error.filename}: {error.strerror or error}"
    else:
        rendered = str(error)
    return " ".join(rendered.splitlines())


def _run_command(arguments: argparse.Namespace) -> None:
    recording = FDRReader().read(arguments.input)
    if arguments.command == "validate":
        return
    if arguments.command == "inspect":
        summary = _inspection_summary(recording, arguments.first_utc_date)
        _write_stdout(_strict_json(summary) if arguments.json else _human_summary(summary))
        return
    document = recording_to_geojson(recording, first_utc_date=arguments.first_utc_date)
    _write_atomic_json(document, arguments.output, overwrite=arguments.overwrite)


def main(argv: list[str] | None = None) -> int:
    """Run one offline command and return its process status."""
    parser = build_parser()
    try:
        arguments = parser.parse_args(argv)
    except _ParserExit as exit_request:
        if exit_request.exit_message is not None:
            sys.stderr.write(exit_request.exit_message)
        return exit_request.status
    try:
        _run_command(arguments)
    except (FDRError, OSError, ValueError, BaseExceptionGroup) as error:
        sys.stderr.write(f"xplane-fdr: {arguments.command} failed: {_format_error(error)}\n")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - console script is the supported surface
    raise SystemExit(main())
