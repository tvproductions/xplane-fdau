# Strict heavy starter adoption evidence

Observed 2026-10-25. Owner: Jeff / tvproductions and the FDAU implementer.
Plan: [strict heavy onboarding](../superpowers/plans/2026-10-25-strict-heavy-starter-onboarding.md).
Spec: [approved design](../superpowers/specs/2026-10-11-skills-first-native-adoption-design.md).

## Scope and source identity

This is brownfield first adoption, not a release or an already-completed template
upgrade. The user explicitly selected heavy and approved the plan. Backplane
remains disabled; FDAU requirements and BACKLOG/HANDOFF remain authoritative.
Cognitive analysis is UNKNOWN pending the external gzkit library extraction and
shared starter contract. No local substitute or acceptance waiver is authorized.

Starting main HEAD: `3a5211bfe3c1ab80e25758fce61356dd6ef7cbef`.
Implementation branch: `chore/strict-heavy-onboarding` in
`.worktrees/strict-heavy-onboarding`. Main already contained the uncommitted
approved specification and new plan; they were copied into the isolated branch,
and the originals remain preserved on main. The separate pre-existing
`chore/dependency-refresh-2026-10-18` worktree is outside this change.

Released starter: v0.6.0 / `c0a6945b2170e1cf5bee3e80738916f5b62d13a5`.
The live latest-release endpoint still identifies v0.6.0. A separate temporary
checkout resolves the annotated tag to that commit. Its own pinned uv 0.13.1 /
Python 3.14.8 environment passed bundle/both-catalog validation and the read-only
backport assessment. This helper environment is separate from FDAU; its unused
legacy cognitive dependency is not installed in FDAU or used for acceptance.

The shared catalog selects SP v7.0.0, gz-skills v0.8.0 and disabled Backplane.
Official releases now include SP v7.0.1 and gz-skills v0.8.3; retain the reviewed
released catalog rather than inventing FDAU-specific component substitutions.
Installed/enabled old-source `gz-skills@gz-skills` is 0.8.3, while FDAU's old
configuration asks for 0.5.0. Other native copies are disabled here. Installation
and loaded-source reconciliation are pending, not inferred from cache presence.

Rollback references are the starting HEAD plus the preserved approved-document
diff and native inventory in the ignored plan workspace. Main's old Superpowers
junction/target remain untouched. No remote push, tag, release or external
repository edit is included in this work.

## Exact environment and candidate tool selection

Initial isolated environment: uv 0.13.5; managed CPython 3.12.15, AMD64, with its
own `.venv` and editable import rooted in this worktree. The original frozen
sync succeeded. The uv_build range still selects the older family and needs
reconciliation. Python's official 3.12.15 release and current uv 0.13.5 release
were checked; the latter also updates managed-Python build trust material.

Official PyPI release metadata was checked for every baseline tool. These are
**candidates**, not compatibility/installation passes. Package metadata admits
Python 3.12.15; actual installation, probes and project checks remain required.

| Tool | Candidate | Selected family / purpose |
| --- | --- | --- |
| uv / uv_build | 0.13.5 | 0.13.x; exact resolver/build inputs |
| Ruff | 0.17.2 | 0.17.x, already entered by existing 0.17.0 lock; strict routine rules |
| ty | 0.0.91 | Current 0.0.x beta; revisit stable release / scoped maintenance |
| pre-commit | 4.7.0 | 4.x routine hook runner |
| Cosmic Ray | 8.7.0 | 8.x bounded mutation |
| Lizard | 1.24.3 | 1.24.x complexity; parser/corpus proof pending |
| cohesion | 1.2.0 | 1.x responsibility review |
| Interrogate | 1.7.0 | 1.x documentation presence |
| Vulture | 2.16 | 2.x dead-code candidates |
| Bandit | 1.9.4 | 1.x security analysis |
| Coverage.py | 7.17.0 | 7.x branch and statement coverage |
| deptry | 0.25.1 | 0.25.x dependency declaration analysis |
| pip-audit | 2.10.1 | 2.x exact-export advisory analysis |
| Import Linter | 2.15 | 2.x project boundary contracts |
| detect-secrets | 1.5.0 | 1.x retained explicit secret controls |
| Cognitive analyzer | Unavailable | External extraction; no fabricated package/pin/API |

This is a scoped onboarding update, not a completed full dependency refresh.
Original documentation/artifact dependencies keep their separate purposes.

