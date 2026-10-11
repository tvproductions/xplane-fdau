# C1.3 gate 2

- **Child:** `C1.3`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-11
- **Subject:** Coercion, null, invalid shape and closed vocabulary rejection.

The numeric-coercion, variant, declaration-boundary, null, lexical-token, mixed-invalid and subclass tests assert exact error class/path. Full-object shape checks precede canonical domains and semantics. Null is never omission, irrelevant properties fail even when null, unknown tags fail, and primitive arrays reject heterogeneous and nested values.

Verified source: `0b25c7c6a46791aaae94b08ba5c18a3c8bfe79b0` on Python 3.12.15.

The focused values/canonical/parser/identity/provenance/public API/installed smoke/runtime boundary command passed 88 tests. Ruff lint/format, ty, and affected Xenon passed. The complete offline hygiene command `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` exited 0: 606 unittest tests, 95% coverage (2538 statements, 125 missed), offline lock/backlog audit, strict MkDocs, all-files hooks, lint/types/security/docstrings/dead-code/complexity, and fresh external wheel/sdist strict metadata and inventory verification. Docstring coverage: 41.1%. Failure messages emitted by deliberate fixture subprocesses are expected test negative controls; the aggregate suite and command passed.

External installed-wheel smoke passed on Python 3.12.15 outside the checkout. Hygiene and installed artifacts have identical SHA-256 values:

- Wheel: `2878107402c38ce9deec534970a3efc427c814c27c8a75ee3ae230cb1e1732f9`
- Sdist: `8dc840cbec4119f8208c5588824e72a370611c508cf302d227dd1571f4f5caf0`

The independent review and executor disposition are in `review.md`; both Important findings have RED-to-GREEN regressions. No required verification dimension was skipped.
