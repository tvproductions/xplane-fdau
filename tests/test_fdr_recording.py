"""Tests for push-first recording sessions and artifact resolution."""

from __future__ import annotations

from collections.abc import Iterator
import dataclasses
from datetime import UTC, datetime, time, timedelta, timezone
import io
import math
from pathlib import Path
import tempfile
from typing import cast, override
import unittest

from xplane_fdau.formats.xplane_fdr import (
    FDRDataref,
    FDRHeader,
    FDRReader,
    FDRRecordingDefinition,
    FDRRecordingSession,
    FDRRecordingStateError,
    FDRSample,
    FDRSampleSource,
    FDRSamplingPolicy,
    FDRStoragePolicy,
    FDRValidationError,
)


def make_header(*, dataref_count: int = 0) -> FDRHeader:
    """Build a minimal version 4 header with a hand-selected row width."""
    return FDRHeader(
        4,
        "A",
        (),
        (),
        tuple(FDRDataref(f"sim/test/value_{index}", 1) for index in range(dataref_count)),
        (),
        None,
    )


def make_sample(
    *,
    time_utc: time = time(12),
    additional_values: tuple[int | float, ...] = (),
) -> FDRSample:
    """Build one valid semantic sample."""
    return FDRSample(time_utc, -87.9, 41.9, 700, 270, 2, -1, additional_values, ())


def make_definition(
    *,
    header: FDRHeader | None = None,
    directory: Path = Path("Output/FDR files"),
    filename: str | None = None,
) -> FDRRecordingDefinition:
    """Build a recording definition with explicit immutable policies."""
    return FDRRecordingDefinition(
        header=header or make_header(),
        sampling=FDRSamplingPolicy(),
        storage=FDRStoragePolicy(directory=directory, filename=filename),
    )


class OwnershipStream(io.StringIO):
    """Caller stream that records flushes and remains caller-owned."""

    def __init__(self) -> None:
        super().__init__()
        self.flush_count = 0

    @override
    def flush(self) -> None:
        self.flush_count += 1
        super().flush()


class SampleIterable:
    """Concrete structural implementation of the source protocol."""

    def __init__(self, samples: tuple[FDRSample, ...]) -> None:
        self.samples = samples
        self.iteration_count = 0

    def __iter__(self) -> Iterator[FDRSample]:
        self.iteration_count += 1
        return iter(self.samples)


class TrackingRecordingSession(FDRRecordingSession):
    """Session variant that makes ``record_from`` forwarding observable."""

    recorded_samples: list[FDRSample]

    @override
    def record(self, sample: FDRSample) -> None:
        self.recorded_samples.append(sample)
        super().record(sample)


class FDRRecordingPolicyTests(unittest.TestCase):
    """Verify definitions are immutable and reject invalid policy values."""

    def test_policies_and_definition_are_frozen_slotted_values(self) -> None:
        values = (FDRSamplingPolicy(), FDRStoragePolicy(), make_definition())

        for value in values:
            with self.subTest(value=type(value).__name__):
                self.assertTrue(dataclasses.is_dataclass(value))
                self.assertFalse(hasattr(value, "__dict__"))
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    value.__setattr__(dataclasses.fields(value)[0].name, None)

    def test_sampling_policy_requires_positive_finite_floats(self) -> None:
        self.assertEqual((0.1, None), (FDRSamplingPolicy().interval_seconds, FDRSamplingPolicy().duration_seconds))
        self.assertEqual(12.5, FDRSamplingPolicy(0.25, 12.5).duration_seconds)

        for bad_value in (0.0, -0.1, math.inf, -math.inf, math.nan, True, 1):
            with self.subTest(value=bad_value), self.assertRaises(FDRValidationError):
                FDRSamplingPolicy(interval_seconds=bad_value)
            with self.subTest(duration=bad_value), self.assertRaises(FDRValidationError):
                FDRSamplingPolicy(duration_seconds=bad_value)

    def test_definition_requires_a_version_4_header_and_policy_instances(self) -> None:
        version_3 = FDRHeader(3, "A", (), (), (), (), None)
        invalid = (
            lambda: FDRRecordingDefinition(version_3, FDRSamplingPolicy(), FDRStoragePolicy()),
            lambda: FDRRecordingDefinition(cast(FDRHeader, "header"), FDRSamplingPolicy(), FDRStoragePolicy()),
            lambda: FDRRecordingDefinition(make_header(), cast(FDRSamplingPolicy, None), FDRStoragePolicy()),
            lambda: FDRRecordingDefinition(make_header(), FDRSamplingPolicy(), cast(FDRStoragePolicy, None)),
        )

        for constructor in invalid:
            with self.subTest(constructor=constructor), self.assertRaises(FDRValidationError):
                constructor()


