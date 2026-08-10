# Agent Instructions

## Session Entry

- Read `HANDOFF.md` before taking any project action.
- Read `ROADMAP.md` for capability order and release gates, then `BACKLOG.md`
  for the active slice, status, governing documents, and acceptance evidence.
- Read the complete parent architecture at
  `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`.
- Read the completed migration specification at
  `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`
  and its completed plan at
  `docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
- Read the current canonical-contract specification and plan linked from
  `BACKLOG.md` before changing canonical FDAU behavior. A draft specification
  is review material, not implementation authority.
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
