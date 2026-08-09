"""Tests for standards-conforming GeoJSON conversion."""

from __future__ import annotations

from datetime import date, time
import json
from typing import cast
import unittest

from xplane_fdau.formats.xplane_fdr import (
    FDRDataref,
    FDRHeader,
    FDRMetadata,
    FDRRecording,
    FDRSample,
    recording_to_geojson,
)


def make_sample(
    *,
    time_utc: time = time(12, 34, 56, 123456),
    longitude: int | float = -87.9048,
    latitude: int | float = 41.9742,
    altitude_msl_ft: int | float = 100,
    heading_magnetic_deg: int | float = 271.5,
    pitch_deg: int | float = 2.25,
    roll_deg: int | float = -1.75,
    additional_values: tuple[int | float, ...] = (3, 0.25),
) -> FDRSample:
    """Return one deterministic version 4 sample."""
    return FDRSample(
        time_utc,
        longitude,
        latitude,
        altitude_msl_ft,
        heading_magnetic_deg,
        pitch_deg,
        roll_deg,
        additional_values,
        (),
    )


def make_recording(
    *samples: FDRSample,
    metadata: tuple[FDRMetadata, ...] = (),
) -> FDRRecording:
    """Return a version 4 recording with two differently scaled DataRefs."""
    header = FDRHeader(
        4,
        "A",
        (),
        metadata,
        (
            FDRDataref("sim/test/count", 2, "Raw count"),
            FDRDataref("sim/test/ratio", 0.5),
        ),
        (),
        None,
    )
    return FDRRecording(header, samples)


def feature_list(document: dict[str, object]) -> list[dict[str, object]]:
    """Narrow the public JSON-compatible return type for test assertions."""
    return cast(list[dict[str, object]], document["features"])


def feature_geometry(feature: dict[str, object]) -> dict[str, object]:
    """Narrow one GeoJSON feature geometry for test assertions."""
    return cast(dict[str, object], feature["geometry"])


def feature_properties(feature: dict[str, object]) -> dict[str, object]:
    """Narrow one GeoJSON feature property mapping for test assertions."""
    return cast(dict[str, object], feature["properties"])


class FDRGeoJSONTests(unittest.TestCase):
    """Verify GeoJSON structure, semantics, time resolution, and path safety."""

    def test_each_sample_becomes_a_two_dimensional_point_with_semantic_properties(self) -> None:
        first = make_sample()
        second = make_sample(
            longitude=-87.8,
            latitude=42,
            altitude_msl_ft=10_000,
            additional_values=(7, 0.75),
        )

        document = recording_to_geojson(make_recording(first, second))

        self.assertEqual("FeatureCollection", document["type"])
        features = feature_list(document)
        self.assertEqual(3, len(features))
        point = features[0]
        self.assertEqual("Feature", point["type"])
        self.assertEqual(
            {"type": "Point", "coordinates": [-87.9048, 41.9742]},
            feature_geometry(point),
        )
        self.assertEqual(
            {
                "time_utc": "12:34:56.123456",
                "altitude_msl_ft": 100,
                "altitude_msl_m": 30.48,
                "heading_magnetic_deg": 271.5,
                "pitch_deg": 2.25,
                "roll_deg": -1.75,
                "additional_values": {
                    "sim/test/count": 3,
                    "sim/test/ratio": 0.25,
                },
            },
            feature_properties(point),
        )
        self.assertEqual(3_048, feature_properties(features[1])["altitude_msl_m"])
        coordinates = cast(list[int | float], feature_geometry(point)["coordinates"])
        self.assertEqual(2, len(coordinates))
        json.dumps(document, allow_nan=False)

    def test_path_is_absent_below_two_samples_and_is_a_line_string_otherwise(self) -> None:
        empty = recording_to_geojson(make_recording())
        singleton = recording_to_geojson(make_recording(make_sample()))
        recording = make_recording(
            make_sample(longitude=-88, latitude=41),
            make_sample(longitude=-87, latitude=42),
        )

        document = recording_to_geojson(recording)

        self.assertEqual([], feature_list(empty))
        self.assertEqual(1, len(feature_list(singleton)))
        self.assertEqual(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-88, 41], [-87, 42]],
                },
                "properties": {},
            },
            feature_list(document)[-1],
        )

    def test_antimeridian_crossings_split_and_interpolate_each_boundary(self) -> None:
        eastbound = make_recording(
            make_sample(longitude=170, latitude=10),
            make_sample(longitude=-170, latitude=30),
            make_sample(longitude=170, latitude=50),
        )

        path = feature_list(recording_to_geojson(eastbound))[-1]
        geometry = feature_geometry(path)

        self.assertEqual("MultiLineString", geometry["type"])
        self.assertEqual(
            [
                [[170, 10], [180, 20.0]],
                [[-180, 20.0], [-170, 30], [-180, 40.0]],
                [[180, 40.0], [170, 50]],
            ],
            geometry["coordinates"],
        )
        lines = cast(list[list[list[int | float]]], geometry["coordinates"])
        self.assertTrue(all(len(line) >= 2 for line in lines))

    def test_opposite_antimeridian_representations_keep_valid_child_lines(self) -> None:
        recording = make_recording(
            make_sample(longitude=180, latitude=10),
            make_sample(longitude=-180, latitude=30),
        )

        path = feature_list(recording_to_geojson(recording))[-1]

        self.assertEqual(
            {
                "type": "MultiLineString",
                "coordinates": [
                    [[180, 10], [180, 10]],
                    [[-180, 10], [-180, 30]],
                ],
            },
            feature_geometry(path),
        )

    def test_timestamp_requires_explicit_utc_date_and_resolves_midnight_rollover(self) -> None:
        recording = make_recording(
            make_sample(time_utc=time(23, 59, 59, 500000)),
            make_sample(time_utc=time(0, 0, 1, 250000)),
            metadata=(FDRMetadata("DATE", "08/08/2026"),),
        )

        without_date = recording_to_geojson(recording)
        with_date = recording_to_geojson(recording, first_utc_date=date(2026, 8, 9))

        without_date_properties = feature_properties(feature_list(without_date)[0])
        first_properties = feature_properties(feature_list(with_date)[0])
        second_properties = feature_properties(feature_list(with_date)[1])
        self.assertNotIn("timestamp_utc", without_date_properties)
        self.assertEqual(
            "2026-08-09T23:59:59.500000Z",
            first_properties["timestamp_utc"],
        )
        self.assertEqual(
            "2026-08-10T00:00:01.250000Z",
            second_properties["timestamp_utc"],
        )


if __name__ == "__main__":
    unittest.main()
