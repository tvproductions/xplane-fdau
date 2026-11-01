# C2.2 Measurement Catalog Implementation Plan

- **Governance:** active
- **Status:** approved
- **Date:** 2026-11-01
- **Roadmap child:** `C2.2`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** 2026-11-01 — Jeff / tvproductions; corrected plan approved in chat; execution deferred until after handoff and method selection
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the immutable version-1 measurement catalog, exact catalog and definition identities, strict family I/O, and matching packaged/published schema, satisfying C2.2's four gates.

**Architecture:** Measurements owns the catalog model, private mapping validators, wire projection and four public I/O functions. Reuse C2.1's staged definition-entry helpers and contracts' lexical parser, canonical encoder and preimage primitives without reversing dependencies. A self-contained schema is a packaged resource and a byte-identical documentation artifact; runtime loading uses Python validation, never a schema library.

**Tech Stack:** Python 3.12 standard library at runtime; unittest, locked all-group uv, Ruff, ty, strict MkDocs, offline hygiene and external installed-wheel smoke. During execution declare a direct development-only `jsonschema==4.26.0` dependency, already present transitively at that exact version in `uv.lock`.

**Spec:** [Approved canonical design](../specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md), especially lines 174–247, 255–330, 397–420, 476–604, 1288–1497, 1657–1674 and 1862–1867; [scope amendment](../../architecture/xplane_fdau_core_scope_amendment.md). Repository-root `ROADMAP.md`, C2 epic, and `BACKLOG.md`, C2.2, own scope and mutable delivery state. C2.1 is verified, integrated and a prerequisite; its [completed plan](2026-11-01-c2-1-measurement-definition.md) records the C4.3 shared-API deferral.

## Global Constraints

- Implement only C2.2. Python support remains `>=3.12,<3.13`, selected patch `.python-version`; runtime dependencies remain `[]`. Use unittest only. No provider, simulator, network or executable-plugin dependency.
- “Every public structural model class above is a frozen, slotted, keyword-only dataclass.” “Sequence inputs are defensively copied to tuples before validation.” Accept supported ordered list/tuple inputs, reject sets and arbitrary iterables, and never silently sort or deduplicate.
- “JSON object property order is never semantic.” “Optional properties are omitted when absent.” “JSON `null` is prohibited throughout version 1.” Preserve integer-versus-real lexical domains; `bool` is not an integer. Constructor and loader paths must agree.
- “Definitions are unique by `(definition_id, definition_revision)` and appear in ascending ID then revision order.” Multiple revisions of one ID are permitted in ascending revision order. Catalog definitions and provenance are nonempty; provenance has at most 256 entries, definitions at most 65535; document nesting depth is at most 64 including the catalog root.
- “A top-level record's preimage is the canonical JSON encoding of that object with only its root `content_hash` property omitted, including the final LF.” “Nested objects keep their hashes when an enclosing hash is computed.” Entry hashes retain their C2.1 family/version-bound preimage.
- “No model can hold a caller-supplied stale self-hash.” `content_hash` is computed, read-only and never a constructor argument. Catalog metadata changes do not change an unchanged entry's hash.
- “There is no implicit latest-version loader.” Only the measurement-catalog family URI and integer schema version `1` are accepted by the public v1 loader. No aliases, coercion, migration, public resolver, generic registry or common serializer dispatch is added.
- “No generated timestamp, producer, provider, adapter, or resource property is permitted.” Tests/examples use synthetic `test.*` identities. No stock, aircraft, q4xpcc or provider catalog ships, including as a runtime example.
- Contracts remain inward dependencies: `contracts` must not import `measurements`, `bindings` or `acquisition`. Keep contracts' public surface, root version-only namespace and native FDR unchanged. Shared `definition_ref`, `record_ref`, `compute_content_hash` and model dispatch in public `canonical_bytes` remain C4.3 work.
- Schema resources use Draft 2020-12, local `$defs`/`$ref` only, no defaults, canonical UTF-8 without BOM and one final LF. Schema order does not determine validation precedence; Python remains authoritative for lexical numbers, NFC, ordering, hashes and semantic policies.
- Full offline hygiene once at stable source closeout supplies the complete gate because new package modules/resources and development metadata change. Do not repeat a separate aggregate on unchanged inputs. Mandatory commit hooks remain enabled. Tags, push, publication and release retain separate authority; STRICT/G1 gaps remain open.

## Review Focus

1. An earlier entry's semantic/hash failure must not hide a later entry's shape or canonical-domain failure: whole-document phases and a no-construction barrier are tested in Task 2.
2. Changing an entry, including its declared hash, must invalidate the enclosing hash; changing catalog metadata alone must preserve entry identity: independent preimage and competing-hash tests in Tasks 1–2.
3. Same ID with several revisions is valid; duplicate pairs, descending revisions and descending IDs fail without sorting: exact-path tests in Task 1 and loader parity in Task 2.
4. Integer-looking reals, booleans, null, Unicode and container limits must not acquire different meanings through schema validation: runtime/schema boundary cases in Tasks 2–3.
5. User-owned nonseekable streams and installed resource access outside the checkout must work without closing streams or consulting source files: Task 2 stream tests and Task 4 external wheel smoke.

## Planning decisions and boundaries

The approved canonical specification already supplies the reviewed design; this is its single-child implementation plan, not a new design approval. Jeff approved the following implementation choices with the corrected plan on November 1; execution-method selection remains pending:

