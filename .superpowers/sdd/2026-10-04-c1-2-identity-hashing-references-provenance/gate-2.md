# C1.2 gate 2 — Canonical self-hash preimages

- **Child:** `C1.2`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-04
- **Subject:** Definition and record self-hashes use their prescribed canonical preimages.

`tests.test_contract_content_hash` pins exact UTF-8 record and definition preimage literals, including the final LF, and independently computed literal SHA-256 digests. Record hashing removes only root `content_hash`; definition hashing wraps the entry in its catalog family, integer schema version 1, and `definition`, removing only that entry's hash. Nested hashes remain included. Missing/present self-hash forms and reordered object properties converge. Changed identity, revision, authority, provenance, body, nested hash, family, or array order changes the digest. Malformed declared self-hashes and unsupported definition families fail without mutating caller data.

The final focused integration run passed 41 tests. External installed smoke repeats byte-exact record/definition and literal-digest assertions using the built wheel on Python 3.12.14. Full artifact hashes and complete gate evidence appear in `completion.md`.
