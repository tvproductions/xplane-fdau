# C1.3 Typed Values and Content-Addressed Payload References Implementation Plan

- **Governance:** active
- **Status:** draft
- **Date:** 2026-10-04
- **Roadmap child:** `C1.3`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** —
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver immutable, strictly typed inline values, representation/shape/unit declarations, and metadata-only payload references satisfying C1.3's four backlog gates.

**Architecture:** `contracts.values` owns the exact public values and their private wire projections. A private `_value_io` module converts parsed nested wire objects using the same validation rules and property paths as construction; it does not introduce a top-level contract family or public loader. Explicit canonical serialization dispatch admits the delivered C1.3 model types while retaining C1.1's standalone parameter-object contract.

**Tech Stack:** Python 3.12 standard library at runtime; `unittest`, uv, Ruff, ty, offline repository hygiene, external installed-wheel smoke.

**Spec:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`, especially “Contract families and versions,” “Shared values and payload references,” the representation/shape/unit paragraphs under catalogs, “Public API and errors,” and C1.3 acceptance criteria. The core-scope amendment governs Python support.

## Global Constraints

- Implement only C1.3. `C1.2` is verified at 4/4 gates. C1.3 remains `specified`, 0/4, and unselected until this plan is explicitly approved and the guarded adapter changes its lifecycle.
- Runtime remains pure Python and standard-library-only; use `unittest` only. Root `xplane_fdau.__all__` remains `["__version__"]`.
- Public structural models are frozen, slotted, keyword-only dataclasses. Closed vocabularies are `enum.StrEnum`. Copy sequence inputs into tuples; preserve order rather than sorting or deduplicating them.
- `Int64` is `-9223372036854775808..9223372036854775807`; `UInt63` is `0..9223372036854775807`. A real requires an actual finite binary64 float, never an integer or Boolean. No numeric, text, or enumeration coercion is permitted.
- Optional wire properties are omitted; JSON `null` is prohibited. Internally distinguish an omitted variant property from a supplied `None` when absence matters. Do not accept a wire null as an omitted optional field.
- Field validation follows shape, canonical domain, then semantics across the whole nested object, with semantic property order inside each tier. Use RFC 6901 paths, including array indices. Do not echo inline or payload contents in diagnostics.
- Preserve C1.1 encoding, lexical integer/real distinction, UTF-8, NFC, final LF, parser precedence, and parameter-object bounds. Preserve C1.2 identity, provenance, and hashing behavior.
- Add no family model, family loader, schema resource, conformance corpus, reference factory, public self-hash dispatch, clock/quality model, algorithm execution, storage resolver, provider adapter, or native-FDR behavior.
- Enumeration values at this layer enforce Identifier syntax only. Measurement-member existence and reserved-member rejection belong to later catalog-resolved validation; a raw inline value may preserve an unknown/reserved source code.
- Payload length/hash describe the original claimed bytes for every retention status. Validation must not open a file, resolve a URI, inspect storage, or invent bytes.
- During implementation use focused `unittest`, Ruff, and ty. New runtime modules require one stable-candidate full offline hygiene gate and a Python 3.12 external installed-wheel smoke; hygiene supplies the full quality gate.
- No commit/push workflow, release, tag, publication, or external-repository edit is authorized by drafting this plan. Execution's scoped local commits are recorded below and require plan approval.

## Review Focus

1. Integer versus integral-real values and Boolean elements must remain distinct through construction, parsed wire input, and canonical serialization; Task 1 and Task 4 test this.
2. Later shape errors must outrank earlier canonical-domain or semantic errors; Task 4 tests mixed-invalid nested values and indexed paths.
3. Caller mutation of an input vector, array, or allow-list must not alter stored values or canonical bytes; Tasks 1 and 3 test defensive copying.
4. An omitted property must not become wire null, and an irrelevant property must fail even if supplied as null; Tasks 1, 3, and 4 test the variant boundary.
5. Missing/omitted/unverified payload claims must retain original metadata and perform no storage access; Tasks 2 and 5 test all statuses and fault-injected I/O.

## Baseline and file map

Observed baseline: clean `main` at `e56e6a9de3ba961315f2d60d5ba22c5daca1ddc0`, only the primary worktree, no selected child. Backlog `audit` and `next` both exit zero with no findings and recommend `action=write_plan child=C1.3`. Recheck at execution entry; this observation is not a permanent baseline pin.

| Responsibility | Files |
| --- | --- |
| Public vocabularies, values, declarations, validation, explicit private wire projections | Create `src/xplane_fdau/contracts/values.py` |
| Strict nested wire readers with parser-token preservation and pointer context | Create `src/xplane_fdau/contracts/_value_io.py` |
| Canonical model dispatch and semantic package exports | Modify `src/xplane_fdau/contracts/canonical_json.py`, `src/xplane_fdau/contracts/__init__.py` |
| Behavioral and loaded-validation parity tests | Create `tests/test_contract_values.py`; extend `tests/test_canonical_json.py` |
| Export, runtime-module inventory, installed behavior | Modify `tests/test_public_api.py`, `tests/test_installed_smoke.py`, `tools/installed_smoke.py`; use existing `tests/test_runtime_import_boundary.py` |
| Lifecycle and execution evidence | Update this plan after approval; guarded edits to `BACKLOG.md`; create `.superpowers/sdd/2026-10-04-c1-3-typed-values-payload-references/` during execution |

Reuse `_identity_validation` scalar helpers, `_json_parse._parse_json_document`, `_NumberToken`, `_ObjectPairs`, `_materialize_number`, and `_pointer`. Do not replace their verified behavior. Existing artifact inventory discovers modules beneath `src/xplane_fdau`; no packaging manifest change is expected.

## Execution entry — after approval

- [ ] Recheck authorities, backlog audit/next, branch, HEAD, clean status, and worktrees. Stop on changed authority or audit findings.
- [ ] Use `superpowers:using-git-worktrees` to establish a temporary C1.3 feature worktree from the clean baseline; drafting this plan does not create one.
- [ ] Record explicit plan approval. Link this plan, select C1.3, and transition through `planned` to `in_progress` using the backlog adapter's dry-run, target SHA-256, and apply workflow. Inspect each diff and rerun audit. Commit only the approved plan and C1.3 lifecycle changes.
- [ ] Follow the user's chosen execution method. Recommend native execution followed by one independent whole-branch review: the tasks share validators and wire paths, making a single implementer economical. Earlier C1.2 execution approval is not approval of this plan.

---

### Task 1: Exact inline value domains

**Files:** Create `contracts/values.py` under `src/xplane_fdau` and `tests/test_contract_values.py`; update `tests/test_installed_smoke.py`'s exact module inventory.

**Interfaces:** Produce `ValueRepresentation` with `boolean`, `integer`, `real`, `string`, `enumeration`, `vector`, `fixed_array`, `variable_array`, `referenced_bytes`; `ScalarRepresentation` with the first five only. Produce `InlineValue` with fields in semantic order `representation`, variant-only `element_representation`, `value`. Primitive values have their exact spec domain; vector values and arrays are defensively copied tuples. Private `_inline_value_wire(value: InlineValue) -> dict[str, object]` emits only the selected variant's properties and plain ordered arrays. Shared private validation must support an enclosing pointer without changing public constructors.

- [ ] **Step 1: Write behavior-specific failing tests.** Establish an importable surface before collecting RED; missing imports alone are not evidence. Use `unittest` assertions equivalent to:

  ```python
  integer = InlineValue(representation="integer", value=1)
  real = InlineValue(representation="real", value=1.0)
  self.assertIs(type(integer.value), int)
  self.assertIs(type(real.value), float)
  vector_input = [2.0, 1.0]
  vector = InlineValue(representation="vector", value=vector_input)
  vector_input[0] = 99.0
  self.assertEqual((2.0, 1.0), vector.value)
  with self.assertRaises(ContractShapeError) as caught:
      InlineValue(representation="integer", value=True)
  self.assertEqual("/value", caught.exception.path)
  ```

  Cover signed integer endpoints/overflow; real integer rejection, negative zero, subnormal/max-finite, NaN/infinity; string length 1/16384 and empty/16385/non-NFC/surrogate rejection; enumeration dotted-Identifier syntax and a display label such as `Reserved` rejected as an identifier. Preserve syntactically valid `test.unknown` and `test.reserved`. Cover vector empty/65535/65536, scalar array types, heterogeneous/nested arrays, Boolean elements in numeric arrays, empty fixed/variable inline arrays (length constraints belong to the representation declaration), and preserved array order. Reject `referenced_bytes` inline, unknown tags, missing array element tag, scalar element tag outside its vocabulary, and irrelevant properties. Assert dataclass freezing, slots, keyword-only fields, and exact error class/path.
- [ ] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_values tests.test_installed_smoke -v`; capture a domain/order assertion failure.
- [ ] **Step 3: Implement the two vocabularies, InlineValue, and wire projection.** Validate all shapes before canonical domains and semantics. Accept enum members or their exact string spellings, store the corresponding enum, and never accept general string-like or numeric coercion. Use the common 65535 collection bound; vector's declared maximum 1024 is imposed by RepresentationSpec, not the raw InlineValue alone.
- [ ] **Step 4: Verify GREEN** with Step 2, focused Ruff check/format on the changed files, and `uv run --offline --frozen ty check`.
- [ ] **Step 5: Commit the scoped files** with `feat: preserve exact inline value domains`.

