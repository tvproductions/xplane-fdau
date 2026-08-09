# Task 6 Report: Native FDR Reader Header Complexity

## Scope

Refactored only `FDRSampleStream` native-header parsing.  The refactor splits
origin parsing, version parsing, header collection, header-record dispatch, and
header construction into private helpers backed by a private `_HeaderState`
accumulator.  It preserves the public reader API and existing parse, validation,
source, line-number, metadata-ordering, and encoding behavior.

## Characterization evidence

Before production changes, added and ran the table-driven
`FDRReaderHeaderCharacterizationTests.test_headers_preserve_records_samples_and_failure_lines`.
It characterizes:

- ordered blank lines, comments, opaque metadata, `DATE`, v4 `DREF`
  declarations, and the first v4 sample boundary;
- v3 `TIME`, legacy `DREF` metadata, `DATE`, and the first `DATA` sample
  boundary; and
- missing-comma and malformed-key header failures, including `memory.fdr`
  source context, exact line 3, and exact parser messages.

The pre-refactor reader suite passed with 28 tests.  The intentional RED gate
was `uv run python tools/quality.py complexity`, which reported:

`xplane_fdau\\formats\\xplane_fdr\\reader.py:185 _parse_header` has rank D.

## Xenon result

After decomposition, the exact configured command
`uv run xenon --max-absolute C --max-modules B --max-average A xplane_fdau`
exited zero.  No Xenon block is worse than C.

## Verification

- Focused reader suite: 28 tests passed.
- Focused reader/model/CLI suites passed.
- Full `unittest discover -v`: 193 tests passed.
- Ruff check and format check passed.
- `ty check` passed.
- Exact Xenon target passed.
- `git diff --check` passed before this report was added; it must be rerun as
  part of the final commit verification.

## Concern

The aggregate `uv run python tools/quality.py check` exits 1 at the
detect-secrets baseline step.  It flags two SHA-256 provenance literals in the
migration plan and their two matching literals in `tests/test_documentation.py`.
All four are present at the declared Task 6 base commit; Task 6 does not modify them.
No unrelated documentation or security-baseline change was made.

## Fix Round 1

Review found one semantic regression in the initial decomposition.  BASE used
direct `int()` conversion for a lexically numeric version, so Python's integer
digit limit caused a 5,000-digit version to raise raw `ValueError` without FDR
source or line context.  The initial Task 6 change translated that failure to
`FDRParseError` with an `invalid version integer` diagnostic.

Added
`test_unbounded_numeric_version_preserves_raw_integer_conversion_failure`
before changing production code.  Its RED run failed because the observed
exception type was `FDRParseError`, not exact `ValueError`.  Restoring direct
conversion made the focused regression test and all 29 reader tests pass while
retaining the helper decomposition.

Fix-round verification:

- focused reader/model/CLI suites: 85 tests passed;
- full `unittest discover -v`: 194 tests passed;
- Ruff check and format check passed;
- `ty check` passed; and
- exact Xenon max-C target passed.
