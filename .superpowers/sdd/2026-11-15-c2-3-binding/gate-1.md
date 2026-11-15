# C2.3 Exact measurement reference identity

- **Child:** `C2.3`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-15
- **Subject:** Exact measurement reference identity

Reviewed implementation: `364db7f3a2ef6aa73cb7e3cbbdf4b8d2d1af692c`, base `ff26d12fd08d37c51440ca59cd6765dc3d3c808e`, plus the parameter-domain ordering correction pinned by raw input hashes in [verification.json](verification.json). This avoids a self-referential source-commit claim for the commit containing this evidence and the correction. The reviewed specification is `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`; the executed plan is `docs/superpowers/plans/2026-11-15-c2-3-source-binding-definition.md`.

Tasks 2–3 retain the exact measurement ID, revision and lowercase SHA-256 triple. Reference syntax/ranges are validated; opaque valid references remain constructible without a catalog. Identity is independently checked against the source-binding family preimage; altered pinned hashes change identity, and stale entry hashes are rejected.

Focused evidence: `tests.test_source_binding_definition.SourceBindingDefinitionTests.test_binding_pins_exact_measurement_triple; tests.test_source_binding_definition.SourceBindingDefinitionTests.test_binding_identity_has_independent_family_preimage; tests.test_source_binding_definition_io.SourceBindingDefinitionIOTests.test_binding_entry_round_trip_preserves_exact_references; tests.test_source_binding_definition_io.SourceBindingDefinitionIOTests.test_stale_hash_precedes_graph_but_reference_hashes_are_opaque`.

The 102-test final focused run, complete corrected-candidate offline hygiene, strict artifacts and external Python 3.12.16 installed smoke passed. Whole-entry duplicate/shape/domain/hash/semantic ordering and preconstruction barriers passed. Raw execution logs and public-constructor/irrelevant-policy negative controls remain local under `.superpowers/sdd/2026-11-15-c2-3-source-binding-definition/`.

C2.4/C3/A1.4/C4.3 boundaries remain as documented; this receipt grants no integration, sync or publication authority.
