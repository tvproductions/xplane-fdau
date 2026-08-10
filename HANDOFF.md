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
is the measurable delivery ledger. The active canonical-contract design is:

`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`

That specification is drafted for written review and is not yet implementation
authority. After approval it is executed through four separately reviewed plans
tracked as backlog slices `C1` through `C4`; the first plan is the canonical
contract foundation. Do not collapse the four slices into one oversized plan.

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

Use `unittest`; never introduce pytest. Keep runtime code standard-library-only
and do not add Web API, XPLM, XPPython3, q4xpcc, or network-client dependencies.
