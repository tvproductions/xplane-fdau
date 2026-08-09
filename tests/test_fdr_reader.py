"""Tests for incremental version 4 FDR parsing."""

from __future__ import annotations

from datetime import date, time
import io
from pathlib import Path
import tempfile
from typing import override
from unittest import mock
import unittest

from xplane_fdr import FDRParseError, FDRReader, FDRSampleStream, FDRValidationError


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fdr"


def fdr_text(*records: str, origin: str = "A", version: str = "4") -> str:
    """Build literal FDR text without borrowing parser logic."""
    return "\n".join((origin, version, *records, ""))


class NamedStringIO(io.StringIO):
    """A real in-memory text stream with a diagnostic source name."""

    def __init__(self, value: str, name: str = "memory.fdr") -> None:
        super().__init__(value)
        self.name = name


class ShortChunkTextIO(NamedStringIO):
    """Return fewer characters than requested and reject line iteration."""

    def __init__(self, value: str, chunk_size: int) -> None:
        super().__init__(value, "short-chunks.fdr")
        self.chunk_size = chunk_size
        self.request_sizes: list[int] = []

    @override
    def read(self, size: int | None = -1, /) -> str:
        if size is None or size < 1:
            raise AssertionError("reader must request bounded positive chunks")
        self.request_sizes.append(size)
        return super().read(min(size, self.chunk_size))

    @override
    def readline(self, size: int | None = -1, /) -> str:
        raise AssertionError("reader must normalize lines from bounded chunks")


class FDRReaderValidV4Tests(unittest.TestCase):
    """Verify accepted version 4 syntax and preservation behavior."""

    def test_open_streams_samples_and_read_collects_the_same_parser(self) -> None:
        reader = FDRReader()

        with reader.open(FIXTURE_ROOT / "version4-minimal.fdr") as stream:
            self.assertIsInstance(stream, FDRSampleStream)
            self.assertEqual(4, stream.header.source_version)
            first = next(stream)
            self.assertEqual(-87.9048, first.longitude)
            self.assertEqual((0.25,), first.additional_values)
        recording = reader.read(FIXTURE_ROOT / "version4-minimal.fdr")

        self.assertEqual(2, len(recording.samples))
        self.assertEqual(stream.header, recording.header)

    def test_header_is_eager_but_sample_validation_is_lazy(self) -> None:
        source = NamedStringIO(
            fdr_text(
                "TAIL, N123XF",
                "12:00:00, 1, 2, 3, 4, 5, 6",
                "12:00:01, not-a-number, 2, 3, 4, 5, 6",
            )
        )

        stream = FDRReader().open(source)

        self.assertEqual("N123XF", stream.header.metadata_value("TAIL"))
        self.assertEqual(1, next(stream).longitude)
        with self.assertRaises(FDRParseError) as caught:
            next(stream)
        self.assertEqual(5, caught.exception.line)

    def test_origin_markers_and_version_suffix_are_accepted(self) -> None:
        for origin in ("A", "I"):
            with self.subTest(origin=origin):
                source = NamedStringIO(
                    fdr_text(
                        "12:00:00, 1, 2, 3, 4, 5, 6",
                        origin=origin,
                        version="4 X-Plane 12.1.4",
                    )
                )

                recording = FDRReader().read(source)

                self.assertEqual(origin, recording.header.source_origin)
                self.assertEqual(4, recording.header.source_version)

    def test_cr_lf_and_crlf_are_normalized_from_short_chunks(self) -> None:
        records = (
            "COMM, split boundaries",
            "12:00:00, 1, 2, 3, 4, 5, 6",
            "12:00:01, 2, 3, 4, 5, 6, 7",
        )
        for separator in ("\r", "\n", "\r\n"):
            with self.subTest(separator=repr(separator)):
                text = separator.join(("A", "4", *records, ""))
                source = ShortChunkTextIO(text, chunk_size=1)

                recording = FDRReader().read(source)

                self.assertEqual(2, len(recording.samples))
                self.assertEqual(("split boundaries",), recording.header.comments)
                self.assertTrue(source.request_sizes)
                self.assertTrue(all(0 < size <= 8192 for size in source.request_sizes))

    def test_metadata_comments_and_dataref_details_remain_ordered(self) -> None:
        recording = FDRReader().read(
            NamedStringIO(
                fdr_text(
                    "COMM, first comment",
                    "ZZZZ, opaque value",
                    "TAIL, N111AA",
                    "TAIL, N222BB",
                    "DATE, 2026-08-09",
                    "DREF, sim/test/one -2.5 // signed conversion",
                    "DREF, sim/test/two 3 //",
                    "COMM, second comment",
                    "01:02:03.123456, 1, 2, 3, 4, 5, 6, 7, 8",
                )
            )
        )

        header = recording.header
        self.assertEqual(("first comment", "second comment"), header.comments)
        self.assertEqual(
            (("ZZZZ", "opaque value"), ("TAIL", "N111AA"), ("TAIL", "N222BB"), ("DATE", "2026-08-09")),
            tuple((item.key, item.value) for item in header.metadata),
        )
        self.assertEqual("N222BB", header.metadata_value("TAIL"))
        self.assertEqual(date(2026, 8, 9), header.local_date)
        self.assertEqual(
            (("sim/test/one", -2.5, "signed conversion"), ("sim/test/two", 3, "")),
            tuple((item.path, item.scale, item.comment) for item in header.datarefs),
        )
        self.assertEqual(time(1, 2, 3, 123456), recording.samples[0].time_utc)

    def test_integer_lexemes_stay_exact_and_decimal_exponents_are_floats(self) -> None:
        huge = "9" * 400
        recording = FDRReader().read(
            NamedStringIO(
                fdr_text(
                    f"DREF, sim/test/huge {huge}",
                    f"01:02:03.5, -1, +2, {huge}, 4e1, .5, -6., {huge}",
                )
            )
        )

        sample = recording.samples[0]
        self.assertIs(type(recording.header.datarefs[0].scale), int)
        self.assertIs(type(sample.longitude), int)
        self.assertIs(type(sample.latitude), int)
        self.assertIs(type(sample.altitude_msl_ft), int)
        self.assertIs(type(sample.heading_magnetic_deg), float)
        self.assertIs(type(sample.pitch_deg), float)
        self.assertIs(type(sample.roll_deg), float)
        self.assertEqual(int(huge), sample.altitude_msl_ft)
        self.assertEqual((int(huge),), sample.additional_values)


