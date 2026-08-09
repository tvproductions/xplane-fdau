"""Command-line contract tests for the offline FDR toolkit."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import override
from unittest import mock
import unittest

from xplane_fdau.formats.xplane_fdr import FDROutputError
from xplane_fdau.cli import _write_atomic_json, build_parser, main


VALID_FDR = """A
4
COMM, deterministic fixture
DATE, 08/07/2026
ACFT, Q4XP
DREF, sim/test/value 2.0 // Test value
23:59:59, -87.9048, 41.9742, 1000, 270, 2, -1, 3
00:00:01, -87.8, 42.0, 1100, 271, 1, 0, 4
"""


class FailingAtomicStream:
    """Real sibling stream with narrowly injected output failures."""

    def __init__(self, path: Path, *, failure: str = "none", close_failure: bool = False) -> None:
        self._stream = path.open("x", encoding="utf-8", newline="\n")
        self._failure = failure
        self._close_failure = close_failure

    @property
    def closed(self) -> bool:
        """Expose the real stream's ownership state."""
        return self._stream.closed

    def write(self, text: str) -> int:
        """Write unless this stream injects a write failure."""
        if self._failure == "write":
            raise OSError("injected write failure")
        return self._stream.write(text)

    def flush(self) -> None:
        """Flush unless this stream injects a flush failure."""
        if self._failure == "flush":
            raise OSError("injected flush failure")
        self._stream.flush()

    def fileno(self) -> int:
        """Return the real file descriptor for fsync."""
        return self._stream.fileno()

    def close(self) -> None:
        """Close the real stream, optionally reporting a cleanup failure."""
        self._stream.close()
        if self._close_failure:
            raise OSError("injected close cleanup failure")


