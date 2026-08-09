"""Tests for immutable FDR domain models and structured public errors."""

from __future__ import annotations

import dataclasses
from datetime import UTC, date, datetime, time, timedelta, timezone
import math
from pathlib import Path
from typing import Literal, cast
import unittest

from xplane_fdr import (
    FDRConfigError,
    FDRDataref,
    FDRError,
    FDRHeader,
    FDRLegacyColumn,
    FDRMetadata,
    FDRNormalizationResult,
    FDROutputError,
    FDRParseError,
    FDRRecording,
    FDRRecordingStateError,
    FDRSample,
    FDRValidationError,
)


def make_v4_header(
    *,
    comments: tuple[str, ...] | list[str] = (),
    metadata: tuple[FDRMetadata, ...] | list[FDRMetadata] = (),
    datarefs: tuple[FDRDataref, ...] | list[FDRDataref] = (),
    local_date: date | None = None,
) -> FDRHeader:
    """Build a minimal valid version 4 header."""
    return FDRHeader(
        source_version=4,
        source_origin="A",
        comments=cast(tuple[str, ...], comments),
        metadata=cast(tuple[FDRMetadata, ...], metadata),
        datarefs=cast(tuple[FDRDataref, ...], datarefs),
        legacy_columns=(),
        local_date=local_date,
    )


def make_sample(
    *,
    time_utc: time = time(12),
    additional_values: tuple[int | float, ...] | list[int | float] = (),
    legacy_values: tuple[int | float, ...] | list[int | float] = (),
) -> FDRSample:
    """Build a minimal valid navigation sample."""
    return FDRSample(
        time_utc=time_utc,
        longitude=-87.9048,
        latitude=41.9742,
        altitude_msl_ft=640,
        heading_magnetic_deg=270,
        pitch_deg=2,
        roll_deg=-1,
        additional_values=cast(tuple[int | float, ...], additional_values),
        legacy_values=cast(tuple[int | float, ...], legacy_values),
    )


class FDRErrorTests(unittest.TestCase):
    """Verify the public hierarchy and each error's applicable context."""

    def test_public_errors_share_fdr_error_base(self) -> None:
        for error_type in (
            FDRParseError,
            FDRValidationError,
            FDRConfigError,
            FDRRecordingStateError,
            FDROutputError,
        ):
            with self.subTest(error_type=error_type.__name__):
                self.assertTrue(issubclass(error_type, FDRError))

    def test_parse_error_preserves_source_and_line_context(self) -> None:
        error = FDRParseError("bad row", source="flight.fdr", line=12)

        self.assertEqual("bad row", error.message)
        self.assertEqual(("flight.fdr", 12), (error.source, error.line))
        self.assertEqual("flight.fdr:12: bad row", str(error))
        self.assertFalse(hasattr(error, "property_path"))
        self.assertFalse(hasattr(error, "artifact_path"))

    def test_validation_error_omits_absent_source_context_from_text(self) -> None:
        error = FDRValidationError("invalid sample")

        self.assertIsNone(error.source)
        self.assertIsNone(error.line)
        self.assertEqual("invalid sample", str(error))

    def test_config_error_exposes_only_property_path_context(self) -> None:
        error = FDRConfigError("unknown property", property_path="$.storage.overwrite")

        self.assertEqual("unknown property", error.message)
        self.assertEqual("$.storage.overwrite", error.property_path)
        self.assertEqual("$.storage.overwrite: unknown property", str(error))
        self.assertFalse(hasattr(error, "source"))
        self.assertFalse(hasattr(error, "artifact_path"))

    def test_recording_state_error_has_no_location_context(self) -> None:
        error = FDRRecordingStateError("session is closed")

        self.assertEqual("session is closed", error.message)
        self.assertEqual("session is closed", str(error))
        self.assertFalse(hasattr(error, "source"))
        self.assertFalse(hasattr(error, "property_path"))
        self.assertFalse(hasattr(error, "artifact_path"))

    def test_output_error_preserves_artifact_context_and_oserror_cause(self) -> None:
        cause = OSError("disk full")

        try:
            try:
                raise cause
            except OSError as error:
                raise FDROutputError("cannot write", artifact_path=Path("flight.fdr")) from error
        except FDROutputError as caught:
            self.assertEqual("cannot write", caught.message)
            self.assertEqual(Path("flight.fdr"), caught.artifact_path)
            self.assertEqual("flight.fdr: cannot write", str(caught))
            self.assertIs(cause, caught.__cause__)
            self.assertFalse(hasattr(caught, "source"))