class FDRReaderOwnershipTests(unittest.TestCase):
    """Verify resource ownership independently of parse results."""

    def test_caller_stream_remains_open_after_success_close_and_failure(self) -> None:
        successful = NamedStringIO(fdr_text("12:00:00, 1, 2, 3, 4, 5, 6"))
        with FDRReader().open(successful) as stream:
            self.assertEqual(1, next(stream).longitude)
        self.assertFalse(successful.closed)

        malformed = NamedStringIO("X\n4\n")
        with self.assertRaises(FDRParseError):
            FDRReader().open(malformed)
        self.assertFalse(malformed.closed)

    def test_path_opened_stream_is_closed_on_context_exit_and_header_failure(self) -> None:
        good_stream = NamedStringIO(fdr_text("12:00:00, 1, 2, 3, 4, 5, 6"), "good.fdr")
        with mock.patch("pathlib.Path.open", return_value=good_stream):
            with FDRReader().open(Path("good.fdr")) as samples:
                self.assertEqual(1, next(samples).longitude)
        self.assertTrue(good_stream.closed)

        bad_stream = NamedStringIO("X\n4\n", "bad.fdr")
        with mock.patch("pathlib.Path.open", return_value=bad_stream):
            with self.assertRaises(FDRParseError):
                FDRReader().open(Path("bad.fdr"))
        self.assertTrue(bad_stream.closed)

    def test_path_opened_stream_is_closed_when_lazy_sample_parsing_fails(self) -> None:
        owned_stream = NamedStringIO(fdr_text("12:00:00, invalid, 2, 3, 4, 5, 6"), "lazy-error.fdr")
        with mock.patch("pathlib.Path.open", return_value=owned_stream):
            samples = FDRReader().open(Path("lazy-error.fdr"))
            with self.assertRaises(FDRParseError):
                next(samples)

        self.assertTrue(owned_stream.closed)

    def test_real_path_source_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flight.fdr"
            path.write_text(fdr_text("12:00:00, 1, 2, 3, 4, 5, 6"), encoding="utf-8")

            recording = FDRReader().read(path)

        self.assertEqual(1, recording.samples[0].longitude)


