# Verification prerequisite: native FDR hour-range compatibility

This is a separately reviewed compatibility correction to the existing native
FDR reader, not a T1.3 tooling deliverable or a new runtime capability.

## Existing intent and observed regression

`tests/test_fdr_reader.py` already requires both v3 TIME headers and v4 sample
times to reject `24:00:00` with contextual FDRParseError. The runtime supports
Python 3.12 through 3.14. Task 4's installed Python 3.14.4 full run failed those
two unchanged tests, and an isolated export of base `1e00bdd` reproduces both.
The controller also observed `datetime.time.fromisoformat('24:00:00')` return
`00:00:00` on that interpreter. The current reader's lexical hour pattern is
one or two arbitrary digits and delegates hour validity to this conversion.

## Bounded correction

Own only `xplane_fdau/formats/xplane_fdr/reader.py`,
`tests/test_fdr_reader.py` if needed, and your report. Make the lexical hour
range explicitly 0-23 while preserving existing one-digit-hour support,
fractional precision, minute/second validation, and contextual exceptions.
Prefer the minimal `_TIMESTAMP_PATTERN` correction; no runtime dependencies,
version-policy changes, broad reader refactor, or weakened/skipped tests.

1. Run the two existing failing methods on installed Python 3.14.4 and record
   RED before editing:
   `FDRReaderMalformedV3Tests.test_time_header_is_required_and_must_be_zulu_time`
   and `FDRReaderMalformedV4Tests.test_malformed_times_are_rejected` in
   `tests.test_fdr_reader`.
2. Apply the minimal fix. Use meaningful existing or added boundary controls
   proving single-digit valid hours, midnight, last valid hour/fractions, and
   invalid hour 24 remain consistent for v3/v4. Do not add implementation-mirror
   tests merely to assert the regex.
3. Run the complete reader module on installed Python 3.12, 3.13, and 3.14,
   then full unittest discovery on 3.14 and the repository's aggregate
   `uv run python tools/quality.py check`, strict MkDocs, and `git diff --check`.
   Inspect exit codes. Existing Task4 real-document findings are unrelated.
4. Self-review, commit explicit files with a compatibility-fix subject, and
   write exact commands, versions, RED/GREEN output, counts, scope, and concerns
   to `python314-time-report.md` beside this brief. Commit the report explicitly.
   Do not spawn subagents; controller supplies independent scoped review.

This restores previously asserted behavior across supported interpreters.
No release, publication, remote synchronization, or new format authority is
implied. The original Task4 evidence must continue to record the baseline failure.
