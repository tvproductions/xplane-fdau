# B1.1 gate 2 — Physical path tooling and checks

- **Child:** `B1.1`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** Physical-path tooling and unchanged checks.

Quality source commands, source scanners, public API and schema lookup, code-quality guidance, native FDR source link, and release validation use src/xplane_fdau. Coverage and import guards continue to use the xplane_fdau package name. Task 2's test-first focused suite passed 16 tests with Ruff and ty. Full offline hygiene exited 0: Ruff lint and format (66 files), ty, 521 unittest tests, 43.9% coverage against 40%, strict MkDocs, and all-files pre-commit. The gate-discovered live backlog status test was corrected to accept a selected local child. The detect-secrets baseline was regenerated with four unchanged reviewed findings, two updated line numbers, and its self-baseline filter. No runtime package bytes changed.
