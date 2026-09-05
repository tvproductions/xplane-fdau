# Task 5 implementation candidate report

Date: 2026-09-05. Task base: `f92a88f200872099509c2bd6aa666716b8aa2091`.
Worktree: `C:/Users/Jeff/source/repos/xp/xplane-fdau/.worktrees/t1-3-structural-audit`.
Branch: `t1-3-structural-audit`. Scope: Task 5 implementation candidate,
awaiting controller task review, whole-branch review, and evidence closeout.
This is an implementer report, not accepted review or child completion evidence.

## Delivered candidate

`audit_repository` combines source, structural, adherence, lifecycle/evidence,
and release-policy findings. Both commands use the same audited report;
`status --json` preserves the exact version-1 shape. Findings sort using the
shared ordering; any error returns 1, warnings alone return 0, usage errors
return 2. Parse failures preserve independently valid authorities and JSON.
Git observation failure adds `git.unavailable`, retains an empty Git object,
and explicitly renders unavailable in human output. Audit has no JSON option;
future commands remain invalid usage.

Git observation disables optional locks, so mtime-only source changes cannot
refresh index bytes. BACKLOG integer conversion limits become contextual
`backlog.gate-count` findings without disabling Python's conversion limit.
The executable stdout stream uses UTF-8 and LF on Windows; in-process injected
streams and usage stderr behavior are preserved.

Complete temporary Git fixtures include committed evidence and policy instead
of pretending syntax-only fixture evidence is eligible. Tests exercise real
Git index/source/HEAD preservation, independent parse failures, unavailable
Git, warnings, stable reporting, legacy pipe encoding, and every missing,
duplicate, modified, or checked managed release form. A release fixture has
G1 satisfied with its verified prerequisite and committed evidence; the
publication guard still blocks all prohibited managed forms.

## RED and scoped GREEN

All unittest commands used Python 3.12.13 unless a matrix version is named.

1. `uv run python -m unittest tests.test_backlog_status_cli tests.test_backlog_status_report -v`
   initially exited 1: 21 tests, 9 failures and 3 errors. This included one
   fixture-token typo. After correcting that typo, the same RED command exited
   1: 21 tests, 11 failures and 2 errors. Expected evidence: audit returned 2;
   semantic-invalid status returned 0; malformed status emitted no JSON;
   oversized count raised raw ValueError; status and JSON changed index bytes;
   report rejected the new findings argument; unavailable Git lacked findings.
2. After wiring, the same 21-test command exited 1 with two failures: the real
   repository's known governance drift and an obsolete test treating `audit`
   as unknown usage. All new fixture regressions passed. The actual audit
   command exited 1 with exactly 23 findings: 22 accepted adherence corrections
   and dependent D1.2 `lifecycle.historical-plan`.
3. `uv run python -m unittest tests.test_backlog_status_cli.BacklogStatusCliTests.test_executable_stdout_is_utf8_with_lf_even_under_legacy_pipe_encoding -v`
   first encountered unreconciled findings (exit 1). On the reconciled tree,
   it exited 1 with UnicodeDecodeError for legacy byte `0x96`. After the bounded
   entrypoint fix, the process test passed for JSON and audit with UTF-8/LF.
4. The focused command adding `tests.test_backlog_governance` exposed old
   expectations tied to D1.2's earlier readiness summary. Those assertions now
   use its explicitly linked detailed design and exact numbered lead-in.
   Intermediate 54/55-test runs reported that assertion failure/error; the
   final command below passed all 55 tests in 33.512 seconds:

   `uv run python -m unittest tests.test_backlog_status_cli tests.test_backlog_status_report tests.test_backlog_governance -v`

5. Scoped Ruff identified long new expected strings and one import placement;
   these were formatted/fixed. Scoped ty identified stdout's broad TextIO type
   and dynamic module annotation; the entrypoint now narrows TextIOWrapper and
   test loading returns ModuleType. The first aggregate gate stopped on the
   resulting unused old type suppression; removing it allowed the next gate.

