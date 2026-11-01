# C2.1 Measurement Definition Implementation Plan

- **Governance:** active
- **Status:** approved
- **Date:** 2026-11-01
- **Roadmap child:** `C2.1`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** 2026-11-01 — Jeff / tvproductions; plan approved in chat; execution method pending
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver immutable measurement definitions with explicit semantics, representation-dependent validation, deterministic identity, and strict private definition-entry round trips, satisfying C2.1's four gates.

**Architecture:** Extend `measurements.models` with the approved supporting values and `MeasurementDefinition`. Private validation and wire modules share staged validation between constructors and entry readers; common canonical encoding and definition-preimage primitives remain in contracts. Public catalog loaders and schemas arrive in C2.2.

**Tech Stack:** Python 3.12 standard library, unittest, locked all-group uv, Ruff, ty, strict MkDocs, offline hygiene, external installed-wheel smoke.

**Spec:** [Approved canonical design](../specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md), especially lines 202–245, 251–330, 395–420, 459–604, 1288–1472 and 1852–1867; [core scope amendment](../../architecture/xplane_fdau_core_scope_amendment.md); repository-root `BACKLOG.md`, section “C2.1 — Measurement-definition model and semantic invariants.”

## Global Constraints

- Implement only C2.1; C1.3 and C1.5 are verified. Preserve delivered C1 primitives and native FDR behavior.
- “Every public structural model class above is a frozen, slotted, keyword-only dataclass.” “Named closed vocabularies are `enum.StrEnum` classes and are not dataclasses.”
- “Sequence inputs are defensively copied to tuples before validation.” Reject unordered containers and arbitrary iterables; never sort or deduplicate array-sets.
- “JSON `null` is prohibited throughout version 1.” Absent optional wire properties are omitted. Use the existing private omitted sentinel where explicit `None` must remain distinguishable from absence.
- “Definition and record self-hashes are computed cached properties, never init-fields.” Cache in a private non-init, non-comparing slot with a read-only `content_hash` property.
- “The root `xplane_fdau.__init__` continues to export only `__version__`.” Export only names delivered by this child from owning packages; no later model shells.
- Runtime is pure Python and standard-library-only; support remains `>=3.12,<3.13`. Execute through locked all-group uv and the exact `.python-version` selection (currently 3.12.16). Use unittest only; preserve mandatory hooks.
- No stock catalog entries, provider resource identities, transforms, acquisition, sample validation, simulator I/O, recording, ARINC or FDM implementation. No public definition-entry loader, dynamic serializer registry, caller-code hook, or new contract family.
- Jeff approved this plan on November 1 and separately requested a fresh handoff and ordinary Git sync. Record only the approved/planned checkpoint; no child is selected and no implementation or delivery gate is started. Execution method remains pending. Release retains separate authorization.

## Review Focus

1. Numeric equality can hide integer/real/Boolean confusion: Tasks 1–2 assert exact primitive domains, including arrays and integral reals.
2. A shallow freeze can leave caller lists controlling identity: Tasks 1–3 mutate every sequence input after construction and require unchanged fields, bytes and hashes.
3. A later shape error can be masked by an earlier semantic failure: Tasks 2–3 test whole-entry shape/domain/hash/semantic precedence and nested RFC 6901 paths.
4. An unchanged friendly ID/revision can conceal edited semantics: Task 3 proves semantic edits change the hash and stale declared hashes fail. Shared reference factories remain deferred; no constructor can accept an injected self-hash.
5. A slots-only object cannot use `functools.cached_property`: Task 3 tests repeated hash access, no `__dict__`, and rejection of constructor-supplied or assigned self-hashes.

## Planning baseline and decisions

Observed November 1: clean `main` at `b6f9c820019fc863dbecf030184f18efbc116377`, matching the local `origin/main` reference; no remote freshness claim. The handoff's older HEAD was advanced by its recorded handoff/sync commit. The unrelated `chore/dependency-refresh-2026-10-18` worktree remains untouched. Fresh backlog audit has no findings and `next` reports `write_plan C2.1`; no child is selected, C2.1 is specified with 0/4 gates.