## Baseline measurements and known adapter defects

The isolated, unmodified tooling baseline passed **604 unittest tests in
366.153 seconds** on Python 3.12.15. Focused governance/documentation checks
passed 42 tests, the strict backlog audit/next found no findings, ty passed and
strict MkDocs built successfully. These observations establish a baseline,
not acceptance of the revised engineering configuration.

Legacy Xenon C/B/A over `src/xplane_fdau` passes. Diagnostic Ruff C901 at 20
over runtime/tests/tools/project adapters identifies five functions: backlog
`_backlog_link_findings` (24), `_roadmap_findings` (23), `_backlog_findings` (27),
and dependency-refresh `collect_status` (24), `_remaining_constraints` (22).

Diagnostic Lizard 1.24.0 over 93 Python files measured 1,384 functions with an
overall mean about 3.48. Several test/tool/adapter functions exceed 20, and
`tools/dependency_refresh.py`, `tools/runtime_imports.py` and backlog rules
exceed the module-mean ceiling 10. The diagnostic name/line comparison also
reports mismatches requiring investigation with the selected analyzer; it is
not an accepted function-discovery proof. Reports preserve original paths,
hashes and measurements in the ignored workspace; do not compare metric names
as if they were equivalent counts.

The required pre-change dependency status ran but returned nonzero: its
preview uv advisory parser rejects current advisory records, and its bounded
Index reader rejected the coverage response as untrusted or oversized. No
advisory-free or complete-refresh claim is justified. Preserve guards and
diagnose the actual response shapes/size before changing this adapter.

## Task 2 verification

The exact selected environment is installed: Python 3.12.15, uv/uv_build
0.13.5, Ruff 0.17.2 and ty 0.0.91. Routine and deeper dependencies are separated;
all reviewed groups synchronized exactly and the lock check passes. Explicit
Ruff/ty targets are Python 3.12 and project-owned adapters are analyzed.
Strict Ruff check/format and ty pass over 105 Python files.

Regression evidence: eight original exact-pin/source/matrix assertion failures
became green; 59 focused source/refresh/matrix/metadata tests pass. Another 188
runtime/configuration/immutability/tool tests and 132 backlog/import-boundary
tests pass. Existing intentionally invalid-input tests retain their runtime
checks using dynamic operations; no blanket lint/type exclusions were added.
Python 3.12 aliases are annotation-only; existing consumers perform no alias
introspection. Exception cause rewrites retain the causes set by existing helpers.

Two observed source defects were reproduced with assertion-level failing tests:
current uv advisories use dependency/fix_versions; coverage's official Index is
6,212,381 JSON bytes and 5,259,255 HTML bytes, both beyond the former 5 MiB cap.
The parser now preserves advisory identity/fix versions, and an 8 MiB bound
retains official-origin/media/oversized rejection tests.

The corrected audit exposed 18 advisories across certifi, filelock, gitpython
and virtualenv. Only those four affected packages were upgraded within existing
constraints: certifi 2026.10.23, filelock 4.2.4, gitpython 3.2.1 and virtualenv
21.14.13. Current uv audit reports zero vulnerabilities/adverse statuses across
133 audited packages. The original status command now returns no pre-apply
blockers or current findings. Required pip-audit/export acceptance is still pending;
this uv audit is supporting evidence, not its replacement or a full refresh claim.

CI, installed artifacts, deeper compatibility and cognitive proof remain pending.

## Task 3 candidate verification

The local quality aggregate now invokes only locked Ruff check, Ruff format,
ty and unittest, once each. All reviewed groups are explicit because routine
unittest also verifies repository tooling. Hooks enforce the same four checks;
ty/unittest run once without per-file arguments. Hygiene uses its all-files
hook invocation as the single routine suite, retaining lock/backlog/docs and
safe artifact checks. The previous direct second quality invocation is removed.

Ten assertion-level negative controls became 33 passing focused tests, with
strict whole-source lint/format and ty passing. CI/readiness YAML uses verified
immutable Action commits: checkout v7.0.1, setup-uv v10.3.2, upload-artifact
v7.0.2 and download-artifact v8.0.2. Every setup records uv 0.13.5 and Python
3.12.15; the duplicate CI unittest job is removed and artifact handoff remains.
No exact-commit remote CI result is available yet.

The native pre-commit hook was installed after observing no pre-existing hook.
Its launcher uses the retained feature environment; after verified main
integration it must be reinstalled from main before feature-worktree removal.
The Task 3 commit observes actual hook execution; whole-candidate all-files
hook proof belongs to stable hygiene to avoid repeating the same full suite.

