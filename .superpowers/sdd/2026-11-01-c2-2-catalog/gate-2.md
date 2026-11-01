# C2.2 duplicate and noncanonical definition order rejection

- **Child:** `C2.2`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** duplicate and noncanonical definition order rejection

Verified source commit: `510a11805bfaa3bb8f59a09489b188a2b5d5173a`. Governing approved specification:
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`.
Executed plan: `docs/superpowers/plans/2026-11-01-c2-2-measurement-catalog.md`.
The committed `verification.json` binds 145 source/test/tool/configuration inputs,
artifact hashes, installed identity and observed command results. Raw execution
logs are local-only under this directory's `execution/`; the plan ledger is
local-only under `.superpowers/sdd/2026-11-01-c2-2-measurement-catalog/`.

The explicit pair matrix accepts several ascending revisions of one ID and
rejects duplicate pairs/descending revisions at `/definitions/1/definition_revision`
and descending IDs at `/definitions/1/definition_id` without sorting inputs.
Fresh-hash loader fixtures preserve those semantic paths; stale hashes retain
their earlier hash tier. Competing-error regressions prove all shapes precede
all canonical domains, which precede all hashes, which precede semantics.
A malformed root hash retains its final semantic position. The installed wheel
rejects ordering and stale hashes and retains exact references after round trip.