class FDRReaderMalformedV4Tests(unittest.TestCase):
    """Verify malformed structures fail with typed source context."""

    def assert_parse_error(self, text: str, *, line: int, message_part: str) -> None:
        source = NamedStringIO(text)
        with self.assertRaises(FDRParseError) as caught:
            FDRReader().read(source)
        self.assertEqual("memory.fdr", caught.exception.source)
        self.assertEqual(line, caught.exception.line)
        self.assertIn(message_part, caught.exception.message)
        self.assertIn(f"memory.fdr:{line}:", str(caught.exception))

    def test_malformed_origin_and_version_markers_are_rejected(self) -> None:
        cases = (
            ("", 1, "origin"),
            ("X\n4\n", 1, "origin"),
            ("A extra\n4\n", 1, "origin"),
            ("A\n", 2, "version"),
            ("A\n5\n", 2, "version"),
            ("A\n4suffix\n", 2, "version"),
        )
        for text, line, message in cases:
            with self.subTest(text=repr(text)):
                self.assert_parse_error(text, line=line, message_part=message)

    def test_malformed_header_records_and_declarations_are_rejected(self) -> None:
        cases = (
            (fdr_text("BAD, value"), 3, "metadata"),
            (fdr_text("TOOLONG, value"), 3, "metadata"),
            (fdr_text("ABCD value"), 3, "comma"),
            (fdr_text("DREF, sim/test/value"), 3, "DataRef"),
            (fdr_text("DREF, 1"), 3, "DataRef"),
            (fdr_text("DREF, sim/test/value 1 trailing"), 3, "DataRef"),
        )
        for text, line, message in cases:
            with self.subTest(text=text):
                self.assert_parse_error(text, line=line, message_part=message)

    def test_python_only_number_lexemes_are_rejected(self) -> None:
        bad_numbers = ("1_000", "0x10", "1+2j", "--1", "+")
        for bad_number in bad_numbers:
            with self.subTest(number=bad_number):
                self.assert_parse_error(
                    fdr_text(f"12:00:00, {bad_number}, 2, 3, 4, 5, 6"),
                    line=3,
                    message_part="number",
                )

    def test_malformed_times_are_rejected(self) -> None:
        bad_times = ("24:00:00", "12:60:00", "12:00:60", "12:00", "12:00:00.", "12:00:00.1234567")
        for bad_time in bad_times:
            with self.subTest(time=bad_time):
                self.assert_parse_error(
                    fdr_text(f"{bad_time}, 1, 2, 3, 4, 5, 6"),
                    line=3,
                    message_part="time",
                )

    def test_row_widths_must_match_mandatory_and_declared_fields(self) -> None:
        cases = (
            fdr_text("12:00:00, 1, 2, 3, 4, 5"),
            fdr_text("12:00:00, 1, 2, 3, 4, 5, 6, 7"),
            fdr_text("DREF, sim/test/value 1", "12:00:00, 1, 2, 3, 4, 5, 6"),
            fdr_text("DREF, sim/test/value 1", "12:00:00, 1, 2, 3, 4, 5, 6, 7, 8"),
        )
        for text in cases:
            with self.subTest(text=text):
                expected_line = 4 if text.startswith("A\n4\nDREF") else 3
                self.assert_parse_error(text, line=expected_line, message_part="columns")

    def test_duplicate_datarefs_are_validation_errors_at_the_declaration(self) -> None:
        source = NamedStringIO(fdr_text("DREF, sim/test/value 1", "DREF, sim/test/value 2"))

        with self.assertRaises(FDRValidationError) as caught:
            FDRReader().read(source)

        self.assertEqual(("memory.fdr", 4), (caught.exception.source, caught.exception.line))
        self.assertIn("unique", caught.exception.message)

    def test_header_records_after_samples_are_rejected_lazily(self) -> None:
        source = NamedStringIO(
            fdr_text(
                "12:00:00, 1, 2, 3, 4, 5, 6",
                "COMM, too late",
            )
        )

        with FDRReader().open(source) as stream:
            self.assertEqual(1, next(stream).longitude)
            with self.assertRaises(FDRParseError) as caught:
                next(stream)

        self.assertEqual(("memory.fdr", 4), (caught.exception.source, caught.exception.line))
        self.assertIn("header", caught.exception.message)

    def test_model_validation_failures_keep_source_and_line(self) -> None:
        source = NamedStringIO(fdr_text("12:00:00, 181, 2, 3, 4, 5, 6"), "coordinates.fdr")

        with self.assertRaises(FDRValidationError) as caught:
            FDRReader().read(source)

        self.assertEqual(("coordinates.fdr", 3), (caught.exception.source, caught.exception.line))
        self.assertIn("longitude", caught.exception.message)

    def test_nonfinite_lexemes_and_float_overflow_are_validation_errors(self) -> None:
        for value in ("nan", "+Inf", "-Infinity", "1e9999"):
            with self.subTest(value=value):
                source = NamedStringIO(fdr_text(f"12:00:00, {value}, 2, 3, 4, 5, 6"))

                with self.assertRaises(FDRValidationError) as caught:
                    FDRReader().read(source)

                self.assertEqual(3, caught.exception.line)
                self.assertIn("finite", caught.exception.message)


if __name__ == "__main__":
    unittest.main()
