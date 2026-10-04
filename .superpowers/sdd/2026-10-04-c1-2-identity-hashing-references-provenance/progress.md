# SDD ledger — plan: docs/superpowers/plans/2026-10-04-c1-2-identity-hashing-references-provenance.md
Pre-flight: Task 1 validators feed Tasks 2 and 4; signatures and error paths align.
Pre-flight: Task 2 reference values and Task 4 provenance values feed Task 5; exact wire converters remain private.
Pre-flight: Task 3 hashing helpers feed Task 5; C1.1 private document encoder is already present.
Setup: Ruling: planned-to-in_progress transition requires plan metadata Status: in_progress — update plan metadata before guarded transition; cost if wrong: lifecycle audit would reject the branch state.
Task 1: RED observed 19 behavior assertion failures on surface-only validator stubs; GREEN 12 focused tests, Ruff check/format, and ty passed.
Task 1: Ruling: use focused unittest per task and one full offline hygiene gate at stable closeout — repository AGENTS.md testing cadence overrides generic TDD full-suite-per-task guidance; cost if wrong: an unrelated regression is discovered at closeout rather than after this task.
Task 1: complete (commits dd49748..89dff9d, tests: .venv/Scripts/python.exe -m unittest tests.test_contract_identity tests.test_installed_smoke -q → OK)
Task 2: RED observed missing wire fields and rejected-reference assertions on surface-only dataclasses; GREEN 18 focused tests, Ruff check/format, and ty passed.
Task 2: Ruling: parameter depth counts containers, including the root; the initial test used 32 objects plus a scalar and passed correctly, so the boundary test now uses 33 objects — matches C1.1 depth definition; cost if wrong: a depth boundary could be off by one.
Task 2: complete (commits 89dff9d..32dd36b, tests: .venv/Scripts/python.exe -m unittest tests.test_contract_identity tests.test_public_api tests.test_installed_smoke -q → OK)
Task 3: RED observed three byte-preimage/validation assertion failures on helper stubs; GREEN 25 focused tests, Ruff check/format, and ty passed.
Task 3: Ruling: update the C1.1 exact public-export regression test for additive C1.2 reference exports — Task 2 plan file map omitted tests/test_canonical_json.py; cost if wrong: public API drift could be masked by a broad expected set.
Task 3: complete (commits 32dd36b..89643b6, tests: .venv/Scripts/python.exe -m unittest tests.test_contract_content_hash tests.test_canonical_json tests.test_installed_smoke -q → OK)
Task 4: RED observed four behavior assertion failures on surface-only models; GREEN 32 focused tests, Ruff check/format, and ty passed.
Task 4: Ruling: catalog provenance accepts a Sequence and copies it to a tuple — the spec requires defensive copies of caller sequences, while the plan signature said tuple; cost if wrong: a broader input boundary is accepted.
Task 4: complete (commits 89643b6..9db9ff0, tests: .venv/Scripts/python.exe -m unittest tests.test_contract_provenance tests.test_public_api tests.test_installed_smoke tests.test_canonical_json -q → OK)
Task 5: RED observed three installed-smoke fault-injection assertion failures; GREEN 35 focused tests, Ruff check/format, and ty passed. Integration candidate committed; review and gates pending.
Final: five Important findings reproduced with 14 assertion failures; corrected bounded parameter copying, nested Mapping parity, canonical equality, model-wide tiers, and Int64 overflow; GREEN 41 focused tests, Ruff, ty. Full suite pending in hygiene.
Final: Ruling: classify signed-64-bit overflow as CanonicalJSONError and validate all model shapes before domains before semantics — specification error tiers override conflicting Task 1 plan expectations; cost if wrong: callers would receive the wrong exception class or first property path.
Final: Ruling: retain the approved staged boundary for factories, public model hash dispatch, loaders, schemas, and loaded-document integration — their eligible models belong to C2/C3/C4; cost if wrong: a later consumer would lack its expected API until that child.
Final: Ruling: private hash helpers require already validated family-shaped trees — the approved plan assigns semantic document validation to later family models/loaders; cost if wrong: direct private callers could hash a semantically invalid tree.
Final: Ruling: do not add Python dictionary-key hashability for AlgorithmRef — the spec requires immutability and comparison but does not promise hash(); cost if wrong: consumers attempting hash(ref) receive TypeError.
Final: Ruling: complete hygiene and installed-wheel evidence in executor closeout — independent review explicitly left these pending and does not substitute for them; cost if wrong: a delivery defect could be accepted without artifact proof.
Final: Ruling: preserve the plan workspace evidence directory and ledger — the approved repository plan requires durable receipts here, overriding generic workspace deletion; cost if wrong: ignored scratch remains until worktree cleanup.
Task 5: Ruling: update tests/test_backlog_governance.py exact plan inventory and successor expectations — full-suite assertions still encoded C1.1-only delivery despite the approved C1.2 plan; cost if wrong: governance drift could be hidden by incorrect fixture expectations.
Final: fixed bounded parameter copying — test_parameter_copy_bounds_cycles_and_deep_inputs RED→GREEN, suite 581/581.
Final: fixed list/tuple nested Mapping parity — test_parameter_mapping_copy_is_independent_of_array_container RED→GREEN, suite 581/581.
Final: fixed canonical reference equality — test_algorithm_equality_preserves_nested_primitive_types RED→GREEN, suite 581/581.
Final: fixed model-wide error tiers — test_constructor_error_tiers_precede_earlier_semantics and test_shape_then_canonical_failures_precede_semantics RED→GREEN, suite 581/581.
Final: fixed integer overflow classification — test_revisions_and_counters_reject_bool_and_out_of_range and model error-tier assertions RED→GREEN, suite 581/581.
Final: complete offline hygiene passed on 127eaa4; 581 tests, 95% coverage; external Python 3.12.14 installed smoke passed; artifact digests match the hygiene build. No deferred minors.