### Task 2: Metadata-only payload references

**Files:** Extend `src/xplane_fdau/contracts/values.py` and `tests/test_contract_values.py`.

**Interfaces:** Produce `RetentionStatus` with `retained`, `intentionally_omitted`, `missing`, `unverified`; `PayloadReference(*, media_type: str, byte_length: int, sha256: str, storage_role: str, retention_status: RetentionStatus)`; and private `_payload_reference_wire(value: PayloadReference) -> dict[str, object]`. Constructor field order is exactly the signature above.

- [ ] **Step 1: Write failing tests.** For each retention status, assert a claim `application/octet-stream`, length `0` or `2**63-1`, hash `"a" * 64`, role `test.raw_payload` retains all five fields. Patch storage-opening functions while constructing and projecting references; assert no calls. Reject Boolean/negative/overflow length, uppercase/short hash, unqualified role, and unknown status at the corresponding property path. Media type is NFC length 1..127 and full-matches `[a-z0-9][a-z0-9!#$&^_.+-]{0,126}/[a-z0-9][a-z0-9!#$&^_.+-]{0,126}`; reject uppercase, parameters, whitespace, malformed separators, and total length 128. Do not require nonempty payload bytes or a locator.
- [ ] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_values -v`.
- [ ] **Step 3: Implement the vocabulary, reference, and projection** using existing UInt63, Identifier, Sha256, and NFC helpers; enforce the total media-type length as well as regex syntax. Preserve original metadata for every status without looking up storage.
- [ ] **Step 4: Verify GREEN** with Step 2, focused Ruff check/format, and ty.
- [ ] **Step 5: Commit** with `feat: describe content-addressed payload claims`.

### Task 3: Representation, shape, payload, and unit declarations

**Files:** Extend `src/xplane_fdau/contracts/values.py` and `tests/test_contract_values.py`.

**Interfaces:** Produce `PayloadSpec(allowed_media_types, allowed_storage_roles)`, `RepresentationSpec`, `ShapeSpec`, and `UnitSpec`, all keyword-only. Their constructor fields follow the source specification's semantic order:

| Model | Selected fields and bounds |
| --- | --- |
| PayloadSpec | Nonempty unique lexically ordered media-type and Identifier arrays, each at most 65535; immutable tuples |
| RepresentationSpec | `kind`; vector `length` 1..1024; fixed array `element_representation`, `length` 1..65535; variable array `element_representation`, `minimum_length`, `maximum_length`, 0..65535 with min <= max; referenced bytes `payload: PayloadSpec`; scalars only kind |
| ShapeSpec | `kind` scalar/fixed/variable; scalar only kind; fixed length 1..65535; variable minimum/maximum 0..65535 with min <= max |
| UnitSpec | `kind` unitless/unit; unitless only kind; unit `quantity_id`, `unit_id` Identifier fields |

For RepresentationSpec, field order is `kind`, `element_representation`, `length`, `minimum_length`, `maximum_length`, `payload`. For ShapeSpec it is `kind`, `length`, `minimum_length`, `maximum_length`; UnitSpec is `kind`, `quantity_id`, `unit_id`. Use private omitted sentinels as needed to enforce exact variants. Private per-model `_payload_spec_wire`, `_representation_spec_wire`, `_shape_spec_wire`, `_unit_spec_wire` return exact-property dictionaries.

- [ ] **Step 1: Write failing assertions** for every row/variant, minimum/maximum boundaries, zero-length variable declarations, min > max, overflow, Boolean counts, invalid element representation, and irrelevant or missing variant fields. Assert vector 1024 accepted/1025 rejected, fixed 65535 accepted/65536 rejected. Assert duplicate/unsorted allow-lists fail rather than being rewritten; caller list mutation does not change either tuple. Cover optional-property omission, invalid nested PayloadSpec type, bad unit identifiers, and absence of fabricated unitless semantics. Defer quantity matching and unit-versus-representation compatibility to C2.1/C2.4.
- [ ] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_values -v`.
- [ ] **Step 3: Implement the four dataclasses and projections.** Use explicit variant inventories, shared scalar domains, and defensive copies. Do not couple a raw value to a catalog or invent a public value-vs-definition validator in this child.
- [ ] **Step 4: Verify GREEN** with Step 2, focused Ruff check/format, and ty.
- [ ] **Step 5: Commit** with `feat: declare canonical value shapes and units`.

