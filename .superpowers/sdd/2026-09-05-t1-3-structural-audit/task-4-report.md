# Task 4 report: Git evidence and lifecycle sufficiency

Status: DONE_WITH_CONCERNS

Scope: `t1-3-structural-audit` worktree, implementation base `1e00bdd`;
controller refinement `770133f` authorizes the separate lifecycle module and
required audit source-section locations. The implementation commit accompanies
this report. No runtime package, authority document, policy bytes, remote, or
release state was changed.

## Changes

- Added frozen `EvidenceArtifact` and `parse_evidence(root, path)` with the exact
  contiguous ordered metadata family, positive optional gate ordinal, valid ISO
  date, and nonempty subject.
- Added `evidence_findings` and read-only `observed_bytes` in `backlog/evidence.py`.
  Git uses argument vectors, `shell=False`, literal pathspecs, NUL-delimited
  index/tree entries, and binary blob reads. Eligibility requires a contained
  regular Markdown file, a regular stage-zero entry, identical worktree/index
  bytes, and optional identical regular HEAD bytes. Ignored or untracked files,
  conflicts, index symlinks, missing/deleted files, raw newline changes, and Git
  failure close eligibility. Errors retain the referring node and gate.
- Added `lifecycle_findings` and `historical_plan_findings` in
  `backlog/lifecycle.py`, consuming typed admission data without child-ID
  conditionals. Ordinary requirements are stage-specific. Only current
  in-progress state requires selection; suspended in-progress state retains
  its plan requirement without selection. Later states retain design/plan
  approval, completion, review, and all-gate requirements. Dependencies use
  ROADMAP rather than mutable backlog dependency cells.
- Historical admission checks effective verified state, exact policy identity
  and digest, plan worktree/index/HEAD bytes, completed metadata and a
  disposition naming the child, approved covering design, verified prerequisites,
  relevant structural/adherence checks, and HEAD-backed review/all-gate evidence.
  It creates no approval or completion evidence and preserves suspension.
- Added separate lexical evidence ordering/duplicate checks and fixed slot-kind
  policy use for gates, completion, review, and release evidence. Kind and result
  failures remain distinct. Release evidence uses the release ID and absent gate.
- Added dashboard prerequisite/evidence checks and
  `release_authorization_findings` in `rules.py`. Exact managed prohibition and
  open publication-review forms are checked using section-bounded source facts.
  Missing sections are audit parse errors; missing forms retain section line
  context. Released child claims fail separately. Unrelated ordinary Git-sync
  prose does not grant publication or fail the publication guard.
- Extended fixture support with deterministic isolated Git setup, local identity,
  disabled hooks/signing/autocrlf, real evidence contents, and release sections.
  Added 20 focused unittest methods covering the required matrix and mutations.
  Existing version-1 serialization and CLI integration are unchanged.

Files changed: `backlog/audit.py`, `evidence.py`, `lifecycle.py`, `model.py`,
`parse.py`, `parse_sources.py`, `rules.py` under the hidden backlog-status scripts;
`tests/backlog_audit_support.py`, `tests/test_backlog_status_evidence.py`,
`tests/test_backlog_status_lifecycle.py`, and this report.

## TDD evidence

Initial RED, before implementation:

```text
uv run python -m unittest tests.test_backlog_status_evidence tests.test_backlog_status_lifecycle -v
Ran 17 tests in 0.002s
FAILED (failures=17)
AssertionError: unexpectedly None : evidence rule module must exist
AssertionError: unexpectedly None : lifecycle rule module must exist
exit 1
```

Additional historical structural-admission regression RED:

```text
uv run python -m unittest tests.test_backlog_status_lifecycle.LifecycleTests.test_historical_requires_structural_and_governing_acceptance_match -v
Ran 1 test in 0.712s
FAILED (failures=1)
AssertionError: 'lifecycle.historical-plan' not found in set()
exit 1
```

Intermediate scoped/all-backlog runs exposed a test-fixture inconsistency: making
the shared design draft while leaving the sibling child specified. The fixture
now makes that sibling queued. Adding relevant adherence checks then exposed
the real D1.2 gate drift described below; the positive control was moved to an
explicitly aligned isolated copy. An initial copy-rewrite bug consumed adjacent
gate lines and was corrected to replace only the gate's continuation lines.
The full quality gate also required `typing.override` on the new `setUp` methods;
those declarations were added and the complete gate restarted.

Final scoped GREEN:

```text
uv run python -m unittest tests.test_backlog_status_evidence tests.test_backlog_status_lifecycle -v
Ran 20 tests in 34.522s
OK
exit 0
```

All previous backlog audit tests were included in final full discovery. An
earlier explicit backlog-only discovery ran 113 tests and found only the
subsequently corrected designing-fixture problem.

## Final verification

Windows, default Python 3.12.13, unchanged production candidate:

