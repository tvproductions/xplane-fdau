# C1.2 Identity, Hashing, References, Authority, and Provenance Implementation Plan

- **Governance:** active
- **Status:** completed
- **Date:** 2026-10-04
- **Roadmap child:** `C1.2`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** 2026-10-04 — Jeff / tvproductions
- **Completion evidence:** `.superpowers/sdd/2026-10-04-c1-2-identity-hashing-references-provenance/completion.md`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Deliver the shared C1.2 identity, reference, authority, provenance, and self-hash primitives that later canonical families consume.

**Architecture:** Private validators enforce exact wire domains and RFC 6901 paths. Public frozen values in `contracts.identity` and `contracts.provenance` own semantic fields and defensive copies; private wire helpers preserve their exact field order and optional-property absence. Private hashing helpers build the two specified preimages using C1.1's canonical document encoder. Family models, loaders, the model-only reference factories, and the model-only public `compute_content_hash` dispatch are introduced by their later children, when eligible model types exist.

**Tech Stack:** Python 3.12 standard library at runtime; `unittest`, Ruff, ty, uv, repository offline hygiene, and Python 3.12 installed-wheel smoke.

**Spec:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`, especially “Contract families and versions,” “Shared identity and provenance,” “Canonical JSON and content hashing,” “Shared values and payload references,” “Public API and errors,” and the C1.2 acceptance criteria. `docs/architecture/xplane_fdau_core_scope_amendment.md` governs current Python compatibility.

## Global Constraints

- Implement only `C1.2` and its four `BACKLOG.md` gates. Do not create catalog/record models, family loaders, schemas, a conformance corpus, algorithm execution, or a dynamic model registry.
- The source specification's final `identity.__all__` adds `definition_ref` and `record_ref` when their eligible models arrive in C2/C3. C1.2 exports the three usable reference values; it does not publish factories that reject every possible current input.
- Preserve C1.1 canonical bytes, its lexical integer/real distinction, and its parser/error precedence. A loaded family checks version and shape before canonical-domain validation when its loader arrives in a later child.
- Public structural models are frozen, slotted, keyword-only dataclasses with required then optional constructor properties in semantic order. Optional properties are omitted on the wire; `null` is never a substitute.
- Semantic `Identifier` uses `[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+`, at most 255 ASCII characters. `Revision` is `1..2^63-1`; generation and sequence are `0..2^63-1`; `Sha256` is 64 lowercase hex characters. Signed-64-bit overflow is a canonical-domain error; in-domain revision `0` and counter `-1` are semantic errors. Constructors check all shapes, then canonical domains, then semantics in the specification's field order.
- `Uuid` uses the exact lowercase RFC 9562 grammar in the source spec, with version `1..8` and variant `8`, `9`, `a`, or `b`; the kernel validates but never generates identities.
- `VersionText` is NFC text of 1..128 code points with no `Cc` or `Cf` character. Provenance `scope` is `NfcText(1024)` and optional `locator` is `NfcText(2048)`.
- Hashes are SHA-256 of the C1.1 canonical UTF-8 bytes, including the final LF. Record preimages omit only root `content_hash`; definition preimages wrap the entry in `contract_family`, integer `schema_version: 1`, and `definition`, omitting only the entry's `content_hash`. Nested hashes remain included.
- Runtime imports remain standard-library and package-local only. Preserve `xplane_fdau.__all__ == ["__version__"]` and the native FDR boundary. Use `unittest` only.
- During edits use focused `unittest`, Ruff, and ty. Runtime package additions require one full offline hygiene gate at stable closeout and a Python 3.12 external installed-wheel smoke. No redundant full gate on an unchanged candidate.
- A RED must be a behavior-specific `unittest` assertion failure. Establish a new import surface first if needed; an import error or missing symbol alone is not RED evidence.
- No Git sync, push, tag, package publication, GitHub release, or external-client edit is authorized by this plan.

## Review Focus

1. Python `bool` passed as a revision, generation, sequence, or schema version must fail at the correct property path; Task 1 tests each domain.
2. Uppercase, nil/max, invalid-version, or invalid-variant UUID text must fail without normalization; Task 1 tests each form.
3. Caller mutation of an algorithm parameter nested object or array after construction must not change its stored value or reference equality; Task 2 tests this.
4. A nested `content_hash` must remain in a parent preimage while only the parent's own hash is omitted; Task 3 tests byte-exact preimages and literal digests.
5. A provenance source with both revision and version, neither, or a duplicate identity in an ordered catalog provenance tuple must fail with an indexed JSON Pointer; Task 4 tests these.

## File map

| Responsibility | Exact files |
| --- | --- |
| Private scalar validation and wire-property/path helpers | Create `src/xplane_fdau/contracts/_identity_validation.py`; test in `tests/test_contract_identity.py` |
| Definition/record/algorithm references and private wire conversion | Create `src/xplane_fdau/contracts/identity.py`; test in `tests/test_contract_identity.py` |
| Record and definition canonical preimages and digests | Create `src/xplane_fdau/contracts/_content_hash.py`; reuse C1.1's private document encoder; test in `tests/test_contract_content_hash.py` |
| Authority and source/producer/provider/adapter provenance values | Create `src/xplane_fdau/contracts/provenance.py`; test in `tests/test_contract_provenance.py` |
| Public package surface and installed import proof | Modify `src/xplane_fdau/contracts/__init__.py`, `tests/test_public_api.py`, `tests/test_installed_smoke.py`, and `tools/installed_smoke.py` |
| Review and delivery evidence after execution | Update this plan and `BACKLOG.md` through the guarded backlog adapter; add `.superpowers/sdd/2026-10-04-c1-2-identity-hashing-references-provenance/` receipts |

The existing distribution inventory discovers modules beneath `src/xplane_fdau`; change `tools/release.py` only if a focused test proves an inventory assumption wrong. This child adds no schema or fixture resource.

## Execution entry — after plan review and approval

Jeff approved this plan on 2026-10-04. Before Task 1, recheck `HANDOFF.md`, `ROADMAP.md`, `BACKLOG.md`, the governing design, backlog `audit`/`next`, Git branch, HEAD, and clean status. Use `superpowers:using-git-worktrees` for a temporary C1.2 feature worktree from the verified baseline, then link this approved plan from C1.2 and apply `select`, `planned`, and `in_progress` through the backlog adapter's dry-run and target-hash workflow. Audit after each change. Commit the approved plan and lifecycle state before code. The plan does not authorize a remote sync.

---

### Task 1: Exact identity domains

**Files:** Create `src/xplane_fdau/contracts/_identity_validation.py` and `tests/test_contract_identity.py`; modify `tests/test_installed_smoke.py`'s exact module inventory.

**Interfaces:** Produce private `_identifier(value: object, *, path: str) -> str`, `_revision(value: object, *, path: str) -> int`, `_counter(value: object, *, path: str) -> int`, `_uuid(value: object, *, path: str) -> str`, `_sha256(value: object, *, path: str) -> str`, `_version_text(value: object, *, path: str) -> str`, and `_nfc_text(value: object, *, path: str, maximum: int) -> str`. Wrong Python/JSON type raises `ContractShapeError`; canonical-domain text violations and signed-64-bit integer overflow raise `CanonicalJSONError`; in-domain syntax/range violations raise `ContractValidationError`. All errors carry the supplied RFC 6901 path.

- [x] **Step 1: Write failing `unittest` assertions** for accepted dotted IDs at length 255, revision `1` and `2^63-1`, counters `0` and `2^63-1`, a canonical v1/v8 UUID, and lowercase SHA-256. Reject one-segment/uppercase/non-ASCII/length-256 IDs; revision `0`/overflow; counter negative/overflow; `bool` for every integer domain; UUID uppercase/nil/max/version-0/version-9/bad variant; uppercase/short SHA-256; empty, non-NFC, surrogate, `Cc`, and `Cf` version text. Assert each exception class and exact property path, including a path with `~` and `/`. Add the private module to the installed exact-module test.
- [x] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_identity tests.test_installed_smoke -v`. Establish the import surface, then observe the domain assertions fail before implementing validation.
- [x] **Step 3: Implement the seven validators** with exact `type(value)` checks before integer bounds, compiled full-match ASCII patterns, Unicode NFC/scalar checks, and no ID/UUID normalization or generation. Use the C1.1 pointer convention for nested callers; do not add public aliases or type wrappers.
- [x] **Step 4: Verify GREEN** with the Task 1 `unittest` command, `uv run --offline --frozen ruff check src/xplane_fdau/contracts tests/test_contract_identity.py tests/test_installed_smoke.py`, `uv run --offline --frozen ruff format --check src/xplane_fdau/contracts tests/test_contract_identity.py tests/test_installed_smoke.py`, and `uv run --offline --frozen ty check`.
- [x] **Step 5: Review and commit Task 1 files** with `feat: validate canonical identities`.

### Task 2: Immutable pinned references

**Files:** Create `src/xplane_fdau/contracts/identity.py`; modify `src/xplane_fdau/contracts/__init__.py`, `tests/test_contract_identity.py`, `tests/test_public_api.py`, and `tests/test_installed_smoke.py`.

**Interfaces:** Produce public keyword-only `DefinitionRef(definition_id: str, definition_revision: int, definition_hash: str)`, `RecordRef(record_id: str, contract_family: str, schema_version: int, content_hash: str)`, and `AlgorithmRef(definition_id: str, definition_revision: int, definition_hash: str, parameters: Mapping[str, object])`. Produce private `_definition_ref_wire`, `_record_ref_wire`, and `_algorithm_ref_wire` converters returning exact-property plain dictionaries for later family IO. The later model-owning children add `definition_ref(value)` and `record_ref(value)` with the spec's exact accepted model unions, copying identity and hash without caller override.

- [x] **Step 1: Write failing `unittest` assertions** for exact constructor fields, frozen/slotted/keyword-only behavior, reference equality, all five allowed RecordRef family URIs with version integer `1`, rejection of unknown family/version/invalid hash at their exact paths, and AlgorithmRef parameters accepted in the C1.1 data-only object domain. Verify nested parameter dictionaries/lists are defensively copied and exposed through read-only mappings/tuples while wire conversion retains object/array shape and order. Reject parameter `null`, bytes, invalid Identifier keys, depth 33, and `bool` as schema version. Assert `identity.__all__` is exactly the three reference classes at C1.2, without the later model-only factories; assert package exports and module inventory.
- [x] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_identity tests.test_public_api tests.test_installed_smoke -v`, observing behavior assertions after the import surface exists.
- [x] **Step 3: Implement the three reference models and private wire conversion.** Validate each property with Task 1 helpers. Copy algorithm parameters recursively into immutable mappings/tuples and convert back to plain objects for canonical bytes; do not resolve or execute algorithms. Export exactly `DefinitionRef`, `RecordRef`, and `AlgorithmRef` from `identity` for this child. Keep the root `xplane_fdau` namespace unchanged.
- [x] **Step 4: Verify GREEN** with the Task 2 `unittest` command, focused Ruff check/format, and `uv run --offline --frozen ty check`.
- [x] **Step 5: Review and commit Task 2 files** with `feat: pin canonical references`.

### Task 3: Exact self-hash preimages

**Files:** Create `src/xplane_fdau/contracts/_content_hash.py` and `tests/test_contract_content_hash.py`; modify `tests/test_installed_smoke.py`.

**Interfaces:** Produce private `_record_content_hash(document: dict[str, object]) -> str` and `_definition_content_hash(contract_family: str, definition: dict[str, object]) -> str` for already validated family-shaped trees. Both use `_encode_document` and return lowercase SHA-256. Also produce private `_record_preimage` and `_definition_preimage` returning the exact bytes so later model integration can assert its preimage. The definition helper accepts only the measurement-catalog or source-binding-catalog family URI. No family model or arbitrary public mapping hash API is introduced. Once C2/C3 add the exact eligible model classes, their computed properties and the spec's model-only public `compute_content_hash` use these helpers.

- [x] **Step 1: Write failing byte-exact `unittest` assertions** for a record preimage that omits only root `content_hash` and retains a nested `content_hash`; a definition preimage with literal family URI, integer `schema_version: 1`, and `definition` entry lacking only its own `content_hash`; changed ID, revision, authority, provenance, body, nested hash, or array order changing the digest; and reordered input object properties producing the same digest. Pin literal SHA-256 values computed independently from the asserted byte literals, including the final LF. Assert the same digest when the input has no self-hash property (programmatic model) or has one (loaded wire instance). Reject a malformed self-hash when supplied and unsupported family URI for a definition; assert neither helper mutates its input dictionary.
- [x] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_content_hash tests.test_canonical_json tests.test_installed_smoke -v`, observing a preimage/ digest assertion fail after the private import surface exists.
- [x] **Step 3: Implement the four private helpers** using C1.1 `_encode_document`, `hashlib.sha256`, and shallow root/entry copies so nested hashes remain present. Permit an absent self-hash for programmatic objects, validate its syntax when present, reject unknown definition family, avoid caller-data mutation, and leave `canonical_bytes`' public parameter-object restriction intact. Future family loaders, rather than these preimage helpers, require and compare the declared wire hash. Do not make `compute_content_hash` accept dictionaries or publish a placeholder that claims model support before the models exist.
- [x] **Step 4: Verify GREEN** with the Task 3 `unittest` command, focused Ruff check/format, and `uv run --offline --frozen ty check`.
- [x] **Step 5: Review and commit Task 3 files** with `feat: hash canonical contract preimages`.

### Task 4: Immutable authority and provenance

**Files:** Create `src/xplane_fdau/contracts/provenance.py` and `tests/test_contract_provenance.py`; modify `src/xplane_fdau/contracts/__init__.py`, `tests/test_public_api.py`, and `tests/test_installed_smoke.py`.

**Interfaces:** Produce public keyword-only `Authority`, `ProvenanceSource`, `ProducerIdentity`, `ProviderIdentity`, and `AdapterIdentity` with exactly the required/optional properties in the design. Produce private per-type wire converters and a private `_catalog_provenance(value: tuple[ProvenanceSource, ...], *, path: str) -> tuple[ProvenanceSource, ...]` for later catalog models; it preserves declared order and rejects empty, more than 256, or duplicate `(source_id, source_revision or source_version)` identities.

- [x] **Step 1: Write failing `unittest` assertions** for each model's exact fields, frozen/slotted/keyword-only behavior, round-trip through its private plain-object converter/constructor path with optional fields omitted, independent `locator`/`sha256` optionality, `source_revision` XOR `source_version`, and source revision's `VersionText` type for producers. Assert nonempty ordered catalog provenance and rejection of empty/257-entry arrays; reject repeated `(source_id, source_revision)` and `(source_id, source_version)` pairs at indexed pointers while allowing distinct revision/version identities. Cover non-NFC/oversized scope and locator, invalid authority revision, and forbidden `Cc`/`Cf` version text. Assert exact `provenance.__all__` and package/module inventories.
- [x] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_provenance tests.test_public_api tests.test_installed_smoke -v`, observing field or round-trip assertions fail after the import surface exists.
- [x] **Step 3: Implement the five models and private wire helpers** with Task 1 validators and exact semantic field order. Do not add generated timestamps, provider objects to producer identity, or licensed text to a public contract. Defensively copy provenance sequences to tuples in `_catalog_provenance` and report the first duplicate in declared order.
- [x] **Step 4: Verify GREEN** with the Task 4 `unittest` command, focused Ruff check/format, and `uv run --offline --frozen ty check`.
- [x] **Step 5: Review and commit Task 4 files** with `feat: preserve canonical provenance`.

### Task 5: C1.2 integration, review, and four-gate evidence

**Files:** Modify `tools/installed_smoke.py` and `tests/test_installed_smoke.py`; extend `tests/test_contract_identity.py`, `tests/test_contract_content_hash.py`, `tests/test_contract_provenance.py`, `tests/test_public_api.py`, and `tests/test_runtime_import_boundary.py` as needed for integration; after verification update this plan, `BACKLOG.md`, and `.superpowers/sdd/2026-10-04-c1-2-identity-hashing-references-provenance/`.

**Interfaces:** Installed smoke constructs a `DefinitionRef`, a `ProvenanceSource`, and a deterministic record/definition preimage, asserting expected installed behavior outside the checkout. The public contracts package exposes the C1.1 exports plus the exact C1.2 identity and provenance exports, with no added root namespace exports.

- [x] **Step 1: Write failing integration `unittest` assertions** for public exports, nested reference/provenance wire values surviving round-trip without coercion, deterministic literal preimage/digest values, stable values after caller mutation, installed smoke fault injection for a wrong reference/hash result, exact wheel module inventory, and a clean standard-library-only import graph. Verify that later C1.3/C2/C3/C4 API names and resources are absent.
- [x] **Step 2: Verify RED** with `uv run --offline --frozen python -m unittest tests.test_contract_identity tests.test_contract_content_hash tests.test_contract_provenance tests.test_public_api tests.test_installed_smoke tests.test_runtime_import_boundary -v`; the smoke fault injection must fail its assertion before changing the smoke implementation.
- [x] **Step 3: Add the minimal installed-smoke checks** and fix only evidenced integration defects. Do not add a generic serializer, family loader, model shell, schema, fixture corpus, or static stock catalog.
- [x] **Step 4: Verify focused GREEN** with the Step 2 `unittest` command, Ruff check/format for changed files, and `uv run --offline --frozen ty check`.
- [x] **Step 5: Request independent code review** of the C1.2 diff against its four backlog gates, the preimage bytes, public export boundary, construction/loaded path parity that can be proved without family loaders, and runtime/import constraints. Resolve load-bearing findings with focused tests.
- [x] **Step 6: Run one complete stable-candidate gate** using `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` on Python 3.12. This supplies the complete quality gate, strict docs, hooks, backlog audit, and a fresh exact wheel/sdist pair; do not repeat `tools/quality.py check` on the unchanged candidate.
- [x] **Step 7: Build a fresh external wheel/sdist pair and run installed smoke** on Python 3.12 outside the checkout. Run the following Windows commands from the feature worktree (use `bin/python` on POSIX). Record both artifact hashes and preserve failed artifacts for diagnosis.

```powershell
$repo = (Get-Location).Path
$version = (uv version --short).Trim()
if ($LASTEXITCODE -ne 0 -or -not $version) { throw "Cannot determine project version" }
$artifactDir = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-c1-2-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $artifactDir | Out-Null
uv build --offline --no-sources --out-dir $artifactDir
if ($LASTEXITCODE -ne 0) { throw "Artifact build failed" }
$wheel = Join-Path $artifactDir "xplane_fdau-$version-py3-none-any.whl"
$sdist = Join-Path $artifactDir "xplane_fdau-$version.tar.gz"
uv run --offline --frozen twine check --strict $wheel $sdist
if ($LASTEXITCODE -ne 0) { throw "Artifact metadata check failed" }
uv run --offline --frozen python tools/release.py check-dist $artifactDir
if ($LASTEXITCODE -ne 0) { throw "Artifact inventory check failed" }
Get-FileHash $wheel, $sdist -Algorithm SHA256
$venv = Join-Path $artifactDir "installed-3.12"
uv venv $venv --python 3.12
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 environment creation failed" }
$interpreter = Join-Path $venv "Scripts/python.exe"
uv pip install --python $interpreter $wheel
if ($LASTEXITCODE -ne 0) { throw "Wheel installation failed" }
Push-Location $artifactDir
try {
    & $interpreter (Join-Path $repo "tools/installed_smoke.py") $version
    if ($LASTEXITCODE -ne 0) { throw "Installed-wheel smoke failed" }
} finally { Pop-Location }
```
- [ ] **Step 8: Record accepted review and all four gates** using the backlog adapter's dry-run then hash-guarded apply. Receipts must separately prove exact ID/revision/UUID/counter validation; record/definition canonical preimages and SHA-256; pinned definition/record references; and immutable authority/provenance/producer round-trip. Advance C1.2 to `verified` only when all four receipts and independent review pass. Keep G1 waiting.
- [ ] **Step 9: Commit the verified C1.2 evidence and present local integration options.** Do not merge, push, tag, publish, or release without the separately required user decision and checks.
