# C2.1 representation and numeric semantic invariants

- **Child:** `C2.1`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** C2.1 measurement-definition implementation 594d7414ec67c323d18e6bdc29a4aa47de118d60

`tests.test_measurement_definition` exercises all nine representations and every scalar fixed/variable-array element, required/prohibited numeric and enumeration metadata, unit/unitless quantity agreement, coordinate variants and vector axis counts, precision/resolution/range domains and enumeration ordering/unknown/reserved metadata. Explicit binary64 acceptance and independent integer resolution/minimum/maximum rejection cover real, vector and both real-array kinds. Boolean is never a numeric primitive. The Task 2 independent coverage finding was fixed and re-reviewed; no open load-bearing finding remains.

Evidence is bound to source commit `594d7414ec67c323d18e6bdc29a4aa47de118d60` and the 141 canonical raw inputs in `inputs.json`. The complete offline hygiene command passed on this unchanged candidate: `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. It includes strict backlog/docs, all-files Ruff/format/ty/unittest hooks and fresh strict artifacts. The separately built wheel/sdist hashes exactly match hygiene's pair, and the external Python 3.12.16 wheel-only smoke passed with empty runtime requirements. `verification.json` records hashes and historical import origins. Both successful external artifact environments were removed. Raw execution logs are local-only in the execution archive; they are not fresh-clone inputs.
