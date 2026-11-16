# C2.4 Completed binding catalog and validation

- **Child:** `C2.4`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-15
- **Subject:** Completed binding catalog and validation

Reviewed technical candidate `9efe2701e3ef55344cdde7dba12eee64d17e3364`, tree `34c807e6df9e6b5ea7094afcd0143882bbfc7940`, base `1359c99032425ad4c10f6ca0e4ee75ad517a70c9`. [verification.json](verification.json) pins 144 runtime/tool/test/packaging inputs and artifact identities. The approved canonical specification and [completed plan](../../../docs/superpowers/plans/2026-11-15-c2-4-binding-catalog-validation.md) govern this work.

All five tasks and acceptance gates passed: immutable catalogs, strict family-specific I/O, pure cross-catalog validation, normative schema, public documentation and installed proof. Native execution produced five task commits. Independent final review accepted with zero findings; no fix pass or deferred minor remains.

Full offline hygiene exited 0, including lock/backlog checks, strict documentation, all-files Ruff/format/ty, full unittest and a fresh strict artifact pair. Separate fresh external Python 3.12.16 wheel installation contained only xplane-fdau 0.1.0, with empty runtime requirements, correct site-packages origin and packaged schema. Full installed smoke passed. Windows was executed; macOS/Linux were not.

Published baseline -> pending initial unpublished `0.1.0`: remote tag/release checks were empty. BACKLOG owns the finite C/A/R/P vertical slice through G1. Completed scope adds C2.4; C3/C4/A1/R1/P1/G1 remain. S/F/external adoption/T3.1 remain outside this bundle. Metadata/runtime/lock/changelog versions agree; no published contract changes or version increment. G1, STRICT/cognitive/Lizard gaps and older recorded plugin pins remain separate.

Rulings in execution order:

- Ruling: Add eol=lf to the existing .gitattributes text=auto rule — fresh Windows checkout and the portability audit proved CRLF translation breaks required byte identities — cost if wrong: other detected text files check out with LF; binary detection and FDR -text fixture bytes remain preserved. No global configuration or other worktree changed.
- Ruling: Use explicit UTF-8 and errors=replace in the changed installed-smoke subprocess runner — scoped audit and real 0xff child regression proved locale-dependent diagnostics — cost if wrong: invalid diagnostic bytes become replacement characters, while failed status/context remain. The real test failed first on missing U+FFFD under locale decoding.
- Ruling: Retain opaque algorithm declarations — approved A1.4 ownership — cost if wrong: declaration compatibility does not prove numerical algorithm results.
- Ruling: Retain C3 ownership of sample disposition/normalization/evidence evaluation — this child authorizes declarations only — cost if wrong: actual sample evaluation is unavailable in C2.4.
- Ruling: Preserve C4.3 shared convenience dispatch closure — approved deferral and existing APIs remain unchanged — cost if wrong: callers must use the delivered family-specific I/O until C4.3.
- Ruling: Do not infer release/STRICT/other-platform acceptance from this review — G1, existing adoption gaps and unexecuted platforms remain separate — cost if wrong: these readiness claims remain unavailable.

Integration, sync, tags and publication retain separate authority. The temporary branch/worktree and external proof are preserved pending the integration choice. Raw execution evidence is archived locally in execution/ with a hash manifest before removing the plan scratch directory.
