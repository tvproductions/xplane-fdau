# C2.3 Explicit declared-source and evidence boundary

- **Child:** `C2.3`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-15
- **Subject:** Explicit declared-source and evidence boundary

Reviewed implementation: `364db7f3a2ef6aa73cb7e3cbbdf4b8d2d1af692c`, base `ff26d12fd08d37c51440ca59cd6765dc3d3c808e`, plus the parameter-domain ordering correction pinned by raw input hashes in [verification.json](verification.json). This avoids a self-referential source-commit claim for the commit containing this evidence and the correction. The reviewed specification is `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`; the executed plan is `docs/superpowers/plans/2026-11-15-c2-3-source-binding-definition.md`.

Tasks 1–3 enforce provider/adapter/resource identities, closed selection/representation/shape/unit variants, applicability/dependency/companion declarations, phase and replay policy. Collections and selections are defensively owned. Both observed_representation and observed_shape are rejected on source and binding wire objects with exact pointers. Separate executable public-constructor negative controls reject both observed properties as unexpected keyword arguments.

Focused evidence: `tests.test_binding_models.BindingModelTests.test_source_representation_shape_payload_matrix; tests.test_binding_models.BindingModelTests.test_resource_selection_is_closed_and_frozen; tests.test_source_binding_definition.SourceBindingDefinitionTests.test_provenance_applicability_and_limitations_invariants; tests.test_source_binding_definition_io.SourceBindingDefinitionIOTests.test_binding_entry_rejects_observed_fields`.

The 102-test final focused run, complete corrected-candidate offline hygiene, strict artifacts and external Python 3.12.16 installed smoke passed. Whole-entry duplicate/shape/domain/hash/semantic ordering and preconstruction barriers passed. Raw execution logs and public-constructor/irrelevant-policy negative controls remain local under `.superpowers/sdd/2026-11-15-c2-3-source-binding-definition/`.

C2.4/C3/A1.4/C4.3 boundaries remain as documented; this receipt grants no integration, sync or publication authority.
