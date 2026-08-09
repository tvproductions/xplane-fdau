# Project Handoff

## Active architecture and implementation plan

The authoritative parent architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`, copied with its
recorded q4xpcc provenance. The active repository-specific specification is
`docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`.
Its reviewed implementation plan is
`docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.

The project is the unreleased `xplane-fdau` virtual FDAU/FDIU distribution:

- Repository: `https://github.com/tvproductions/xplane-fdau.git`
- Distribution: `xplane-fdau`
- Import package: `xplane_fdau`
- Python: 3.12 and newer
- Runtime dependencies: none

Native X-Plane FDR v3/v4 remains retained migration material beneath explicit
format and sink boundaries. It is a deliberately lossy projection, replay
format, and recording sink; it is not the canonical FDAU archive.

## Release boundary

No release, tag, push, GitHub release, or PyPI publication is authorized for
this increment. The next release remains prohibited until the canonical
vertical slice defines measurement, binding, observation, sample, frame,
timing, quality, acquisition, archive, replay, and native-projection contracts
through separately reviewed work.

Use `unittest`; never introduce pytest. Keep runtime code standard-library-only
and do not add Web API, XPLM, XPPython3, q4xpcc, or network-client dependencies.
