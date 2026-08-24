# Verification Evidence

- **Child:** `D1.2`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-23
- **Subject:** Exact versioned families, invariants, outcomes, and future resources

The approved design fixes all 32 acquisition, demand, transform, session,
continuity, fan-out, failure, recording, archive, checkpoint, manifest,
recovery, replay, projection, and deployment families. Each family has an
exact version-1 dispatch boundary, identity or record key, owned property
order, tagged variants, closed codes, immutable hash-pinned references,
cardinality and ordering rules, state transitions, and deterministic
validation and causal-failure precedence.

The design distinguishes malformed contract data from runtime inability,
defines exact tagged outcomes and `FailureEvidence` ownership, closes
record/definition and artifact/content identity, and fixes cross-record
reference closure for acquisition, recording, recovery, replay, native-FDR
projection, and deployment evidence. Native X-Plane FDR remains an inward,
deliberately lossy projection and sink; it is neither the canonical archive
nor a source of canonical reconstruction.

Future schema resources are fixed at
`xplane_fdau/schemas/<stem>-v1.schema.json` with byte-identical documentation
copies. Future accepted, rejected, and canonical cases retain the three
approved conformance roots. D1.2 creates none of those resources; each owning
future child must separately implement, test, review, and verify them.
