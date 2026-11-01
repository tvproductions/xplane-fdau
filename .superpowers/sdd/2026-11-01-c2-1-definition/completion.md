# C2.1 implementation and verification completion

- **Child:** `C2.1`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** C2.1 measurement-definition implementation 594d7414ec67c323d18e6bdc29a4aa47de118d60

Jeff approved the corrected plan and explicitly selected subagent-driven execution. The four implementation tasks are complete: supporting immutable semantic values; MeasurementDefinition and invariants; cached identity and staged private entry IO; installed smoke and guide. Per-task reviewers approved all tasks after the recorded fixes, and the whole-branch fix review closed both final Important findings.

Implementation checkpoints: b0de5e0, 951fd52, a4c89fa, d2ceb2d, 8cc01bc, 5ab8530 and final source 594d741. Each mandatory commit hook passed; no hooks were bypassed. Focused TDD evidence and failed attempts remain recorded. The final fix's 49 focused tests, full offline hygiene and exact external Python 3.12.16 wheel-only smoke passed. Four gate receipts substantiate the acceptance criteria; delivery-state transitions are controlled through the backlog adapter and committed separately.

C2.1 preserves inward dependencies and leaves contracts/native FDR, metadata/lockfiles and runtime requirements unchanged. Shared convenience APIs remain C4.3 work; catalogs/schemas/public family loaders remain C2.2. No global historical revision policing, normalized sample evaluation, platform/embedded-host execution, STRICT acceptance or release readiness is claimed. Main is unchanged; integration and any new remote push require their own user choice.

Evidence is bound to source commit `594d7414ec67c323d18e6bdc29a4aa47de118d60` and the 141 canonical raw inputs in `inputs.json`. The complete offline hygiene command passed on this unchanged candidate: `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. It includes strict backlog/docs, all-files Ruff/format/ty/unittest hooks and fresh strict artifacts. The separately built wheel/sdist hashes exactly match hygiene's pair, and the external Python 3.12.16 wheel-only smoke passed with empty runtime requirements. `verification.json` records hashes and historical import origins. Both successful external artifact environments were removed. Raw execution logs are local-only in the execution archive; they are not fresh-clone inputs.