## Commit-hook isolation incident and correction

The first installed-hook run passed lint/format/ty but failed unittest. Git's
repository-local hook variables redirected disposable fixture Git operations
into the feature repository. The fixture commits changed its branch ref/index
and set the shared repository bare flag. All working files survived. Recovery
preserved the fixture tip under a local recovery ref, restored the recorded
Task 2 feature HEAD/index (37cb6e3) without checking out or discarding working
files, and restored non-bare operation. Main remained at 3a5211b and the unrelated
worktree branch remained at f81c4c2. A recovery copy of the affected configuration
and failed-hook output is retained in ignored execution evidence.

A real two-disposable-repository regression first failed, then passed after
clearing Git's documented repository-local routing variables in fixture Git
operations and explicit-root backlog policy/evidence/report reads. It verifies
both fixture repository creation/reading and preservation of the sentinel's
HEAD, index and config. Unrelated process/user settings remain inherited.
The full-hook retry is required before claiming installed enforcement passes.

Three other failures were ordered __all__ snapshots after Ruff sorted exports;
export membership and identity/importability are unchanged. The checks now use
exact multiset comparison, retaining rejection of missing/extra/duplicate names
without freezing incidental ordering. Seven focused public-API/isolation checks
and strict static checks pass. This does not close the broader weak-test audit.

## A01–A18 acceptance matrix

### Current implementation observations

The installed Task 3 commit hook retry passed all four checks at `a28d084`.
The prior incident is corrected by the real two-repository isolation regression;
the earlier sentence requiring a retry records its state before that observation.

Released native configuration is now applied through the verified starter helper.
No-op, conflicting-content, changed-pin and symlink refusal probes passed without
overwriting protected fixture bytes. The native marketplace was initially cached
at the older `b6f76dd` revision; the scoped native upgrade brought it to the exact
selected `c0a6945` revision. Installed Superpowers and gz-skills Git HEADs match
the shared catalog's full component pins. Native add changed two global disabled
defaults to enabled; those two original false tables were restored surgically.
All native user plugin/marketplace tables match the captured before state.
Project native inspection enables the selected pair and disables Backplane;
the outside-project control activates neither starter source. Old installed
copies and main's legacy junction/target are preserved.

The selected upstream setup helper initialized settings and recorded the user's
explicit heavy choice. A fresh read-only native Codex session subsequently
discovered and read the exact selected `superpowers:using-superpowers`,
`gz-skills:gzs-router` and project `update-gz-template` skill. It verified entry
bytes/source revisions and reported no active duplicate source. Temporary-path
access warnings and a failed remote catalog request were reported; no whole-stack
or current-upstream freshness claim follows. Parent-session outside-project
control is separate evidence. This supersedes earlier pending native-discovery
notes, and does not certify Python engineering acceptance.

Explicit analysis now retains original source hashes, reconciles native Lizard
function locations with AST declarations, runs independent static dimensions
after failures, and returns nonzero for the cognitive UNKNOWN prerequisite.
Real fixtures cover 20/10/5 boundaries, malformed reports, missing/escaping/linked
source, original inline suites and function-free modules. Real Import Linter
accepts the actual graph and rejects all twelve forbidden direct/indirect fixture
edges. Exact export tests preserve hashes, disable the second resolver and prove
cleanup. Reports are created exclusively; an existing report survives untouched.

Observed runtime analysis: Interrogate 41.1% against 40%; deptry, Vulture and
three import contracts pass. The first full static run exposes five C901
violations, real security-review findings and four Lizard discovery mismatches.
Dependency-refresh responsibilities were subsequently separated without changing
their guarded workflow: 29 consuming tests pass; C901 passes for that module;
native Lizard maximum is 20 and module mean 9.75, versus 57/14.33 before.
Other required findings remain open; this is not a clean whole-project analysis.
The secret scan updated two existing reviewed fixture line numbers and its
timestamp only; no finding was removed or newly blessed.

The bounded disposable Cosmic Ray session passed its unmodified 48-test baseline
and completed 1,436 mutations: 1,199 killed, 236 survived and one incompetent.
The incompetent result was an actual CP1252/UTF-8 decoding error, reproduced by
a subprocess fixture and corrected by explicit UTF-8 bootstrap streams. The
survivors and affected native rerun remain review/acceptance work; no percentage
waiver or complete mutation claim is made. The source checkout was never mutated.

