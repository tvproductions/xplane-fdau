# C2.3 Closed explicit failure dispositions

- **Child:** `C2.3`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-15
- **Subject:** Closed explicit failure dispositions

Reviewed implementation: `364db7f3a2ef6aa73cb7e3cbbdf4b8d2d1af692c`, base `ff26d12fd08d37c51440ca59cd6765dc3d3c808e`, plus the parameter-domain ordering correction pinned by raw input hashes in [verification.json](verification.json). This avoids a self-referential source-commit claim for the commit containing this evidence and the correction. The reviewed specification is `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`; the executed plan is `docs/superpowers/plans/2026-11-15-c2-3-source-binding-definition.md`.

Tasks 1–3 require all six failure conditions and closed explicit dispositions, with no policy defaults. Unavailable, orphaned and read-error conditions reject accept_flagged; irrelevant properties are rejected. Task 4 proves the installed public behavior and its negative controls. C2.4 retains measurement authorization, and C3 retains sample disposition evaluation/precedence.

Focused evidence: `tests.test_binding_models.BindingModelTests.test_closed_binding_vocabularies; tests.test_binding_models.BindingModelTests.test_failure_policy_rejects_unusable_flagged_conditions; tests.test_installed_smoke.InstalledSmokeTests.test_source_binding_smoke_detects_ineffective_rejections`.

The 102-test final focused run, complete corrected-candidate offline hygiene, strict artifacts and external Python 3.12.16 installed smoke passed. Whole-entry duplicate/shape/domain/hash/semantic ordering and preconstruction barriers passed. Raw execution logs and public-constructor/irrelevant-policy negative controls remain local under `.superpowers/sdd/2026-11-15-c2-3-source-binding-definition/`.

C2.4/C3/A1.4/C4.3 boundaries remain as documented; this receipt grants no integration, sync or publication authority.
