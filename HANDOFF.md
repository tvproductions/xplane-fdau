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

`T1.1` is `verified`: all four gates and the accepted independent review have
committed evidence. `T1.2` is selected and `implemented` with four committed
verification gates; it awaits independent review under its approved focused
implementation plan:

`docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md`

The tooling does not govern consumer projects or ship in the distribution.

## q4xpcc contract-handoff readiness

The approved D1 design is:

`docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`

The next-agent sequence is exact: independently review `T1.2`; execute `D1.1`
canonical-design approval; execute `D1.2` contract-only A1/R1/P1 design;
execute `D1.3` reviewed consumer brief; then report the met `I1.0` condition
so the user can reconcile q4xpcc's Phase 24A specification and plans.

The external q4xpcc thresholds remain distinct:

- `I1.0` permits Phase 24A specification and plan reconciliation only after
  `D1.3`.
- `I1.1` permits delivered contract-model, schema, fixture, and runtime
  adoption only after `C4.4`.
- `I1.2` permits live XPLM acquisition adoption only after `A1.9`.

`D1.1` through `D1.3` are specified, not complete. Do not emit the D1.3
consumer brief or invent a revision pin before its gates are satisfied.

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

The canonical-contract design remains:

`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`

Its written review is still pending. `C1` through `C4` are architectural epics,
decomposed in `BACKLOG.md` into child slices `C1.1` through `C4.4`. The first
canonical slice remains `C1.1`, canonical JSON and number encoding. Do not
create a separate handoff workflow or collapse an epic into one implementation
plan.

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