The first pip-audit attempt exceeded its 600-second total deadline. Windows
launchers left child processes; only the identified audit-owned tree was stopped.
A real disposable parent/child regression now proves tree termination before
temporary cleanup. The retry uses the locked environment's current interpreter,
explicit hashes, no dependency resolver and bounded process-tree cleanup.
Until a successful native result is observed, dependency audit remains UNKNOWN;
the separately passing earlier uv audit is not substituted for required pip-audit.

Current focused evidence includes 49 analysis/mutation/refresh tests, 43
archive/native-configuration/installed-smoke fixtures and 57 governance/docs/API
tests. Strict MkDocs and full Ruff/format/ty checks passed before the latest
bounded refresh refactor; its own focused static and behavior checks pass.
Three affected obsolete wording snapshots were removed; real configuration,
command composition, archive, import and public-API controls remain. The broader
test-quality audit is still open. Final candidate hygiene, coverage, fresh
installed artifacts, independent branch review and exact-commit remote CI remain
separate observations below. No remote operation or main integration occurred.

Each row records actual status, applicability, executed scope and remaining
proof. UNKNOWN is not PASS. All required rows must pass for strict acceptance;
Backplane whole-stack readiness is independently deferred.

| ID | Applicability / observed status | Evidence / remaining work |
| --- | --- | --- |
| A01 | PASS for initial identity/scope/rollback capture | Starting HEAD, dirty-document provenance, isolated branch, native inventory and preserved main recorded above; update at candidate closeout |
| A02 | PASS on the reviewed candidate | Installed src package, CLI and external import-origin smoke pass |
| A03 | PASS | Exact uv_build 0.13.5 declaration; actual pure wheel built from sdist, Generator uv 0.13.5 |
| A04 | PASS for current declared scopes | Recorded effective configuration/provenance; complete runtime/test/tool/adapter Ruff/format/ty checks pass |
| A05 | PASS for selected execution lane | Exact managed 3.12.15 locally and externally; py312/3.12 tool targets and immutable CI inputs reconciled; remote execution remains A09 UNKNOWN |
| A06 | PASS for recorded selected families | Dated official release/compatibility review and actual installation/gates; no whole-stack latest-release claim |
| A07 | PASS | Exact groups/lock selection; offline frozen execution and lock check pass |
| A08 | PASS for the four routine checks | All-files installed hooks pass Ruff check, format check, ty and full unittest; deeper acceptance remains A18 |
| A09 | UNKNOWN | Local installed-hook enforcement passes; exact-commit remote CI not run, no push authority inferred |
| A10 | PASS | Project runtime dependencies empty; fresh wheel publishes no Requires-Dist; dev/build tools retained outside runtime |
| A11 | PASS | Actual offline no-sources build explicitly builds wheel from sdist; exact inventories and hashes retained |
| A12 | PASS | Fresh wheel-only external 3.12.15 environment passes CLI/resources/imports/canonical/public-value smoke |
| A13 | PASS | Installed py.typed and public annotations; external ty accepts valid bytes consumer and rejects assigning bytes to int |
| A14 | N/A | One distribution and no uv workspace declaration; installed/build inventories confirm the single-package boundary |
| A15 | N/A for alternate/private-source variants | No tool.uv.sources/private index declarations or corresponding runtime dependencies; standard registry lane applies |
| A16 | N/A for host/native/container variants | Delivered pure-Python wheel/sdist has no simulator plugin, native binary or container artifact; adapters remain external |
| A17 | UNKNOWN | Exact hashed export/no-second-resolver controls pass, but both required native pip-audit attempts timed out |
| A18 | FAIL / UNKNOWN | Current static findings and mutation survivors remain unresolved; four Lizard discovery errors and required external cognitive proof prevent complete measurement |

## Reviewed candidate verification

Independent whole-branch review covered starting base `3a5211b` through `a28d084`
plus staged tree `59cbb20b7e77ccf7b05072f7dc749388b8a9ffd7`. It retained no new
Critical/Important/Minor defects and judged the foundation suitable for continued
governed onboarding, without certifying STRICT acceptance. Its attempted focused
test run hit sandbox user-temp ACL errors and supplies no regression/pass evidence;
the parent-owned approved native checks below supply execution evidence. It did
not independently certify freshness, native activation, every-platform cleanup,
security clearance, mutation strength, artifacts, coverage or remote CI.

