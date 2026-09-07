# Project Handoff

## Architecture and completed migration plan

The authoritative parent architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`, copied with its
recorded q4xpcc provenance. The approved repository-owned scope amendment is
`docs/architecture/xplane_fdau_core_scope_amendment.md`. It makes
`xplane-fdau` the X-Plane-specific, transport-free core; assigns reusable
ARINC and FDM/FOQA-support behavior here; and keeps concrete XPPython3/XPLM and
`xplane-webapi` implementations in external clients.

The implemented repository-specific migration specification is
`docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`.
Completed implementation plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.

Identity and native-FDR-kernel migration: implemented and verified, but unreleased.

## Current session checkpoint — 2026-09-06

### Current state and last completed action

T1.5 guarded child-state and gate-evidence mutations are governance-only,
independently reviewed, and verified with 5/5 evidence gates. No local child is
selected. The valid backlog report recommends `T1.6` with `write_plan`.

The temporary `t1-5-guarded-mutations` branch is locally complete but unmerged,
pending the user's finishing choice. No push, tag, package publication, GitHub
release, or other release action occurred.

### Important context and constraints

`ROADMAP.md` remains the capability-order authority and `BACKLOG.md` the only
mutable delivery ledger. Runtime remains pure Python and standard-library-only;
simulator I/O, XPLM/XPPython3, `xpwebapi`, and q4xpcc remain outside this
repository. Use `unittest`, never pytest. Tags, package publication, GitHub
releases, and the unreleased `0.1.0` distribution remain separately gated.

`C1.1` through `C4.4` remain unimplemented. Consequently `I1.1` and `I2.1`
remain ineligible. `A1.9` remains unready, so `I1.2` is also unready. Do not
modify q4xpcc from this repository.

### Decisions

- The T1.5 implementation edits repository governance state only; it adds no
  runtime dependency or external client.
- The accepted implementation revision is `3cef7da`; its independent rereview
  reported zero unresolved Critical, Important, or Minor findings.
- Finishing-branch integration, worktree removal, and any ordinary Git sync are
  intentionally deferred to the user's explicit choice.

### Immediate next actions

1. Let the user choose the finishing action for the locally complete T1.5
   branch; do not integrate or push implicitly.
2. After authorized integration and merged-result verification, write the
   single-child T1.6 plan using `superpowers:writing-plans` and audit it with
   `gzs-plan-audit` before implementation.
3. Preserve the governed dependency path: `T1.6 -> T2.1 -> T2.2/T3.1 -> B1.1
   -> C1.1`.

### Pending work, blockers, and open loops

T1.6 must precede T2.1; T2.1 unlocks peer children T2.2 and T3.1. Both peers
must be verified before B1.1 can resume, and B1.1 must be verified before C1.1
implementation begins. The C1→C2→C3→C4.4 chain must close before I1.1 or I2.1
adoption. A1.9 and I1.2 remain farther downstream. Formal release gate G1
remains waiting.

### Verification already run and still required

T1.5 correction revision `3cef7da` passed the full repository quality gate:
449 discovery tests in 260.582 seconds, 449 coverage tests in 261.039 seconds
at 94%, and all configured analyzers. Its accepted rereview passed 106 focused
tests in 181.469 seconds. Fresh branch-closeout quality, strict documentation,
hygiene, backlog audit/status/next, and Git checks are recorded in the T1.5
completion evidence. Merged-result verification remains pending the
user's finishing choice.

### Evidence and artifact references

- T1.5 plan: `docs/superpowers/plans/2026-09-06-t1-5-guarded-child-state-mutations.md`
- T1.5 completion: `.superpowers/sdd/2026-09-06-t1-5-guarded-child-state-mutations/completion.md`
- T1.5 accepted review: `.superpowers/sdd/2026-09-06-t1-5-guarded-child-state-mutations/review.md`
- T1.5 verification: `.superpowers/sdd/2026-09-06-t1-5-guarded-child-state-mutations/gate-1.md` through `gate-5.md`
- Governing T1 design: `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- Consumer planning brief: `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`