## Accepted reconciliation and preservation

Applied only `reconciliation-review.md`'s exact correction population:
C2.4 0/5; C3.3, T2.2, T3.1, and D1.2 statements match their directly linked
approved designs. Previously open gates remain open. D1.2 retains verified
4/4 with identical evidence links; independent reconciliation review had
already established every expanded clause's committed evidence coverage.

The active canonical design's single C4.4 sentence now matches existing
explicit-only ordinary Git-sync policy while preserving separate release
authorization. The exact old/new sentence, date, and existing AGENTS/HANDOFF
and approved adoption authority are recorded in the current Task 5 plan.
No original approval metadata or historical D1.1 review was relabeled.
Four historical dispositions append only the accepted current-authority path;
their execution bodies remain unchanged.

Read-only Python compared 20 protected files with index, HEAD, and Task 5 base
`f92a88f`: the supplement, three D1 plans, detailed D1.2 design, and fifteen
D1 review/gate artifacts. Every comparison passed and all three pinned plan
hashes matched. Supplement SHA-256 remains
`f9586a102c34acb39e3afe2b20086ba758964f23b8263324c86f02ccc6e52441`.

## Required final checks

The source candidate remains unchanged during these checks. All listed commands
exited 0; outputs were inspected rather than inferred from command launch.

| Command | Observed output |
| --- | --- |
| `uv run python -m unittest discover -v` (executed by aggregate gate) | 368 tests, 72.826 seconds, OK |
| `uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts` | All checks passed |
| `uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts` | 13 files already formatted |
| `uv run ty check .codex/skills/backlog-status/scripts` | All checks passed |
| `uv run python tools/quality.py check` | Exit 0; Ruff/format/ty, unittest, coverage, Bandit, detect-secrets, Interrogate, Vulture, Xenon passed |
| `uv run python -m unittest tests.test_public_api tests.test_documentation -v` | 15 tests, 0.039 seconds, OK |
| `uv run mkdocs build --strict` | Documentation built in 1.42 seconds, exit 0 |
| `uv run python tools/quality.py docs` | Interrogate 43.6%, minimum 40%, passed |
| `uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit` | Findings: none; 64 local children |
| `uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json` | schema_version=1, valid=true, findings=[], recommendation=null, 64 children |
| `git diff --check` | No output, exit 0 |

Aggregate coverage reran 368 tests in 81.971 seconds, OK; runtime coverage is
94% (1527 statements, 98 missed). The detect-secrets audit retained existing
verified-false provenance hashes; no baseline change. MkDocs emitted its
existing vendor notice about future MkDocs 2.0, with no strict-build failure.
Raw real-command output was captured in ignored task-5-audit-output.txt and
task-5-status-output.json beside this report and inspected as UTF-8/JSON.
These observation logs are not governance authority or gate evidence.

Supported-version matrix: all final entries exited 0 on the unchanged source
candidate, with 368 tests and `OK` on each interpreter:

| Command | Actual Python | Observed time |
| --- | --- | --- |
| `uv run --python 3.12 python -m unittest discover -v` | 3.12.13 | 83.137 seconds |
| `uv run --python 3.13 python -m unittest discover -v` | 3.13.14 | 79.656 seconds |
| `uv run --python 3.14 python -m unittest discover -v` | 3.14.4 | 79.019 seconds |

Raw matrix outputs are ignored task-5-python312-output.txt,
task-5-python313-green-output.txt, and task-5-python314-output.txt beside this
report; every final exit and summary was inspected. The candidate commit
contains this report; its hash is returned to the controller separately.

The initial Python 3.13.14 matrix exited 1 after 368 tests in 83.201 seconds:
only the existing native console help test failed. Its nested
`uv run --frozen xplane-fdau --help` selected the repository's default 3.12.13,
then Windows denied removing the active 3.13 `.venv/Scripts` directory.
The corrected matrix invocation propagates `UV_PYTHON` for the selected
interpreter into nested uv calls. This is environment consistency, with no
native test/code change. Matrix calls also set `UV_OFFLINE=1` and
`UV_PYTHON_DOWNLOADS=never`; no dependencies were refreshed or downloaded.