```text
uv run python tools/quality.py check
All checks passed!                         (Ruff)
57 files already formatted                 (repository format check)
All checks passed!                         (ty)
Ran 354 tests in 41.661s
OK
Ran 354 tests in 44.133s                    (coverage run)
OK
TOTAL 1527 98 94%                          (coverage report)
RESULT: PASSED (minimum: 40.0%, actual: 43.6%)  (Interrogate)
Bandit, tracked-file detect-secrets, Vulture, Xenon: passed
exit 0

uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts
All checks passed!
exit 0

uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts
13 files already formatted
exit 0

uv run ty check .codex/skills/backlog-status/scripts
All checks passed!
exit 0

uv run mkdocs build --strict
Documentation built in 1.64 seconds
exit 0

git diff --check
git diff --cached --check
no output; exit 0

uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
schema_version=1 valid=True
exit 0
```

The status smoke is the existing pre-integration parser/report path; it does
not yet include these new rules. Task 5 owns CLI aggregation and the required
malformed-release audit/status JSON controls. MkDocs emitted its existing
Material advisory banner about a future framework version; strict build passed.

Supported-target verification uses already installed interpreters without
changing the shared virtual environment or downloading tools:

```text
& C:/Users/Jeff/AppData/Local/Programs/Python/Python313/python.exe -m unittest discover -v
Python 3.13.15
Ran 354 tests in 43.659s
OK
exit 0

& C:/Users/Jeff/AppData/Roaming/uv/python/cpython-3.14-windows-x86_64-none/python.exe -m unittest discover -v
Python 3.14.4
Ran 354 tests in 43.057s
FAILED (failures=2)
exit 1
```

The two Python 3.14 failures are unchanged runtime tests:
`tests.test_fdr_reader.FDRReaderMalformedV3Tests.test_time_header_is_required_and_must_be_zulu_time`
and `tests.test_fdr_reader.FDRReaderMalformedV4Tests.test_malformed_times_are_rejected`.
Both fail for `24:00:00` with `AssertionError: FDRParseError not raised`.
All Task 4 tests passed in that run. This is not an all-target full-suite pass.

Baseline reproduction exported `xplane_fdau`, `tests/__init__.py`, and
`tests/test_fdr_reader.py` from `git ls-tree -r --name-only -z 1e00bdd -- ...`
and binary `git show 1e00bdd:<path>` reads into a TemporaryDirectory, then ran
the following argument-vector command there:

```text
C:/Users/Jeff/AppData/Roaming/uv/python/cpython-3.14-windows-x86_64-none/python.exe -m unittest tests.test_fdr_reader.FDRReaderMalformedV3Tests.test_time_header_is_required_and_must_be_zulu_time tests.test_fdr_reader.FDRReaderMalformedV4Tests.test_malformed_times_are_rejected -v
Ran 2 tests in 0.002s
FAILED (failures=2)
AssertionError: FDRParseError not raised
exit 1

git diff 1e00bdd -- xplane_fdau tests/test_fdr_reader.py
no output; exit 0
```

The failure therefore precedes this task. Runtime changes are explicitly outside
Task 4; the compatibility concern is reported to the controller for separate
handling. No runtime fix, skipped test, or weakened expectation was introduced.

## Real repository findings and fixture normalization

The final new-family observation used `load_audit(Path.cwd())`,
`lifecycle_findings(loaded)`, and `release_authorization_findings(loaded)`:

```text
load 0 {}
lifecycle 1 {'lifecycle.historical-plan': 1}
Finding(code='lifecycle.historical-plan', severity='error', path='BACKLOG.md', line=91, node='D1.2', gate=None, message='historical admission requires valid structure and governing acceptance criteria')
release_authorization 0 {}
```

D1.2's four known `artifact.gate-drift` findings occur in
`docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md`
at lines 3972, 3976, 3980, and 3985. Historical admission must fail while these
remain: the supplement replaces only active-plan approval/completion fields,
not the structural or governing gate requirements. The controller confirmed
this interpretation and reserved the existing reviewed reconciliation for Task 5.
No real backlog, design, historical plan, evidence, or policy was corrected.

The D1.1-D1.3 positive control copies actual authority documents and linked
evidence into a temporary repository, changes only the copied D1.2 backlog gate
statements to its exact detailed approved design acceptance, and commits that
fixture. Historical plans, policy, and evidence retain exact original bytes.
All three admissions pass there. Generic historical fixtures independently test
suspended verified states, wrong identity/path/hash/state/disposition, missing or
edited evidence, unlisted historical links, and gate drift without exemptions.

## Self-review and limits

- Reviewed paths, raw Git mode/stage/blob handling, separate result diagnostics,
  ordinal context, effective versus current state, ordinary/historical plan
  boundary, independent error retention, and release section boundaries.
- Fixture Git writes use explicit local paths and local identity, no global Git
  configuration, hooks, signing, credentials, or network. TemporaryDirectory
  owns cleanup; no recursive shell deletion is used.
