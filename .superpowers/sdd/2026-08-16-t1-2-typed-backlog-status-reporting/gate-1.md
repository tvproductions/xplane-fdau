# Verification Evidence

- **Child:** `T1.2`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-16
- **Subject:** Frozen typed model and strict Markdown parser fixtures

Fresh accepted-review remediation verification passed 62 focused model,
parser, report, CLI, and governance tests. The parser regressions cover exact
delimiter parity for every managed table family, exact-one-blank artifact
metadata, shared repository-relative path validation, letter-only epic `S`,
first-difference metadata line attribution, independent displayed gate counts,
and em-dash optional artifact fields. Scoped Ruff, format, and ty checks also
passed. The complete `uv run python tools/quality.py check` gate passed 266
tests with 94% product coverage.

Accepted-review fix round 2 added 21 doubled-edge row regressions: leading,
trailing, and both-edge doubled delimiters across all seven managed table row
families. RED accepted all 21 malformed rows because `_cells` stripped every
edge delimiter. GREEN rejects all 21 after removing exactly one required outer
delimiter. The focused suite now passes 63 tests, and the complete quality gate
passes 267 tests with 94% product coverage.
