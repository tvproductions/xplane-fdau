# C2.1 strict fields and semantic identity mismatch rejection

- **Child:** `C2.1`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** C2.1 measurement-definition implementation 594d7414ec67c323d18e6bdc29a4aa47de118d60

Representation-inapplicable fields, unknown properties/tags and primitive coercions fail closed. `tests.test_measurement_definition_io` proves parse/shape/domain/hash/semantic/build precedence, exact nested source/pointer context, stale-hash rejection after changes to semantic fields or revision, and no model construction before acceptance. Definition hashes include containing family/version context and all semantic identity/body fields. The final independent review's null-resolution tier/path defect and cyclic preprocessing hang were corrected with assertion-level regressions, bounded child-process controls, acyclic-alias checks and clean independent fix review.

The approved gate interpretation is exact current revision/hash identity and stale-content rejection. A stateless model cannot detect an author's reuse of an old published revision without historical state; author revision responsibility is documented. Shared reference factories and catalog cross-reference resolution remain later work.

Evidence is bound to source commit `594d7414ec67c323d18e6bdc29a4aa47de118d60` and the 141 canonical raw inputs in `inputs.json`. The complete offline hygiene command passed on this unchanged candidate: `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. It includes strict backlog/docs, all-files Ruff/format/ty/unittest hooks and fresh strict artifacts. The separately built wheel/sdist hashes exactly match hygiene's pair, and the external Python 3.12.16 wheel-only smoke passed with empty runtime requirements. `verification.json` records hashes and historical import origins. Both successful external artifact environments were removed. Raw execution logs are local-only in the execution archive; they are not fresh-clone inputs.
