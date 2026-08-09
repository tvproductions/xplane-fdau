"""Tests for canonical, durable version 4 FDR writing."""

from __future__ import annotations

from dataclasses import replace
from datetime import time
import io
import os
from pathlib import Path
import tempfile
from typing import cast, Literal, override
from unittest import mock
import unittest

from xplane_fdr import (
    FDRDataref,
    FDRHeader,
    FDRMetadata,
    FDRNormalizationResult,
    FDROutputError,
    FDRReader,
    FDRRecording,
    FDRRecordingStateError,
    FDRSample,
    FDRStreamWriter,
    FDRValidationError,
    FDRWriter,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fdr"


def make_header(
    *,
    origin: Literal["A", "I"] = "A",
    comments: tuple[str, ...] = (),
    metadata: tuple[FDRMetadata, ...] = (),
    datarefs: tuple[FDRDataref, ...] = (),
) -> FDRHeader:
    """Build a directly constructed v4 header."""
    return FDRHeader(4, origin, comments, metadata, datarefs, (), None)


def make_sample(
    *,
    time_utc: time = time(1, 2, 3, 123456),
    additional_values: tuple[int | float, ...] = (),
) -> FDRSample:
    """Build a directly constructed semantic sample."""
    return FDRSample(time_utc, 1.25, 2, 3.5, 4, 5.0, -6.25, additional_values, ())


def make_recording(*, samples: tuple[FDRSample, ...] | None = None) -> FDRRecording:
    """Build a recording whose bytes have hand-checkable values."""
    header = make_header(
        origin="I",
        comments=("first café", "second, comment"),
        metadata=(FDRMetadata("ZZZZ", "opaque value"), FDRMetadata("TAIL", "N123XF")),
        datarefs=(FDRDataref("sim/test/one", -2.5, "signed conversion"), FDRDataref("sim/test/two", 3, "")),
    )
    return FDRRecording(header, samples if samples is not None else (make_sample(additional_values=(7, 8.0)),))


class OwnershipStream(io.StringIO):
    """Caller stream that records flushes and rejects durability ownership."""

    def __init__(self) -> None:
        super().__init__()
        self.flush_count = 0
        self.fileno_count = 0

    @override
    def flush(self) -> None:
        self.flush_count += 1
        super().flush()

    @override
    def fileno(self) -> int:
        self.fileno_count += 1
        raise AssertionError("caller stream fileno must not be requested")


class BodyAndCleanupFailureStream(OwnershipStream):
    """Fail the first sample write, then fail abort-time flushing."""

    def __init__(self) -> None:
        super().__init__()
        self.write_count = 0

    @override
    def write(self, value: str) -> int:
        self.write_count += 1
        if self.write_count == 2:
            raise OSError("body write failed")
        return super().write(value)

    @override
    def flush(self) -> None:
        raise OSError("cleanup flush failed")


class FDRWriterCanonicalTests(unittest.TestCase):
    """Verify one deterministic serializer serves complete and streamed writes."""

    def test_write_emits_exact_utf8_lf_v4_bytes_in_model_order(self) -> None:
        expected = (
            b"A\n"
            b"4\n"
            b"COMM, first caf\xc3\xa9\n"
            b"COMM, second, comment\n"
            b"ZZZZ, opaque value\n"
            b"TAIL, N123XF\n"
            b"DREF, sim/test/one -2.5 // signed conversion\n"
            b"DREF, sim/test/two 3 //\n"
            b"01:02:03.123456, 1.25, 2, 3.5, 4, 5.0, -6.25, 7, 8.0\n"
        )
        recording = make_recording()

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            result = FDRWriter().write(recording, destination)

            self.assertEqual(expected, destination.read_bytes())
            canonical = replace(recording, header=replace(recording.header, source_origin="A"))
            self.assertEqual(canonical, FDRReader().read(destination))
        self.assertEqual(FDRNormalizationResult(recording, ()), result)

    def test_complete_and_streamed_writes_produce_identical_text(self) -> None:
        recording = make_recording()
        complete = io.StringIO()
        streamed = io.StringIO()

        FDRWriter().write(recording, complete)
        with FDRWriter().open(recording.header, streamed) as sink:
            for sample in recording.samples:
                sink.write_sample(sample)
            sink.commit()

        self.assertEqual(complete.getvalue(), streamed.getvalue())

    def test_rendering_is_repeatable_and_does_not_copy_source_origin(self) -> None:
        recording = make_recording()
        first = io.StringIO()
        second = io.StringIO()

        FDRWriter().write(recording, first)
        FDRWriter().write(recording, second)

        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertTrue(first.getvalue().startswith("A\n4\n"))
        self.assertNotIn("DATE,", first.getvalue())

    def test_stream_rejects_a_sample_with_the_wrong_declared_width_before_writing(self) -> None:
        header = make_header(datarefs=(FDRDataref("sim/test/value", 1),))
        stream = io.StringIO()

        with FDRWriter().open(header, stream) as sink:
            before = stream.getvalue()
            with self.assertRaises(FDRValidationError):
                sink.write_sample(make_sample())
            self.assertEqual(before, stream.getvalue())

    def test_header_is_fully_validated_before_a_partial_is_created(self) -> None:
        header = make_header(comments=("line one\nline two",))

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            with self.assertRaises(FDRValidationError):
                FDRWriter().open(header, destination)

            self.assertEqual((), tuple(Path(directory).iterdir()))


class FDRWriterNormalizationTests(unittest.TestCase):
    """Verify writing v3 data requires the model's explicit lossy opt-in."""

    def test_version_3_refusal_happens_before_output_creation(self) -> None:
        recording = FDRReader().read(FIXTURE_ROOT / "version3-minimal.fdr")

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "legacy.fdr"
            with self.assertRaises(FDRValidationError):
                FDRWriter().write(recording, destination)

            self.assertEqual((), tuple(Path(directory).iterdir()))

    def test_lossy_version_3_write_reports_omissions_and_writes_readable_v4(self) -> None:
        recording = FDRReader().read(FIXTURE_ROOT / "version3-minimal.fdr")

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "normalized.fdr"
            result = FDRWriter().write(recording, destination, allow_lossy_legacy=True)
            reread = FDRReader().read(destination)

        self.assertEqual(tuple(column.field_id for column in recording.header.legacy_columns), result.omitted_legacy_field_ids)
        self.assertEqual(4, reread.header.source_version)
        self.assertEqual((), reread.header.legacy_columns)
        self.assertEqual(
            (recording.samples[0].longitude, recording.samples[0].latitude),
            (reread.samples[0].longitude, reread.samples[0].latitude),
        )


class FDRStreamWriterOwnershipTests(unittest.TestCase):
    """Verify caller streams retain lifecycle and durability ownership."""

    def test_commit_flushes_caller_stream_without_closing_or_requesting_fileno(self) -> None:
        stream = OwnershipStream()

        with FDRWriter().open(make_header(), stream) as sink:
            self.assertIsInstance(sink, FDRStreamWriter)
            sink.write_sample(make_sample())
            sink.commit()

        self.assertFalse(stream.closed)
        self.assertEqual(1, stream.flush_count)
        self.assertEqual(0, stream.fileno_count)

    def test_context_exit_without_commit_aborts_and_rejects_future_operations(self) -> None:
        stream = OwnershipStream()

        with FDRWriter().open(make_header(), stream) as sink:
            sink.write_sample(make_sample())

        self.assertFalse(stream.closed)
        with self.assertRaises(FDRRecordingStateError):
            sink.commit()
        with self.assertRaises(FDRRecordingStateError):
            sink.write_sample(make_sample())

    def test_body_and_abort_cleanup_failures_are_grouped_primary_first(self) -> None:
        stream = BodyAndCleanupFailureStream()

        with self.assertRaises(BaseExceptionGroup) as caught:
            with FDRWriter().open(make_header(), stream) as sink:
                sink.write_sample(make_sample())

        primary, cleanup = caught.exception.exceptions
        self.assertIsInstance(primary, FDROutputError)
        self.assertEqual("body write failed", str(primary.__cause__))
        self.assertIsInstance(cleanup, FDROutputError)
        self.assertEqual("cleanup flush failed", str(cleanup.__cause__))
        self.assertFalse(stream.closed)

    def test_zero_sample_commit_and_double_commit_are_state_errors(self) -> None:
        empty_stream = io.StringIO()
        empty = FDRWriter().open(make_header(), empty_stream)
        with self.assertRaises(FDRRecordingStateError):
            empty.commit()
        empty.abort()

        committed_stream = io.StringIO()
        committed = FDRWriter().open(make_header(), committed_stream)
        committed.write_sample(make_sample())
        committed.commit()
        with self.assertRaises(FDRRecordingStateError):
            committed.commit()


class FDRWriterPathPublicationTests(unittest.TestCase):
    """Verify path writes synchronize partials and publish only at commit."""

    def test_path_commit_fsyncs_then_publishes_and_removes_partial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            with (
                mock.patch("xplane_fdr.writer.os.fsync", wraps=os.fsync) as fsync,
                mock.patch("xplane_fdr.writer.os.link", wraps=os.link) as link,
                mock.patch("xplane_fdr.writer.os.replace", wraps=os.replace) as replace,
            ):
                sink = FDRWriter().open(make_header(), destination)
                partial = sink.partial_path
                self.assertEqual(destination, sink.destination_path)
                self.assertIsNotNone(partial)
                self.assertTrue(cast(Path, partial).exists())
                self.assertFalse(destination.exists())
                sink.write_sample(make_sample())
                sink.commit()

            fsync.assert_called_once()
            link.assert_called_once()
            replace.assert_not_called()
            self.assertTrue(destination.exists())
            self.assertFalse(cast(Path, partial).exists())

    def test_existing_target_is_untouched_until_no_replace_commit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            destination.write_text("existing", encoding="utf-8")
            sink = FDRWriter().open(make_header(), destination)
            sink.write_sample(make_sample())
            self.assertEqual("existing", destination.read_text(encoding="utf-8"))

            with self.assertRaises(FDROutputError) as caught:
                sink.commit()

            self.assertEqual("existing", destination.read_text(encoding="utf-8"))
            self.assertIsInstance(caught.exception.__cause__, FileExistsError)
            self.assertTrue(cast(Path, sink.partial_path).exists())

    def test_overwrite_replaces_only_during_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            destination.write_text("existing", encoding="utf-8")
            sink = FDRWriter().open(make_header(), destination, overwrite=True)
            sink.write_sample(make_sample())
            self.assertEqual("existing", destination.read_text(encoding="utf-8"))

            with mock.patch("xplane_fdr.writer.os.replace", wraps=os.replace) as replace:
                sink.commit()

            replace.assert_called_once()
            self.assertTrue(destination.read_bytes().startswith(b"A\n4\n"))

    def test_fsync_failure_is_wrapped_and_preserves_diagnostic_partial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            sink = FDRWriter().open(make_header(), destination)
            sink.write_sample(make_sample())
            partial = cast(Path, sink.partial_path)

            with mock.patch("xplane_fdr.writer.os.fsync", side_effect=OSError("sync failed")):
                with self.assertRaises(FDROutputError) as caught:
                    sink.commit()

            self.assertEqual(partial, caught.exception.artifact_path)
            self.assertEqual("sync failed", str(caught.exception.__cause__))
            self.assertTrue(partial.exists())
            self.assertFalse(destination.exists())

    def test_clean_context_abort_preserves_unpublished_partial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            with FDRWriter().open(make_header(), destination) as sink:
                sink.write_sample(make_sample())
                partial = cast(Path, sink.partial_path)

            self.assertFalse(destination.exists())
            self.assertTrue(partial.exists())


if __name__ == "__main__":
    unittest.main()