class FDRLeafModelTests(unittest.TestCase):
    """Verify declarations and samples validate their own values."""

    def test_sample_preserves_semantic_fields(self) -> None:
        sample = FDRSample(
            time_utc=time(23, 59, 59, 500000),
            longitude=-87.9048,
            latitude=41.9742,
            altitude_msl_ft=640,
            heading_magnetic_deg=270,
            pitch_deg=2,
            roll_deg=-1,
            additional_values=(0.75,),
            legacy_values=(),
        )

        self.assertEqual(time(23, 59, 59, 500000), sample.time_utc)
        self.assertEqual((0.75,), sample.additional_values)

    def test_models_are_frozen_and_slotted(self) -> None:
        values = (
            FDRMetadata("ACFN", "Cessna 172"),
            FDRDataref("sim/flightmodel/weight/m_fuel_total", 1),
            FDRLegacyColumn("longitude"),
            make_v4_header(),
            make_sample(),
            FDRRecording(make_v4_header(), ()),
            FDRNormalizationResult(FDRRecording(make_v4_header(), ()), ()),
        )
        for value in values:
            with self.subTest(model=type(value).__name__):
                self.assertTrue(dataclasses.is_dataclass(value))
                self.assertFalse(hasattr(value, "__dict__"))
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    value.__setattr__(dataclasses.fields(value)[0].name, None)

    def test_caller_lists_are_frozen_without_aliasing(self) -> None:
        comments = ["created by test"]
        metadata = [FDRMetadata("TAIL", "N12345")]
        datarefs = [FDRDataref("sim/test/value", 1)]
        additional = [3.5]
        samples = [make_sample(additional_values=additional)]

        header = make_v4_header(comments=comments, metadata=metadata, datarefs=datarefs)
        recording = FDRRecording(header, cast(tuple[FDRSample, ...], samples))
        comments.append("later")
        metadata.clear()
        datarefs.clear()
        additional.append(9)
        samples.clear()

        self.assertEqual(("created by test",), header.comments)
        self.assertEqual((FDRMetadata("TAIL", "N12345"),), header.metadata)
        self.assertEqual((FDRDataref("sim/test/value", 1),), header.datarefs)
        self.assertEqual((3.5,), recording.samples[0].additional_values)
        self.assertEqual(1, len(recording.samples))

    def test_ordered_fields_reject_none_and_unordered_containers(self) -> None:
        sample = make_sample()
        recording = FDRRecording(make_v4_header(), (sample,))
        invalid_constructors = (
            ("comments None", lambda: make_v4_header(comments=cast(tuple[str, ...], None))),
            ("comments set", lambda: make_v4_header(comments=cast(tuple[str, ...], {"first", "second"}))),
            (
                "metadata set",
                lambda: make_v4_header(metadata=cast(tuple[FDRMetadata, ...], {FDRMetadata("TAIL", "N1")})),
            ),
            (
                "datarefs set",
                lambda: make_v4_header(datarefs=cast(tuple[FDRDataref, ...], {FDRDataref("sim/test/value", 1)})),
            ),
            (
                "legacy columns set",
                lambda: FDRHeader(
                    3,
                    "A",
                    (),
                    (),
                    (),
                    cast(tuple[FDRLegacyColumn, ...], {FDRLegacyColumn("longitude")}),
                    None,
                ),
            ),
            (
                "additional values set",
                lambda: dataclasses.replace(sample, additional_values=cast(tuple[int | float, ...], {1, 2})),
            ),
            (
                "legacy values set",
                lambda: dataclasses.replace(sample, legacy_values=cast(tuple[int | float, ...], {1, 2})),
            ),
            (
                "samples set",
                lambda: FDRRecording(make_v4_header(), cast(tuple[FDRSample, ...], {sample})),
            ),
            (
                "omissions set",
                lambda: FDRNormalizationResult(recording, cast(tuple[str, ...], {"legacy_one", "legacy_two"})),
            ),
        )

        for label, constructor in invalid_constructors:
            with self.subTest(field=label), self.assertRaises(FDRValidationError):
                constructor()

    def test_text_fields_reject_wrong_or_empty_values(self) -> None:
        invalid_constructors = (
            lambda: FDRMetadata("", "value"),
            lambda: FDRMetadata(cast(str, 1), "value"),
            lambda: FDRMetadata("DATE", cast(str, 1)),
            lambda: FDRDataref("", 1),
            lambda: FDRDataref("sim/test", 1, comment=cast(str, 1)),
            lambda: FDRLegacyColumn(""),
            lambda: FDRLegacyColumn("value", comment=cast(str, 1)),
        )

        for constructor in invalid_constructors:
            with self.subTest(constructor=constructor), self.assertRaises(FDRValidationError):
                constructor()

    def test_numeric_fields_reject_booleans(self) -> None:
        sample = make_sample(additional_values=(1,), legacy_values=(2,))
        sample_fields = (
            "longitude",
            "latitude",
            "altitude_msl_ft",
            "heading_magnetic_deg",
            "pitch_deg",
            "roll_deg",
        )
        for field_name in sample_fields:
            with self.subTest(field_name=field_name), self.assertRaises(FDRValidationError):
                dataclasses.replace(sample, **{field_name: True})
        for field_name in ("additional_values", "legacy_values"):
            with self.subTest(field_name=field_name), self.assertRaises(FDRValidationError):
                dataclasses.replace(sample, **{field_name: (True,)})
        with self.assertRaises(FDRValidationError):
            FDRDataref("sim/test/value", True)

    def test_numeric_fields_reject_non_finite_floats(self) -> None:
        for bad_value in (math.inf, -math.inf, math.nan):
            with self.subTest(value=bad_value):
                with self.assertRaises(FDRValidationError):
                    FDRDataref("sim/test/value", bad_value)
                with self.assertRaises(FDRValidationError):
                    dataclasses.replace(make_sample(), altitude_msl_ft=bad_value)
                with self.assertRaises(FDRValidationError):
                    dataclasses.replace(make_sample(), additional_values=(bad_value,))

    def test_exact_arbitrary_size_integers_are_preserved(self) -> None:
        huge = 10**400

        dataref = FDRDataref("sim/test/value", huge)
        sample = dataclasses.replace(
            make_sample(),
            altitude_msl_ft=huge,
            heading_magnetic_deg=-huge,
            additional_values=(huge,),
        )

        self.assertIs(type(dataref.scale), int)
        self.assertEqual(huge, dataref.scale)
        self.assertEqual((huge, -huge, (huge,)), (sample.altitude_msl_ft, sample.heading_magnetic_deg, sample.additional_values))

    def test_coordinates_enforce_inclusive_geographic_bounds(self) -> None:
        self.assertEqual((-180, -90), (dataclasses.replace(make_sample(), longitude=-180, latitude=-90).longitude, -90))
        self.assertEqual((180, 90), (dataclasses.replace(make_sample(), longitude=180, latitude=90).longitude, 90))
        for field_name, bad_value in (("longitude", -181), ("longitude", 181), ("latitude", -91), ("latitude", 91)):
            with self.subTest(field_name=field_name, value=bad_value), self.assertRaises(FDRValidationError):
                dataclasses.replace(make_sample(), **{field_name: bad_value})

    def test_sample_time_must_be_unzoned_time(self) -> None:
        for bad_value in (datetime(2026, 8, 9, 12), time(12, tzinfo=timezone.utc)):
            with self.subTest(value=bad_value), self.assertRaises(FDRValidationError):
                dataclasses.replace(make_sample(), time_utc=cast(time, bad_value))


