"""Tests for strict adapter-neutral recording configuration."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
import io
from importlib.resources import files
import json
import math
from pathlib import Path
import tempfile
from typing import Literal, cast
import unittest

from xplane_fdr import (
    FDRConfigError,
    FDRDatarefConfig,
    FDRMetadataConfig,
    FDRRecordConfig,
    FDRSamplingPolicy,
    FDRStoragePolicy,
    get_profile,
    load_record_config,
    resolve_recording_definition,
)


def load_text(text: str) -> FDRRecordConfig:
    """Load configuration from a caller-owned in-memory stream."""
    return load_record_config(io.StringIO(text))


class FDRConfigLoadingTests(unittest.TestCase):
    """Configuration loading applies strict defaults and owns only path streams."""

    def test_minimal_document_uses_standard_profile_ten_hz_and_xplane_directory(self) -> None:
        config = load_text('{"schema_version": 1}')
        definition = resolve_recording_definition(config)

        self.assertEqual(1, config.schema_version)
        self.assertEqual(("standard",), config.profiles)
        self.assertEqual((0.1, None), (definition.sampling.interval_seconds, definition.sampling.duration_seconds))
        self.assertEqual(Path("Output/FDR files"), definition.storage.directory)
        self.assertIsNone(definition.storage.filename)
        self.assertEqual(get_profile("standard").datarefs, definition.header.datarefs)

    def test_explicit_empty_and_minimal_profiles_remain_empty(self) -> None:
        for profiles in ("[]", '["minimal"]'):
            with self.subTest(profiles=profiles):
                config = load_text(f'{{"schema_version": 1, "profiles": {profiles}}}')
                self.assertEqual((), resolve_recording_definition(config).header.datarefs)

    def test_full_document_loads_immutable_values_and_maps_ordered_metadata(self) -> None:
        stream = io.StringIO(
            """{
              "$schema": "https://example.test/config.schema.json",
              "schema_version": 1,
              "profiles": ["minimal"],
              "sampling": {"interval_seconds": 0.25, "duration_seconds": 600},
              "metadata": {
                "aircraft_path": "Aircraft/Test.acf",
                "tail_number": "N172SP",
                "local_date": "2026-08-08",
                "pressure_in_hg": 29.92,
                "isa_offset_c": 0,
                "wind_direction_deg": 270,
                "wind_speed_kt": 12,
                "comments": ["first", "second"]
              },
              "datarefs": [{"path": "vendor/system/value", "scale": -2.5, "comment": "signed"}],
              "storage": {"directory": "Output/Custom FDR", "filename": "training.fdr"}
            }"""
        )

        config = load_record_config(stream)
        definition = resolve_recording_definition(config)

        self.assertFalse(stream.closed)
        self.assertEqual(date(2026, 8, 8), config.metadata.local_date)
        self.assertEqual(FDRSamplingPolicy(0.25, 600.0), definition.sampling)
        self.assertEqual(FDRStoragePolicy(Path("Output/Custom FDR"), "training.fdr"), definition.storage)
        self.assertEqual(("first", "second"), definition.header.comments)
        self.assertEqual(
            (
                ("ACFT", "Aircraft/Test.acf"),
                ("TAIL", "N172SP"),
                ("DATE", "2026-08-08"),
                ("PRES", "29.92"),
                ("DISA", "0"),
                ("WIND", "270,12"),
            ),
            tuple((item.key, item.value) for item in definition.header.metadata),
        )
        self.assertEqual(date(2026, 8, 8), definition.header.local_date)
        self.assertEqual(
            ("vendor/system/value", -2.5, "signed"),
            (
                definition.header.datarefs[0].path,
                definition.header.datarefs[0].scale,
                definition.header.datarefs[0].comment,
            ),
        )
        for value in (config, config.metadata, config.datarefs[0]):
            with self.subTest(value=type(value).__name__), self.assertRaises(FrozenInstanceError):
                setattr(value, next(iter(value.__dataclass_fields__)), None)

    def test_path_input_is_utf8_and_releases_its_owned_stream(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "café.json"
            path.write_text('{"schema_version": 1, "metadata": {"comments": ["café"]}}', encoding="utf-8")

            config = load_record_config(path)
            path.unlink()

        self.assertEqual(("café",), config.metadata.comments)


class FDRConfigResolutionTests(unittest.TestCase):
    """Profile and custom declarations retain stable positions and explicit values."""

    def test_custom_datarefs_follow_profiles_and_override_in_first_position(self) -> None:
        standard_first = get_profile("standard").datarefs[0]
        text = json.dumps(
            {
                "schema_version": 1,
                "profiles": ["standard", "standard", "systems"],
                "datarefs": [
                    {"path": standard_first.path, "scale": 2.0, "comment": "override"},
                    {"path": "vendor/new", "comment": "custom"},
                ],
            }
        )

        datarefs = resolve_recording_definition(load_text(text)).header.datarefs

        expected_profile_count = len(get_profile("standard").datarefs) + len(get_profile("systems").datarefs)
        self.assertEqual(expected_profile_count + 1, len(datarefs))
        self.assertEqual((standard_first.path, 2.0, "override"), (datarefs[0].path, datarefs[0].scale, datarefs[0].comment))
        self.assertEqual(("vendor/new", 1.0, "custom"), (datarefs[-1].path, datarefs[-1].scale, datarefs[-1].comment))

    def test_omitted_custom_properties_preserve_an_earlier_declaration(self) -> None:
        path = get_profile("standard").datarefs[0].path
        config = FDRRecordConfig(
            schema_version=1,
            profiles=("standard",),
            sampling=FDRSamplingPolicy(),
            metadata=FDRMetadataConfig(),
            datarefs=(FDRDatarefConfig(path=path, scale=None, comment=None),),
            storage=FDRStoragePolicy(),
        )

        resolved = resolve_recording_definition(config).header.datarefs[0]

        self.assertEqual((1.0, None), (resolved.scale, resolved.comment))


class FDRConfigValidationTests(unittest.TestCase):
    """Malformed JSON and invalid semantics fail with exact source context."""

    def assert_config_error(self, document: object, property_path: str) -> FDRConfigError:
        """Assert one JSON-compatible value is rejected at the named property."""
        with self.assertRaises(FDRConfigError) as caught:
            load_text(json.dumps(document))
        self.assertEqual(property_path, caught.exception.property_path)
        return caught.exception

    def test_syntax_error_reports_source_line_and_column(self) -> None:
        stream = io.StringIO('{\n  "schema_version": 1,\n  "profiles": [\n}')
        stream.name = "flight.json"

        with self.assertRaises(FDRConfigError) as caught:
            load_record_config(stream)

        self.assertEqual("flight.json", getattr(caught.exception, "source"))
        self.assertEqual(4, getattr(caught.exception, "line"))
        self.assertGreater(getattr(caught.exception, "column"), 0)
        self.assertIn("flight.json:4:", str(caught.exception))

    def test_semantic_error_reports_path_source_and_property_path(self) -> None:
        stream = io.StringIO('{"schema_version": 1, "sampling": {"interval_seconds": 0}}')
        stream.name = "flight.json"

        with self.assertRaises(FDRConfigError) as caught:
            load_record_config(stream)

        self.assertEqual("flight.json", getattr(caught.exception, "source"))
        self.assertEqual("$.sampling.interval_seconds", caught.exception.property_path)
        self.assertIn("flight.json: $.sampling.interval_seconds", str(caught.exception))

    def test_root_schema_and_unknown_properties_are_strict(self) -> None:
        invalid = (
            ({}, "$.schema_version"),
            ({"schema_version": True}, "$.schema_version"),
            ({"schema_version": 1.0}, "$.schema_version"),
            ({"schema_version": 2}, "$.schema_version"),
            ({"schema_version": 1, "$schema": 7}, "$.$schema"),
            ({"schema_version": 1, "connection": {}}, "$.connection"),
            ({"schema_version": 1, "overwrite": True}, "$.overwrite"),
            ({"schema_version": 1, "output_path": "live.fdr"}, "$.output_path"),
            ({"schema_version": 1, "sampling": {"interval_seconds": 0.1, "extra": 1}}, "$.sampling.extra"),
            ({"schema_version": 1, "metadata": {"extra": 1}}, "$.metadata.extra"),
            ({"schema_version": 1, "datarefs": [{"path": "sim/test", "extra": 1}]}, "$.datarefs[0].extra"),
            ({"schema_version": 1, "storage": {"extra": 1}}, "$.storage.extra"),
        )
        for document, property_path in invalid:
            with self.subTest(document=document):
                self.assert_config_error(document, property_path)

    def test_arrays_strings_and_profile_names_are_strict(self) -> None:
        invalid = (
            ({"schema_version": 1, "profiles": "standard"}, "$.profiles"),
            ({"schema_version": 1, "profiles": [1]}, "$.profiles[0]"),
            ({"schema_version": 1, "profiles": ["STANDARD"]}, "$.profiles[0]"),
            ({"schema_version": 1, "metadata": {"comments": "comment"}}, "$.metadata.comments"),
            ({"schema_version": 1, "metadata": {"comments": [1]}}, "$.metadata.comments[0]"),
            ({"schema_version": 1, "datarefs": {}}, "$.datarefs"),
            ({"schema_version": 1, "datarefs": ["sim/test"]}, "$.datarefs[0]"),
            ({"schema_version": 1, "storage": []}, "$.storage"),
        )
        for document, property_path in invalid:
            with self.subTest(document=document):
                self.assert_config_error(document, property_path)

    def test_numbers_reject_booleans_nonfinite_values_and_invalid_ranges(self) -> None:
        invalid = (
            ({"schema_version": 1, "sampling": {"interval_seconds": True}}, "$.sampling.interval_seconds"),
            ({"schema_version": 1, "sampling": {"interval_seconds": math.nan}}, "$.sampling.interval_seconds"),
            ({"schema_version": 1, "sampling": {"duration_seconds": math.inf}}, "$.sampling.duration_seconds"),
            ({"schema_version": 1, "sampling": {"duration_seconds": -1}}, "$.sampling.duration_seconds"),
            ({"schema_version": 1, "metadata": {"pressure_in_hg": False}}, "$.metadata.pressure_in_hg"),
            ({"schema_version": 1, "metadata": {"isa_offset_c": math.nan}}, "$.metadata.isa_offset_c"),
            ({"schema_version": 1, "metadata": {"wind_direction_deg": -0.1}}, "$.metadata.wind_direction_deg"),
            ({"schema_version": 1, "metadata": {"wind_direction_deg": 360.1}}, "$.metadata.wind_direction_deg"),
            ({"schema_version": 1, "metadata": {"wind_speed_kt": -0.1}}, "$.metadata.wind_speed_kt"),
            ({"schema_version": 1, "datarefs": [{"path": "sim/test", "scale": True}]}, "$.datarefs[0].scale"),
            ({"schema_version": 1, "datarefs": [{"path": "sim/test", "scale": -math.inf}]}, "$.datarefs[0].scale"),
        )
        for document, property_path in invalid:
            with self.subTest(document=document):
                self.assert_config_error(document, property_path)

    def test_dates_comments_paths_filenames_and_duplicate_datarefs_are_strict(self) -> None:
        invalid = (
            ({"schema_version": 1, "metadata": {"local_date": "08/08/2026"}}, "$.metadata.local_date"),
            ({"schema_version": 1, "metadata": {"comments": ["line one\nline two"]}}, "$.metadata.comments[0]"),
            ({"schema_version": 1, "datarefs": [{"path": ""}]}, "$.datarefs[0].path"),
            ({"schema_version": 1, "datarefs": [{"path": "sim/test\u0000value"}]}, "$.datarefs[0].path"),
            ({"schema_version": 1, "datarefs": [{"path": "sim/test", "comment": "a\rb"}]}, "$.datarefs[0].comment"),
            (
                {"schema_version": 1, "datarefs": [{"path": "sim/test"}, {"path": "sim/test"}]},
                "$.datarefs[1].path",
            ),
            ({"schema_version": 1, "storage": {"directory": ""}}, "$.storage.directory"),
            ({"schema_version": 1, "storage": {"directory": "bad\u0000path"}}, "$.storage.directory"),
            ({"schema_version": 1, "storage": {"filename": "flight.txt"}}, "$.storage.filename"),
            ({"schema_version": 1, "storage": {"filename": "folder/flight.fdr"}}, "$.storage.filename"),
            ({"schema_version": 1, "storage": {"filename": "folder\\flight.fdr"}}, "$.storage.filename"),
        )
        for document, property_path in invalid:
            with self.subTest(document=document):
                self.assert_config_error(document, property_path)

    def test_duplicate_json_object_properties_are_rejected(self) -> None:
        with self.assertRaises(FDRConfigError) as caught:
            load_text('{"schema_version": 1, "storage": {"filename": "a.fdr", "filename": "b.fdr"}}')
        self.assertEqual("$.storage.filename", caught.exception.property_path)

    def test_programmatic_config_values_enforce_the_same_semantic_contract(self) -> None:
        invalid = (
            lambda: FDRRecordConfig(schema_version=cast(Literal[1], True)),
            lambda: FDRRecordConfig(schema_version=1, profiles=("unknown",)),
            lambda: FDRMetadataConfig(local_date=cast(date, "2026-08-08")),
            lambda: FDRMetadataConfig(wind_direction_deg=361),
            lambda: FDRMetadataConfig(comments=("line one\nline two",)),
            lambda: FDRDatarefConfig(path=""),
            lambda: FDRDatarefConfig(path="sim/test", scale=math.nan),
            lambda: FDRRecordConfig(
                schema_version=1,
                datarefs=(FDRDatarefConfig("sim/test"), FDRDatarefConfig("sim/test")),
            ),
        )

        for constructor in invalid:
            with self.subTest(constructor=constructor), self.assertRaises(FDRConfigError):
                constructor()


class FDRConfigSchemaTests(unittest.TestCase):
    """The packaged editor contract mirrors runtime structure without adding dependencies."""

    def test_schema_is_available_as_an_installed_package_resource(self) -> None:
        resource = files("xplane_fdr.schemas").joinpath("fdr-record-config-v1.schema.json")
        schema = json.loads(resource.read_text(encoding="utf-8"))

        self.assertEqual("https://tvproductions.github.io/xplane-fdr/schemas/fdr-record-config-v1.schema.json", schema["$id"])
        self.assertEqual(["schema_version"], schema["required"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(1, schema["properties"]["schema_version"]["const"])
        self.assertEqual(0, schema["properties"]["sampling"]["properties"]["interval_seconds"]["exclusiveMinimum"])
        self.assertEqual(360, schema["properties"]["metadata"]["properties"]["wind_direction_deg"]["maximum"])
        self.assertFalse(schema["properties"]["sampling"]["additionalProperties"])
        self.assertFalse(schema["properties"]["metadata"]["additionalProperties"])
        self.assertFalse(schema["properties"]["datarefs"]["items"]["additionalProperties"])
        self.assertFalse(schema["properties"]["storage"]["additionalProperties"])
        serialized = json.dumps(schema)
        for forbidden in ("connection", "xplm", "overwrite", "output_path"):
            self.assertNotIn(forbidden, serialized.lower())


if __name__ == "__main__":
    unittest.main()