### Task 4: Parsed wire validation and canonical model serialization

**Files:** Create `src/xplane_fdau/contracts/_value_io.py`; modify `src/xplane_fdau/contracts/canonical_json.py`, `src/xplane_fdau/contracts/__init__.py`, `tests/test_contract_values.py`, `tests/test_canonical_json.py`, `tests/test_public_api.py`, and `tests/test_installed_smoke.py`.

**Interfaces:** Produce private `_inline_value_from_wire`, `_payload_reference_from_wire`, `_payload_spec_from_wire`, `_representation_spec_from_wire`, `_shape_spec_from_wire`, `_unit_spec_from_wire`, each `(value: object, *, path: str = "", source: str = "<memory>") ->` its named model. Accept parser-preserved objects as well as materialized wire dictionaries. Share staged validation and reuse constructors after shape/domain checks; do not add public loads/dumps functions. The spec's exact `values.__all__` is `ValueRepresentation`, `ScalarRepresentation`, `RetentionStatus`, `InlineValue`, `PayloadReference`, `PayloadSpec`, `RepresentationSpec`, `ShapeSpec`, `UnitSpec`. Re-export these in contracts after provenance and before canonical_json exports.

- [ ] **Step 1: Write failing round-trip/parity tests.** Pin exact canonical bytes for integer `1` versus real `1.0`, vector `[2.0,1.0]`, ordered scalar arrays, payload metadata, and every declaration variant. Parse with `_parse_json_document`, decode with the private reader, and assert equal model/canonical bytes. Use literal expected bytes including final LF, rather than constructing expectations with the serializer under test. Assert constructors and wire readers report the same local pointer for each invalid domain, and a nested reader prefixes paths correctly (e.g. `/test.value/value/1`). Unknown/missing properties are shape errors; duplicate properties across JSON are parse errors; null never becomes omission.

  Add mixed-invalid cases: earlier bad media-type syntax plus later Boolean byte length yields `ContractShapeError` at `/byte_length`; earlier non-NFC media text plus later missing role yields shape first; earlier negative length plus later non-NFC role yields canonical-domain first. Cover real token `1` versus `1.0`/`1e0`, integer overflow before materialization, array index paths, nested payload paths, and source labels without invented line/column context.

  Assert canonical_bytes still accepts an empty parameter object and rejects standalone scalar/array roots, arbitrary dataclasses, mappings containing unqualified parameter keys, unsupported host objects, and unowned model subclasses. Existing C1.1/C1.2 regression vectors remain identical.