class FDRCliTests(unittest.TestCase):
    """Verify the public command shapes, streams, statuses, and summaries."""

    @override
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.input = self.root / "flight.fdr"
        self.input.write_text(VALID_FDR, encoding="utf-8", newline="")

    def capture_main(self, arguments: list[str]) -> tuple[int, str, str]:
        """Run the public entry point with captured text streams."""
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(arguments)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_parser_accepts_only_the_documented_offline_command_shapes(self) -> None:
        parser = build_parser()
        commands = (
            ["fdr", "validate", str(self.input)],
            ["fdr", "inspect", str(self.input), "--json", "--first-utc-date", "2026-08-07"],
            [
                "fdr",
                "to-geojson",
                str(self.input),
                str(self.root / "flight.geojson"),
                "--first-utc-date",
                "2026-08-07",
                "--overwrite",
            ],
        )

        for arguments in commands:
            with self.subTest(command=arguments[1]):
                parsed = parser.parse_args(arguments)
                self.assertEqual("fdr", parsed.domain)
                self.assertEqual(arguments[1], parsed.command)
        status, stdout, stderr = self.capture_main(["live-record"])
        self.assertEqual((2, ""), (status, stdout))
        self.assertIn("invalid choice", stderr)

    def test_help_lists_the_fdr_domain_on_stdout(self) -> None:
        status, stdout, stderr = self.capture_main(["--help"])

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("fdr", stdout)
        for command in ("inspect", "validate", "to-geojson"):
            self.assertNotIn(command, stdout)
        self.assertNotIn("live-record", stdout)

    def test_fdr_help_lists_exactly_the_three_offline_native_commands(self) -> None:
        status, stdout, stderr = self.capture_main(["fdr", "--help"])

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        for command in ("inspect", "validate", "to-geojson"):
            self.assertIn(command, stdout)
        self.assertNotIn("live-record", stdout)

    def test_flat_native_commands_are_rejected(self) -> None:
        for arguments in (
            ["validate", str(self.input)],
            ["inspect", str(self.input)],
            ["to-geojson", str(self.input), str(self.root / "flight.geojson")],
        ):
            with self.subTest(arguments=arguments):
                status, stdout, stderr = self.capture_main(arguments)
                self.assertEqual((2, ""), (status, stdout))
                self.assertIn("invalid choice", stderr)
                self.assertNotIn("Traceback", stderr)

    def test_validate_is_silent_on_success(self) -> None:
        status, stdout, stderr = self.capture_main(["fdr", "validate", str(self.input)])

        self.assertEqual((0, "", ""), (status, stdout, stderr))

    def test_library_failures_are_concise_stderr_only_with_line_context(self) -> None:
        self.input.write_text("A\n4\n12:00:00, invalid, 2, 3, 4, 5, 6\n", encoding="utf-8")

        status, stdout, stderr = self.capture_main(["fdr", "validate", str(self.input)])

        self.assertEqual(1, status)
        self.assertEqual("", stdout)
        self.assertEqual(1, len(stderr.splitlines()))
        self.assertIn("xplane-fdau: validate failed", stderr)
        self.assertIn(f"{self.input}:3:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_missing_input_is_a_concise_stderr_only_failure(self) -> None:
        missing = self.root / "missing.fdr"

        status, stdout, stderr = self.capture_main(["fdr", "inspect", str(missing)])

        self.assertEqual(1, status)
        self.assertEqual("", stdout)
        self.assertEqual(1, len(stderr.splitlines()))
        self.assertIn("inspect failed", stderr)
        self.assertIn(str(missing), stderr)
        self.assertNotIn("Traceback", stderr)

    def test_inspect_json_is_compact_sorted_strict_and_exactly_lf_terminated(self) -> None:
        status, stdout, stderr = self.capture_main(["fdr", "inspect", str(self.input), "--json"])

        document = json.loads(stdout)
        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertTrue(stdout.endswith("\n"))
        self.assertFalse(stdout.endswith("\n\n"))
        self.assertNotIn(": ", stdout)
        self.assertEqual(sorted(document), list(document))
        self.assertEqual(4, document["version"])
        self.assertEqual("A", document["origin"])
        self.assertEqual("2026-08-07", document["local_date"])
        self.assertEqual(2, document["sample_count"])
        self.assertEqual("23:59:59", document["start_utc"])
        self.assertEqual("00:00:01", document["end_utc"])
        self.assertEqual(2.0, document["duration_seconds"])
        self.assertEqual("Q4XP", document["effective_metadata"]["ACFT"])
        self.assertEqual("sim/test/value", document["datarefs"][0]["path"])
        self.assertEqual("sim/test/value", document["fields"][-1])

    def test_inspect_json_bypasses_windows_newline_translation(self) -> None:
        raw_stdout = io.BytesIO()
        translated_stdout = io.TextIOWrapper(raw_stdout, encoding="utf-8", newline="\r\n")
        stderr = io.StringIO()
        with redirect_stdout(translated_stdout), redirect_stderr(stderr):
            status = main(["fdr", "inspect", str(self.input), "--json"])
            translated_stdout.flush()

        self.assertEqual(0, status)
        self.assertNotIn(b"\r", raw_stdout.getvalue())
        self.assertTrue(raw_stdout.getvalue().endswith(b"\n"))
        self.assertEqual("", stderr.getvalue())

    def test_inspect_resolves_the_explicit_first_utc_date_across_midnight(self) -> None:
        status, stdout, stderr = self.capture_main(["fdr", "inspect", str(self.input), "--json", "--first-utc-date", "2026-08-07"])

        document = json.loads(stdout)
        self.assertEqual(0, status)
        self.assertEqual("2026-08-07T23:59:59Z", document["start_utc"])
        self.assertEqual("2026-08-08T00:00:01Z", document["end_utc"])
        self.assertEqual("", stderr)

    def test_inspect_human_output_contains_the_normalized_summary(self) -> None:
        status, stdout, stderr = self.capture_main(["fdr", "inspect", str(self.input)])

        self.assertEqual(0, status)
        for text in (
            "Version: 4",
            "Origin: A",
            "Samples: 2",
            "Start UTC: 23:59:59",
            "Duration: 2.000 seconds",
            "sim/test/value",
            "ACFT: Q4XP",
        ):
            self.assertIn(text, stdout)
        self.assertEqual("", stderr)

    def test_invalid_arguments_return_status_two_without_a_traceback(self) -> None:
        cases = (
            ["fdr", "inspect", str(self.input), "--first-utc-date", "2026-02-30"],
            ["fdr", "inspect", str(self.input), "--first-utc-date", "20260807"],
            ["fdr", "inspect", str(self.input), "--first-utc-date", "2026-W32-5"],
            ["fdr", "validate"],
            ["fdr", "to-geojson", str(self.input)],
        )

        for arguments in cases:
            with self.subTest(arguments=arguments):
                status, stdout, stderr = self.capture_main(list(arguments))
                self.assertEqual(2, status)
                self.assertEqual("", stdout)
                self.assertNotEqual("", stderr)
                self.assertNotIn("Traceback", stderr)

    def test_to_geojson_writes_strict_canonical_atomic_output_with_timestamps(self) -> None:
        output = self.root / "flight.geojson"

        status, stdout, stderr = self.capture_main(["fdr", "to-geojson", str(self.input), str(output), "--first-utc-date", "2026-08-07"])

        payload = output.read_bytes()
        document = json.loads(payload)
        self.assertEqual((0, "", ""), (status, stdout, stderr))
        self.assertTrue(payload.endswith(b"\n"))
        self.assertNotIn(b"\r", payload)
        self.assertNotIn(b": ", payload)
        self.assertEqual("FeatureCollection", document["type"])
        self.assertEqual(
            "2026-08-07T23:59:59Z",
            document["features"][0]["properties"]["timestamp_utc"],
        )
        self.assertEqual([], list(self.root.glob(f".{output.name}.*.partial")))

    def test_to_geojson_protects_existing_output_unless_overwrite_is_explicit(self) -> None:
        output = self.root / "flight.geojson"
        output.write_text("existing\n", encoding="utf-8")

        status, stdout, stderr = self.capture_main(["fdr", "to-geojson", str(self.input), str(output)])

        self.assertEqual((1, ""), (status, stdout))
        self.assertIn("already exists", stderr)
        self.assertEqual("existing\n", output.read_text(encoding="utf-8"))
        self.assertEqual([], list(self.root.glob(f".{output.name}.*.partial")))

        status, stdout, stderr = self.capture_main(["fdr", "to-geojson", str(self.input), str(output), "--overwrite"])
        self.assertEqual((0, "", ""), (status, stdout, stderr))
        self.assertEqual("FeatureCollection", json.loads(output.read_text(encoding="utf-8"))["type"])

    def test_to_geojson_serializes_before_creating_any_partial(self) -> None:
        output = self.root / "flight.geojson"

        with (
            mock.patch("xplane_fdau.cli.json.dumps", side_effect=ValueError("strict JSON failure")),
            mock.patch("xplane_fdau.cli._create_partial") as create_partial,
        ):
            status, stdout, stderr = self.capture_main(["fdr", "to-geojson", str(self.input), str(output)])

        self.assertEqual((1, ""), (status, stdout))
        self.assertIn("strict JSON failure", stderr)
        self.assertFalse(output.exists())
        create_partial.assert_not_called()

    def test_console_script_executes_the_public_help_surface(self) -> None:
        completed = subprocess.run(
            ["uv", "run", "--frozen", "xplane-fdau", "--help"],
            cwd=Path(__file__).parents[1],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("fdr", completed.stdout)
        self.assertNotIn("to-geojson", completed.stdout)
        self.assertEqual("", completed.stderr)


class FDRCliAtomicOutputTests(unittest.TestCase):
    """Verify publication races, durability ordering, and cleanup evidence."""

    @override
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_no_overwrite_commit_uses_a_unique_sibling_and_removes_it(self) -> None:
        output = self.root / "flight.geojson"
        real_link = os.link
        observed: list[tuple[Path, Path]] = []

        def observe_link(source: str | os.PathLike[str], destination: str | os.PathLike[str]) -> None:
            source_path = Path(source)
            destination_path = Path(destination)
            observed.append((source_path, destination_path))
            self.assertEqual(output.parent, source_path.parent)
            self.assertTrue(source_path.name.startswith(f".{output.name}."))
            self.assertTrue(source_path.name.endswith(".partial"))
            real_link(source_path, destination_path)

        with mock.patch("xplane_fdau.cli.os.link", side_effect=observe_link):
            _write_atomic_json({"type": "FeatureCollection", "features": []}, output, overwrite=False)

        self.assertEqual(1, len(observed))
        self.assertEqual(output, observed[0][1])
        self.assertEqual([], list(self.root.glob(f".{output.name}.*.partial")))
        self.assertEqual(
            b'{"features":[],"type":"FeatureCollection"}\n',
            output.read_bytes(),
        )

    def test_prepublication_failures_remove_the_owned_partial_and_keep_destination_absent(self) -> None:
        for stage in ("write", "flush", "fsync", "link"):
            with self.subTest(stage=stage):
                output = self.root / f"{stage}.geojson"
                partial = self.root / f".{output.name}.injected.partial"

                def create_partial(_destination: Path) -> tuple[Path, FailingAtomicStream]:
                    failure = stage if stage in {"write", "flush"} else "none"
                    return partial, FailingAtomicStream(partial, failure=failure)

                patches = [mock.patch("xplane_fdau.cli._create_partial", side_effect=create_partial)]
                if stage == "fsync":
                    patches.append(mock.patch("xplane_fdau.cli.os.fsync", side_effect=OSError("injected fsync failure")))
                elif stage == "link":
                    patches.append(mock.patch("xplane_fdau.cli.os.link", side_effect=OSError("injected link failure")))

                with patches[0]:
                    if len(patches) == 1:
                        with self.assertRaisesRegex(ValueError, f"injected {stage} failure"):
                            _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=False)
                    else:
                        with patches[1], self.assertRaisesRegex(ValueError, f"injected {stage} failure"):
                            _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=False)

                self.assertFalse(partial.exists())
                self.assertFalse(output.exists())

    def test_a_no_overwrite_race_preserves_the_raced_destination(self) -> None:
        output = self.root / "flight.geojson"
        partial = self.root / ".flight.geojson.injected.partial"

        def create_partial(_destination: Path) -> tuple[Path, FailingAtomicStream]:
            return partial, FailingAtomicStream(partial)

        def race_destination(_source: Path, destination: Path) -> None:
            destination.write_text("raced\n", encoding="utf-8")
            raise FileExistsError("injected link race")

        with (
            mock.patch("xplane_fdau.cli._create_partial", side_effect=create_partial),
            mock.patch("xplane_fdau.cli.os.link", side_effect=race_destination),
            self.assertRaisesRegex(ValueError, "injected link race"),
        ):
            _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=False)

        self.assertEqual("raced\n", output.read_text(encoding="utf-8"))
        self.assertFalse(partial.exists())

    def test_post_link_partial_cleanup_failure_keeps_published_output_and_partial(self) -> None:
        output = self.root / "flight.geojson"
        partial = self.root / ".flight.geojson.injected.partial"
        real_unlink = os.unlink
        unlink_calls: list[Path] = []

        def create_partial(_destination: Path) -> tuple[Path, FailingAtomicStream]:
            return partial, FailingAtomicStream(partial)

        def fail_partial_unlink(path: str | os.PathLike[str]) -> None:
            unlink_calls.append(Path(path))
            if Path(path) == partial:
                raise OSError("injected partial unlink failure")
            real_unlink(path)

        with (
            mock.patch("xplane_fdau.cli._create_partial", side_effect=create_partial),
            mock.patch("xplane_fdau.cli.os.unlink", side_effect=fail_partial_unlink),
            self.assertRaises(FDROutputError) as caught,
        ):
            _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=False)

        self.assertIn("publication succeeded but partial cleanup failed", str(caught.exception))
        self.assertEqual(partial, caught.exception.artifact_path)
        self.assertEqual("injected partial unlink failure", str(caught.exception.__cause__))
        self.assertEqual([partial], unlink_calls)
        self.assertTrue(output.exists())
        self.assertTrue(partial.exists())
        partial.unlink()

    def test_partial_already_absent_after_link_is_a_successful_publication(self) -> None:
        output = self.root / "flight.geojson"
        partial = self.root / ".flight.geojson.injected.partial"
        real_unlink = os.unlink

        def create_partial(_destination: Path) -> tuple[Path, FailingAtomicStream]:
            return partial, FailingAtomicStream(partial)

        def remove_partial_then_report_missing(path: str | os.PathLike[str]) -> None:
            real_unlink(path)
            if Path(path) == partial:
                raise FileNotFoundError("partial was already removed")

        with (
            mock.patch("xplane_fdau.cli._create_partial", side_effect=create_partial),
            mock.patch("xplane_fdau.cli.os.unlink", side_effect=remove_partial_then_report_missing),
        ):
            try:
                _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=False)
            except Exception as error:
                self.fail(f"already-absent partial must be successful: {error!r}")

        self.assertFalse(partial.exists())
        self.assertEqual("FeatureCollection", json.loads(output.read_text(encoding="utf-8"))["type"])

    def test_partial_unlink_failure_never_removes_a_replaced_destination(self) -> None:
        output = self.root / "flight.geojson"
        partial = self.root / ".flight.geojson.injected.partial"
        replacement = self.root / "replacement.tmp"
        replacement.write_text("replacement\n", encoding="utf-8")
        real_unlink = os.unlink

        def create_partial(_destination: Path) -> tuple[Path, FailingAtomicStream]:
            return partial, FailingAtomicStream(partial)

        def replace_destination_then_fail(path: str | os.PathLike[str]) -> None:
            if Path(path) == partial:
                os.replace(replacement, output)
                raise OSError("injected partial unlink failure after replacement")
            real_unlink(path)

        with (
            mock.patch("xplane_fdau.cli._create_partial", side_effect=create_partial),
            mock.patch("xplane_fdau.cli.os.unlink", side_effect=replace_destination_then_fail),
            self.assertRaisesRegex(ValueError, "injected partial unlink failure after replacement"),
        ):
            _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=False)

        self.assertTrue(output.exists())
        self.assertEqual("replacement\n", output.read_text(encoding="utf-8"))
        self.assertTrue(partial.exists())
        partial.unlink()

    def test_to_geojson_reports_published_output_with_partial_cleanup_failure(self) -> None:
        input_path = self.root / "flight.fdr"
        input_path.write_text(VALID_FDR, encoding="utf-8")
        output = self.root / "flight.geojson"

        with mock.patch("xplane_fdau.cli.os.unlink", side_effect=OSError("injected partial cleanup failure")):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main(["fdr", "to-geojson", str(input_path), str(output)])

        partials = list(self.root.glob(f".{output.name}.*.partial"))
        self.assertEqual(1, status)
        self.assertEqual("", stdout.getvalue())
        self.assertEqual(1, len(partials))
        self.assertIn("publication succeeded but partial cleanup failed", stderr.getvalue())
        self.assertIn(str(partials[0]), stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
        self.assertTrue(output.exists())

    def test_primary_and_close_cleanup_failures_keep_primary_first_and_unlink_partial(self) -> None:
        output = self.root / "flight.geojson"
        partial = self.root / ".flight.geojson.injected.partial"

        def create_partial(_destination: Path) -> tuple[Path, FailingAtomicStream]:
            return partial, FailingAtomicStream(partial, failure="write", close_failure=True)

        with (
            mock.patch("xplane_fdau.cli._create_partial", side_effect=create_partial),
            self.assertRaises(BaseExceptionGroup) as caught,
        ):
            _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=False)

        messages = [str(error) for error in caught.exception.exceptions]
        self.assertIn("injected write failure", messages[0])
        self.assertIn("injected close cleanup failure", messages[1])
        self.assertFalse(partial.exists())
        self.assertFalse(output.exists())

    def test_overwrite_uses_replace_only_and_preserves_existing_on_failure(self) -> None:
        output = self.root / "flight.geojson"
        output.write_text("existing\n", encoding="utf-8")

        with mock.patch("xplane_fdau.cli.os.replace", side_effect=OSError("injected replace failure")):
            with self.assertRaisesRegex(ValueError, "injected replace failure"):
                _write_atomic_json({"type": "FeatureCollection"}, output, overwrite=True)

        self.assertEqual("existing\n", output.read_text(encoding="utf-8"))
        self.assertEqual([], list(self.root.glob(f".{output.name}.*.partial")))

        with mock.patch("xplane_fdau.cli.os.link", side_effect=AssertionError("overwrite must not link")):
            _write_atomic_json({"type": "FeatureCollection", "features": []}, output, overwrite=True)

        self.assertEqual("FeatureCollection", json.loads(output.read_text(encoding="utf-8"))["type"])


if __name__ == "__main__":
    unittest.main()