### Suggested skills for the next session

Use `superpowers:finishing-a-development-branch` only after the user chooses a
finishing action. After integration, use `gzs-router`, the backlog-status
command, `superpowers:writing-plans`, and `gzs-plan-audit` for T1.6. Use
`gzs-session-handoff` or `gzs-git-sync` only on an explicit user request.

## Historical local integration checkpoint

This checkpoint predates the current D1.3 branch. On 2026-09-05, the user
authorized local integration and removal of the completed D1.2 worktree. Local
`main` fast-forwarded to
`327bc4b91a8eee23cc425d08ac0ad0100cad9dbb`. Fresh merged-result verification
passed 280 standard-library `unittest` tests, 94% statement coverage, the full
repository quality gate, strict MkDocs, and Git whitespace checks. The final
independent branch review found no Critical, Important, or Minor issue.

The `d1-2-contract-verification` branch and its
`.worktrees/d1-2-contract-verification` worktree were removed after verification.
All reviewed deliverables are committed on `main`; the five ignored working
notes were copied and hash-checked into the primary checkout's existing
`.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/`
directory. Only the primary `main` worktree remained at that checkpoint.

Before reporting backlog status or selecting another increment, inspect
`git worktree list --porcelain` and the status and commits of any linked
worktrees. Report completed but unmerged work explicitly so it is integrated
through the authorized workflow before being mistaken for unfinished work.
The selected next increment at that checkpoint was `D1.3`, the reviewed q4xpcc
consumer brief.
No push, tag, publication, or release occurred. That sentence records the
checkpoint's historical activity; it is not a current prohibition on a
separately requested ordinary Git sync.

## Historical verified maintenance progress

Local `main` includes the reviewed GeoJSON no-overwrite collision correction:

- `4623275` (`fix: stabilize GeoJSON destination conflicts`) translates a
  `FileExistsError` raised by the atomic no-replace publication step into the
  stable consumer-facing error `<destination>: GeoJSON output already exists`.
  It retains `os.link()` as the race-safe commit point, preserves an existing
  or raced destination, removes the unpublished partial, and keeps the original
  `FileExistsError` as the domain error's cause.
- `a1b32ee` (`test: strengthen GeoJSON collision cause assertion`) applies the
  independent review's only minor suggestion by proving the exact collision
  exception remains chained. The review reported no Critical or Important
  findings.

Merged-result verification on 2026-08-23 passed 276 standard-library
`unittest` tests with 94% statement coverage, all repository quality gates,
`git diff --check`, and the strict MkDocs build. The clean integration
checkpoint was `a1b32eedc736f0dd87276255f14ec52b64300119` on local `main`, 17
commits ahead of `origin/main`; no push, tag, publication, or release occurred.
This maintenance correction did not itself satisfy a D1 acceptance gate. At
that historical checkpoint, `D1.1` was the next selected work. Later D1
completion is recorded below. The no-push statement describes that historical
maintenance activity, not the current explicit Git-sync policy.

## Current roadmap and design review

`ROADMAP.md` is the capability-order and release-gate authority. `BACKLOG.md`
is the measurable delivery ledger. Point Superpowers to the backlog and advance
one primary child slice per run.

The pre-canonical build correction is `B1.1`, governed by:

`docs/superpowers/specs/2026-08-09-src-layout-migration-design.md`

It moves the runtime package to `src/xplane_fdau` and strengthens installed
import isolation without changing the distribution identity, public API, or
runtime dependency boundary. The written specification is approved and its
draft plan is:

`docs/superpowers/plans/2026-08-09-src-layout-migration.md`

`B1.1` is `specified`, not implemented, and resumes only after peer local
repository-workflow prerequisites `T2.2` and `T3.1` are verified.

The active repository-governance design is:

`docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`

It defines the repository-local `T1` governance-tooling epic as six run-sized
children, `T1.1` through `T1.6`. `T1.1`, Markdown authority and explicit
inventory normalization, is historical verified work. Its completed
implementation plan is:

`docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md`

`T1.1` through `T1.4` are historical `verified` work: each has four committed
gates and accepted independent-review evidence. `T1.5` is also `verified`,
with five committed gates and accepted independent-review evidence. `T1.2`
review correction commit
`1468c98` closed all findings without weakening the implementation, release,
or publication gates. Its approved focused implementation plan remains:

`docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md`

The tooling does not govern consumer projects or ship in the distribution.

`T1.4` delivers deterministic, read-only next-action selection through the
backlog-status human report, schema-version-1 JSON report, and human-only
`next` command. Independent review accepted implementation revision
`972a36767aa2e372ac6d742a5fe92716509cafad` with no unresolved finding. The
review and four gate records became committed evidence at `7feb4f2` and
`dc5fb1a`; the verified ledger transition is
`680f258cc37ecfcf83502554d61ed8f016e0cf99`. Fresh verification passed 33
focused tests in 55.108 seconds, the full quality gate with 382 tests twice
(111.886 and 110.398 seconds), 94% statement coverage, and strict MkDocs in
2.95 seconds. No runtime, distribution, deployment, release, or q4xpcc surface
changed.

The final pre-handoff hygiene candidate also passed the offline lock check,
382 discovered tests in 109.769 seconds, 382 coverage tests in 109.412 seconds
at 94%, every configured quality analyzer, and all pre-commit hooks. The
documentation-specific pass ran 15 tests, strict MkDocs in 1.41 seconds, and
the 43.6% documentation threshold.

No local child is selected. The deterministic next action is `T1.6` with
`write_plan`. Its dependency chain continues through `T2.1`, the peer children
`T2.2` and `T3.1`, and `B1.1` before canonical implementation can begin at
`C1.1`.

## Canonical workflow catalog

On 2026-09-05 Jeff adopted all eleven workflows from
`https://github.com/tvproductions/gz-skills` and sunset the localized Git-sync
version. The canonical unmodified snapshots are discovered at
`.agents/skills/gzs-*`; `gz-skills.lock.json` pins source revision
`e925081362eec2517ab429517e250ecca6877cdc`, paths, versions, and full-tree
hashes. The catalog is `gzs-agent-context-diet`, `gzs-cross-platform-python`,
`gzs-git-sync`, `gzs-intent-audit`, `gzs-plan-audit`, `gzs-quality-gate`,
`gzs-repository-hygiene`, `gzs-router`, `gzs-session-handoff`,
`gzs-tech-debt-review`, and `gzs-update-dependencies`.

Project-local quality, hygiene, documentation, and release guidance remains
subordinate command/domain adaptation. `gzs-git-sync` and
`gzs-session-handoff` are explicit-only; installation, ordinary coding, local
integration, or another workflow never invokes them. An explicit Git-sync
request authorizes an ordinary guarded commit and push, followed by a fresh
fetch and proof of `ahead=0`, `behind=0`. It never authorizes force push,
destructive reset, hook bypass, unrelated cleanup, tags, package publication,
or a GitHub release.

This dated current-policy amendment supersedes older no-push wording only for
explicitly requested ordinary Git synchronization. Accepted D1 designs, the
D1.3 brief, and other provenance-locked historical evidence remain unchanged;
their implementation and release boundaries still apply, but their historical
no-push statements are not the current routine-Git rule.

## q4xpcc contract-handoff readiness

The approved D1 design is:

`docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`

`D1.1` canonical C1-C4 design approval is verified. Its focused execution plan,
accepted independent review, and four gate records are:

- `docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md`;
- `.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/review.md`; and
- `.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-1.md`
  through `gate-4.md`.

Final local verification passed 70 focused governance/status tests, 278 full
standard-library `unittest` tests, 94% statement coverage, the complete
repository quality gate, 15 public-API/documentation tests, strict MkDocs, the
documentation quality gate, human/JSON status with no finding, and Git
whitespace/scope checks.

`D1.2` acquisition, recording, projection, and pinning contract design is
verified. Its approved contract-only design, completed execution plan, accepted
independent review, and four verification records are:

