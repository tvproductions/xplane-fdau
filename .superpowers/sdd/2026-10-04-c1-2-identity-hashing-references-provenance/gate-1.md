# C1.2 gate 1 — Exact identity domains

- **Child:** `C1.2`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-04
- **Subject:** Semantic identifiers, revisions, UUIDs, generations, and sequences.

`tests.test_contract_identity.IdentityValidationTests` verifies dotted ASCII identifiers at the 255-character boundary, revisions `1..2^63-1`, and counters `0..2^63-1`. It rejects Boolean integers, semantic range violations, signed-64-bit canonical overflow, uppercase/noncanonical UUIDs, nil/max UUIDs, and unsupported UUID versions/variants. SHA-256, NFC/scalar text, and VersionText boundaries retain exact property paths. Constructor regressions prove model-wide shape/canonical/semantic precedence; parameter-key paths escape `/` and `~` using RFC 6901.

The final focused integration command passed 41 unittest tests with Ruff and ty. Independent review findings were reproduced and resolved. Complete gate and artifact evidence is recorded in `completion.md`.
