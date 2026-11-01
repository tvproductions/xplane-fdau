# C2.1 explicit policies and provenance

- **Child:** `C2.1`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** C2.1 measurement-definition implementation 594d7414ec67c323d18e6bdc29a4aa47de118d60

Definition constructors require explicit freshness, interpolation, discontinuity, allowed validity/quality, sensitivity, applicability, authority and provenance. Focused tests cover optional freshness thresholds and ordering, lexical/unique array sets, empty quality without inferred validity, ordered unique limitations/provenance, selector class uniqueness, limits and defensive copies. Required constructor parameters precede optional numeric/enumeration; semantic validation keeps its independent property order. No source acquisition, interpolation execution or operational finding is inferred from metadata.

Evidence is bound to source commit `594d7414ec67c323d18e6bdc29a4aa47de118d60` and the 141 canonical raw inputs in `inputs.json`. The complete offline hygiene command passed on this unchanged candidate: `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. It includes strict backlog/docs, all-files Ruff/format/ty/unittest hooks and fresh strict artifacts. The separately built wheel/sdist hashes exactly match hygiene's pair, and the external Python 3.12.16 wheel-only smoke passed with empty runtime requirements. `verification.json` records hashes and historical import origins. Both successful external artifact environments were removed. Raw execution logs are local-only in the execution archive; they are not fresh-clone inputs.