Native inventory and actual checkout revisions match `.skills-first/bundle.lock.json`: starter 0.8.0 at `e0b752fcc13b87ec7868fe0b0f85badefdb6bf52`, Superpowers 7.0.1 at `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`, gz-skills 0.8.3 at `d6acc26e28ca1c4f43e5bb46d8973021d7d006c3`. Selected entry skills are discovered in this fresh session. Heavy is already selected; Backplane is disabled. Existing cognitive/Lizard/STRICT acceptance limitations remain open. The CLI's remote plugin-catalog request failed in the restricted environment; local inventory and actual Git checkout checks succeeded.

The approved design already fixes the product behavior; repeated brainstorming is unnecessary unless planning discovers a real design gap. The following implementation seams were reviewed with this plan:

- `NumericSpec` validates homogeneous integer or binary64 resolution/bounds intrinsically. `MeasurementDefinition` selects the permitted domain from its representation. This avoids adding an undocumented numeric-kind constructor field.
- Definition round trips use a private reader for a complete definition entry, including its required declared hash. No public family loader or schema is introduced early.
- Keep the dependency direction `measurements` → `contracts`. This child computes `MeasurementDefinition.content_hash` and private entry bytes inside measurements, using contracts' existing plain-data encoding/preimage helpers. Leave public `canonical_bytes` dispatch, `compute_content_hash`, and `definition_ref` unchanged: the latter two are still absent, as existing public API tests require. Their eventual owned-model integration remains a public API closure obligation under C4.3, where its design must reconcile the shared public surface with the declared dependency graph before implementation. C2.1 neither grants an upward-import exception nor claims that later integration delivered. No reference factory or standalone public serializer is necessary for C2.1's four gates.
- Raw entry validation operates on field mappings, not partially constructed dataclasses. Constructors explicitly project their owned nested values into the same field representation; the reader performs whole-entry shape/domain/hash/semantic checks before calling any model constructor. The exact reader stages and their tests are in Task 3.
- “Semantic revision mismatches” means exact revision/hash identity and stale-content rejection at this slice. A stateless constructor cannot know that an external author reused an old revision; document the author's revision obligation. Historical revision policing and cross-catalog reference resolution are not invented here.
- Python 3.12 review retains frozen keyword-only slotted dataclasses and `StrEnum`. Use a private cached slot rather than `cached_property`, whose documented implementation requires an instance dictionary ([dataclasses](https://docs.python.org/3.12/library/dataclasses.html), [functools](https://docs.python.org/3.12/library/functools.html#functools.cached_property)). No filesystem/process behavior is added to the runtime.

## File responsibilities

| Responsibility | Exact files |
| --- | --- |
| Owned structural models, enums, ordered exports | Modify `src/xplane_fdau/measurements/models.py`, `src/xplane_fdau/measurements/__init__.py` |
| Staged intrinsic and enclosing-definition invariants | Create `src/xplane_fdau/measurements/_definition_validation.py`; reuse `measurements/_quality.py` without changing its existing semantics |
| Exact private wire mappings and entry reader | Create `src/xplane_fdau/measurements/_definition_io.py` |
| Canonical encoding and family-bound definition hashing | Reuse `src/xplane_fdau/contracts/canonical_json.py` and `contracts/_content_hash.py` unchanged; measurements owns the entry projection |
| Semantic/round-trip/golden tests | Create `tests/test_measurement_definition.py`, `tests/test_measurement_definition_io.py`; modify `tests/test_public_api.py` |
| Installed module/behavior proof | Modify `tools/installed_smoke.py`, `tests/test_installed_smoke.py`; run `tests/test_runtime_import_boundary.py` |
| User/API guidance | Create `docs/reference/measurement-definitions.md`; modify `mkdocs.yml` |
| Approved execution and four gate receipts | This plan, guarded `BACKLOG.md`, `.superpowers/sdd/2026-11-01-c2-1-definition/` |

Do not edit contracts, schemas, packaging metadata, lockfiles, native FDR, other repositories, shared plugin caches, or deferred catalogs. New private runtime modules change installed inventory and require hygiene at stable closeout.

## Approval checkpoint and execution entry

- [x] Record explicit plan approval: November 1 — Jeff / tvproductions approved the reviewed plan and requested a fresh handoff and ordinary Git sync. This approves the plan; execution choice remains pending.
- [ ] Obtain the execution choice before starting implementation. Recheck relevant authority, plugin sources, HEAD, worktrees, clean baseline and audit/next. Stop on findings or authority drift. Do not ask for plan approval again solely because the session changed.
- [ ] Use `superpowers:using-git-worktrees` to create a temporary C2.1 branch/worktree from the synced approved-plan baseline. Do not stash, discard or absorb unrelated changes.
- [ ] After the execution choice, use backlog dry-run/digest/apply commands to select only C2.1 and transition planned → in_progress. The approval checkpoint links this plan and transitions specified → planned without selecting a child. Inspect every proposed diff and audit. No gate is recorded at entry.

## Task 1: Deliver supporting measurement semantics

**Files:** `measurements/models.py`, `measurements/__init__.py`, new `measurements/_definition_validation.py`, new `tests/test_measurement_definition.py`, `tests/test_public_api.py`.

**Interfaces:** Reuse contracts `RepresentationSpec`, `UnitSpec`, `Authority`, `ProvenanceSource`, identifier/domain validators and private omitted sentinel. Add these exact public enum members (uppercase Python names):

| Enum | Exact values in declaration order |
| --- | --- |
| `EnumerationMemberKind` | `known`, `unknown`, `reserved` |
| `InterpolationPolicy` | `prohibited`, `hold`, `linear` |
| `DiscontinuityPolicy` | `preserve`, `start_new_epoch`, `reject` |
| `Sensitivity` | `public`, `operational`, `restricted`, `unknown` |

Add frozen/slotted/keyword-only models with these constructor fields in semantic order; `?` denotes an omitted optional field, never a wire null:

```text
AxisSpec(axis_id: str, direction: str, sign_convention: str)
CoordinateSpec(kind: str, reference_frame_id?: str, datum_id?: str,
               handedness?: str, axes?: sequence[AxisSpec])
NumericSpec(storage_precision_bits: int, resolution: int | float,
            minimum?: int | float, maximum?: int | float)
EnumerationMember(code: str, label: str, kind: EnumerationMemberKind | str)
EnumerationSpec(members: sequence[EnumerationMember])
FreshnessSpec(fresh_for_ns?: int, stale_after_ns?: int)
ApplicabilitySelector(class_id: str, value: str)
```

`CoordinateSpec` selects exactly `not_applicable` or `applicable`; the latter requires reference frame, handedness (`left`/`right`) and axes, with optional datum. `NumericSpec` has one numeric domain across all present resolution/bounds; Boolean is neither domain. Numeric domain selection by measurement is Task 2. Sequence inputs accept actual lists/tuples and become tuples. Private validation helpers have signature `_validate_<stem>_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None`, for stems `axis`, `coordinates`, `numeric`, `enumeration_member`, `enumeration`, `freshness`, `applicability`; phases are shape, canonical domain, semantics (0, 1, 2). These helpers consume plain nested field mappings and sequences, never require an instance of the model they validate, and never construct one. Constructors explicitly form those mappings from their arguments, projecting exact owned nested models by named fields and omitting only sentinel-marked optional fields. Invalid nested object types remain visible to shape validation rather than being dereferenced. This is a private data representation, not a public wire API or reflection-based serializer. Task 3 reuses the mapping validators on parsed input after its staged shape/domain preparation.

- [ ] **Step 1: Write failing unittest cases.** `MeasurementSemanticValueTests` checks exact enum names/values and alias absence; dataclass frozen/slots/keyword-only behavior; constructor inventories; rejected foreign enums/unknown vocabulary; all accepted model variants and omitted optional fields.
- [ ] **Step 2: Add intrinsic boundary assertions.** Axis IDs use Identifier; direction/label/applicability value 1–256 NFC code points, sign 1–512. Coordinates require 1–32 ordered axes, unique axis IDs; reject missing/irrelevant fields at their precise pointers. Numeric precision accepts 1 and 64, rejects 0/65/Boolean; resolution is positive, bounds inclusive and ordered; reject mixed integer/real fields, nonfinite/underflow/overflow, null and Boolean values. Enumeration members are nonempty, code-sorted, unique, at most one unknown; reserved metadata is accepted. Freshness requires at least one UInt63 field, permits zero and equal limits, rejects reversed limits. Collections respect 65535 default entries, axes 32; no implicit sorting. Assert representative errors at `/axes/1/axis_id`, `/members/1/code`, `/resolution`, `/stale_after_ns`.
- [ ] **Step 3: Verify RED.** Run `uv run --locked --all-groups python -m unittest tests.test_measurement_definition tests.test_public_api -v`; require expected missing-model failures, not unrelated environment failures.
- [ ] **Step 4: Implement models and private phased checks.** Reuse common validators and omission conventions. Required/forbidden field selection happens before domain and semantic checks. Defensively freeze member/axis sequences; expose no extra public classes. Extend exports in approved table order with only delivered supporting names, retaining C1.5 enum identities.
- [ ] **Step 5: Verify GREEN** with Step 3 and focused static commands below. Mutation tests change original axis/member lists and require unchanged tuples. Commit the exact Task 1 files as `feat: add explicit measurement semantic values`, with mandatory hooks and authorized execution checkpoints.

## Task 2: Enforce complete measurement-definition invariants

**Files:** `measurements/models.py`, `measurements/__init__.py`, `measurements/_definition_validation.py`, `tests/test_measurement_definition.py`, `tests/test_public_api.py`.

**Interfaces:** Add `MeasurementDefinition` with required fields `definition_id: str`, `definition_revision: int`, `authority: Authority`, `provenance: sequence[ProvenanceSource]`, `title: str`, `description: str`, `limitations: sequence[str]`, `quantity_id: str`, `representation: RepresentationSpec`, `unit: UnitSpec`, `coordinates: CoordinateSpec`, `freshness: FreshnessSpec`, `interpolation_policy: InterpolationPolicy | str`, `discontinuity_policy: DiscontinuityPolicy | str`, `allowed_validity: sequence[ValidityState | str]`, `allowed_quality: sequence[QualityFlag | str]`, `sensitivity: Sensitivity | str`, `applicability: sequence[ApplicabilitySelector]`; optional omitted `numeric: NumericSpec` and `enumeration: EnumerationSpec`. Declare constructor fields in exactly that order: all required parameters first, then optional `numeric` and `enumeration`, preserving semantic order within each group. Every parameter is keyword-only. Validation uses the separate semantic inventory order, where numeric/enumeration precede freshness; constructor declaration order must not control error precedence. Private `_validate_definition_fields(fields: Mapping[str, object], phase: int, *, path: str = "") -> None` applies whole-object phases in semantic property order over nested field mappings. The constructor projects validated owned nested values explicitly into that representation; it does not accept raw dictionaries as substitutes for those public model arguments. Task 3 adds the hash property after successful validation.

- [ ] **Step 1: Write failing definition matrix tests.** `MeasurementDefinitionTests.test_representation_matrix` covers all nine representation kinds and every scalar element kind for both array kinds, with synthetic `test.*` definitions. Assert integer/real/vector/numeric arrays require numeric; scalar and array enumeration require enumeration; all irrelevant numeric/enumeration fields fail. Non-numeric scalar/array representations require unitless; numeric kinds may be unitless or unit. A unit's quantity must equal the definition quantity.
- [ ] **Step 2: Add exact cross-field tests.** Integer and integer-array numeric triples use Int64; real/vector/real-array triples use binary64, including rejection of integer `1` where `1.0` is required. Linear interpolation is accepted only for real/vector/numeric arrays (including integer arrays); scalar integer rejects linear. Applicable vector axis count equals length; every other representation uses at most one axis. Assert nested shape is one-dimensional via existing RepresentationSpec; referenced-byte payload constraints reuse existing PayloadSpec validation. Do not evaluate normalized sample values here.
- [ ] **Step 3: Add explicit metadata and collection tests.** Title/description limits 256/4096; limitations unique and order-preserving, each 1–1024, at most 256, empty permitted. Provenance nonempty, at most 256, unique by source ID plus revision/version, order-preserving. Allowed validity is nonempty, unique lexical; quality may be empty, unique lexical; neither infers the other. Applicability at most 256, empty permitted, class IDs unique and lexical. Preserve authority and every policy explicitly; reject missing required fields, invalid IDs/revisions, nulls and unlisted fields. Frozen fields and caller sequence mutation cannot change accepted meaning.
- [ ] **Step 4: Add signature and precedence assertions and verify RED.** `test_constructor_signature_order` uses `inspect.signature(MeasurementDefinition)` to assert the exact required-field sequence in Interfaces followed by `numeric`, `enumeration`, all keyword-only, required parameters without defaults, optional parameters with the omitted sentinel, and no `content_hash` parameter. Separately, `test_validation_order_is_independent_of_signature_order` supplies otherwise valid real-definition field mappings with numeric `resolution=0.0` and freshness `fresh_for_ns=2, stale_after_ns=1`; `_validate_definition_fields(..., 2)` must report `/numeric/resolution` first, although numeric is declared later in the constructor. Supply an early semantic unit mismatch plus a later malformed applicability item and require shape first; supply non-NFC title plus a later wrong primitive type and require shape first. Assert constructor RFC 6901 paths, no invented source location, no sensitive payload echo. Run `uv run --locked --all-groups python -m unittest tests.test_measurement_definition tests.test_measurement_quality tests.test_public_api -v` and observe expected absent-definition failures.
- [ ] **Step 5: Implement the definition and phased validation.** Check every shape before any domain, and every domain before semantics across nested fields. Reuse C1.5 vocabulary rules without moving or replacing enum ownership; whole-entry staging must precede helpers that perform local semantics. Reject arbitrary iterables without consuming them. Do not add a catalog or sample validator.
- [ ] **Step 6: Verify GREEN** with Step 4 and focused static checks. Assert exact exports are the specification's measurements model row minus only `MeasurementCatalog`; no measurement models are re-exported by contracts or root. Commit Task 2 files as `feat: validate measurement definition semantics` with mandatory hooks.

## Task 3: Bind definition hashes and staged private entry round trips

**Files:** New `measurements/_definition_io.py`, `tests/test_measurement_definition_io.py`; modify `measurements/models.py`, `measurements/_definition_validation.py`, `tests/test_public_api.py`. Contracts and their public exports remain unchanged.

**Interfaces:** Private `_measurement_definition_wire(value: MeasurementDefinition, *, include_hash: bool = True) -> dict[str, object]`, `_measurement_definition_bytes(value: MeasurementDefinition) -> bytes`, and `_measurement_definition_from_wire(value: object, *, path: str = "", source: str = "<memory>") -> MeasurementDefinition`. Supporting explicit wire projections are `_axis_spec_wire`, `_coordinate_spec_wire`, `_numeric_spec_wire`, `_enumeration_member_wire`, `_enumeration_spec_wire`, `_freshness_spec_wire`, `_applicability_selector_wire`, each accepting its owned type and returning `dict[str, object]`. Entry bytes use existing contracts `_encode_document`; hashing uses `_definition_content_hash`. These helpers stay private to measurements; no common public dispatcher imports measurements.

The reader's exact private stages live in `_definition_io.py`:

```python
_definition_entry_shape(value: object, *, path: str = "") -> dict[str, object]
_definition_entry_domains(fields: Mapping[str, object], *, path: str = "") -> dict[str, object]
_definition_entry_hash(fields: Mapping[str, object], *, path: str = "") -> None
_definition_entry_semantics(fields: Mapping[str, object], *, path: str = "") -> None
_definition_entry_build(fields: Mapping[str, object]) -> MeasurementDefinition
```

`shape` accepts parser `_ObjectPairs` or exact dictionaries, recursively checks property inventories, tags and lexical numeric types, and returns nested plain field dictionaries/sequences with number tokens retained. It checks the entire entry, including nested authority, provenance, representation, unit, and payload shapes. It does not call any `*_from_wire` helper that constructs a model. `domains` materializes preserved number tokens and validates NFC, null prohibition, integer/binary64 domains, array/object limits and depth at most 64; it returns plain values without constructing models or enforcing semantic ranges/order. Both use the specification's semantic field order. `hash` computes the family-bound preimage from plain fields with the declared hash removed, and compares a syntactically valid declared hash; malformed SHA-256 text is left for semantic validation rather than treated as a valid digest mismatch. `semantics` applies `_validate_definition_fields(fields_without_hash, 2)` plus declared-hash syntax checks in the specification's field order. `build` explicitly constructs nested owned values and the definition only after every earlier stage succeeds. Constructors can repeat validation as an integrity check, but cannot determine an earlier reader failure.

`_measurement_definition_from_wire` checks duplicates first, then runs the five stages in order. Its one outer error-context adapter retains the supplied source and pointer prefix exactly once; helpers use relative pointers and invent no locations. No partially initialized dataclass, `object.__new__` bypass, caller callback or reflection-based construction is permitted. Future C2.2 family readers must extend staging across the whole catalog before calling entry build stages; this entry helper alone does not establish catalog-wide precedence.

- [ ] **Step 1: Write independent golden tests and verify RED.** Build one minimal synthetic Boolean/unitless definition with explicit policies, freshness, provenance and `unknown` validity, empty quality/limitations/applicability. Write literal expected canonical entry bytes (including LF) and family/version/definition preimage bytes; independently compute SHA-256 with hashlib rather than the production hash helper. Assert `_measurement_definition_bytes`, `content_hash` and `_definition_preimage` match those exact expectations. Add integer/real, coordinate, enumeration, array and referenced-byte entry round trips. Run `uv run --locked --all-groups python -m unittest tests.test_measurement_definition_io tests.test_public_api -v`; require expected absent private-reader/hash failures.
- [ ] **Step 2: Add identity and dependency assertions.** Editing each semantic field, authority/provenance or revision changes the hash; changing input property order does not. Negative real zero canonicalizes identically to positive real zero. Ordered provenance/axes/limitations affect identity. Caller sequence mutation cannot change bytes/hash; repeated hash access retains its cached value; no `__dict__`, public hash setter or constructor hash exists. In `tests/test_public_api.py`, add `test_contracts_do_not_import_measurements`: inspect every contracts Python module's AST, including nested functions and TYPE_CHECKING blocks, and reject relative or absolute imports resolving to measurements. Retain the existing assertions that `definition_ref` and `compute_content_hash` are absent. No importlib-based lookup, registry or structural duck-typed dispatch may replace a direct upward import.
- [ ] **Step 3: Add strict reader and stage-order assertions.** Use the existing duplicate-preserving JSON parser. Missing/unknown properties, irrelevant variants and wrong lexical numeric types raise ContractShapeError; null/NFC/overflow/underflow/depth failures raise CanonicalJSONError. Missing hash is shape; valid but stale hash is ContractHashError; malformed hash syntax reaches semantic validation. Recompute correct declared hashes independently for semantic-only negative cases. Test `/definitions/2/numeric/resolution` and `source="definition.json"`, constructor/reader equivalent paths, and object-order/whitespace tolerance. Require parse → shape → domain → hash → semantics precedence. In particular: stale hash plus a structurally valid zero numeric resolution raises ContractHashError; correct hash plus zero resolution raises ContractValidationError at `/numeric/resolution`; stale hash plus a later malformed applicability item raises ContractShapeError; stale hash plus non-NFC title raises CanonicalJSONError. Patch `_definition_entry_build` to raise AssertionError if invoked, and require all four invalid entries to report their expected contract error without reaching build. For an accepted entry, wrap build and assert it is called exactly once with materialized primitives. These tests prevent eager nested constructors from bypassing staging.
- [ ] **Step 4: Implement wire projections, stages and cached hash.** Reuse `_definition_content_hash` with literal family `https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog` and version 1. Preimage wraps the complete entry under `definition` with only its own hash omitted. Pass a hash-free mapping to the existing preimage helper so that its own SHA-256 syntax validator cannot preempt reader semantics. Cache once after successful constructor validation and serialize that cache. Keep optional fields omitted. Implement explicit named-field construction in build and plain-mapping validation in earlier stages. Do not change contracts or add public convenience APIs. Test both package import orders in fresh processes.
- [ ] **Step 5: Verify GREEN.** Repeat Step 1 plus `tests.test_measurement_definition`, `tests.test_canonical_json`, `tests.test_contract_values`, `tests.test_contract_identity`, `tests.test_runtime_import_boundary`, then focused static checks. Commit Task 3 files as `feat: bind measurement definitions to canonical identity` with mandatory hooks.

## Task 4: Verify installed behavior and publish focused guidance

**Files:** `tools/installed_smoke.py`, `tests/test_installed_smoke.py`, new `docs/reference/measurement-definitions.md`, `mkdocs.yml`.

**Interfaces:** Private `tools.installed_smoke._measurement_definition_smoke() -> None`, called by the existing smoke flow, raising existing SmokeError for failed acceptance checks. No additional runtime API.

- [ ] **Step 1: Write failing installed smoke tests.** Add the two new private runtime modules to the exact discovered module inventory. Require smoke acceptance of a synthetic Boolean definition, immutable canonical-entry/hash round trip, and rejection of an irrelevant numeric field and stale hash. Patch the private reader to accept tampered content and require SmokeError, ensuring the smoke detects an ineffective check. Run `uv run --locked --all-groups python -m unittest tests.test_installed_smoke -v` and observe expected missing-helper/inventory failure.
- [ ] **Step 2: Implement smoke through installed imports.** Check public package ownership, private canonical-entry bytes/hash consistency, strict private entry behavior, and constructor immutability. Use no source-tree fixtures or stock catalog entries. Preserve the existing wheel-origin checks and stdlib-only import scan.
- [ ] **Step 3: Write the guide and MkDocs entry.** Provide one executable synthetic definition example, representation/unit/numeric/coordinate matrix, explicit quality and freshness semantics, semantic revision obligation, and read-only `content_hash` example. Explain reserved enum members are definition metadata and normalized sample authorization arrives later. Render only delivered public API via MkDocstrings. Identify private entry readers as internal integration details; public measurement-catalog loaders/schema remain C2.2 and shared convenience APIs remain pending public API closure. Do not show undelivered functions as usable APIs. Validate examples against tests without phrase-snapshot tests.
- [ ] **Step 4: Verify GREEN.** Run `uv run --locked --all-groups python -m unittest tests.test_measurement_definition tests.test_measurement_definition_io tests.test_measurement_quality tests.test_public_api tests.test_installed_smoke tests.test_runtime_import_boundary tests.test_documentation -v`, focused static checks and `uv run --locked --all-groups mkdocs build --strict`. Commit exact Task 4 files as `docs: document and verify measurement definitions`, retaining hooks.

## Focused static verification

After each task's focused tests, run Ruff check and Ruff format --check on its exact changed Python paths, then `uv run --locked --all-groups ty check`. Once all planned files exist, the combined commands are:

```powershell
uv run --locked --all-groups ruff check src/xplane_fdau/measurements tests/test_measurement_definition.py tests/test_measurement_definition_io.py tests/test_public_api.py tools/installed_smoke.py tests/test_installed_smoke.py
uv run --locked --all-groups ruff format --check src/xplane_fdau/measurements tests/test_measurement_definition.py tests/test_measurement_definition_io.py tests/test_public_api.py tools/installed_smoke.py tests/test_installed_smoke.py
uv run --locked --all-groups ty check
```

## Stable closeout and evidence

- [ ] Perform independent review via `superpowers:requesting-code-review` at the approved execution checkpoints and over the whole branch before finishing. Resolve load-bearing findings and bind evidence to the actual candidate.
- [ ] Use canonical `gzs-quality-gate`/`gzs-repository-hygiene` with the project adapters. New shipped modules change package inventory, so run full offline hygiene once at stable closeout; it supplies the complete active-Python gate and fresh strict artifacts. Do not separately repeat the standalone gate on unchanged inputs:

```powershell
uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py
```

- [ ] Run the release skill's existing external Python 3.12 installed-wheel smoke on the exact validated wheel because installed imports changed. Record wheel/sdist hashes, Python version, import origins and result. No broader Python-minor matrix or release-readiness claim.
- [ ] Record four gate receipts under `.superpowers/sdd/2026-11-01-c2-1-definition/`: gate 1 representation/unit/coordinate/numeric/enum matrix (Tasks 1–2); gate 2 explicit metadata/policies/provenance (Tasks 1–2); gate 3 irrelevant fields and exact semantic identity mismatch rejection (Tasks 2–3); gate 4 immutable hash-stable synthetic round trips (Tasks 3–4). Keep failures and corrections visible. Commit evidence only when it exists.
- [ ] Through guarded backlog operations advance only C2.1 to implemented/reviewed/verified when review and committed gates justify each transition. Complete plan tracking and completion evidence; do not claim C2.2 schema/catalog delivery.
- [ ] Use `superpowers:finishing-a-development-branch` and obtain the user's integration choice. If local integration is selected, follow AGENTS.md's exact fast-forward procedure and hygiene's focused main checks; keep branch/worktree until main verification passes, then remove them. Remote sync, tagging and publication retain separate authorization.

## Planning audit

This is a direct document comparison under `gzs-plan-audit`, not implementation evidence.

| Intent → scope | Classification | Evidence |
| --- | --- | --- |
| Explicit provider-neutral measurement meaning within X-Plane | Aligned | Design lines 11–37, 496–604; BACKLOG lines 193–201; Tasks 1–2 |
| Pure immutable contracts, no provider acquisition or stock content | Aligned | Design lines 77–97, 459–474, 603–604; global constraints and file boundaries |
| Definition identity includes semantics, authority, provenance and revision | Aligned | Design lines 395–420; BACKLOG lines 199–201; Task 3 |
| Catalog/schema and downstream execution stay separate | Aligned | ROADMAP lines 131–134; design lines 1861–1867; explicit C2.2 exclusions |

| Scope → plan | Classification | Evidence |
| --- | --- | --- |
| Representation, unit, coordinates, precision, resolution, range, enumeration | Aligned | BACKLOG lines 195–196; Tasks 1–2 and gate 1 |
| Explicit freshness, policies, sensitivity, applicability, provenance | Aligned | BACKLOG lines 197–198; Tasks 1–2 and gate 2 |
| Reject irrelevant fields and semantic identity mismatches | Aligned | BACKLOG line 199; Tasks 2–3 and gate 3; stateless revision limit documented |
| Immutable synthetic definitions with stable hashes and round trips | Aligned | BACKLOG line 200; Tasks 3–4 and gate 4 |
| Inward dependency direction | Aligned | Design lines 150–172; planning decision and Task 3 leave contracts unchanged, with a whole-package AST import assertion |
| Executable raw-entry validation before construction | Aligned | Design lines 1407–1455; Tasks 1–3 define mapping validators, five reader stages, and error-precedence/build-barrier tests |
| Required-then-optional constructor signature, independent semantic validation order | Aligned | Design lines 1340–1345; Task 2 Interfaces and Step 4 explicitly distinguish and test both orders |
| Review, installed imports, documentation, complete candidate gate | Aligned | AGENTS.md testing/workflow; design lines 1716–1734; Task 4 and closeout |

### Review corrections — November 1

The initial self-review PASS was withdrawn after the subsequent plan review identified upward imports and missing raw-stage interfaces. This revision resolves those C2.1 findings:

| Finding | Resolution | Verification specified |
| --- | --- | --- |
| Function-local imports still reverse the dependency graph | Remove common public dispatch/factory work from this child; retain measurement-owned private entry encoding and public read-only definition hashes. C4.3 must reconcile the final shared convenience surface with architecture before implementing it. | Task 3's whole-contracts AST assertion and unchanged public API absence checks |
| Model-only validators cannot stage a raw entry before construction | Replace their signatures with plain field-mapping validators; define raw shape/domain/hash/semantic/build interfaces and their exact sequence. | Task 3's competing-error tests and patched-build barrier |
| Optional definition parameters preceded required parameters | Declare every required parameter first, then numeric/enumeration; retain the separate semantic validation inventory. | Task 2's signature inspection and independent validation-order tests |

Gap list: none within C2.1's four gates after this revision. Planning verdict: **PASS for C2.1 coverage and scope**; Jeff approved the corrected plan on November 1. Execution choice remains pending. Shared public convenience API integration is explicitly deferred, not resolved for the whole C1–C4 design or claimed delivered by this plan. No architecture exception or delivery acceptance is claimed. Self-review checked interface consistency, removed obsolete dispatch edits/tests/examples, semantic/domain precedence, cached-slot compatibility, and all five Review Focus tests.
