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

The active repository-governance design is:

`docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`

It defines `T1.1`, a Markdown-native backlog status and guarded state-management
skill. The written specification is drafted for review and is not yet
implementation authority. It remains repository-local and does not govern
consumer projects or ship in the distribution.

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
