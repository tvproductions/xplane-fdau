# Python 3.14 native-reader compatibility correction

Date: 2026-09-05
Baseline: `3d6e0a1c616f651db9e75156639a69842d9aaa21`
Scope: `xplane_fdau/formats/xplane_fdr/reader.py`,
`tests/test_fdr_reader.py`, and this report only.

## Root cause

Python 3.14.4 normalizes `time.fromisoformat("24:00:00")` to midnight. The
reader's prior lexical pattern accepted any one- or two-digit hour, so the
existing v3 and v4 malformed-time tests no longer raised `FDRParseError`.

## RED

Interpreter version command:

```powershell
& 'C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe' --version
```

Output: `Python 3.14.4` (exit code 0).

Required failing-test command:

```powershell
& 'C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe' -m unittest tests.test_fdr_reader.FDRReaderMalformedV3Tests.test_time_header_is_required_and_must_be_zulu_time tests.test_fdr_reader.FDRReaderMalformedV4Tests.test_malformed_times_are_rejected -v
```

Result: `Ran 2 tests`; `FAILED (failures=2)` (exit code 1). The failures were
the v3 `TIME, 24:00:00` case and the v4 `24:00:00` sample case; both reported
`AssertionError: FDRParseError not raised`.

The added boundary characterization was run before the production edit:

```powershell
& 'C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe' -m unittest tests.test_fdr_reader.FDRReaderValidV4Tests.test_hour_boundaries_are_valid_for_v3_and_v4 -v
```

Result: `Ran 1 test`; `OK` (exit code 0).

## Correction and GREEN

`_TIMESTAMP_PATTERN` now lexically accepts hours `0` through `23`, including
single-digit and leading-zero forms, while retaining the existing minute,
second, and one-to-six-digit fractional syntax. The boundary test exercises
`0:00:00`, `00:00:00`, and `23:59:59.999999` for both v3 header times and v4
sample times. Existing malformed tests continue to exercise `24:00:00` for
both versions and preserve source-line context.

Installed interpreter versions:

| Interpreter | Version |
| --- | --- |
| `C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe` | Python 3.12.13 |
| `C:\Users\Jeff\AppData\Local\Programs\Python\Python313\python.exe` | Python 3.13.15 |
| `C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe` | Python 3.14.4 |

For each interpreter, this command passed:

```powershell
& '<interpreter>' -m unittest tests.test_fdr_reader -v
```

Result for each: `Ran 30 tests`; `OK` (exit code 0).

Full Python 3.14 discovery:

```powershell
& 'C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe' -m unittest discover
```

Result: `Ran 355 tests in 37.014s`; `OK` (exit code 0). The first sandboxed
attempt reached the same suite but failed in an existing subprocess test with
`PermissionError: [WinError 5]` while launching `uv`; the passing rerun used
the required elevated execution boundary.

Aggregate repository quality gate:

```powershell
uv run python tools/quality.py check
```

Result: exit code 0. Ruff, format check, ty, 355 unittest tests, 94% total
coverage, Bandit, detect-secrets, Interrogate, Vulture, and Xenon all passed.

Strict documentation build:

```powershell
uv run mkdocs build --strict
```

Result: exit code 0; documentation built successfully. MkDocs emitted the
upstream Material-for-MkDocs 2.0 informational warning.

Whitespace check:

```powershell
git diff --check
```

Result: exit code 0.

## Review and concerns

The final diff contains only the bounded lexical-hour correction, its
behavioral boundary test, and this report. No runtime dependency, format
authority, version policy, or unrelated reader behavior changed. The only
environmental concern was the sandbox's inability to launch `uv`; required
checks passed with elevation. The change is committed with subject:
`fix: bound native fdr timestamp hours`.