class FDRHeaderTests(unittest.TestCase):
    """Verify ordered declarations and DATE semantics."""

    def test_header_rejects_duplicate_identifiers(self) -> None:
        duplicate_datarefs = (
            FDRDataref("sim/test/value", 1),
            FDRDataref("sim/test/value", 2),
        )
        duplicate_legacy = (FDRLegacyColumn("longitude"), FDRLegacyColumn("longitude"))

        with self.assertRaises(FDRValidationError):
            make_v4_header(datarefs=duplicate_datarefs)
        with self.assertRaises(FDRValidationError):
            FDRHeader(3, "I", (), (), (), duplicate_legacy, None)

    def test_version_specific_declarations_remain_separate(self) -> None:
        with self.assertRaises(FDRValidationError):
            FDRHeader(3, "A", (), (), (FDRDataref("sim/test/value", 1),), (), None)
        with self.assertRaises(FDRValidationError):
            FDRHeader(4, "A", (), (), (), (FDRLegacyColumn("longitude"),), None)

    def test_header_rejects_invalid_version_origin_and_entry_types(self) -> None:
        invalid_headers = (
            lambda: FDRHeader(cast(Literal[3, 4], True), "A", (), (), (), (), None),
            lambda: FDRHeader(cast(Literal[3, 4], 5), "A", (), (), (), (), None),
            lambda: FDRHeader(4, cast(Literal["A", "I"], "X"), (), (), (), (), None),
            lambda: FDRHeader(4, "A", cast(tuple[str, ...], (1,)), (), (), (), None),
            lambda: FDRHeader(4, "A", (), cast(tuple[FDRMetadata, ...], ("TAIL N1",)), (), (), None),
            lambda: FDRHeader(4, "A", (), (), cast(tuple[FDRDataref, ...], ("sim/test",)), (), None),
        )
        for constructor in invalid_headers:
            with self.subTest(constructor=constructor), self.assertRaises(FDRValidationError):
                constructor()

    def test_header_rejects_unhashable_version_and_origin_with_validation_error(self) -> None:
        invalid_headers = (
            lambda: FDRHeader(cast(Literal[3, 4], []), "A", (), (), (), (), None),
            lambda: FDRHeader(4, cast(Literal["A", "I"], []), (), (), (), (), None),
        )

        for constructor in invalid_headers:
            with self.subTest(constructor=constructor), self.assertRaises(FDRValidationError):
                constructor()

    def test_date_metadata_accepts_documented_formats_and_derives_local_date(self) -> None:
        cases = (
            ("08/09/2026", date(2026, 8, 9)),
            ("08/09/26", date(2026, 8, 9)),
            ("2026-08-09", date(2026, 8, 9)),
        )
        for declared, expected in cases:
            with self.subTest(declared=declared):
                header = make_v4_header(metadata=(FDRMetadata("DATE", declared),))
                self.assertEqual(expected, header.local_date)

    def test_header_rejects_invalid_or_inconsistent_local_date(self) -> None:
        invalid_headers = (
            lambda: make_v4_header(metadata=(FDRMetadata("DATE", "02/30/2026"),)),
            lambda: make_v4_header(metadata=(FDRMetadata("DATE", "2026/08/09"),)),
            lambda: make_v4_header(local_date=date(2026, 8, 9)),
            lambda: make_v4_header(metadata=(FDRMetadata("DATE", "08/09/2026"),), local_date=date(2026, 8, 10)),
            lambda: make_v4_header(
                metadata=(FDRMetadata("DATE", "08/09/2026"),),
                local_date=cast(date, datetime(2026, 8, 9)),
            ),
        )
        for constructor in invalid_headers:
            with self.subTest(constructor=constructor), self.assertRaises(FDRValidationError):
                constructor()

    def test_metadata_value_returns_last_ordered_value(self) -> None:
        header = make_v4_header(metadata=(FDRMetadata("TAIL", "N1"), FDRMetadata("TAIL", "N2")))

        self.assertEqual("N2", header.metadata_value("TAIL"))
        self.assertIsNone(header.metadata_value("ACFN"))


