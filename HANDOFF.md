# Project Handoff

## Resume point — 2026-09-27, after C1.1

Observed 2026-09-27 23:28 UTC, before this handoff and Git-sync commit: `main`
was clean at `93a04156d460e920e2711ae97e514ca53f6bac3b`, one commit ahead
of `origin/main`. Only the main worktree existed. Recheck Git and backlog state
on return because the requested ordinary sync will create a later commit.

**Current objective:** `C1.2` identity, hashing, references, authority, and
provenance is the first dependency-ready local child. It is `specified`, has
0/4 delivery gates, and has no implementation plan. The governing
[canonical-contract design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md)
is approved. `BACKLOG.md` remains the delivery-state authority; no child is
currently selected.

**Latest result:** `C1.1` canonical JSON and binary64/integer encoding is
`verified` with 4/4 gates and accepted independent review. Its
[completed plan](docs/superpowers/plans/2026-09-27-c1-1-canonical-json-number-encoding.md),
[completion record](.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/completion.md),
and [review](.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/review.md)
are committed. The completed C1.1 selection was cleared in `93a0415`; this
local commit is the one pending sync at observation time. Strict backlog
`audit` and `next` on 2026-09-27 found no findings and recommended
`action=write_plan child=C1.2`.

**First permissible action on return:** Read `AGENTS.md` and its linked
authorities; run backlog `audit` and `next`. Use
`superpowers:writing-plans` to create a single-child C1.2 implementation plan
from the approved design. Expected result: a reviewable plan with exact files,
test-first steps, verification, and commit boundaries. Obtain plan approval
before selecting C1.2 or starting implementation. Stop on an audit finding,
changed authority, or missing approval.

**Maintenance and boundaries:** The explicit 2026-09-27 dependency refresh
passed its guarded apply, focused `unittest`, full offline hygiene, and external
Python 3.12 source and installed-wheel checks. `uv lock --upgrade` changed no
tracked files. Four older transitive packages remain explained by Wily/Radon
version constraints. The project supports only Python 3.12
(`>=3.12,<3.13`); the local virtual environment uses 3.12.13. The installed
`gz-skills@gz-skills` plugin remains verified at the project pin v0.5.0.
Temporary refresh artifacts under the system temp directory are local-only.
No tag, package publication, GitHub release, or q4xpcc edit was authorized.
Release gate `G1` remains waiting.

## Prior resume point — 2026-09-27, before C1.1

Observed 2026-09-27 20:58 UTC, before this handoff commit: `main` was clean at
`b6f55eb92ede85df07fe8125d0cd419d00ae59ac` and matched `origin/main`.
`git worktree list` showed only the `main` checkout; no C1.1 feature branch or
worktree exists. Recheck Git state on return because this handoff's Git sync
will create a later commit.

**Current objective:** C1.1 canonical JSON and number encoding. Its approved
[cross-epic design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md)
has a reviewed but still
[draft implementation plan](docs/superpowers/plans/2026-09-27-c1-1-canonical-json-number-encoding.md).
`BACKLOG.md` remains authoritative: C1.1 is `specified`, has 0/4 gates, and
has not entered implementation. No C1.1 runtime code or delivery evidence was
created by the planning reviews or Git sync.

**Last completed action:** The Python 3.12-only compatibility and dependency/
tooling maintenance, together with the C1.1 draft plan, was committed as
`b6f55eb` and synced to `origin/main`. Full offline hygiene passed with 94%
coverage; a fresh wheel/sdist passed strict metadata and exact-inventory
checks, and an external Python 3.12.13 installed-wheel smoke passed. Its
temporary artifact directory is local-only:
`C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-sync-5254e7536f78456abfe6153ccc766e17`.
No tag, package publication, GitHub release, or q4xpcc edit occurred.

**First permissible action on return:** Read `AGENTS.md` and its linked
authorities; run backlog `audit` and `next`. Obtain Jeff's explicit approval
of the C1.1 plan before selecting the child or starting Task 1. With that
approval and a clean current `main`, use `superpowers:using-git-worktrees` to
create the temporary C1.1 branch/worktree from the verified HEAD, then follow
the plan's guarded lifecycle and test-first execution steps. Stop on an audit
finding, changed baseline, or missing approval; this handoff and ordinary Git
sync do not themselves authorize implementation or release.

## Prior resume point — 2026-09-20

2026-09-27 maintenance update: support the Python 3.12 minor line only for
now, matching XPPython3's embedded interpreter. The dependency refresh includes
the reviewed gz-skills v0.5.0 project pin and ignored Superpowers checkout
v6.4.2. Direct full offline hygiene passed. The guarded refresh also exited
successfully after its external Python 3.12 source tests and installed-wheel
smoke. Four older transitive packages remain constrained by Wily/Radon; no
release or Git sync was performed.

**Current objective:** `B1.1` source-layout migration is verified with 5/5
gates and accepted independent review, and was locally integrated into `main`
at `1f66a0f`. The temporary worktree and branch were removed. The project
reviewed and adopted `gz-skills` v0.4.0 before implementation; the project pin
has since advanced to reviewed v0.5.0. `T2.2` remains
verified. `C1.1` is the next canonical local child.

**Exact next action on return:** Read AGENTS.md and the linked authorities,
then run the backlog audit and next commands. The reported action is to write
an approved single-child `C1.1` implementation plan from its approved
canonical-contract design.

## Observed state and evidence