class FDRDestinationResolutionTests(unittest.TestCase):
    """Verify explicit destination and filename precedence."""

    def test_complete_destination_has_highest_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "explicit.bin"
            session = FDRRecordingSession.open(
                destination,
                make_definition(filename="configured.fdr"),
                xplane_root=Path(directory) / "unused",
                filename="caller.fdr",
                utc_clock=lambda: (_ for _ in ()).throw(AssertionError("clock must not be read")),
            )

        self.assertEqual(destination, session.destination_path)

    def test_caller_filename_uses_configured_directory_and_overrides_configured_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = FDRRecordingSession.open(
                None,
                make_definition(directory=Path("Output/FDR files"), filename="configured.fdr"),
                xplane_root=root,
                filename="caller.fdr",
            )

            self.assertEqual(root / "Output/FDR files" / "caller.fdr", session.destination_path)

    def test_configured_filename_precedes_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session = FDRRecordingSession.open(
                None,
                make_definition(directory=Path("records"), filename="training.fdr"),
                xplane_root=directory,
                utc_clock=lambda: (_ for _ in ()).throw(AssertionError("clock must not be read")),
            )

            self.assertEqual(Path(directory) / "records" / "training.fdr", session.destination_path)

    def test_generated_name_uses_exact_aware_utc_microsecond_form(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            started = datetime(2026, 8, 8, 18, 30, 12, 123456, tzinfo=UTC)
            session = FDRRecordingSession.open(None, make_definition(), xplane_root=directory, started_at_utc=started)

            self.assertEqual("xplane-fdau-20260808T183012123456Z.fdr", cast(Path, session.destination_path).name)

    def test_generated_name_uses_injected_clock_once_and_normalizes_zero_offset_utc(self) -> None:
        calls = 0

        def clock() -> datetime:
            nonlocal calls
            calls += 1
            return datetime(2026, 1, 2, 3, 4, 5, 6, tzinfo=timezone(timedelta(0), "Zulu"))

        with tempfile.TemporaryDirectory() as directory:
            session = FDRRecordingSession.open(None, make_definition(), xplane_root=directory, utc_clock=clock)

        self.assertEqual(1, calls)
        self.assertEqual("xplane-fdau-20260102T030405000006Z.fdr", cast(Path, session.destination_path).name)

    def test_generated_name_rejects_naive_and_non_utc_instants(self) -> None:
        invalid = (
            datetime(2026, 8, 8, 18, 30),
            datetime(2026, 8, 8, 18, 30, tzinfo=timezone(timedelta(hours=-5))),
        )

        with tempfile.TemporaryDirectory() as directory:
            for started in invalid:
                with self.subTest(started=started), self.assertRaises(FDRValidationError):
                    FDRRecordingSession.open(None, make_definition(), xplane_root=directory, started_at_utc=started)
            with self.assertRaises(FDRValidationError):
                FDRRecordingSession.open(
                    None,
                    make_definition(),
                    xplane_root=directory,
                    utc_clock=lambda: cast(datetime, "not a datetime"),
                )

    def test_relative_storage_requires_xplane_root_but_absolute_storage_does_not(self) -> None:
        with self.assertRaises(FDRValidationError):
            FDRRecordingSession.open(None, make_definition(filename="flight.fdr"))

        with tempfile.TemporaryDirectory() as directory:
            absolute = Path(directory) / "records"
            session = FDRRecordingSession.open(None, make_definition(directory=absolute, filename="flight.fdr"))

            self.assertEqual(absolute / "flight.fdr", session.destination_path)

    def test_configured_and_caller_filenames_must_be_fdr_basenames(self) -> None:
        invalid_names = ("", "flight.txt", "FLIGHT.FDR", "nested/flight.fdr", r"nested\flight.fdr", "D:flight.fdr")

        for filename in invalid_names:
            with self.subTest(configured=filename), self.assertRaises(FDRValidationError):
                FDRStoragePolicy(filename=filename)
        with tempfile.TemporaryDirectory() as directory:
            for filename in invalid_names:
                with self.subTest(caller=filename), self.assertRaises(FDRValidationError):
                    FDRRecordingSession.open(None, make_definition(), xplane_root=directory, filename=filename)

    def test_caller_stream_bypasses_storage_and_clock_resolution(self) -> None:
        stream = OwnershipStream()
        session = FDRRecordingSession.open(
            stream,
            make_definition(),
            utc_clock=lambda: (_ for _ in ()).throw(AssertionError("clock must not be read")),
        )

        self.assertIsNone(session.destination_path)


class FDRRecordingSessionTests(unittest.TestCase):
    """Verify prepared, active, committed, and aborted session behavior."""

    def test_context_records_callback_samples_and_commits_readable_output(self) -> None:
        samples = (make_sample(time_utc=time(12)), make_sample(time_utc=time(12, 0, 1)))

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            with FDRRecordingSession.open(destination, make_definition()) as session:
                session.record(samples[0])
                session.record(samples[1])
                self.assertEqual(destination, session.commit())

            self.assertEqual(samples, FDRReader().read(destination).samples)

    def test_recording_before_entry_and_after_close_are_state_errors(self) -> None:
        stream = OwnershipStream()
        session = FDRRecordingSession.open(stream, make_definition())

        with self.assertRaises(FDRRecordingStateError):
            session.record(make_sample())
        with session:
            session.record(make_sample())
        with self.assertRaises(FDRRecordingStateError):
            session.record(make_sample())

    def test_double_commit_and_empty_commit_are_state_errors(self) -> None:
        session = FDRRecordingSession.open(OwnershipStream(), make_definition())
        with self.assertRaises(FDRRecordingStateError):
            with session:
                pass

        committed = FDRRecordingSession.open(OwnershipStream(), make_definition())
        with committed:
            committed.record(make_sample())
            self.assertIsNone(committed.commit())
            with self.assertRaises(FDRRecordingStateError):
                committed.commit()

    def test_invalid_width_is_rejected_before_append_and_session_can_continue(self) -> None:
        stream = OwnershipStream()
        definition = make_definition(header=make_header(dataref_count=1))

        with FDRRecordingSession.open(stream, definition) as session:
            before = stream.getvalue()
            with self.assertRaises(FDRValidationError):
                session.record(make_sample())
            self.assertEqual(before, stream.getvalue())
            session.record(make_sample(additional_values=(42,)))

        self.assertEqual((42,), FDRReader().read(io.StringIO(stream.getvalue())).samples[0].additional_values)

    def test_time_of_day_samples_preserve_midnight_rollover_semantics(self) -> None:
        samples = (
            make_sample(time_utc=time(23, 59, 59, 750000)),
            make_sample(time_utc=time(0, 0, 0, 250000)),
        )
        stream = OwnershipStream()

        with FDRRecordingSession.open(stream, make_definition()) as session:
            session.record_from(SampleIterable(samples))

        recording = FDRReader().read(io.StringIO(stream.getvalue()))
        self.assertEqual(samples, recording.samples)
        self.assertEqual(timedelta(microseconds=500000), recording.duration)

    def test_record_from_consumes_source_once_via_record_and_returns_count(self) -> None:
        source: FDRSampleSource = SampleIterable((make_sample(time_utc=time(1)), make_sample(time_utc=time(2))))
        stream = OwnershipStream()
        session = cast(TrackingRecordingSession, TrackingRecordingSession.open(stream, make_definition()))
        session.recorded_samples = []

        with session:
            count = session.record_from(source)

        self.assertEqual(2, count)
        self.assertEqual(1, source.iteration_count)
        self.assertEqual(tuple(source.samples), tuple(session.recorded_samples))
        self.assertEqual(2, len(FDRReader().read(io.StringIO(stream.getvalue())).samples))

    def test_exception_aborts_and_preserves_path_partial_without_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "flight.fdr"
            session = FDRRecordingSession.open(destination, make_definition())
            with self.assertRaisesRegex(RuntimeError, "capture failed"):
                with session:
                    session.record(make_sample())
                    raise RuntimeError("capture failed")

            self.assertFalse(destination.exists())
            self.assertIsNotNone(session.partial_path)
            self.assertTrue(cast(Path, session.partial_path).exists())
            with self.assertRaises(FDRRecordingStateError):
                session.commit()

    def test_caller_stream_remains_open_and_commit_returns_none(self) -> None:
        stream = OwnershipStream()
        session = FDRRecordingSession.open(stream, make_definition())

        with session:
            session.record(make_sample())

        self.assertIsNone(session.destination_path)
        self.assertIsNone(session.partial_path)
        self.assertFalse(stream.closed)
        self.assertEqual(1, stream.flush_count)


if __name__ == "__main__":
    unittest.main()
