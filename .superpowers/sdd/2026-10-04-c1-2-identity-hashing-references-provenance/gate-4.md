# C1.2 gate 4 — Immutable authority and provenance

- **Child:** `C1.2`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-04
- **Subject:** Authority, provenance, producer, provider, and adapter values are immutable and round-trip.

`tests.test_contract_provenance` verifies all five models' exact semantic field order, frozen/slotted keyword-only construction, and plain-object constructor/converter round-trip. Optional properties are omitted, with independent locator/hash optionality. Provenance sources enforce exactly one revision/version; producer source revisions use VersionText. NFC, length, revision, Cc/Cf, and model-wide error-tier regressions report exact paths. Catalog provenance copies caller sequences to tuples, preserves order, enforces 1..256 entries, and reports the first repeated revision/version identity at its indexed pointer. Runtime provenance deduplication uses explicit validation rather than assertions.

The final focused integration run passed 41 tests. External installed smoke checks the exact provenance wire value on Python 3.12.14. Complete hygiene, immutable artifact hashes, and review disposition appear in `completion.md`.