- `docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md`;
- `docs/superpowers/plans/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts.md`;
- `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/review.md`; and
- `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-1.md`
  through `gate-4.md`.

The eleven-pass review accepted design revision
`7e8490f4db9fe5b97603c0e0f9d516d2a14d1cd5` with no unresolved Critical,
Important, or Minor finding. The four gates establish complete q4xpcc Slice
2A-2D and A1/R1/P1 contract coverage, exact versioned families and future
resources, reproducible deployment pinning with closed-world
no-divergent-subset proof, and preserved implementation/adoption/release
boundaries.

Final D1.2 local verification passed 72 focused governance/status tests, 280
full standard-library `unittest` tests, 94% statement coverage, the complete
repository quality gate, 15 public-API/documentation tests, strict MkDocs, the
43.6% documentation quality gate, human/JSON status with no finding or
recommendation, and Git whitespace checks.

This is a contract-only outcome. It delivers no A1/R1/P1 runtime model,
schema, fixture, conformance corpus, implementation plan, artifact, deployment
receipt, native-FDR output, or q4xpcc adoption. All downstream delivery gates
remain zero; the four standards children blocked by unavailable licensed
sources retain their truthful blocked states and queued resume states.

`D1.3` reviewed q4xpcc Phase 24A consumer handoff is verified. Its planning
brief, completed plan, accepted independent review, and four verification
records are:

- `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`;
- `docs/superpowers/plans/2026-09-05-d1-3-q4xpcc-handoff.md`;
- `.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/review.md`; and
- `.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/gate-1.md` through
  `gate-4.md`.

Independent review accepted corrected brief revision
`a1d15ed243eb91fc81b775e8026261067c385250` with SHA-256
`8c0184fd5c28da6a3fcc8ddd44466861d090eacfe718a8d07f9416ad1324083c`.
The clean delivery envelope emitted that exact `HEAD` followed by the brief
from that commit. The source-snapshot pin inside the brief remains the distinct
input-document revision `f86c6f939f1fdbfd354660c432363b9aa7f8444d`.

`I1.0` is eligible as the next reportable external action so the user can
reconcile q4xpcc's Phase 24A specification and plans. `T1.3` is verified at
4/4 under its [completed plan](docs/superpowers/plans/2026-09-05-t1-3-structural-audit.md)
and [accepted review](.superpowers/sdd/2026-09-05-t1-3-structural-audit/review.md)
of source `1211466`. `T1.4` is also historical verified work at 4/4 under its
[completed plan](docs/superpowers/plans/2026-09-06-t1-4-deterministic-next-action-selection.md)
and [accepted review](.superpowers/sdd/2026-09-06-t1-4-deterministic-next-action-selection/review.md)
of source `972a367`. `T1.5` is verified at 5/5 under its
[completed plan](docs/superpowers/plans/2026-09-06-t1-5-guarded-child-state-mutations.md)
and [accepted review](.superpowers/sdd/2026-09-06-t1-5-guarded-child-state-mutations/review.md)
of source `3cef7da`. No local child is selected; the status command now
recommends `T1.6` with `write_plan`. External eligibility does not add an
external boundary to the local-child inventory. T1.4 was integrated into
`main`, verified there, synchronized to `origin/main`, and its temporary branch
and worktree were removed; T1.5 remains locally complete and unmerged pending
the user's finishing choice.

The external q4xpcc thresholds remain distinct:

- `I1.0` now permits Phase 24A specification and plan reconciliation because
  `D1.3` is verified.
- `I1.1` permits delivered contract-model, schema, fixture, and runtime
  adoption only after `C4.4`.
- `I1.2` permits live XPLM acquisition adoption only after `A1.9`.

