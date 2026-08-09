# Agent Instructions

## Session Entry

- Read `HANDOFF.md` before taking any project action.
- Read the complete parent architecture at
  `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`.
- Read the approved migration specification at
  `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`
  and its current plan at
  `docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
- The next release remains prohibited until a reviewed canonical vertical slice
  is complete. Do not push, tag, publish, or create a release in this increment.

## Testing

- **NO pytest. EVER.** Do not add, suggest, or assume pytest as a testing
  framework.
- Use Python's `unittest` framework.

## Runtime Boundary

- `xplane-fdau` must remain pure Python and standard-library-only at runtime.
- Do not introduce a dependency on `xpwebapi`, XPPython3, XPLM, or any network
  client.
