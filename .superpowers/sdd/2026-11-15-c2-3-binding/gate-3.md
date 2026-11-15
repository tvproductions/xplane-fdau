# C2.3 Immutable data-only transforms and local graph

- **Child:** `C2.3`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-15
- **Subject:** Immutable data-only transforms and local graph

Reviewed implementation: `364db7f3a2ef6aa73cb7e3cbbdf4b8d2d1af692c`, base `ff26d12fd08d37c51440ca59cd6765dc3d3c808e`, plus the parameter-domain ordering correction pinned by raw input hashes in [verification.json](verification.json). This avoids a self-referential source-commit claim for the commit containing this evidence and the correction. The reviewed specification is `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`; the executed plan is `docs/superpowers/plans/2026-11-15-c2-3-source-binding-definition.md`.

Tasks 1–3 pin algorithm ID/revision/hash with recursively frozen data-only parameters that are never evaluated. Local symbol resolution admits primary, dependencies and prior steps; companions, unknown/self/forward edges, duplicate/reserved identities and mismatched value metadata are rejected. Source tuple uniqueness is per binding, independent of owner/provider/adapter versions. Algorithms are never executed. Valid repeated algorithm/input references preserve declared order.

Focused evidence: `tests.test_binding_models.BindingModelTests.test_transform_inputs_and_parameters_are_deeply_owned; tests.test_source_binding_definition.SourceBindingDefinitionTests.test_source_ids_and_resource_keys_are_jointly_unique; tests.test_source_binding_definition.SourceBindingDefinitionTests.test_transform_edges_resolve_only_prior_value_inputs; tests.test_source_binding_definition.SourceBindingDefinitionTests.test_transform_input_matches_resolved_declaration`.

The 102-test final focused run, complete corrected-candidate offline hygiene, strict artifacts and external Python 3.12.16 installed smoke passed. Whole-entry duplicate/shape/domain/hash/semantic ordering and preconstruction barriers passed. Raw execution logs and public-constructor/irrelevant-policy negative controls remain local under `.superpowers/sdd/2026-11-15-c2-3-source-binding-definition/`.

C2.4/C3/A1.4/C4.3 boundaries remain as documented; this receipt grants no integration, sync or publication authority.