This is a reviewed planning-only handoff. It delivers no canonical model,
runtime API, schema, fixture, conformance corpus, implementation artifact,
deployment receipt, native-FDR output, or q4xpcc adoption. It does not satisfy
`I1.1`, `I1.2`, or `G1`, and does not authorize release, push, tag, or
publication.
`C1.1` through `C4.4` remain unimplemented, so no consumer-ready C4.4 handoff
exists and `I1.1` remains ineligible. `A1.1` through `A1.9` also remain
unimplemented; `A1.9` and `I1.2` are not live-acquisition-ready.
That historical D1 operation did not request Git sync; current explicit-sync
authority remains governed separately by `gzs-git-sync`.

The approved translation of q4xpcc's remaining project-local workflows is:

`docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`

It defines future deterministic project adapters: `T2.1` supplies exact
xplane-fdau hygiene commands beneath `gzs-repository-hygiene`, `T2.2` supplies
dependency/toolchain mechanics beneath `gzs-update-dependencies`, and `T3.1`
supplies guarded project state handling beneath `gzs-git-sync`. All remain
`specified` with zero gates satisfied; the canonical suite installation does
not deliver them. `T2.2` keeps an exact `uv` pin moving toward new stable
releases while ordinary development dependencies use compatible declarations
plus the complete lock. Superpowers remains an external dependency and is
excluded from parity comparison and dependency refresh; no Superpowers skill
is copied or treated as a local onboarding target. The ignored
`.agents/superpowers` checkout supplies
the upstream workflow through the ignored `.agents/skills/superpowers`
discovery junction; `.codex/skills` remains project-specific. Completed
feature worktrees merge back to `main`, pass merged-result verification, and
are removed with their temporary branches. q4xpcc is read-only design input
and is not a runtime, tooling, or checkout dependency.

The approved canonical-contract design is:

`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`

Its five-pass independent whole-design review ended `ACCEPTED` with no
Critical, Important, or Minor finding. `C1` through `C4` are architectural
epics, decomposed in `BACKLOG.md` into 18 child slices `C1.1` through `C4.4`.
All 18 are now `specified`; `C1.1` through `C4.3` remain at `0/4`, `C4.4`
remains at `0/5`, every C Plan/Review/Resume/Reason field remains `—`, and no C
acceptance checkbox is satisfied. No runtime code, schema, fixture,
conformance corpus, artifact, C implementation plan, release, push, tag, or
publication was created by D1.1. Do not create a separate handoff workflow or
collapse an epic into one implementation plan.

The project is the unreleased `xplane-fdau` virtual FDAU/FDIU distribution:

- Repository: `https://github.com/tvproductions/xplane-fdau.git`
- Distribution: `xplane-fdau`
- Import package: `xplane_fdau`
- Approved Python policy: `>=3.12,<3.15`, verified on 3.12, 3.13, and 3.14;
  the metadata-bound update is queued in `T2.2`
- Runtime dependencies: none

Native X-Plane FDR v3/v4 remains retained migration material beneath explicit
format and sink boundaries. It is a deliberately lossy projection, replay
format, and recording sink; it is not the canonical FDAU archive.

## Required next specifications

Before any release, separately reviewed increments must define, in order:

1. measurement, binding, observation, sample, frame, timing, and quality contracts;
2. acquisition profiles, demand resolution, continuity, and generic fan-out;
3. the canonical archive, manifest, recovery, and deterministic replay; and
4. projection from canonical samples to the native FDR sink with explicit loss
   reporting.

ARINC profiles and codecs remain later local standards-governed work using
licensed, edition-pinned sources. FDM and FOQA-support mechanics are later
local `F1.1` through `F1.6` work informed by FAA AC 120-82. Approved-program
governance, identity custody, corrective-action authority, protections, and
regulatory claims remain external.

## Release boundary

No release tag, GitHub release, or PyPI publication is authorized. Version
`0.1.0` remains unreleased until the required canonical vertical slice is
implemented and independently reviewed. A separately requested ordinary Git
sync may push through `gzs-git-sync` safeguards and does not change release
readiness or publication authority.

Use only Python's standard-library test framework. Keep runtime code
standard-library-only and do not add Web API, XPLM, XPPython3, q4xpcc, or
network-client dependencies.