- Unicode and spaces, LF/CRLF, untracked/ignored/staged/committed/dirty/deleted,
  conflicting and symlink-mode entries are exercised with real local Git.
  Outside-root resolution is exercised through a controlled Path.resolve seam;
  actual platform symlink creation is not required. Linux/macOS execution was
  unavailable; the available Windows supported Python targets are recorded here.
- The full coverage figure measures the repository's configured runtime source
  paths, not hidden tooling coverage; hidden tooling is verified by focused
  unittest, explicit Ruff/ty commands, and regression controls.
- The remaining D1.2 finding is intentional fail-closed behavior, not suppressed
  debt. Publication remains prohibited. CLI integration is explicitly Task 5.
- Python 3.14.4 has the two independently reproduced baseline runtime failures
  above. Python 3.12.13 aggregate and Python 3.13.15 compatibility passed. This
  task does not claim every supported-target full suite is green.

## Review fix round 1

Base: `6022dda`; Task 4 reviewed implementation: `676d52e`. The separate
compatibility worker fixed the previously recorded Python 3.14 runtime failures
in `6022dda`; this correction round did not edit runtime files or their tests.
The independent review's two Important findings were reproduced and corrected.

1. `parse_evidence` now translates a failed positive-ordinal integer conversion
   to `MarkdownParseError` with `evidence.gate-mismatch` at metadata line 4.
   `evidence_findings` retains the referring child/gate. The regression uses a
   real committed 4,301-digit ordinal and confirms lifecycle aggregation also
   retains an independent missing-review `evidence.path` finding.
2. `_prefixed_statements` now collects a complete top-level list statement,
   joins continuations, and folds whitespace before checking the release
   prefix. Source locations retain the original first line. Tests cover four
   equivalent forms, all sixteen ordered duplicate pairs, and copies outside
   the Current-position section. Spaced and wrapped prefixes are recognized
   equally; equivalent duplicates produce `release.authorization` at the
   original second statement line.

The initial test run also exposed an error in subtest fixture reset handling;
restoration was moved to each subtest's beginning before recording the covering
RED. No production fix had been applied at that point.

Covering RED:

```text
uv run python -m unittest tests.test_backlog_status_evidence.EvidenceTests.test_oversized_gate_is_a_contextual_domain_finding tests.test_backlog_status_lifecycle.LifecycleTests.test_oversized_evidence_gate_preserves_independent_findings tests.test_backlog_status_lifecycle.LifecycleTests.test_release_prefix_normalization_precedes_discovery -v
Ran 3 tests in 1.186s
FAILED (failures=18, errors=2)
exit 1
```

The two errors were the reproduced uncaught `ValueError` from the 4,301-digit
Gate; the eighteen subtest failures were rejected valid forms or absent/wrongly
located equivalent-duplicate findings.

Covering GREEN, same exact command:

```text
Ran 3 tests in 1.137s
OK
exit 0
```

Final static and documentation verification:

```text
uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts
All checks passed!
exit 0
uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts
13 files already formatted
exit 0
uv run ty check .codex/skills/backlog-status/scripts
All checks passed!
exit 0
uv run mkdocs build --strict
Documentation built in 1.59 seconds
exit 0 (existing nonblocking Material advisory banner remains)
git diff --check
git diff --cached --check
no output; exit 0
```

Real source observation is unchanged: load 0, lifecycle 1, release authorization
0. The sole lifecycle finding remains `lifecycle.historical-plan` for D1.2 at
BACKLOG.md:91, caused by the preexisting four governing gate drifts. Authority
documents and this finding were preserved. The oversized BACKLOG gate-count
conversion is separately reserved for Task 5 and was not changed here.

Self-review checked that conversion error translation preserves exception
chaining without introducing an arbitrary ordinal range; normalization happens
after full-statement collection and before prefix selection; and source line
and section boundaries survive folding. Only the two reviewed corrections,
their three tests, and this report were changed in this round.

Supported-version full unittest results on the unchanged fix candidate:

```text
& C:/Users/Jeff/AppData/Local/Programs/Python/Python313/python.exe -m unittest discover -v
Ran 358 tests in 45.866s
OK
exit 0
& C:/Users/Jeff/AppData/Roaming/uv/python/cpython-3.14-windows-x86_64-none/python.exe -m unittest discover -v
Ran 358 tests in 45.062s
OK
exit 0
```

Required aggregate, run once on the unchanged production fix candidate:

```text
uv run python tools/quality.py check
All checks passed!                         (Ruff)
57 files already formatted
All checks passed!                         (ty)
Ran 358 tests in 45.703s                    (Python 3.12.13)
OK
Ran 358 tests in 41.379s                    (coverage run)
OK
TOTAL 1527 98 94%                          (configured runtime coverage)
RESULT: PASSED (minimum: 40.0%, actual: 43.6%)  (Interrogate)
Bandit, tracked-file detect-secrets, Vulture, Xenon: passed
exit 0
```

Round 1 result: both Important review findings corrected and covered; all
required gates and supported Python full unittest targets pass. Remaining
concerns are the unchanged D1.2 historical finding and Task 5 CLI integration.
