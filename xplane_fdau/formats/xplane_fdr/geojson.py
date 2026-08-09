"""Standards-conforming GeoJSON conversion for validated FDR recordings."""

from __future__ import annotations

from datetime import date, datetime

from .models import FDRRecording, FDRSample

_FEET_TO_METRES = 0.3048


def _exact_metres_decimal(numerator: int) -> str:
    """Render an exact signed decimal for a metres numerator over 1250."""
    sign = "-" if numerator < 0 else ""
    whole_metres, remainder = divmod(abs(numerator), 1250)
    return f"{sign}{whole_metres}.{remainder * 8:04d}".rstrip("0")


def _metres_from_feet(altitude_msl_ft: int | float) -> int | float | str:
    """Convert feet using the exact 0.3048 ratio while keeping strict JSON safe."""
    if type(altitude_msl_ft) is int:
        numerator = altitude_msl_ft * 381
        metres, remainder = divmod(numerator, 1250)
        if remainder == 0:
            return metres
        try:
            return altitude_msl_ft * _FEET_TO_METRES
        except OverflowError:
            return _exact_metres_decimal(numerator)
    return altitude_msl_ft * _FEET_TO_METRES


def _position(sample: FDRSample) -> list[int | float]:
    """Return a two-dimensional GeoJSON position for one FDR sample."""
    return [sample.longitude, sample.latitude]


def _point_feature(
    sample: FDRSample,
    dataref_paths: tuple[str, ...],
    timestamp: datetime | None,
) -> dict[str, object]:
    """Return the GeoJSON point feature corresponding to one sample."""
    properties: dict[str, object] = {
        "time_utc": sample.time_utc.isoformat(),
        "altitude_msl_ft": sample.altitude_msl_ft,
        "altitude_msl_m": _metres_from_feet(sample.altitude_msl_ft),
        "heading_magnetic_deg": sample.heading_magnetic_deg,
        "pitch_deg": sample.pitch_deg,
        "roll_deg": sample.roll_deg,
        "additional_values": dict(zip(dataref_paths, sample.additional_values, strict=True)),
    }
    if timestamp is not None:
        properties["timestamp_utc"] = f"{timestamp.isoformat().removesuffix('+00:00')}Z"
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": _position(sample)},
        "properties": properties,
    }


def _path_geometry(samples: tuple[FDRSample, ...]) -> dict[str, object]:
    """Return a path geometry, splitting crossings of the antimeridian."""
    lines: list[list[list[int | float]]] = [[_position(samples[0])]]
    previous = samples[0]
    for sample in samples[1:]:
        longitude_delta = sample.longitude - previous.longitude
        if abs(longitude_delta) <= 180:
            lines[-1].append(_position(sample))
        else:
            boundary_longitude = 180 if longitude_delta < 0 else -180
            unwrapped_longitude = sample.longitude + (360 if boundary_longitude == 180 else -360)
            longitude_span = unwrapped_longitude - previous.longitude
            fraction = 0 if longitude_span == 0 else (boundary_longitude - previous.longitude) / longitude_span
            boundary_latitude = previous.latitude + (sample.latitude - previous.latitude) * fraction
            lines[-1].append([boundary_longitude, boundary_latitude])
            lines.append([[-boundary_longitude, boundary_latitude], _position(sample)])
        previous = sample
    if len(lines) == 1:
        return {"type": "LineString", "coordinates": lines[0]}
    return {"type": "MultiLineString", "coordinates": lines}


def recording_to_geojson(recording: FDRRecording, *, first_utc_date: date | None = None) -> dict[str, object]:
    """Convert an FDR recording to a JSON-compatible GeoJSON FeatureCollection."""
    timestamps = recording.resolved_utc_datetimes(first_utc_date) if first_utc_date is not None else ()
    dataref_paths = tuple(dataref.path for dataref in recording.header.datarefs)
    features: list[dict[str, object]] = []
    for index, sample in enumerate(recording.samples):
        timestamp = timestamps[index] if timestamps else None
        features.append(_point_feature(sample, dataref_paths, timestamp))
    if len(recording.samples) >= 2:
        features.append({"type": "Feature", "geometry": _path_geometry(recording.samples), "properties": {}})
    return {"type": "FeatureCollection", "features": features}
