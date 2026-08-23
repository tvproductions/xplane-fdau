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

## Latest verified maintenance progress

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
This maintenance correction did not itself satisfy a D1 acceptance gate. The
later D1.1 design-only batch is now verified, and the next selected work is
`D1.2`.

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

`T1.1` and `T1.2` are `verified`: each has four committed gates and accepted
independent-review evidence. `T1.2` review correction commit `1468c98` closed
all findings without weakening the implementation, release, or publication
gates. Its approved focused implementation plan remains:

`docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md`

The tooling does not govern consumer projects or ship in the distribution.

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

The next-agent sequence is exact: execute the selected `D1.2` contract-only
A1/R1/P1 design; execute and verify `D1.3` reviewed consumer brief; successful
D1.3 verification makes `I1.0` eligible as the next reportable action so the
user can reconcile q4xpcc's Phase 24A specification and plans.

The external q4xpcc thresholds remain distinct:

- `I1.0` permits Phase 24A specification and plan reconciliation only after
  successful `D1.3` verification.
- `I1.1` permits delivered contract-model, schema, fixture, and runtime
  adoption only after `C4.4`.
- `I1.2` permits live XPLM acquisition adoption only after `A1.9`.

`D1.2` and `D1.3` remain `specified` at `0/4` with no plan, review, or gate
evidence. Do not emit the D1.3 consumer brief or invent a revision pin before
their gates are satisfied.

The approved translation of q4xpcc's remaining project-local workflows is:

`docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`

It defines `T2.1` canonical full-strength `repo-hygiene`, followed by peer
children `T2.2` governed dependency/toolchain refresh and `T3.1` q4xpcc-style
guarded Git synchronization with push disabled. `T2.2` keeps an exact `uv` pin
moving toward new stable releases while ordinary development dependencies use
compatible declarations plus the complete lock. Superpowers remains an
external dependency and is excluded from parity comparison and dependency
refresh; no Superpowers skill is copied or treated as a local onboarding
target. The ignored `.agents/superpowers` checkout supplies
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

No release, tag, push, GitHub release, or PyPI publication is authorized. Version
`0.1.0` remains unreleased until the required canonical vertical slice is
implemented and independently reviewed.

Use only Python's standard-library test framework. Keep runtime code
standard-library-only and do not add Web API, XPLM, XPPython3, q4xpcc, or
network-client dependencies.