- B1.1's 17 runtime files moved byte-for-byte to `src/xplane_fdau`; the
  flat package root is gone. The completed plan and five gate receipts are
  under `docs/superpowers/plans/2026-08-09-src-layout-migration.md` and
  `.superpowers/sdd/2026-08-09-src-layout-migration/`. Full offline hygiene
  passed 521 `unittest` tests, 43.9% coverage, strict docs, and exact wheel/sdist
  checks. External Python 3.12.13 installed-wheel smoke passed. The merged
  `main` checkout passed full offline hygiene: 521 tests in 292.904 seconds,
  43.9% coverage, strict docs, pre-commit, and exact artifacts. The old flat
  checkout held only ignored Python bytecode after merge; its verified cache
  tree was removed before the final green gate. No release or Git push occurred.
- T2.2 was integrated into `main` at commit `431c195`. Its verified backlog
  state and evidence remain unchanged by the local quality-cadence correction.
- The approved plan is
  `docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`.
  Completion, review, and four gate records are under
  `.superpowers/sdd/2026-09-19-t2-2-dependency-toolchain-refresh/`.
- T2.2 originally pinned uv 0.12.17; the 2026-09-27 tooling-policy correction
  retains a supported minimum so newer uv releases can run. The adapter inventories 98 registry packages and records
  five constrained package versions with their upstream owners. It reported no
  yanks, advisories, or blockers. Runtime remains pure Python and
  standard-library-only.
- One wheel/sdist pair passed exact inventory checks. CPython 3.12, 3.13,
  and 3.14 each passed 511 source `unittest` tests and an installed-wheel
  smoke test. The final active-Python quality gate passed 516 tests and 43.9%
  coverage against a 40% minimum. Review accepted the implementation with no
  remaining Critical or Important findings. A minor matrix subprocess-timeout
  concern is recorded in `review.md`.
- The installed and enabled `gz-skills@gz-skills` plugin was verified at
  version 0.5.0 from the pinned official Git marketplace. The original v0.4.0
  adoption evidence is in
  `.superpowers/sdd/2026-09-20-gz-skills-v0-4-0/review.md`. T2.2's Python/uv
  adapter does not mutate the plugin cache.
- The ignored Superpowers checkout was fast-forwarded from v6.3.0 to upstream
  v6.4.2 for the 2026-09-27 dependency refresh.

## Fast local closeout follow-up

Jeff approved a limited correction after B1.1's repeated multi-minute gates:
move existing static, security, docs, hook, and live-state checks ahead of
coverage; keep one complete branch gate; and use documented focused checks
after an exact local fast-forward. The implementation uses existing commands
and adds no merge verifier. Independent review found no code defect; its plan
checklist finding was corrected. The single full offline hygiene gate passed
on branch commit `af2bfc2`, with 94% coverage and an exact wheel/sdist pair.
Jeff selected local integration. Main fast-forwarded to `ed10665`; frozen
sync, lock, strict backlog audit, both live-state tests, and one fresh external
wheel/sdist pair passed on that exact commit. The temporary worktree and branch
were removed. No Git push or release action occurred. The approved design and
plan are under
`docs/superpowers/specs/2026-09-20-fast-local-closeout-design.md` and
`docs/superpowers/plans/2026-09-20-fast-local-closeout.md`. C1.1 remains
the next canonical child planning action after this maintenance correction.

## Quality-control follow-up

Jeff flagged the repeated multi-minute full gates during B1.1 as too costly
for ordinary implementation work. The required full suite took 314.236 seconds
on the feature branch and 292.904 seconds after local integration; failed
closeout runs repeated it while exposing a live-state assertion, a generated
secrets baseline update, and stale bytecode in the pre-existing main checkout.
The current cadence still calls for focused checks during edits and one full
gate at stable closeout. The gate order and state-sensitive preflight were revised in the fast local
closeout change above. Measuring the slow unittest cases remains a separate
follow-up before any suite-policy change.

Jeff narrowed the fix to the local development cadence; GitHub Actions
remains unchanged. During edits, run focused `unittest`, Ruff, and ty checks.
Pre-commit runs staged-file Ruff lint/format and detect-secrets checks without
a full test suite or metrics reports. At stable closeout, run the complete
active-version quality gate once. Edits to existing source files use the
standalone gate. Full offline hygiene is for package layout, shipped resources,
metadata, lockfiles, build rules, or artifact-validation changes; it invokes
the quality gate directly once, then checks docs, hooks, and a fresh artifact
pair. Documentation and governance edits use their focused checks. Reserve
the Python 3.12 source/installed-wheel check for
version-sensitive changes and release readiness. The matrix subprocess-timeout
concern from T2.2 review remains a separate follow-up.

## Decisions and boundaries

Jeff explicitly authorized this handoff and ordinary Git sync. That covers a
checkpoint commit and ordinary push; it does not authorize a tag, package
publication, GitHub release, or q4xpcc edits. T3.1 guarded Git-sync tooling
remains a separate specified child. No release is authorized.

Identity and native-FDR-kernel migration: implemented and verified, but unreleased.
Completed implementation plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
The next canonical vertical slice retains measurement, binding, observation, sample, frame, timing, and quality contracts. ARINC and FDM/FOQA support remain
inside this repository's approved scope.

`D1.1` canonical C1-C4 design approval is verified.
`D1.2` acquisition, recording, projection, and pinning contract design is verified.
`D1.3` reviewed q4xpcc Phase 24A consumer handoff is verified.
`I1.0` is eligible as the next reportable external action.

`I1.0` now permits Phase 24A specification and plan reconciliation because `D1.3` is verified.
`I1.1` permits delivered contract-model, schema, fixture, and runtime adoption only after `C4.4`.
`I1.2` permits live XPLM acquisition adoption only after `A1.9`.
The reviewed brief is `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`.
Do not edit q4xpcc from this repository.