On that unchanged source candidate, full offline hygiene exited 0: lock, backlog,
strict docs, all-files four-check hooks and fresh artifact pair validation passed.
The separate Coverage run passed **630 unittest tests in 404.823 seconds**.
It measured 2,414/2,539 statements (95.08%) and 868/946 branches (91.75%),
94.18% combined, against the retained 40% floor. Standalone cohesion 1.2.0 also
measured invented shared-field versus split-field classes at 100% versus 50%;
this validates the selected CLI without inventing a universal acceptance floor.

Retained artifact pair was built offline with `uv build --no-sources`; the log
explicitly reports “Building wheel from source distribution”. Fresh strict
inventory validation passed. SHA-256 values:

- sdist: `235ba653b978541a37418beb63662bf5635c0e7cead8b31f3ef3a961d78aff50`
- wheel: `867c0a4cee3c468b8843ccafec2b4660326a7dd2d034bc3a61cd93c886b6ae3e`

A new external managed Python 3.12.15 environment installed that wheel only,
offline with no index/dependencies. Installed smoke passed outside the checkout;
origin is the external environment's site-packages. The installed typing marker
exists. ty 0.0.91 accepted the valid public canonical-bytes consumer and rejected
the invalid bytes-to-int assignment, proving consuming typing behavior rather
than marker presence alone. Local raw paths/results remain in the plan workspace.

Current deeper analysis exits **2**, with cognitive UNKNOWN, four Lizard discovery
errors, 1,456 discovered functions, maximum 49 and weighted project mean 3.4904.
Ruff C901 still flags three backlog-tool functions. Lizard also exposes existing
function limits in backlog adherence/edit/lifecycle/rules, hygiene, three test
fixtures and module means in backlog rules (13.0) and runtime_imports (10.8).
Security findings and the 236 mutation survivors still require disposition and
any necessary correction. No required finding was suppressed or limit weakened.
The single encoding-incompetent identifier mutation was rerun natively after
the UTF-8 fix: normal/killed, with original source hash unchanged. The original
batch is preserved; it is not relabeled as a new complete mutation run.

Both pip-audit attempts reached their 600-second total deadline. The corrected
runner stopped the second owned process tree and cleaned its temporary export;
no further retries are planned in this execution. Required network proof remains
UNKNOWN. These results do not authorize a merge, remote sync or release and do
not complete Task 4 or overall STRICT acceptance.

## Ownership and remaining work

### Resumed Task 4 remediation checkpoint

Resume verified feature HEAD `ea50bf03824dd37ceaacfbc21dcf7f4d87ae7b28`
and preserved the twelve existing tooling/test edits. Locked all-groups uv
backlog audit and next returned no findings; C1.4 remains unselected. Native
inspection confirmed the selected SP 7.0.0/gz-skills 0.8.0 sources enabled and
their cached Git revisions matching the bundle. This is current installation
evidence, separate from the earlier fresh-session discovery observation.

The retained complexity remediation was preserved. Additional public-behavior
tests protect Unicode scalars U+D7FF/U+E000, exact primitive types despite caller
equality overrides, irrelevant-field rejection, and deterministic payload error
tiers/property order. Expectations use literal bytes and paths, with no private
signature or prose snapshots. No runtime library implementation changed.

Native differential controls now account for the 121 round-2 survivors:

| Group | Observed disposition |
| --- | --- |
| Unicode boundary rejection | Three survived before the new tests; all three now killed |
| Optional-field filtering | Five killed by existing provenance tests omitted from the original selected suite; no duplicate tests added |
| Exact primitive/omission checks | Eleven now killed, including four follow-up controls; two follow-up controls were already killed by the first new tests |
| Payload error precedence | Four survived before the new cases; all four now killed |
| Reviewed equivalents | 95 mapped individually to current public callers, closed vocabularies, normalized Enums, deferred annotations, redundant checks or explicitly bounded supported-CPython behavior |
| Open questions | Two endpoint-object identity cases and one collection-count error-tier reconciliation |

These are **23 additional differential kills**, not a fresh full mutation batch
or proof that arbitrary string/object identities are interchangeable. Runtime
source hashes remain unchanged. The array-count mutant is not cleared by
freezing current behavior: the design calls general collection bounds shape
limits, while current count checks report semantic errors. The shared taxonomy
question also affects the retained allow-list limit assertion. No error priority
or runtime correction was invented to close that discrepancy.

