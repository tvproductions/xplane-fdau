# C2.2 normative mirrored installed version-1 schema

- **Child:** `C2.2`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** normative mirrored installed version-1 schema

Verified source commit: `510a11805bfaa3bb8f59a09489b188a2b5d5173a`. Governing approved specification:
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`.
Executed plan: `docs/superpowers/plans/2026-11-01-c2-2-measurement-catalog.md`.
The committed `verification.json` binds 145 source/test/tool/configuration inputs,
artifact hashes, installed identity and observed command results. Raw execution
logs are local-only under this directory's `execution/`; the plan ledger is
local-only under `.superpowers/sdd/2026-11-01-c2-2-measurement-catalog/`.

Packaged and documentation schemas are identical canonical UTF-8/LF Draft 2020-12
resources with exact root inventory, family/version and schema URI, local refs,
closed variants and no defaults. Draft202012Validator.check_schema passes.
The representation matrix covers all 17 scalar/vector/array/payload variants,
unit/coordinate/freshness/provenance branches, required/unknown/null properties,
and runtime-only ordering/hash/NFC/lexical-number distinctions. Missing or changed
resources fail strict synthetic wheel/sdist checks; the test-discovery correction
is recorded in the plan ledger and the corrected method explicitly passed.

Installed schema SHA-256: `818b231980b48d7a2d3f553c124fe50748b21e34d3e152314a74464d0f7c0226`.
Strict real wheel/sdist validation and external resource access passed using only
the installed first-party package, without a runtime schema-validator dependency.
The executable guide's examples and schema link pass; strict MkDocs and the
41.8% documentation floor pass. See verification.json for exact artifact hashes.
