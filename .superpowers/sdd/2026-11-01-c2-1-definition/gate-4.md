# C2.1 immutable synthetic definitions and canonical round trips

- **Child:** `C2.1`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** C2.1 measurement-definition implementation 594d7414ec67c323d18e6bdc29a4aa47de118d60

Synthetic `test.*` definitions are frozen/slotted/keyword-only, defensively copy every sequence, cache their computed SHA-256 in a private non-init/non-comparing slot and expose a read-only content_hash. Literal canonical entry and preimage bytes, independent hashlib expectations, final LF, negative-zero normalization, property-order tolerance, semantic edit/revision hash changes, every representation round trip and mutation isolation are tested. No stock catalog ships. Installed smoke verifies public ownership, canonical entry/hash consistency, round trips, immutability and meaningful rejection controls from the exact installed wheel outside the checkout.

Evidence is bound to source commit `594d7414ec67c323d18e6bdc29a4aa47de118d60` and the 141 canonical raw inputs in `inputs.json`. The complete offline hygiene command passed on this unchanged candidate: `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. It includes strict backlog/docs, all-files Ruff/format/ty/unittest hooks and fresh strict artifacts. The separately built wheel/sdist hashes exactly match hygiene's pair, and the external Python 3.12.16 wheel-only smoke passed with empty runtime requirements. `verification.json` records hashes and historical import origins. Both successful external artifact environments were removed. Raw execution logs are local-only in the execution archive; they are not fresh-clone inputs.