Scoped independent review dispositioned all 22 retained Bandit findings:
19 contextual subprocess/import warnings, the baseline-path false positive,
and two retained advisories concerning executable lookup and redirect trust.
No actionable security defect was established; this is not an analyzer-clean
measurement or blanket suppression. The original report remains preserved.

Interactive Python commands and native mutation children used uv. Before the
checkpoint save completed, inspection found the previously installed Git hook
itself still launched pre-commit directly with the venv interpreter. That launch
violated the all-Python-through-uv instruction. The owned commit/test process tree
was stopped without a commit; its incomplete output is not acceptance evidence.
The original launcher is preserved locally. Its replacement invokes pre-commit
through locked all-groups uv with the same feature environment, native hook
arguments and configuration, and fails if uv is unavailable. It must retain this
uv-only property when reinstalled from verified main before worktree removal.
Five subprocess fixture modules now launch through the locked project environment; the descendant
itself signals readiness in the process-tree cleanup test. Mutation composition
now uses explicit project selection through uv for baseline, Cosmic Ray and
mutant tests, and includes the existing provenance module. Dependency-audit
composition likewise uses locked uv, retaining hashed export, no second resolver
and the bounded deadline. Five command-boundary assertion failures preceded
these two tooling corrections; 20 focused analysis/mutation tests subsequently
passed. No network-audit retry or full native mutation batch was executed.
The separate external dependency matrix still constructs direct interpreter
commands and must be reconciled before it is next executed under this policy.

Current focused contract verification passed 76 tests; whole-scope Ruff
lint/format and ty passed. Scoped test and command-composition reviews retained
no new defect after correcting descendant readiness. Stable checkpoint saving
uses the corrected installed four-check commit hooks; the execution ledger records their
actual result rather than inferring it from these focused checks.

Current native Lizard remeasurement discovers 1,512 functions, maximum 20 and
weighted project mean 3.4153, with no measured module above 10. Its four original
discovery mismatches remain errors and the evaluator still returns 2. Current
Bandit remeasurement retains the same 22 finding categories with no analyzer
errors. These raw reports do not convert reviewed warnings or missing functions
into a clean measurement.

Local-only supporting artifacts are under the existing plan workspace:
`task4-unicode-*`, `task4-optionals-existing-tests*`,
`task4-exact-types-*`, `task4-payload-precedence-*`,
`task4-contracts-current.log`, `task4-uv-composition-red.log`,
`task4-uv-composition-green-retry.log`, `task4-uv-child-readiness.log`,
`task4-bandit-disposition.md`, `task4-survivor-disposition-review.md`,
`task4-test-remediation-review.md` and `task4-uv-composition-review.md`.
The stopped attempt is `task4-resume-commit.log`; the corrected launcher attempt
is `task4-resume-commit-uv.log`, whose result must be read before claiming a save.
Raw mutation IDs/diffs and per-ID dispositions remain linked there. Prior dated
coverage/artifact measurements are not relabeled as current-candidate proof.
Task 4, Task 7 and STRICT acceptance remain incomplete; cognitive extraction,
four Lizard omissions, timed-out network proof and exact-commit CI stay open.

Environment/metadata/refresh safeguards: plan Task 2, A04–A08/A10/A18.
Routine composition/hooks/CI: Task 3, A08/A09.
Analysis and affected tool/test/adapter refactoring: Task 4, A18.
Native managed files and packaging: Task 5, A01/A03/A11–A13.
Policy, release/version obligations and current summaries: Task 6.
Candidate measurements, installed artifacts, independent review and native/CI
observations: Task 7. Cognitive extraction belongs to Jeff/upstream maintainers
outside this repository; other tasks can proceed without closing that gap.

Source authority: [starter release](https://github.com/tvproductions/gz-skills-first-starter/releases/tag/v0.6.0),
[Python 3.12.15](https://www.python.org/downloads/release/python-31215/),
[uv 0.13.5](https://github.com/astral-sh/uv/releases/tag/0.13.5),
[Ruff 0.17.2](https://github.com/astral-sh/ruff/releases/tag/0.17.2),
[ty 0.0.91](https://github.com/astral-sh/ty/releases/tag/0.0.91),
and each named package's official PyPI JSON release endpoint. Local raw probe
responses/commands live in the ignored plan workspace and are not portable
proof of future candidate acceptance.

**Overall: onboarding in progress; STRICT acceptance incomplete.**
