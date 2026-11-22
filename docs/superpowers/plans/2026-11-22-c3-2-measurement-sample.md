# C3.2 Measurement Sample Record and Schema Implementation Plan

- **Governance:** active
- **Status:** draft
- **Date:** 2026-11-22
- **Roadmap child:** `C3.2`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** —
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the immutable version-1 measurement sample, its strict binary interchange and its mirrored schema, with executable evidence for all four C3.2 gates.

**Architecture:** The acquisition package owns the sample and its nested declarations. Project each record explicitly and validate the entire wire document in phases before constructing models, including any raw observation embedded in the sample. Reuse the existing reference, value, clock and quality contracts.

**Tech stack:** Python 3.12.16, uv 0.13.6, standard library at runtime, unittest, Ruff, ty, existing development-only jsonschema and MkDocs.

**Spec:** [Approved canonical measurement contract](../specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md#measurement-sample), [core scope amendment](../../architecture/xplane_fdau_core_scope_amendment.md), [roadmap](https://github.com/tvproductions/xplane-fdau/blob/a56489793ad57db35141cec5cb82439f3b6dd68e/ROADMAP.md#L136), and [C3.2 backlog gates](https://github.com/tvproductions/xplane-fdau/blob/a56489793ad57db35141cec5cb82439f3b6dd68e/BACKLOG.md#L317).

## Global constraints

- The literal sample family is `https://tvproductions.github.io/xplane-fdau/contracts/measurement-sample`, with integer version `1`. Its schema ID is `https://tvproductions.github.io/xplane-fdau/schemas/measurement-sample-v1.schema.json`. Omit absent optional properties. Reject `null` and extra properties. The sample hash omits only the sample's root `content_hash` and includes the final LF. Preserve embedded observation hashes, pinned reference hashes and payload SHA-256 in the sample preimage.
- Apply the approved exact property inventories, semantic order and error tiers. Use UTF-8 without BOM and one final LF for canonical output. Carry source, record identity where recoverable, family, exact JSON Pointer, and syntax/duplicate locations where available. Never echo raw inline evidence, payload contents or algorithm parameters.
- C3.2 validates the record and its local consistency. Persist lineage and derivation in their declared order and preserve the optional `UInt63` age. C3.3 owns catalog resolution, transform-prefix and failure-policy authorization, raw identity and status corroboration against binding inputs, exact freshness and stale-threshold calculation, reference resolution and graph closure. Apply the same C3.3 age validation to inline and referenced primary observations. Require a host-monotonic evaluation clock and matching reading domain. Preserve the evaluation clock's producer identity independently of the sample producer, following the exact property description in the design.
- `freshness_age_ns` uses the same integer unit as the shipped freshness thresholds. Actual resolution comes from the adapter's declared clock. Age measures elapsed host time from receipt to evaluation in one clock domain. A 12 ms age is `12_000_000` on the wire. X-Plane cycle information and source timing remain separate evidence, with unavailable source timing omitted.
- C3.4–C3.5 own frames. C4 owns family inventory, conformance corpus and shared public API and artifact closure. Keep `record_ref`, model `canonical_bytes` and `compute_content_hash` dispatch on their existing C4.3 track. A1.4 owns algorithm execution. Runtime remains dependency-free and preserves existing native FDR and raw-observation behavior.

## Planning baseline and release scope

The clean planning base is `a56489793ad57db35141cec5cb82439f3b6dd68e` on `main`, matching the local `origin/main` reference. Strict backlog audit reported no findings, no active child, and `write_plan C3.2` with 0/4 gates. The native Superpowers and gz-skills installations match the handoff's observed revisions. The adoption lock and STRICT acceptance remain separate from this slice.

Fresh November 22 checks found no local or remote tags and an empty GitHub release list. Remote `main` matched the planning base. The [selected release record](https://github.com/tvproductions/xplane-fdau/blob/a56489793ad57db35141cec5cb82439f3b6dd68e/BACKLOG.md#L103) therefore still gives no published baseline → pending initial `0.1.0`. Package metadata, runtime, lock and changelog agree. This is pre-publication wire version 1 with no published consumer migration. M0, B1.1 and C1.1–C3.1 are verified. C3.2–C4.4 remain in the selected release. Acquisition, recording and replay, and projection with G1 are later bundles. Standards, FDM/FOQA, external adoption and T3.1 are outside this bundle. C4.4, supported Python 3.12 source and installed evidence, applicable STRICT acceptance and separate publication approval govern release.

## Review focus

1. Rehashing a sample around a corrupted inline raw observation must still fail. Task 3 pins both hash tiers, the nested path and the construction barrier.
2. A failed or unattempted normalization must resist fabricated `0`, `false`, empty arrays and payload claims. Tasks 1–3 test variant closure and record-local quality compatibility.
3. A known age of zero must survive interchange, and missing age must survive as omission. Tasks 2–3 pin both along with evaluation-clock and reading-domain rejection.
4. Inline and referenced observations can share an identity even when their hashes differ. Task 2 tests that this is a lineage duplicate and checks derivation input order and self-reference separately.
5. A superficially valid reusable schema must retain the embedded raw wire shape and its shared definitions. Tasks 1 and 4 pin installed-resource identity, exact subtree parity and rejection of extra fields.

## Task 1 — Mirror the normative version-1 schema

**Files:** Create `src/xplane_fdau/schemas/measurement-sample-v1.schema.json`, `docs/schemas/measurement-sample-v1.schema.json` and `tests/test_measurement_sample_schema.py`.

**Interfaces:** JSON Schema Draft 2020-12 with the eight allowed root keys. Required instance fields are `contract_family`, `schema_version`, `sample_id`, `producer`, `session_id`, `stream_id`, `epoch_id`, `sequence`, `measurement_ref`, `binding_ref`, `evaluation_clock`, `evaluation_reading`, `normalization`, `applied_transforms`, `validity`, `quality`, `observation_lineage`, `derivation` and `content_hash`. `freshness_age_ns` is the only optional root property.

- [ ] Write `test_sample_schema_identity_and_shared_defs` and `test_sample_schema_variant_closure`. Assert byte equality between the two resources, Draft 2020-12 validation, exact keys/fields, canonical serialization, local-only `$ref` and equality of overlapping `$defs` with the three shipped sibling schemas. Build a synthetic document from the property's literal wire shape. Accept inline and payload success, each absent reason, both observation-lineage variants and both derivation variants. Reject missing selected fields, mixed variant fields even when the value is `false`, missing unit, physical payload unit, empty lineage, empty algorithm inputs, 257 applied steps or derivation inputs, 65,536 lineage entries and wrong reference targets. Verify inline raw shape preserves its closed field set.
- [ ] Run `uv run --locked --all-groups python -m unittest tests.test_measurement_sample_schema -v`. Confirm the missing sample resource fails before implementation.
- [ ] Write the closed schema with literal tagged variants in `$defs`, copying shared definitions unchanged. Use dedicated sample roles around shared definitions to constrain the evaluation clock to `host_monotonic` and the raw/sample `RecordRef` targets to the correct family/version. Embed the C3.1 instance constraints as a local `$defs` entry with its existing shared dependencies and original root closure. Keep hash verification, lexical number spelling, ordered uniqueness by identity and cross-field evidence checks in runtime tests. Serialize the resource exactly once and copy its bytes to the documentation path.
- [ ] Rerun the sample schema suite together with `tests.test_raw_observation_schema tests.test_source_binding_catalog_schema tests.test_measurement_catalog_schema`. Run the static checks below for changed Python paths. Commit the three task files as `feat: define measurement sample v1 schema` with hooks enabled.

## Task 2 — Model the sample and its local invariants

**Files:** Edit `src/xplane_fdau/acquisition/models.py`, `src/xplane_fdau/acquisition/__init__.py` and `tests/test_public_api.py`. Create `src/xplane_fdau/acquisition/_sample_validation.py`, `src/xplane_fdau/acquisition/_sample_wire.py` and `tests/test_measurement_sample.py`.

**Interfaces:** Export `NormalizedAbsentReason`, `AppliedTransform`, `ObservationLineage`, `Normalization`, `DerivationInput`, `Derivation` and `MeasurementSample` through `acquisition.models` and `acquisition`, in the approved ownership order among the existing raw exports. Use frozen, slotted, keyword-only dataclasses with the required-then-optional constructor convention. `MeasurementSample` takes the Task 1 field inventory in semantic order with `freshness_age_ns: int | _Missing = _OMITTED` last and no hash argument. Use owned `ProducerIdentity`, `DefinitionRef`, `ClockDomain`, `ClockReading`, `Normalization` and `Derivation` values and ordered `Sequence` inputs for tuple fields. Keep `contract_family` and `schema_version` explicit constructor fields.

| Nested model | Required fields and variant-selected fields in semantic order |
| --- | --- |
| `AppliedTransform` | `step_id: str`, `algorithm: AlgorithmRef` |
| `ObservationLineage` | `kind` of `inline` or `reference`, then `observation: RawObservation` or `observation_ref: RecordRef` respectively |
| `Normalization` | `kind` of `succeeded` with exactly one of `value: InlineValue` or `payload: PayloadReference` and required `unit: UnitSpec`, or `absent` with `reason: NormalizedAbsentReason` and the reason-selected fields below |
| `DerivationInput` | `input_id: str`, `sample_ref: RecordRef` |
| `Derivation` | `kind` of `direct`, or `algorithm` with `algorithm: AlgorithmRef` and nonempty `inputs: Sequence[DerivationInput]` |

Use omission sentinels for variant-selected fields. `input_unusable` and `normalization_not_attempted` require `input_id` and a `FailureCondition`; `normalization_failed` requires `failed_step_id`; `not_applicable` carries only its reason. `NormalizedAbsentReason` is a `StrEnum` with exactly those four literals. Use the existing `ValidityState` and `QualityFlag` vocabulary.

- [ ] Write `test_sample_identity_and_immutable_fields`. Assert each UUID's path on a bad identity, sequence `0` and `2**63 - 1`, Boolean rejection, exact definition triples and rejection of a foreign reference type. Assert tuple storage, frozen slots, defensive copying of caller lists and no constructor `content_hash`. Mutating caller data after construction must preserve the model hash.
- [ ] Write `test_normalization_and_quality_matrix` and `test_failed_step_and_derived_value`. Exercise every row at design lines 1008–1022 with all four validity states where its normalization form permits. Reject `valid` with absence, any non-`not_applicable` absence with empty quality, mismatched not-applicable reason/state, conversion failure without the flag or failed step, the flag on success, and absent variants carrying a value or payload. A dropped sample needs absence, and an out-of-range or saturated assertion needs a preserved inline value. A failed normalization preserves an ordered completed-step list with no entry claiming the failed step completed. Other absent reasons require an empty list. Do not reject precision or rounding flags solely because a later step failed. Assert duplicate and unsorted flags at their array indices. Algorithm derivation requires success, and a direct derivation forbids algorithm and inputs.
- [ ] Write `test_evaluation_clock_and_optional_age` and `test_lineage_order_reference_kinds_and_identity`. Use a host monotonic clock and check wrong kind at `/evaluation_clock/kind` and mismatched reading at `/evaluation_reading/clock_domain_id`. Check omitted age, explicit `0`, maximum `UInt63`, negative age, Boolean and overflow. Preserve lineage and derivation inputs in deliberately nonlexical order. Reject an observation identity repeated across inline and reference entries at the later identity leaf, even when hashes differ. Reject duplicate derivation input IDs, duplicate exact parent references and a reference naming the current sample UUID, even if the claimed hash differs. Conflicting target hashes for two otherwise distinct parent references are adjudicated when C3.3 resolves them. Use the nested paths for wrong record families, extra/missing fields, empty lineage and list bounds. Update the exact `__all__` expectations for models and package.
- [ ] Run `uv run --locked --all-groups python -m unittest tests.test_measurement_sample tests.test_public_api -v`. Confirm missing exports first and assert the expected local validation failures as the new constructors are introduced.
- [ ] Implement explicit projections and staged plain-field validators shared by constructors and the wire loader. `_measurement_sample_wire(value: MeasurementSample, *, include_hash: bool = True) -> dict[str, object]` preserves ordered arrays and omissions and reuses C3.1 wire projection for inline observations. `_validate_sample_fields(fields: Mapping[str, object], phase: int, *, path: str = "", wire: bool = False) -> None` checks local fields in the approved order with the correct parent path. Reuse owned type projections and checks for definition/algorithm references, clock fields, values and quality. Compare references using their exact pinned fields, and compare observation identities using UUIDs. Enforce only record-local consequences of the approved validity/quality matrix. Calculate the cached read-only `content_hash` after validation with `_record_content_hash`.
- [ ] Rerun the Task 2 tests and `tests.test_raw_observation tests.test_contract_identity tests.test_contract_timing tests.test_contract_values`. Run the static checks below. Commit the exact task paths as `feat: model canonical measurement samples` with hooks enabled.

## Task 3 — Add staged sample interchange

**Files:** Create `src/xplane_fdau/acquisition/_sample_io.py` and `tests/test_measurement_sample_io.py`. Edit `src/xplane_fdau/acquisition/_raw_io.py`, `src/xplane_fdau/acquisition/_sample_validation.py`, `src/xplane_fdau/acquisition/io.py`, `src/xplane_fdau/acquisition/__init__.py`, `tests/test_public_api.py` and `tests/test_measurement_sample_schema.py`.

**Interfaces:** Export `load_measurement_sample_v1(binary_file: BinaryIO, *, source: str = "<memory>") -> MeasurementSample`, `loads_measurement_sample_v1(data: str | bytes, *, source: str = "<memory>") -> MeasurementSample`, `dump_measurement_sample_v1(value: MeasurementSample, binary_file: BinaryIO) -> None` and `dumps_measurement_sample_v1(value: MeasurementSample) -> bytes`. The four raw entry points retain their existing signatures and behavior.

- [ ] Write `test_round_trip_and_independent_preimage` and `test_rehashed_parent_cannot_hide_bad_inline_observation`. Round-trip each normalization variant and both derivation/lineage forms, including nested raw value, source metadata, reference pins, unit and unsorted semantic input order. Pin one literal canonical vector and its expected SHA-256 from an independent preimage with a nontrivial embedded `content_hash`, definition hash and real `1.0`. Check reordered/indented input, string and bytes, one final LF, preservation of zero versus omitted age, and re-dump equality. A stale raw hash with a recomputed sample hash must fail at `/observation_lineage/0/observation/content_hash`. A fresh raw hash with stale sample hash must fail at `/content_hash`. If both well-spelled hashes mismatch, expect the nested path first in semantic order. A reference or payload hash is a pin, so the loader does not attempt to verify its target bytes.
- [ ] Write `test_nested_phases_and_construction_barrier` and `test_binary_stream_ownership_and_progress`. Patch public model initializers to assert zero calls for rejected documents before construction. Pair a nested duplicate with earlier overflow, bad root envelope with invalid body, later parent shape with earlier nested domain or hash, earlier transform parameter depth overflow with a later non-NFC leaf, wrong hash with a locally invalid success, and valid hashes with a locally invalid embedded raw status. Assert error class, path, sample family and recoverable identity and retain parser line/column. Check the embedded raw family/version literals during shape, unlike the outer loader's version dispatch. Pin JSON null, integer versus real tokens and parameter depths 32/33. Exercise exact binary read, nonseekable streams, bounded short writes, zero/`None` progress, invalid write counts, wrong model/text/path inputs and propagated I/O errors. Neither load nor dump closes a caller-owned stream.
- [ ] Run `uv run --locked --all-groups python -m unittest tests.test_measurement_sample_io tests.test_measurement_sample_schema tests.test_public_api -v`. Confirm missing APIs and then assertion-level RED for nested precedence, stale inline hash and short writes.
- [ ] Implement `_read_measurement_sample(data: str | bytes, *, source: str) -> MeasurementSample` with the existing lexical parser. Run complete shape first, then domain materialization in semantic order with canonical lexical traversal of parameter-object keys. Preserve enclosing document depth and parameter-relative depth. Reuse C3.1 staged validation and construction through narrow private operations split from `_read_raw_observation`. Invoke the raw shape, domain, hash and semantic operations at their corresponding sample phases. Validate inline hashes and then the sample hash in semantic order, followed by local semantics and typed construction. Preserve raw standalone diagnostics. Share the existing stream progress rules with two private I/O helpers in `acquisition.io`, `_read_binary(binary_file: BinaryIO) -> bytes` and `_write_binary(data: bytes, binary_file: BinaryIO) -> None`. Keep stream validation, serialization and first-write ordering observable from the four existing raw functions.
- [ ] Assert schema/runtime agreement on rehashed positive and structural negative cases, and assert that valid schema shape can still fail a stale digest, semantic ordering or lexical token check. Rerun the RED modules plus `tests.test_measurement_sample tests.test_raw_observation tests.test_raw_observation_io tests.test_raw_observation_schema tests.test_contract_timing_io tests.test_source_binding_catalog_io`. Run the static checks below. Commit the exact task paths as `feat: load and dump measurement sample v1 records` with hooks enabled.

## Task 4 — Verify the installed public API and show a working example

**Files:** Create `docs/reference/measurement-samples.md`. Edit `mkdocs.yml`, `tools/installed_smoke.py`, `tests/test_installed_smoke.py` and `tests/test_documentation.py`.

**Interface:** `smoke_measurement_sample() -> None` runs through the existing installed smoke entry point. The guide uses synthetic evidence and the package's public imports.

- [ ] Write tests that execute the guide's example and assert exact re-dumping, age preservation and schema link. Add installed-flow tests that require the new smoke and prove it fails when serialization is corrupted, the schema is absent or wrong, or a rehashed invalid sample is accepted.
- [ ] Run `uv run --locked --all-groups python -m unittest tests.test_installed_smoke tests.test_documentation -v`. Confirm failures at the missing guide and smoke.
- [ ] Implement the guide and smoke with versioned public I/O, an exact definition and raw-record pin, a succeeded sample and an explicit absent normalization. Verify canonical bytes and digest, omitted and zero ages, load/dump from binary streams and one rehashed forbidden normalization shape. In the guide, show a synthetic 12 ms receipt-to-evaluation interval and explain how the declared clock's resolution governs the reading. Check the installed schema ID and its closed root. Explain that catalog and lineage resolution is C3.3 work and link the sample schema. Keep synthetic data outside shipped runtime resources.
- [ ] Rerun `tests.test_installed_smoke tests.test_documentation tests.test_public_api`. Run `uv run --locked --all-groups mkdocs build --strict`, `uv run --locked --all-groups python tools/quality.py docs` and the static checks below. Commit the five task paths as `docs: explain and verify measurement sample interchange` with hooks enabled.

## Execution and acceptance evidence

- [ ] After plan approval and execution-method selection, establish the isolated feature worktree per repository instructions. Register the approved plan and manage selection/lifecycle through the guarded backlog adapter. Preview each mutation, inspect the diff and audit, then apply with its exact target digest. Record evidence only after verification succeeds.
- [ ] During implementation run the named suites with `uv run --locked --all-groups python -m unittest <modules> -v`. Run `uv run --locked --all-groups ruff check <changed-python-paths>`, `uv run --locked --all-groups ruff format --check <changed-python-paths>` and `uv run --locked --all-groups ty check` on each task. Require the intended RED cause, then zero exits for GREEN and hooks.
- [ ] Complete independent whole-branch review against this plan, the specification and all four gates. Reproduce any accepted behavior finding test-first and verify its correction before closeout.
- [ ] Run one stable full offline hygiene pass using `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. The new packaged resource requires hygiene, which supplies the full routine gate and wheel/sdist validation. Use the validated artifact pair if retained. Otherwise run `uv build --offline --no-sources --out-dir <new-external-directory>`, then `uv run --locked --all-groups twine check --strict <wheel> <sdist>` and `uv run --locked --all-groups python tools/release.py check-dist <new-external-directory>`. Record the exact candidate and SHA-256 of both artifacts.
- [ ] From outside the checkout, create a fresh external uv-managed Python 3.12.16 environment with `uv venv --offline --python 3.12.16 <external-venv>`. Install the verified wheel with `uv pip install --offline --no-deps --python <external-python> <wheel>` and run `<external-python> <absolute-path-to-tools/installed_smoke.py> 0.1.0` from the external directory. Require installed import origins, the exact resource and dependency-free metadata, and both canonical and native FDR smoke. Retain evidence and record the four gate receipts, acceptance and release-bundle progress. Follow the project's integration choice workflow, including the exact fast-forward path if local integration is selected.

| C3.2 gate | Executable evidence |
| --- | --- |
| 1. Runtime identities, sequence and exact definition references | Task 2 model checks and Task 3 canonical identity round trip |
| 2. Local normalization, unit, transforms, validity, quality and freshness invariants | Tasks 2–3 matrix, preserved order, evaluation clock, omission and zero age |
| 3. Absent or failed normalization carries no fabricated value | Tasks 1–3 variant negatives and rehashed semantic checks, Task 4 installed rejection |
| 4. Schema agrees with runtime shape and canonical hash | Tasks 1 and 3 parity, independent preimage and nested hash vectors, Task 4 external wheel proof |

## Plan audit

| Intent to scope | Verdict | Evidence |
| --- | --- | --- |
| Capture normalized evidence with exact identities and preserve the producer's quality and timing claims | Aligned | Canonical design lines 927–1090 and BACKLOG lines 317–323 |
| Preserve the inline/reference and derivation wire declarations | Aligned | Canonical design lines 1092–1127 and 1462–1463, and the C3.2/C3.3 split in BACKLOG lines 317–333 |
| Deliver versioned interchange with a deterministic self-hash and a mirrored schema | Aligned | Canonical design lines 175–250, 401–420, 1289–1385 and 1475–1492 |

| Scope to plan | Verdict | Evidence |
| --- | --- | --- |
| Record-local validation for gates 1–3 | Aligned | Task 2 constructor tests and Task 3 rehashed document checks |
| Versioned, resource-backed canonical interchange for gate 4 | Aligned | Tasks 1, 3 and 4, including the parent and embedded hash checks |
| C3.1 compatibility and C3.3 catalog/closure ownership | Aligned | Global constraints, Task 3 raw regressions and acceptance table |

**Verdict:** PASS for planning alignment. The local validation boundary, nested wire error ordering and release evidence are review decisions in this draft. No delivery gate is claimed by the plan audit.