- [ ] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_values tests.test_canonical_json tests.test_contract_json_parse tests.test_contract_identity tests.test_contract_provenance tests.test_public_api tests.test_installed_smoke -v`.
- [ ] **Step 3: Implement strict private readers and explicit dispatch.** Preserve number tokens until representation-aware shape checks complete, then materialize with existing helpers. Prefix/recontextualize errors without echoing value contents. Canonical dispatch uses exact owned classes and explicit wire converters, not reflection, a registry, or caller-code hooks. Keep values independent of canonical_json to avoid an import cycle. No standalone value gains a self-hash or family/version envelope.
- [ ] **Step 4: Verify GREEN** with Step 2, focused Ruff check/format, and ty. Confirm exact public exports and no root exports, family loaders, or model-only hash/reference factories appear.
- [ ] **Step 5: Commit** with `feat: validate and serialize canonical value primitives`.

### Task 5: Installed closure, review, and four-gate evidence

**Files:** Modify `tools/installed_smoke.py` and `tests/test_installed_smoke.py`; extend `tests/test_contract_values.py` and `tests/test_public_api.py` only for evidenced integration gaps. After execution update this plan, `BACKLOG.md`, and the C1.3 evidence directory.

**Interfaces:** Installed smoke constructs an inline real array, a referenced-byte declaration, and one payload claim; checks frozen order and literal canonical bytes; verifies byte-only data cannot be inline. Existing native FDR, C1.1, and C1.2 checks remain.

- [ ] **Step 1: Write failing smoke tests** injecting an incorrect canonical value projection and an altered payload field; prove smoke raises `SmokeError`. Verify every new runtime module is discovered/imported. Run storage access mocks around the C1.3 portion of the smoke (the rest of smoke legitimately uses files).
- [ ] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_values tests.test_canonical_json tests.test_public_api tests.test_installed_smoke tests.test_runtime_import_boundary -v`.
- [ ] **Step 3: Implement minimal installed checks** and fix evidenced integration defects without adding later-child resources or behavior.
- [ ] **Step 4: Verify focused GREEN** with Step 2, focused Ruff check/format, and ty; commit with `test: verify installed canonical value primitives`.
- [ ] **Step 5: Obtain independent whole-branch review** against all four gates, staged precedence/path parity, exact wire bytes, immutability, declaration bounds, storage isolation, and the explicit public API. Resolve load-bearing findings with failing `unittest` assertions before fixes.
- [ ] **Step 6: Run one stable-candidate complete offline hygiene gate** on Python 3.12: `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py`. This supplies full quality, strict docs, hooks, backlog audit, and fresh wheel/sdist inventory verification; do not run a duplicate full quality gate on the unchanged candidate.
- [ ] **Step 7: Verify a fresh external installed wheel** using the guarded commands below. Preserve failed artifacts with their exact path; successful cleanup follows the hygiene skill's resolved-path checks.

  ```powershell
  $c13ArtifactDir = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-c1-3-" + [guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Path $c13ArtifactDir | Out-Null
  uv build --offline --no-sources --out-dir $c13ArtifactDir
  if ($LASTEXITCODE -ne 0) { throw "C1.3 artifact build failed" }
  $c13Wheel = Join-Path $c13ArtifactDir 'xplane_fdau-0.1.0-py3-none-any.whl'
  $c13Sdist = Join-Path $c13ArtifactDir 'xplane_fdau-0.1.0.tar.gz'
  uv run --offline --frozen twine check --strict $c13Wheel $c13Sdist
  if ($LASTEXITCODE -ne 0) { throw "C1.3 metadata check failed" }
  uv run --offline --frozen python tools/release.py check-dist $c13ArtifactDir
  if ($LASTEXITCODE -ne 0) { throw "C1.3 inventory check failed" }
  Get-FileHash $c13Wheel, $c13Sdist -Algorithm SHA256
  $c13Env = Join-Path $c13ArtifactDir 'installed-3.12'
  uv venv --offline --python 3.12 $c13Env
  if ($LASTEXITCODE -ne 0) { throw "C1.3 smoke environment failed" }
  $c13Python = Join-Path $c13Env 'Scripts/python.exe'
  uv pip install --offline --python $c13Python $c13Wheel
  if ($LASTEXITCODE -ne 0) { throw "C1.3 wheel installation failed" }
  $c13Smoke = (Resolve-Path -LiteralPath 'tools/installed_smoke.py').Path
  Push-Location $c13ArtifactDir
  try {
      & $c13Python $c13Smoke 0.1.0
      if ($LASTEXITCODE -ne 0) { throw "C1.3 installed smoke failed" }
  } finally { Pop-Location }
  ```

