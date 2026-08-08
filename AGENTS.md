# Agent Instructions

## Session Entry

- Read `HANDOFF.md` before taking any project action.
- Read the complete design at
  `docs/superpowers/specs/2026-08-08-xplane-fdr-core-design.md`.
- The written design is awaiting user review. Do not implement or scaffold the
  package until the user approves that written specification.
- After approval, use the Superpowers `writing-plans` workflow before
  implementation.

## Testing

- **NO pytest. EVER.** Do not add, suggest, or assume pytest as a testing
  framework.
- Use Python's `unittest` framework.

## Runtime Boundary

- `xplane-fdr` must remain pure Python and standard-library-only at runtime.
- Do not introduce a dependency on `xpwebapi`, XPPython3, XPLM, or any network
  client.