- Extend existing measurement ownership rather than adding a catalog framework. New private catalog modules leave the C2.1 entry reader intact; they compose its stages, never call the complete per-entry reader inside an enclosing validation loop. That shortcut would construct early models and interleave error tiers.
- Required constructor fields precede optional title/scope, independently of semantic validation order. Include required literal `contract_family` and `schema_version` constructor parameters as the specification's exact constructor inventory requires; do not synthesize defaults or add hidden public fields.
- Cached hash slots follow C2.1; no `cached_property` or instance dictionaries. `DefinitionRef` can already hold an exact entry ID/revision/hash: tests prove those triples survive a catalog round trip. No undocumented catalog lookup method or reference factory is needed; binding reference resolution belongs to C2.4 and shared factory integration to C4.3.
- The root hash is checked after entry hashes, because `definitions` precedes root `content_hash` in semantic property order. All shape checks still precede all domains; all domains precede every hash; every hash precedes local semantics. Malformed hash spelling is semantic, while a well-formed incorrect hash is a hash-tier error, following C2.1. `_record_content_hash` validates a root hash if one is supplied, so the catalog hash stage must pass it a mapping with only the root `content_hash` omitted and compare only when the declared spelling matches `[0-9a-f]{64}`. Malformed spelling is reported later at the root hash's semantic position; nested entry hashes remain in the preimage.
- Declare `jsonschema==4.26.0` directly in the dev group instead of depending on its current incidental transitive installation. During approved execution, update only that declaration and the corresponding root group lock metadata using `uv lock --offline`; preserve all selected package versions and runtime requirements. This is not a dependency refresh. If the exact locked package cannot be retained, stop and resolve that scoped change before widening it.
- Test the schema with `Draft202012Validator.check_schema` and a table of accepted/rejected structural variants. JSON Schema treats mathematically integral reals as integers; it cannot enforce token distinctions, hashes or all semantic policies. Do not claim identical schema/runtime acceptance sets. Verify the representable shape rules and separately pin runtime-only rules. See [validator documentation](https://python-jsonschema.readthedocs.io/en/v4.26.0/validate/) and the [2020-12 validation vocabulary](https://json-schema.org/draft/2020-12/json-schema-validation).
- Retain Python 3.12 dataclasses, explicit named projections and standard binary streams. Use the positional anchor in `importlib.resources.files("xplane_fdau.schemas").joinpath(...)`; do not assume an installed resource is a filesystem path. This follows the [Python 3.12 resource API](https://docs.python.org/3.12/library/importlib.resources.html). No newer Python minor or broad modernization is proposed.

## File responsibilities

| Responsibility | Exact files |
| --- | --- |
| Catalog model and owned exports | Modify `src/xplane_fdau/measurements/models.py`, `src/xplane_fdau/measurements/__init__.py` |
| Catalog field phases and wire/hash composition | Create `src/xplane_fdau/measurements/_catalog_validation.py`, `src/xplane_fdau/measurements/_catalog_io.py`; reuse `_definition_validation.py` and `_definition_io.py` unchanged |
| Four public versioned functions | Create `src/xplane_fdau/measurements/io.py` |
| Catalog fixtures, model and adversarial I/O proof | Create `tests/measurement_catalog_support.py`, `tests/test_measurement_catalog.py`, `tests/test_measurement_catalog_io.py`; modify `tests/test_public_api.py` |
| Normative schema and published copy | Create `src/xplane_fdau/schemas/__init__.py`, `src/xplane_fdau/schemas/measurement-catalog-v1.schema.json`, `docs/schemas/measurement-catalog-v1.schema.json` |
| Schema, packaging and docs proof | Create `tests/test_measurement_catalog_schema.py`; modify `tests/test_release_tool.py`, `tests/test_documentation.py`, `pyproject.toml`, `uv.lock` |
| Installed surface and guidance | Modify `tools/installed_smoke.py`, `tests/test_installed_smoke.py`, `mkdocs.yml`; create `docs/reference/measurement-catalogs.md` |
| Lifecycle/evidence | This plan, guarded `BACKLOG.md`, `.superpowers/sdd/2026-11-01-c2-2-catalog/` during execution |

No new bindings/acquisition modules, other family schemas, conformance manifest/corpus mirrors, provider data, native-FDR changes or common API additions. The existing artifact validator discovers exact package `.py`/`.json` payloads; extend its adversarial tests for the new resource rather than creating a parallel artifact validator or widening source-inclusion rules.

## Approval checkpoint and execution entry

- [x] Obtain explicit plan approval. November 1 — Jeff / tvproductions approved the corrected plan and requested a fresh handoff and ordinary Git sync, with execution deferred until afterward. Approval metadata is recorded; the guarded specified → planned transition and approved plan registration passed dry-run/digest/apply and the post-change audit. No child was selected or gate closed.
- [ ] Obtain native or subagent-driven execution choice for C2.2. C2.1's execution choice does not select a method for this child. Recheck authorities, native plugin identities/source revisions, HEAD, worktrees and audit/next; stop on findings or authority drift.
- [ ] Use `superpowers:using-git-worktrees` to create the temporary C2.2 implementation worktree, then select only C2.2 and transition planned → in_progress through guarded operations. Preserve unrelated worktrees and changes.
- [ ] Check canonical raw input bytes against the indexed baseline before final evidence/artifacts. The C2.1 native checkout exposed CRLF materialization despite clean Git status; use operation-local LF checkout handling or guarded newline-only restoration, not global Git-setting changes. Record tree and raw input identities.

## Task 1: Immutable catalog meaning, ordering and identity

**Files:** Modify `measurements/models.py`, `measurements/__init__.py`, `tests/test_public_api.py`, `tests/test_installed_smoke.py`; create both private catalog modules and `tests/measurement_catalog_support.py`, `tests/test_measurement_catalog.py` at the exact paths above.

**Interfaces:**

- Produce `MeasurementCatalog(*, contract_family: str, schema_version: int, catalog_id: str, catalog_revision: int, authority: Authority, provenance: Sequence[ProvenanceSource], definitions: Sequence[MeasurementDefinition], title: object = _OMITTED, scope: object = _OMITTED)` in models; `content_hash: str` is a computed read-only property with private non-init/non-compare cached slot. Required parameters and optional parameters each retain their semantic relative order.
- Produce `_catalog_fields(value: MeasurementCatalog) -> dict[str, object]` in models: explicit owned-model projection, no root hash, including complete hashed entry projections. Reject raw mappings substituted for owned child models at their exact paths; preserve null until its domain phase.
- Produce `_validate_catalog_fields(fields: Mapping[str, object], phase: int, *, path: str = "", wire: bool = False) -> None` in `_catalog_validation.py`. Phases 0/1/2 mean shape/domain/semantics. `wire=True` additionally requires/checks the declared root hash field. It validates plain fields; no model construction. Constructor constant mismatches are semantic errors; loader envelope dispatch is separate.
- Produce `_measurement_catalog_wire(value: MeasurementCatalog, *, include_hash: bool = True) -> dict[str, object]` and `_measurement_catalog_bytes(value: MeasurementCatalog) -> bytes` in `_catalog_io.py`. Reuse `_measurement_definition_wire`, contracts' `_encode_document` and `_record_content_hash` unchanged. Add no common dispatch or public convenience API.
- Test support provides `definition(**changes: Any) -> MeasurementDefinition`, `catalog(**changes: Any) -> MeasurementCatalog`, independent literal `ENTRY_PREIMAGE: bytes`, `CATALOG_PREIMAGE: bytes`, `GOLDEN_CATALOG: bytes` and their `DEFINITION_HASH: str`, `CATALOG_HASH: str`. Expected hashes use `hashlib.sha256` over those literals, never production projection/serialization to generate the expected result.

- [ ] **Step 1 — Write failing model tests.** `test_catalog_signature_and_immutability` inspects the exact signature above, rejects supplied `content_hash`, checks frozen slots/no `__dict__`, tuple freezing and isolation after mutating caller lists. `test_catalog_metadata_and_omission` checks required literals, ID, revision `1..9223372036854775807`, exact authority, nonempty unique ordered provenance (maximum 256), omitted title/scope versus explicit null, NFC text lengths 256/2048 and empty-string rejection. Reject wrong owned model types without evaluating arbitrary iterables.
- [ ] **Step 2 — Write failing ordering/identity/hash tests.** `test_definition_pair_order` accepts `(test.a,1),(test.a,2),(test.b,1)`; rejects duplicates/descending revision at `/definitions/1/definition_revision` and descending ID at `/definitions/1/definition_id`, without modifying inputs. Check nonempty definitions and the 65535 bound. `test_catalog_hash_preimage` compares literal canonical bytes/final LF and independently computed root/entry hashes. `test_catalog_metadata_does_not_change_definition_identity` changes catalog ID/revision/authority/scope and verifies the unchanged entry hash; changing an entry changes both hashes. All Task 1 tests must pass using the model and private wire/hash interfaces delivered by this task; create no test, skipped test or placeholder that requires Task 2's public I/O.
- [ ] **Step 3 — Run RED.** `uv run --locked --all-groups python -m unittest tests.test_measurement_catalog -v` must fail on the missing catalog behavior, not an unrelated tool/setup error.

Representative Step 2 assertion (in a `unittest.TestCase`, with the planned support helper and contract error imports):

```python
def test_definition_pair_order(self) -> None:
    first = definition(definition_id="test.a", definition_revision=1)
    second = definition(definition_id="test.a", definition_revision=2)
    self.assertEqual((first, second), catalog(definitions=[first, second]).definitions)
    with self.assertRaises(ContractValidationError) as caught:
        catalog(definitions=[second, first])
    self.assertEqual("/definitions/1/definition_revision", caught.exception.path)
```
- [ ] **Step 4 — Implement the model, field phases and private wire/hash projection.** Semantic root order is `contract_family`, `schema_version`, `catalog_id`, `catalog_revision`, `authority`, `provenance`, optional `title`, optional `scope`, `definitions`, `content_hash`. Definitions are validated in increasing array index; validate each key before pair-order comparison and before its later semantic fields. Programmatic validation completes shape/domain phases before semantics, then caches the computed root hash. Keep optional omission distinct from null. Use local imports only where needed for the existing model/IO ownership cycle.
- [ ] **Step 5 — Verify GREEN and static checks.** Run the model tests plus `tests.test_measurement_definition`, `tests.test_public_api`, `tests.test_installed_smoke`. Add only the two new private modules to the installed-module expected set with this task, so mandatory commit hooks remain meaningful. Run Ruff check/format --check on affected Python files and `uv run --locked --all-groups ty check`.
- [ ] **Step 6 — Commit** the listed Task 1 files with `feat: add immutable measurement catalogs`. Keep hooks enabled; independent task review is required when using subagent-driven execution.

Task 1 GREEN/static commands (all must exit 0):

```powershell
uv run --locked --all-groups python -m unittest tests.test_measurement_catalog tests.test_measurement_definition tests.test_public_api tests.test_installed_smoke -v
uv run --locked --all-groups ruff check src/xplane_fdau/measurements tests/measurement_catalog_support.py tests/test_measurement_catalog.py tests/test_public_api.py tests/test_installed_smoke.py
uv run --locked --all-groups ruff format --check src/xplane_fdau/measurements tests/measurement_catalog_support.py tests/test_measurement_catalog.py tests/test_public_api.py tests/test_installed_smoke.py
uv run --locked --all-groups ty check
```

## Task 2: Whole-catalog staged validation and public binary I/O

**Files:** Extend `_catalog_io.py`, `_catalog_validation.py`, `tests/measurement_catalog_support.py`, `tests/test_measurement_catalog.py`; create `measurements/io.py`, `tests/test_measurement_catalog_io.py`; modify `measurements/__init__.py`, `tests/test_public_api.py`, `tests/test_installed_smoke.py` at the exact source/test roots above.

**Interfaces:**

- Public `load_measurement_catalog_v1(binary_file: BinaryIO, *, source: str = "<memory>") -> MeasurementCatalog`; `loads_measurement_catalog_v1(data: str | bytes, *, source: str = "<memory>") -> MeasurementCatalog`; `dump_measurement_catalog_v1(value: MeasurementCatalog, binary_file: BinaryIO) -> None`; `dumps_measurement_catalog_v1(value: MeasurementCatalog) -> bytes`. These four names, in this order, are `io.__all__`; the measurements package appends them after its model exports. No path/text-stream overload, unversioned alias, stream close or implicit source-name inference.
- Private stages in `_catalog_io.py`: `_catalog_envelope(raw: object) -> None`, `_catalog_shape(raw: object) -> dict[str, object]`, `_catalog_domains(fields: Mapping[str, object]) -> dict[str, object]`, `_catalog_hashes(fields: Mapping[str, object]) -> None`, `_catalog_semantics(fields: Mapping[str, object]) -> None`, `_catalog_build(fields: Mapping[str, object]) -> MeasurementCatalog`.
- `loads` uses the existing lexical `_parse_json_document` for complete syntax/duplicate checking, then calls those stages in order. Shape projection preserves `_NumberToken`s and arranges known fields in semantic order; shape checks use type-only shadows as C2.1 does. Domains materialize tokens only after all root/nested shapes pass and count depth from the catalog root. Hashes check entries by index, then the root. Semantics validate root fields and entry invariants in the specified order. Build constructs every owned nested value only after the entire catalog passed all earlier stages.
- `_catalog_hashes` first invokes the entry hash checks in array order. For the root, compare only if the declared value is a string matching the full `[0-9a-f]{64}` pattern; otherwise defer its spelling error without raising or coercing it. Compute the comparison value with `_record_content_hash({name: value for name, value in fields.items() if name != "content_hash"})`: remove exactly the root field, retaining all nested entry hashes. Never pass the raw catalog with its declared root hash to that helper. `_catalog_semantics` validates root hash spelling only after every preceding root property and definition semantic check, at `/content_hash`. Constructors likewise compute from a root-hash-free projection. Contracts helpers remain unchanged.
- Reuse `_definition_entry_shape`, `_definition_entry_hash`, `_definition_entry_semantics`, `_definition_entry_build` and `_validate_definition_fields` where their phase contracts fit. Whole-document domain traversal must use catalog-relative paths/depth; do not invoke `_measurement_definition_from_wire` or restart depth at each entry. Catalog-level collection bounds are shape checks. Keep C2.1 helpers unchanged unless a concrete compatibility defect requires a separately reviewed correction.

- [ ] **Step 1 — Write failing round-trip/envelope/stream tests.** Create `test_exact_reference_triples_survive_round_trip` entirely in `tests/test_measurement_catalog_io.py` now: construct exact `DefinitionRef` ID/revision/hash triples from entries before and after public dump/load and assert equality, including several revisions of one ID; add no factory. Task 1 neither creates nor runs this test. Cover bytes and Unicode JSON, binary load/dump, arbitrary object-member order/whitespace, canonical UTF-8/final LF, omitted optional fields, same-ID revisions and preserved provenance/definitions order. Test wrong family, integer version `2`, bool and real versions, missing envelope properties, root array/scalar, BOM, malformed UTF-8, syntax, duplicates anywhere and unknown properties including `$schema`, producer/provider/adapter/resource/generated timestamps. A recognized wrong family/version beats malformed body shape; missing/wrong envelope types are shape errors, while null retains its canonical-domain tier. Assert source, family, root catalog or nested definition identity, exact escaped JSON Pointer, and available syntax line/column without inventing duplicate locations.
- [ ] **Step 2 — Write failing precedence tests.** `test_global_shape_before_earlier_entry_hash` corrupts entry 0 hash and entry 1 shape; expect the entry 1 ShapeError. `test_global_domains_before_any_hash` uses an early semantic violation and a later integer overflow/non-NFC/null; expect the later CanonicalJSONError. `test_hashes_before_semantics` combines correctly shaped but stale entry/root hashes with invalid ordering or range; expect the first well-formed hash mismatch. When both entry/root hashes are stale, entry hash wins at `/definitions/0/content_hash`; when only root is stale, `/content_hash`. With fresh hashes, duplicate/order semantic paths match Task 1. Wrong hash syntax is semantic, not a manufactured hash mismatch.

`test_malformed_root_hash_preserves_semantic_order` starts from `GOLDEN_CATALOG`, sets `catalog_id="not-an-identifier"` and `content_hash="BAD"`, and expects `ContractValidationError` at `/catalog_id`, not `/content_hash`. Its companion with a valid catalog ID and only `content_hash="BAD"` expects `ContractValidationError` at `/content_hash`. `test_well_formed_root_hash_mismatch_precedes_semantic_error` uses the same invalid catalog ID but sets the declared root hash to `"0" * 64`; expect `ContractHashError` at `/content_hash`. Keep all entry hashes valid in these fixtures so only the intended root/semantic competition is exercised. Task 1's independent root-preimage assertion continues to pin inclusion of nested entry hashes.
- [ ] **Step 3 — Write failing robustness/build-barrier tests.** `test_invalid_catalog_constructs_no_models` must instrument actual structural dataclass construction, not just builder helpers. Prepare fixture bytes before instrumentation; use `contextlib.ExitStack` with `mock.patch.object(cls, "__init__", autospec=True, side_effect=AssertionError("premature model construction"))` for every class listed below. Patching methods on the original classes preserves class identity and intercepts calls through imported aliases. Also guard `_catalog_build` and `_definition_entry_build` at their actual lookup sites. For invalid documents at each validation tier, including a final-entry semantic failure with fresh hashes, assert the exact expected contract error/path and zero calls to every constructor and builder guard. `test_build_barrier_detects_direct_constructor_bypass` deliberately injects an early `Authority(...)` call into a validation stage while the builder guards are active; assert the constructor guard raises, proving that bypassing both helpers is detected. `test_valid_catalog_reaches_model_construction` is the positive control: forward constructor spies to their original initializers, load a valid fixture and assert catalog/definition construction occurs and the result round-trips. Cover supported representation branches, lexical integer versus real tokens (`1`, `1.0`, overflow/underflow), negative zero, surrogate text, null optionals, 256/257 provenance entries, 65535/65536 definitions and depth accounting. A later duplicate must still beat an earlier overflow; deeply nested rejected input must raise a contract error rather than leak `RecursionError`. Test nonseekable binary streams, caller-owned streams remaining open on success/failure, wrong text streams/paths rejected without coercion, and propagation of ordinary underlying stream I/O failures. Use bounded subprocess regression helpers if a hang risk warrants isolation; kill/reap children, use `sys.executable`, byte pipes and no shell.

The constructor-guard tuple in `tests/test_measurement_catalog_io.py` contains `MeasurementCatalog`, `MeasurementDefinition`, `Authority`, `ProvenanceSource`, `RepresentationSpec`, `PayloadSpec`, `UnitSpec`, `CoordinateSpec`, `AxisSpec`, `NumericSpec`, `EnumerationSpec`, `EnumerationMember`, `FreshnessSpec` and `ApplicabilitySelector`. Closed vocabulary enums are not structural models and remain usable during validation. For the positive control, save each original initializer before patching and use it as the spy's forwarding side effect; do not replace model classes or bypass their validation.
- [ ] **Step 4 — Run RED.** `uv run --locked --all-groups python -m unittest tests.test_measurement_catalog_io -v`; confirm assertion-level failures for missing I/O/staging behavior.

Representative Step 2 precedence assertion (`json`, `copy.deepcopy`, planned fixture and public API imports):

```python
def test_global_shape_before_earlier_entry_hash(self) -> None:
    raw = json.loads(GOLDEN_CATALOG)
    raw["definitions"] = [deepcopy(raw["definitions"][0]), deepcopy(raw["definitions"][0])]
    raw["definitions"][0]["content_hash"] = "0" * 64
    del raw["definitions"][1]["title"]
    with self.assertRaises(ContractShapeError) as caught:
        loads_measurement_catalog_v1(json.dumps(raw), source="late-shape.json")
    self.assertEqual("/definitions/1/title", caught.exception.path)
    self.assertEqual("late-shape.json", caught.exception.source)
```

Use phase-level size-bound tests with repeated lightweight entry mappings for the 65535/65536 structural boundary; test uniqueness with the small explicit pair matrix. Do not build tens of thousands of distinct model/hash fixtures merely to exercise a length check.
- [ ] **Step 5 — Implement the exact public functions and private stages.** Preserve the six error tiers: parse → recognized unsupported envelope → all shapes → all canonical domains → all self-hashes → all semantics. Extract only bounded scalar identity context and rethrow the same error type with the full path/source/family. Never echo document/payload bodies. Dump only owned catalogs through explicit projections; write canonical bytes and retain caller stream ownership.
- [ ] **Step 6 — Verify and commit.** Run both catalog test modules, C2.1 entry-I/O regressions, public API and installed-module tests; Ruff/format/ty. Add the public `measurements.io` module inventory entry now, retain the contracts-to-measurements AST prohibition and root namespace checks. Commit listed Task 2 files with `feat: add strict versioned measurement catalog io` and mandatory hooks.

Task 2 GREEN/static commands (all must exit 0):

```powershell
uv run --locked --all-groups python -m unittest tests.test_measurement_catalog tests.test_measurement_catalog_io tests.test_measurement_definition_io tests.test_public_api tests.test_installed_smoke -v
uv run --locked --all-groups ruff check src/xplane_fdau/measurements tests/measurement_catalog_support.py tests/test_measurement_catalog.py tests/test_measurement_catalog_io.py tests/test_public_api.py tests/test_installed_smoke.py
uv run --locked --all-groups ruff format --check src/xplane_fdau/measurements tests/measurement_catalog_support.py tests/test_measurement_catalog.py tests/test_measurement_catalog_io.py tests/test_public_api.py tests/test_installed_smoke.py
uv run --locked --all-groups ty check
```

## Task 3: Normative schema, parity boundary and artifact resource proof

**Files:** Create `src/xplane_fdau/schemas/__init__.py`, both measurement schema copies and `tests/test_measurement_catalog_schema.py`; modify `pyproject.toml`, `uv.lock`, `tests/test_release_tool.py`, `tests/test_documentation.py`, `tests/test_installed_smoke.py`.

**Interfaces:** `xplane_fdau.schemas` is a resource package with `__all__ = []`, no loader/registry. Resource name is `measurement-catalog-v1.schema.json`. `$id` is exactly `https://tvproductions.github.io/xplane-fdau/schemas/measurement-catalog-v1.schema.json`; `$schema` is exactly `https://json-schema.org/draft/2020-12/schema`. Only root keys `$schema`, `$id`, `title`, `type`, `$defs`, `properties`, `required`, `unevaluatedProperties` are permitted. Root type is `object`; `unevaluatedProperties` is `false`; root properties exactly match the catalog inventory. The root required list contains every nonoptional property, including both envelope fields and the self-hash.

- [ ] **Step 1 — Add the reviewed dev declaration.** Add `jsonschema==4.26.0` to `dependency-groups.dev`; run `uv lock --offline` and inspect the diff: only the direct group/root dependency metadata may change, not resolved versions, runtime requirements, other groups or tool pins. Frozen all-group sync then makes test tooling available. This is scaffolding for this task, not an independent deliverable.
- [ ] **Step 2 — Write failing schema/resource tests.** `test_schema_envelope_and_mirror` asserts exact root keywords/URIs, no defaults or cross-resource refs anywhere, lexical object-key order, no BOM and exactly one final LF, and equality with `_encode_document(json.loads(resource_bytes))`. Require byte-identical package/docs copies and `Draft202012Validator.check_schema` success. Traverse all object variants to check closed properties and required/optional inventories against the specification, independently of production validator constants. Add the resource-package module inventory entry alongside its creation.
- [ ] **Step 3 — Write failing shape matrix and boundary tests.** Test every representation (boolean/integer/real/string/enumeration/vector/fixed_array/variable_array/referenced_bytes), each array element type, unit/coordinate variants, optional numeric bounds, enumeration/freshness branches, applicability and provenance variants. Both schema and runtime reject missing/extra/irrelevant variant fields, invalid tags, primitive type mismatches and null. Both accept the synthetic valid matrix. Explicitly demonstrate schema-accepted but runtime-rejected cases for definition order/duplicate keys, stale hashes, non-NFC, and integer-looking real tokens; schema validation starts from parsed JSON so cannot detect duplicate JSON properties. No equality-of-acceptance-set claim.
- [ ] **Step 4 — Run RED.** `uv run --locked --all-groups python -m unittest tests.test_measurement_catalog_schema -v` must fail on absent schema/rules rather than a missing undeclared test dependency.

Representative structural negative control (`schema` is parsed from the resource):

```python
def test_schema_rejects_provider_properties(self) -> None:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    raw = json.loads(GOLDEN_CATALOG)
    self.assertTrue(validator.is_valid(raw))
    raw["provider"] = {"provider_family_id": "test.provider"}
    self.assertFalse(validator.is_valid(raw))
```
- [ ] **Step 5 — Author the self-contained schema and exact mirror.** Use local `$defs` for identifier, revision, sha256, authority, provenance_source, measurement_definition and all its nested representation/unit/coordinate/numeric/enumeration/freshness/applicability shapes. Reference existing shared shapes consistently; later family schemas must preserve equal-named shared subtree bytes. Encode shape constraints and declarative numeric/text/collection bounds where representable; do not imply enforcement of hashing, ordering, reference closure, NFC or cross-field policies. Close each object/union branch and avoid weakening constraints through union evaluation. Serialize using the project private plain-data encoder, not public parameter-object dispatch or a second JSON number serializer.
- [ ] **Step 6 — Prove packaging and publication shape.** Extend `tests.test_release_tool`'s existing wheel/sdist mutation fixtures: missing or altered measurement schema fails exact artifact checking, runtime requirements remain empty, and provider/catalog content added to an artifact is rejected. Extend documentation tests for package/docs byte equality and link target existence. Normal builds must include the resource through existing package discovery; do not widen sdist source includes to ship governance material. Conformance corpus packaging remains C4.2.
- [ ] **Step 7 — Verify and commit.** Run schema, release-tool, documentation and installed-module tests; Ruff/format/ty; `uv lock --check --offline`; strict MkDocs. Commit listed Task 3 files with `feat: package the measurement catalog v1 schema` with mandatory hooks enabled.

Task 3 GREEN/static commands (all must exit 0):

```powershell
uv run --locked --all-groups python -m unittest tests.test_measurement_catalog_schema tests.test_release_tool tests.test_documentation tests.test_installed_smoke -v
uv run --locked --all-groups ruff check src/xplane_fdau/schemas tests/test_measurement_catalog_schema.py tests/test_release_tool.py tests/test_documentation.py tests/test_installed_smoke.py
uv run --locked --all-groups ruff format --check src/xplane_fdau/schemas tests/test_measurement_catalog_schema.py tests/test_release_tool.py tests/test_documentation.py tests/test_installed_smoke.py
uv run --locked --all-groups ty check
uv lock --check --offline
uv run --locked --all-groups mkdocs build --strict
```

## Task 4: Installed catalog behavior and precise guidance

**Files:** Modify `tools/installed_smoke.py`, `tests/test_installed_smoke.py`, `tests/test_documentation.py`, `mkdocs.yml`; create `docs/reference/measurement-catalogs.md`.

**Interfaces:** Add `smoke_measurement_catalog() -> None` to the existing standalone smoke tool and call it from its existing entry point. Consume only Task 1–2 public measurement APIs for catalog behavior and `importlib.resources` for the schema. No new runtime API.

- [ ] **Step 1 — Write failing installed smoke tests.** Prove the helper constructs a synthetic catalog, dumps/loads via public APIs, checks cached root/entry identities and exact references, rejects reordered definitions/stale root hash/unsupported version, and reads the normative schema from the installed package without a source-tree path or dev-only schema validator. Tests must fail if the helper skips a required check; include a meaningful corrupted result/resource negative control. The installed module set already gained each module with its owning task; do not defer those expectations here.
- [ ] **Step 2 — Run RED.** `uv run --locked --all-groups python -m unittest tests.test_installed_smoke -v` must expose the missing helper behavior.

Representative behavior negative control, with public imports resolved inside the smoke helper as in its existing siblings:

```python
def test_catalog_smoke_detects_broken_serialization(self) -> None:
    with mock.patch("xplane_fdau.measurements.dumps_measurement_catalog_v1", return_value=b"{}\n"):
        with self.assertRaises((FDAUContractError, installed_smoke.SmokeError)):
            installed_smoke.smoke_measurement_catalog()
```
- [ ] **Step 3 — Implement the smoke helper and guide.** Document explicit envelope/constructor fields, ordering including several revisions per ID, exact three-part definition references, root-versus-entry hash scope, four versioned APIs using `io.BytesIO`, caller-owned binary streams, schema resource and published relative link `../schemas/measurement-catalog-v1.schema.json`. Include an executable synthetic round-trip example. Explain that the schema proves representable wire shape; Python enforces lexical/semantic rules. Catalogs describe meaning and do not authorize acquisition, execute conversions, police historical revisions globally or resolve binding/sample closure. Keep C4.3 shared convenience APIs explicitly pending.
- [ ] **Step 4 — Verify GREEN and documentation.** Run `tests.test_installed_smoke`, `tests.test_public_api`, `tests.test_documentation`, both catalog modules and schema tests; run `tests.test_runtime_import_boundary`. Ruff/format/ty, `uv run --locked --all-groups python tools/quality.py docs` and `uv run --locked --all-groups mkdocs build --strict` must pass. The guide example must execute and its schema link must resolve; no new schema-loading runtime dependency is permitted.
- [ ] **Step 5 — Commit** listed Task 4 files with `docs: demonstrate installed measurement catalog contracts`. Keep hooks enabled and require the selected review workflow.

Task 4 GREEN/static commands (all must exit 0):

```powershell
uv run --locked --all-groups python -m unittest tests.test_installed_smoke tests.test_public_api tests.test_documentation tests.test_measurement_catalog tests.test_measurement_catalog_io tests.test_measurement_catalog_schema tests.test_runtime_import_boundary -v
uv run --locked --all-groups ruff check tools/installed_smoke.py tests/test_installed_smoke.py tests/test_documentation.py
uv run --locked --all-groups ruff format --check tools/installed_smoke.py tests/test_installed_smoke.py tests/test_documentation.py
uv run --locked --all-groups ty check
uv run --locked --all-groups python tools/quality.py docs
uv run --locked --all-groups mkdocs build --strict
```

## Stable closeout and four-gate evidence

- [ ] Perform the selected task/whole-branch independent review workflow; close load-bearing findings before acceptance. Preserve negative controls, fixes and scoped re-review evidence. Bind the accepted source commit and raw input hashes to the observed verification result.
- [ ] Run the complete offline project hygiene gate once on the stable reviewed source:

```powershell
uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py
```

This supplies strict backlog/docs, all-files Ruff/format/ty/unittest and fresh strict wheel/sdist checks. Do not separately run the standalone full aggregate on unchanged inputs. Record any existing tooling/portability/STRICT limitations honestly, without treating a feature pass as whole-stack acceptance.

- [ ] From a fresh external Python 3.12 environment, install the exact validated wheel alone with no runtime dependencies and run the existing `tools/installed_smoke.py 0.1.0` outside the checkout. Record artifact SHA-256, selected interpreter patch, installed origins, schema bytes/identity and empty requirements. Preserve failed artifacts; clean successful external environments only after recording proof. No broader minor/platform or release-readiness claim.
- [ ] Write real receipts under `.superpowers/sdd/2026-11-01-c2-2-catalog/`: gate 1 catalog metadata/hash/ordered entries/exact references (Tasks 1–2), gate 2 duplicate/noncanonical order rejection (Tasks 1–2), gate 3 normative schema/runtime shape and mirrored installed resource (Tasks 3–4), gate 4 provider/resource-field rejection and no stock catalog content in source/artifacts (Tasks 2–4). Never close gates merely because this plan describes them.
- [ ] Complete plan tracking and accepted review/completion receipts. Advance only C2.2 implemented/reviewed, record gates through dry-run/digest/apply, commit evidence, then transition verified only when HEAD-backed review/gates justify it. Do not select or implement C2.3 automatically.
- [ ] Use `superpowers:finishing-a-development-branch` and obtain the user's integration choice. If local integration is selected, use AGENTS.md's exact fast-forward main procedure, including required main checks, fresh strict artifacts and external wheel smoke; preserve raw evidence on main before worktree/branch cleanup. Git sync, tag and publication remain separate.

## Planning audit and self-review

This is a direct comparison under `gzs-plan-audit`, not delivery evidence. The canonical design and corrected C2.2 plan are approved. The approval checkpoint advances C2.2 to planned with 0/4 gates, no selected child and no selected execution method.

| Intent → scoped requirement | Result | Evidence |
| --- | --- | --- |
| Provider-neutral measurement meaning within the X-Plane FDAU boundary | Aligned | Canonical design lines 27–52, 476–504, 603–604; amendment; BACKLOG C2.2 gates 1/4 |
| Immutable authority/provenance/semantic identity and strict deterministic bytes | Aligned | Design lines 397–420, 478–500, 1297–1437; C2.2 gates 1/2 |
| Schema-first, independently versioned structural contract without runtime library dependency | Aligned | Design lines 174–247, 1475–1497; C2.2 gate 3 |
| No simulator resources, provider content or downstream execution | Aligned | Design lines 82–97, 491–504, 603–604; C2.2 gate 4 |

| Scoped requirement → executable plan | Result | Evidence |
| --- | --- | --- |
| Catalog ID/revision/hash, authority/provenance, optional title/scope | Aligned | Task 1 exact model/phase/projection signatures, constructor/metadata/preimage tests |
| Sorted unique definition ID/revision pairs and exact references | Aligned | Task 1 ordered-pair matrix; Task 2 round-trip/reference/hash tests; no invented resolver |
| Whole-document error precedence and versioned binary I/O | Aligned | Task 2 exact interfaces, constructor/builder guards with direct-bypass negative control and valid-load positive control, global-phase and stream/context cases |
| Normative Draft 2020-12 resource matching runtime shape | Aligned | Task 3 exact root inventory, structural matrix, representability limits and mirrored byte proof |
| No provider identities or stock catalogs | Aligned | Task 2 forbidden-field tests, synthetic fixtures, Task 3 adversarial package inventories, Task 4 guidance |
| Inward dependency direction, deferred shared APIs and supported runtime | Aligned | Global constraints; Tasks 1–2 public API/AST assertions; unchanged contracts/native FDR; dev-only validator |
| Verified installed imports/resources and reviewable completion | Aligned | Task 4 external-capable smoke; hygiene/external wheel/four receipts/guarded closeout |

Self-review checked required-before-optional constructor order separately from semantic order; entry-before-root hash order separately from global phase order; every cross-task signature and created module's immediate inventory expectation; all five Review Focus tests; schema expressibility limits; independent golden preimages; and staged versus committed evidence requirements. The initial PASS was withdrawn after the first in-chat review found two gaps; the second review identified the root-hash helper's eager spelling check as a further precedence gap. This corrected revision assigns the full round-trip test to Task 2, checks actual constructor calls as well as builders, and specifies root-hash-free helper input with deferred spelling validation and competing-error regressions. Gap list: none of the three reviewed issues remains open in the plan. Updated planning verdict: **PASS for corrected scoped coverage**; Jeff approved the corrected plan on November 1 and deferred execution until after handoff. This is a document-level assessment, not execution of the planned tests, and does not resolve C4.3's shared-API design obligation, C4.2 corpus delivery or STRICT/G1 acceptance.

### Review corrections — November 1

| Finding | Resolution | Verification specified |
| --- | --- | --- |
| Task 1 assigns a round-trip test requiring Task 2's public I/O, blocking its independent GREEN/commit checkpoint | Move creation and all assertions of `test_exact_reference_triples_survive_round_trip` entirely to Task 2's I/O test module; Task 1 has no deferred, skipped or placeholder I/O test | Task 1's focused suite and mandatory hooks pass before public I/O exists; Task 2 owns the complete reference round-trip RED/GREEN cycle |
| Guarding builder helpers cannot prove validators made no direct model constructor calls | Instrument original structural classes' initializers as well as both builders at their lookup sites; retain class identity and validate complete-document rejection before any construction | Invalid late-entry cases assert exact errors and zero constructor/builder calls; injected early `Authority` construction trips the guard despite bypassing builders; a valid-load control forwards to original constructors and proves construction occurs |
| Passing the declared root hash to `_record_content_hash` could validate malformed spelling before earlier semantic fields | Compare only well-formed declared hashes; pass a mapping omitting only root `content_hash`, retain nested hashes, and defer spelling validation to the root hash's semantic position | Malformed root hash plus invalid catalog ID reports `/catalog_id`; malformed root hash alone reports semantic `/content_hash`; well-formed stale root hash beats the invalid catalog ID with `ContractHashError`; independent preimage proof retains entry hashes |

Pre-approval draft verification on November 1: 51 focused governance/adherence/documentation unittest checks, strict MkDocs, whitespace checks, strict backlog audit and next-action reporting passed. The first live audit caught a missing required `Completion evidence` metadata field; the header was corrected to the empty draft value and the audit passed. At that observation C2.2 was specified, 0/4 gates, with no selected child. These are planning checks, not runtime delivery evidence; no product, dependency or tool configuration changed.

Approval checkpoint on November 1: Jeff approved the corrected plan, requested a fresh handoff and ordinary Git sync, and deferred implementation until after handoff. C2.2 is now planned with 0/4 gates and no selected child. Native execution was recommended because tasks share validation interfaces; no execution method has been selected. Resume from the approval/execution-entry checklist without requesting plan approval again.