- [ ] **Step 8: Record committed review, completion, and gate receipts** with observed commands/results and artifact digests. Transition `implemented`, `reviewed`, and `verified` only when their prerequisites hold; record each gate through guarded dry-run/apply. Commit evidence with the corresponding gate ledger changes; do not claim completion before all four pass. Run focused backlog/live-state and documentation checks after governance edits.
- [ ] **Step 9: Use finishing-a-development-branch** after verification. Local integration requires the user's choice and the repository's exact-fast-forward main checks before removing the worktree/branch. No remote sync or release follows automatically.

## Acceptance trace and planning audit

| Intent-to-scope comparison | Classification | Evidence |
| --- | --- | --- |
| Exact typed values and declarations | Aligned | Source specification lines 422, 538; `BACKLOG.md:157` |
| Strict rejection and property paths | Aligned | Source specification line 1288; `BACKLOG.md:157` |
| Metadata-only payload identity | Aligned | Source specification line 442; `BACKLOG.md:163` |
| Runtime and later-child boundaries | Aligned | Source specification lines 77, 99; `docs/architecture/xplane_fdau_core_scope_amendment.md:230`; `ROADMAP.md:117` |

| Scope-to-plan comparison | Classification | Executable evidence |
| --- | --- | --- |
| Gate 1: exact primitive types/order, byte-only representation | Aligned | This plan lines 68, 108, 129; literal canonical byte vectors |
| Gate 2: coercion/null/shape/enum rejection | Aligned | This plan lines 68–144; exact exception and pointer assertions |
| Gate 3: media type, length, hash, role, retention without storage | Aligned | This plan lines 96, 145; all statuses and I/O mocks |
| Gate 4: construction/loaded property-path equivalence | Aligned | This plan line 129; private parsed nested readers, lexical-token and mixed-invalid tests |
| Public ownership, artifact and installed-import closure | Aligned | This plan lines 129, 145; exact exports, module inventory, offline hygiene and external Python 3.12 smoke |

Self-review/planning audit verdict: PASS for intent/scope/plan alignment, with no drifted or missing scoped requirement. No gap or correction remains after clarifying raw enumeration-code preservation. This is a planning verdict, not an implementation or independent code-review result. Final execution approval is pending. Before approval, verify the draft with backlog audit, a whitespace check including this untracked file, and focused documentation/governance checks. This draft introduces no delivery gate evidence.