## Changed files

- `.codex/skills/backlog-status/scripts/backlog/audit.py`
- `.codex/skills/backlog-status/scripts/backlog/parse.py`
- `.codex/skills/backlog-status/scripts/backlog/report.py`
- `.codex/skills/backlog-status/scripts/backlog_status.py`
- `tests/backlog_audit_support.py`
- `tests/test_backlog_status_cli.py`
- `tests/test_backlog_status_report.py`
- `tests/test_backlog_governance.py`
- `BACKLOG.md`, `CHANGELOG.md`
- `docs/superpowers/plans/2026-09-05-t1-3-structural-audit.md`
- `docs/superpowers/plans/2026-08-16-xplane-fdau-architecture-propagation.md`
- `docs/superpowers/plans/2026-08-22-q4xpcc-contract-handoff-readiness-authority.md`
- `docs/superpowers/plans/2026-09-05-gz-skills-adoption.md`
- `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- `docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md`
- This report.

## Self-review and concerns

Inspected implementation and document diffs against Task 5's brief, incorporated
parent contracts, accepted reconciliation, and frozen policy. Runtime package
code, dependencies, protected D1 records, and policy bytes are untouched by
Task 5. CHANGELOG also records the separately reviewed earlier `6022dda`
native reader Python 3.14 compatibility correction. The unchanged golden
version-1 serialization contract passes. No recommendation, mutation command,
integration hook, remote action, or release was delivered.

Cross-platform seams use pathlib, explicit UTF-8, argument-vector subprocesses,
closed/context-managed temporary resources, sys.executable process tests, and
raw index-byte comparison. Windows is the observed host; Linux and macOS were
not available. The supported Python matrix is recorded with final checks.

T1.3 and its plan intentionally remain in_progress, with zero T1.3 gates.
Controller task and whole-branch independent review remain required. Four gate
records, accepted review, child completion, HEAD-backed closure, and the final
HANDOFF current pointer are owned by the later resumed Task 5 closeout. No
accepted review or completion evidence has been fabricated. No merge, push,
tag, publication, or release is authorized by this candidate.

## Consolidated final-review correction wave

Base: `b64c34caed73a00e8b03b423d10249dee5144509`. The whole-branch review
rejected that candidate for the four Important findings in
`whole-branch-review.md`. This section records their single bounded correction
wave; the earlier candidate results above remain historical observations.
Scoped final re-review and gate closure remain pending.

1. Referenced acceptance-list integer conversion failure now becomes an
   unresolved managed reference, yielding `artifact.gate-drift` at the actual
   ordinal line with its child context. Python's integer limit is unchanged,
   and independent malformed artifacts still appear in audit and JSON.
2. Every discovered active plan's populated completion slot is validated once,
   against its declared child and child-level ordinal. Index eligibility
   applies independently of BACKLOG availability; effective verified linkage
   strengthens it to HEAD, including blocked/deferred Resume verified.
   Linked slots produce no duplicate findings. Historical plans are untouched.
3. Plain bullets, numbered items, open tasks, and checked tasks normalize to
   the same acceptance statement. The same normalization applies to referenced
   earlier numbered gates. Source lines and punctuation remain exact; design
   checkbox markers never satisfy a backlog gate. Changed wording still fails.
4. Policy fixtures use the existing isolated shared Git initialization/helper,
   including command-local signing, hooks, identity, and newline controls.
   Inherited unavailable signing and failing-hook configurations are tested in
   temporary environments; global config and real project commit hooks are
   unchanged.

Changed correction files: `backlog/parse_sources.py`, `backlog/lifecycle.py`
under the existing audit scripts; `tests/test_backlog_status_cli.py`,
`tests/test_backlog_status_adherence.py`, `tests/test_backlog_status_lifecycle.py`,
`tests/test_backlog_status_policy.py`; and this report. No new authority,
approval, runtime, dependency, or ledger change belongs to this correction.

### Correction RED and GREEN

On Python 3.12.13, this exact selector command ran RED and then GREEN:

```powershell
uv run python -m unittest tests.test_backlog_status_cli.BacklogStatusCliTests.test_oversized_referenced_gate_ordinal_keeps_independent_contextual_reports tests.test_backlog_status_cli.BacklogStatusCliTests.test_unlinked_plan_completion_is_audited_by_both_commands tests.test_backlog_status_adherence.AdherenceTests.test_design_task_markers_are_formatting_and_do_not_deliver_backlog_gates tests.test_backlog_status_lifecycle.LifecycleTests.test_unlinked_active_completion_slots_validate_declared_child_and_index_bytes tests.test_backlog_status_lifecycle.LifecycleTests.test_linked_completion_keeps_head_requirement_without_duplicate_findings tests.test_backlog_status_policy.AuditPolicyTests.test_fixture_commits_ignore_inherited_signing_and_hooks -v
```

RED: exit 1, six tests in 6.345 seconds, 11 subtest failures and three errors.
The raw ordinal ValueError, ignored completion failures, retained task markers,
signing exit 128, and failing-hook exit 1 all reproduced. The existing linked
HEAD/no-duplicate control passed. No real signer or user hook was invoked.
GREEN after the corrections: exit 0, six tests in 8.079 seconds, OK.

The complete covering run then passed 67 tests in 68.472 seconds, exit 0:

```powershell
uv run python -m unittest tests.test_backlog_status_cli tests.test_backlog_status_adherence tests.test_backlog_status_lifecycle tests.test_backlog_status_policy -v
```

Final scripts Ruff check, format check (13 files), and ty all exited 0, as did
focused test-file Ruff/ty. Public API/documentation contracts passed 15 tests
in 0.031 seconds. Strict MkDocs built in 1.51 seconds with the same nonblocking
vendor notice. Documentation coverage passed at 43.6%. Both real commands
exited 0, with `Findings: none` and JSON valid=true/findings=[]/schema_version=1.
`git diff --check` exited 0. Their commands are the exact required commands in
the earlier final-check table, rerun for this changed candidate.

Read-only comparison confirmed all 20 protected files still match working,
index, HEAD, and this wave's reviewed base `b64c34c`; all pinned hashes match.
The source candidate remains unchanged during the aggregate and matrix checks.
All matrix commands propagate matching `UV_PYTHON`, with `UV_OFFLINE=1` and
`UV_PYTHON_DOWNLOADS=never`, as established by the earlier environment finding.

`uv run python tools/quality.py check` then exited 0: Ruff, format, ty,
`uv run python -m unittest discover -v` (374 tests in 77.207 seconds, OK),
coverage (374 tests in 78.083 seconds, OK; 94% over 1527 runtime statements,
98 missed), Bandit, detect-secrets, Interrogate (43.6%), Vulture, and Xenon all
passed. The unchanged security baseline retains its reviewed provenance hashes.
Final raw output is in ignored `task-5-final-fix-quality.txt`; its actual exit
and all component results were inspected.

The correction candidate's required source matrix also passed, each exit 0
with 374 tests and `OK`:

| Command | Actual Python | Observed time |
| --- | --- | --- |
| `uv run --python 3.12 python -m unittest discover -v` | 3.12.13 | 74.954 seconds |
| `uv run --python 3.13 python -m unittest discover -v` | 3.13.14 | 76.522 seconds |
| `uv run --python 3.14 python -m unittest discover -v` | 3.14.4 | 78.257 seconds |

Ignored `task-5-final-fix-python312.txt`, `task-5-final-fix-python313.txt`, and
`task-5-final-fix-python314.txt` retain raw outputs beside this report. Each
exit and final summary was inspected. No code changed between these checks.
All four reviewed defects are corrected; acceptance remains subject to the
controller's scoped final re-review. No gate, plan status, HANDOFF pointer, or
completion/review evidence advanced in this wave.
