# Project Handoff

## Architecture and completed migration plan

The authoritative parent architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`, copied with its
recorded q4xpcc provenance. The implemented repository-specific specification is
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

`B1.1` is `specified`, not implemented, and resumes only after the local
repository-workflow sequence through `T3.1` is verified.

The active repository-governance design is:

`docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`

It defines the repository-local `T1` governance-tooling epic as six run-sized
children, `T1.1` through `T1.6`. The selected child is `T1.1`, Markdown authority
and explicit inventory normalization. The amended written specification is
approved. `T1.1`'s completed implementation plan is:

`docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md`

`T1.1` is `verified`: all four gates and the accepted independent review have
committed evidence. No local child is selected. `T1.2` is the first
dependency-ready child; it remains `specified` and requires its own focused
implementation plan in a later run. The tooling does not govern consumer
projects or ship in the distribution.

The approved translation of q4xpcc's remaining project-local workflows is:

`docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`

It defines `T2.1` canonical full-strength `repo-hygiene` followed by `T3.1`
q4xpcc-style guarded Git synchronization with push disabled. Superpowers
remains an external dependency; no Superpowers skill is copied or treated as a
local onboarding target. q4xpcc is read-only design input and is not a runtime,
tooling, or checkout dependency.

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
- Python: 3.12 and newer
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

ARINC profiles and codecs remain later standards-governed work. FDM/FOQA remains
later downstream analysis and governance work.

## Release boundary

No release, tag, push, GitHub release, or PyPI publication is authorized. Version
`0.1.0` remains unreleased until the required canonical vertical slice is
implemented and independently reviewed.

Use only Python's standard-library test framework. Keep runtime code
standard-library-only and do not add Web API, XPLM, XPPython3, q4xpcc, or
network-client dependencies.