class FDRRecordingTests(unittest.TestCase):
    """Verify schema widths, duration, and explicit normalization."""

    def test_recording_rejects_additional_and_legacy_row_width_mismatches(self) -> None:
        v4_header = make_v4_header(datarefs=(FDRDataref("sim/test/value", 1),))
        v3_header = FDRHeader(3, "I", (), (), (), (FDRLegacyColumn("longitude"),), None)

        with self.assertRaises(FDRValidationError):
            FDRRecording(v4_header, (make_sample(),))
        with self.assertRaises(FDRValidationError):
            FDRRecording(v4_header, (make_sample(additional_values=(1,), legacy_values=(2,)),))
        with self.assertRaises(FDRValidationError):
            FDRRecording(v3_header, (make_sample(),))
        with self.assertRaises(FDRValidationError):
            FDRRecording(v3_header, (make_sample(additional_values=(1,), legacy_values=(2,)),))

    def test_recording_rejects_wrong_header_and_sample_types(self) -> None:
        with self.assertRaises(FDRValidationError):
            FDRRecording(cast(FDRHeader, "header"), ())
        with self.assertRaises(FDRValidationError):
            FDRRecording(make_v4_header(), cast(tuple[FDRSample, ...], ("sample",)))

    def test_duration_counts_an_observed_midnight_rollover(self) -> None:
        recording = FDRRecording(
            make_v4_header(),
            (
                make_sample(time_utc=time(23, 59, 59, 500000)),
                make_sample(time_utc=time(0, 0, 0, 250000)),
                make_sample(time_utc=time(0, 0, 2)),
            ),
        )

        self.assertEqual(timedelta(seconds=2.5), recording.duration)
        self.assertEqual(timedelta(), FDRRecording(make_v4_header(), ()).duration)

    def test_resolved_datetimes_require_explicit_date_and_use_utc(self) -> None:
        recording = FDRRecording(
            make_v4_header(),
            (make_sample(time_utc=time(23, 59, 59)), make_sample(time_utc=time(0, 0, 1))),
        )

        resolved = recording.resolved_utc_datetimes(date(2026, 8, 9))

        self.assertEqual(
            (
                datetime(2026, 8, 9, 23, 59, 59, tzinfo=UTC),
                datetime(2026, 8, 10, 0, 0, 1, tzinfo=UTC),
            ),
            resolved,
        )
        with self.assertRaises(FDRValidationError):
            recording.resolved_utc_datetimes(cast(date, datetime(2026, 8, 9)))

    def test_v3_normalization_requires_lossy_opt_in_and_reports_omissions(self) -> None:
        legacy_columns = (FDRLegacyColumn("longitude"), FDRLegacyColumn("engine_rpm"))
        v3 = FDRRecording(
            FDRHeader(3, "I", (), (), (), legacy_columns, None),
            (make_sample(legacy_values=(-87.9, 2400)),),
        )

        with self.assertRaises(FDRValidationError):
            v3.normalized_v4()
        result = v3.normalized_v4(allow_lossy_legacy=True)

        self.assertIsInstance(result, FDRNormalizationResult)
        self.assertEqual(("longitude", "engine_rpm"), result.omitted_legacy_field_ids)
        self.assertEqual(4, result.recording.header.source_version)
        self.assertEqual((), result.recording.header.legacy_columns)
        self.assertEqual((), result.recording.samples[0].legacy_values)
        self.assertEqual((-87.9048, 41.9742), (result.recording.samples[0].longitude, result.recording.samples[0].latitude))

    def test_v3_normalization_requires_opt_in_even_without_samples_or_columns(self) -> None:
        recording = FDRRecording(FDRHeader(3, "A", (), (), (), (), None), ())

        with self.assertRaises(FDRValidationError):
            recording.normalized_v4()

    def test_v4_normalization_is_identity_without_omissions(self) -> None:
        recording = FDRRecording(make_v4_header(), (make_sample(),))

        result = recording.normalized_v4()

        self.assertIs(recording, result.recording)
        self.assertEqual((), result.omitted_legacy_field_ids)

    def test_normalization_result_rejects_non_v4_and_invalid_omissions(self) -> None:
        v3 = FDRRecording(FDRHeader(3, "A", (), (), (), (), None), ())

        with self.assertRaises(FDRValidationError):
            FDRNormalizationResult(v3, ())
        with self.assertRaises(FDRValidationError):
            FDRNormalizationResult(FDRRecording(make_v4_header(), ()), cast(tuple[str, ...], (1,)))


if __name__ == "__main__":
    unittest.main()
