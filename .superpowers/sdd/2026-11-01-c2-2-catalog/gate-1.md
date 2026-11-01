# C2.2 exact catalog meaning and identity

- **Child:** `C2.2`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** exact catalog meaning and identity

Verified source commit: `510a11805bfaa3bb8f59a09489b188a2b5d5173a`. Governing approved specification:
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`.
Executed plan: `docs/superpowers/plans/2026-11-01-c2-2-measurement-catalog.md`.
The committed `verification.json` binds 145 source/test/tool/configuration inputs,
artifact hashes, installed identity and observed command results. Raw execution
logs are local-only under this directory's `execution/`; the plan ledger is
local-only under `.superpowers/sdd/2026-11-01-c2-2-measurement-catalog/`.

Observed model and public I/O checks prove required catalog identity/revision,
owned authority, nonempty unique ordered provenance, optional title/scope,
immutability, tuple isolation and exact ID/revision/hash references. Independent
literal canonical preimages pin entry and catalog hashes, including nested entry
hashes. Catalog metadata changes preserve unchanged entry identity. The public
round-trip and all representation branches pass. Whole-document stages validate
before constructing structural models; real constructor/builder guards include
a direct-constructor negative control and a valid-load positive control.

Commands: Task 1 focused suite (67 checks), Task 2 focused suite (80), Task 4
focused suite (88), final correction focused suite (49), complete offline hygiene
and external Python 3.12.16 wheel-only smoke all exited 0 at their recorded stages.
