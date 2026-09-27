# C1.1 Canonical JSON and Number Encoding Implementation Plan

- **Governance:** active
- **Status:** completed
- **Date:** 2026-09-27
- **Roadmap child:** `C1.1`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** 2026-09-27 — Jeff / tvproductions
- **Completion evidence:** `.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/completion.md`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the C1.1 canonical JSON parser and byte encoder, including exact signed-64-bit and IEEE-754 binary64 lexical behavior, without implementing later contract families.

**Architecture:** `contracts` owns contextual errors, a strict private JSON decoder, a private binary64-to-ECMAScript token formatter, and the public `canonical_bytes` entry point. The decoder completes syntax and duplicate detection while preserving lexical number tokens; canonical-domain conversion and validation occur only after that stage, and future family loaders first check their version and shape. The encoder validates the permitted data-only domain and emits UTF-8 plus one LF. Later family implementations can call the private document encoder with validated model-shaped trees and add model dispatch and self-hash preimages without changing the C1.1 byte profile.

**Tech Stack:** Python 3.12 standard library only at runtime; `unittest`, Ruff, ty, uv, repository offline hygiene, and external installed-wheel smoke for verification.

**Spec:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`, especially “Contract families and versions,” “Canonical JSON and content hashing,” “Public API and errors,” and C1.1 acceptance criteria. `docs/architecture/xplane_fdau_core_scope_amendment.md` controls the current Python 3.12-only policy where the older cross-epic text differs.

## Global Constraints

- Implement only `C1.1` and its four `BACKLOG.md` gates. Do not construct identity/reference models (`C1.2`), other contract models, family loaders, schemas, or the C4.2 corpus.
- Preserve `xplane_fdau.__all__ == ["__version__"]`, native FDR behavior, empty runtime dependencies, and the transport-free X-Plane core boundary.
- Public C1.1 entry point: `canonical_bytes(value: object) -> bytes` under `xplane_fdau.contracts.canonical_json`. The final spec's model-specific `compute_content_hash` belongs to C1.2 and later; do not publish a placeholder.
- Runtime imports use only the Python standard library and package-local modules. No XPPython3, XPLM, xpwebapi, network client, callable registry, plugin loader, or dynamic import.
- Canonical output is UTF-8 without BOM, no insignificant whitespace, exactly one final LF, recursive Unicode-scalar key ordering, preserved array order, NFC strings, exact escaping, `Int64`, and finite `Binary64` with the specified real/integer lexical distinction.
- The public data-only parameter root is an object, possibly empty, with Identifier keys and Boolean/Int64/Binary64/NfcText(16384)/array/object values, no `null` or bytes, and depth at most 32. Scalar and array roots are rejected. The private document path supports future validated family objects to depth 64 and 65535 members per container.
- Parsing completes UTF-8, syntax, and duplicate-key checks before any canonical-domain error. Future family loaders check the family/version envelope and shape before surfacing preserved numeric, Unicode, or other canonical-domain errors.
- The RFC 8785 §3.2.2.3 and Appendix B number vectors are normative for binary64 only; the project deliberately differs from full JCS in key ordering, NFC, integer/real distinction, and final LF.
- Use test-first `unittest` for each task, then focused Ruff/ty checks. New runtime package members require one full offline hygiene run at stable closeout; do not repeat its complete quality gate on the unchanged candidate.
- A RED is a behavior-specific `unittest` assertion failure, not an import error, missing symbol exception, or empty import-only test. For a new module, first assert its required importable surface, add only that surface, then require the behavior assertion to fail before implementing behavior; repeat the red/green cycle for each independent behavior.
- Python 3.12 is the sole supported minor version. Perform one external installed-wheel smoke on 3.12, not a 3.12–3.14 matrix.
- No Git sync, push, tag, package publication, GitHub release, or q4xpcc edit is authorized by this plan.

## Review Focus

1. Escaped spellings of the same JSON property (`"a"` and `"\\u0061"`) must fail as a duplicate at `/a`, including when nested and when an earlier value is numerically out of range; Task 1 tests these.
2. A real token that is nonzero but rounds to zero, and one that overflows to infinity, must fail as `CanonicalJSONError`, not silently become zero/infinity; Task 1 tests both.
3. A valid escaped surrogate pair must become one Unicode scalar, while a lone surrogate and decomposed NFC text must fail with their JSON Pointer paths; Task 2 tests each.
4. Depth 32/33 for public parameters and 64/65 for private documents, plus 65535/65536 container members, must have checked boundaries rather than a Python recursion or memory failure; Task 2 tests the boundary pairs.
5. The decimal tie/threshold cases where Python's ordinary JSON spelling differs from ECMAScript must match the RFC bit-pattern vectors, including `1e-6`, `1e-7`, `1e20`, `1e21`, and round-to-even; Task 3 tests them.

## File map

| Responsibility | Exact files |
| --- | --- |
| Contextual public error hierarchy and importable package surface | Create `src/xplane_fdau/contracts/__init__.py` and `src/xplane_fdau/contracts/errors.py`; test in `tests/test_contract_json_parse.py` |
| Strict decoding, token provenance, duplicate detection | Create `src/xplane_fdau/contracts/_json_parse.py`; test in `tests/test_contract_json_parse.py` |
| Canonical tree validation, string/container/integer bytes, public entry point | Create `src/xplane_fdau/contracts/canonical_json.py` and extend `src/xplane_fdau/contracts/__init__.py`; test in `tests/test_canonical_json.py` |
| ECMAScript binary64 formatter | Create `src/xplane_fdau/contracts/_binary64.py` and non-packaged frozen oracle `tests/data/c1_1_binary64_oracle.tsv`; test in `tests/test_contract_binary64.py` |
| Installed import/byte check | Update `tests/test_installed_smoke.py`'s exact module inventory in Tasks 1–3 as each module lands; modify `tools/installed_smoke.py` and add a behavior test in Task 4 |
| Lifecycle, review, evidence | This plan, `BACKLOG.md` through its guarded lifecycle commands after approval, and `.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/` during execution |

The existing `tools/release.py` inventories package files from `src/xplane_fdau` and should recognize the new modules without an allowlist edit. Do not change release tooling unless a focused failing test proves otherwise. No schema or fixture resource is added in C1.1; C4.1/C4.2 own those deliverables.

## Execution entry — after plan review and approval

Keep this plan `draft`, `Approval: —`, and C1.1 `specified` until Jeff reviews it. At execution, first inspect `git status --short`, branch, and HEAD. The dependency/Python-3.12 maintenance and this draft plan were committed before the 2026-09-27 handoff; do not assume that handoff HEAD is still current. If the checkout has changed or is dirty, resolve the actual baseline without stashing, resetting, or discarding unrelated work. Once Jeff has approved this plan and the intended `main` baseline is clean, record its HEAD and use `superpowers:using-git-worktrees` to create the C1.1 feature worktree from that exact commit. This plan does not authorize a remote sync.

In the feature worktree, set this plan to `approved` with the actual approval date, link it as `[plan]` from C1.1, and use the backlog adapter's dry-run-then-`--target-sha256 ... --apply` workflow for `select C1.1 --expect-current none`, `transition C1.1 planned --expect specified`, and then `transition C1.1 in_progress --expect planned`. Audit after each change. Commit the approved plan/lifecycle state before code.

The review draft may be linked as `[draft plan]` while C1.1 remains `specified`; no link or file presence itself satisfies a gate. Do not start Task 1 before approval and a passing isolated baseline.

---

### Task 1: Contextual errors and strict lexical JSON decode

**Files:** Create `src/xplane_fdau/contracts/__init__.py`, `src/xplane_fdau/contracts/errors.py`, `src/xplane_fdau/contracts/_json_parse.py`, and `tests/test_contract_json_parse.py`; modify `tests/test_installed_smoke.py`.

**Interfaces:** Produces `_parse_json_document(data: str | bytes, *, source: str = "<memory>") -> object` for Tasks 2–4. Its returned tree retains private `_NumberToken(text: str, is_real: bool)` leaves; parsing itself reports only UTF-8/BOM, syntax, non-JSON constants, and duplicate-property errors. Produces `_materialize_number(token: _NumberToken, *, source: str = "<memory>", path: str = "") -> int | float` for deferred canonical-domain validation. Produces `FDAUContractError` with read-only `source`, `line`, `column`, `path`, `contract_family`, and `identity` context, plus the six exact subclasses named by the spec. Do not expose these helpers in `__all__`; later family loaders own public load/loads names.

- [ ] **Step 1: Write failing `unittest` methods** in `tests/test_contract_json_parse.py` for `b'{"a":1,"\\u0061":2}'` raising `ContractParseError` at `/a`, a nested duplicate key using `~` and `/` pointer escapes, and `b'{"a":9223372036854775808,"a":0}'` still raising `ContractParseError` rather than early numeric overflow. Cover malformed UTF-8/BOM/syntax with `source="sample.json"` and one-based syntax line/column. Assert the parser preserves distinct `_NumberToken` values for `1`, `1.0`, `1e0`, and `-0` without rejecting overflow; separately assert `_materialize_number` accepts integer `-0` and raises `CanonicalJSONError` at the supplied path for out-of-range integers and `1e999`/`1e-999`. Update `tests/test_installed_smoke.py`'s exact expected module set with `xplane_fdau.contracts`, `xplane_fdau.contracts.errors`, and `xplane_fdau.contracts._json_parse` before creating those modules. Assert exception classes and context fields, not message fragments or echoed payloads.
- [ ] **Step 2: Verify RED.** Run `uv run --offline --frozen python -m unittest tests.test_contract_json_parse tests.test_installed_smoke -v`. First establish an import-surface or exact-module-set assertion failure and add only the minimal package/module/function shells it requires; then rerun each behavior test and observe its specific assertion fail before writing that behavior. Import errors and missing-symbol exceptions do not count as RED evidence.
- [ ] **Step 3: Implement the minimal decoder and errors.** Create the importable `contracts.__init__` with the seven error exports only; Task 2 adds `canonical_bytes`. Use `json.loads` only for syntax/tokenization, with `parse_int`/`parse_float` callbacks returning lexical `_NumberToken` leaves and an object-pairs wrapper. Decode UTF-8 strictly and reject BOM. Traverse the complete pair-wrapper tree for duplicates before any number conversion or NFC/surrogate validation, preserving JSON Pointer paths. In the separate `_materialize_number` helper, range-check integer digit sequences before host conversion so tokens beyond Python's decimal-digit guard get the correct typed overflow error; correctly round real tokens to binary64 and reject overflow or nonzero underflow. Translate malformed JSON and nonfinite JSON constants to `ContractParseError`; do not use `json.loads` to choose serialized float spellings. Catch recursion/size failures into typed contract errors. Keep error messages bounded and avoid raw payload echo. Future family loaders must perform version and shape tiers before calling canonical-domain validation.
- [ ] **Step 4: Verify GREEN and focused static checks.** Run the Task 1 `unittest` command, `uv run --offline --frozen ruff check src/xplane_fdau/contracts tests/test_contract_json_parse.py tests/test_installed_smoke.py`, `uv run --offline --frozen ruff format --check src/xplane_fdau/contracts tests/test_contract_json_parse.py tests/test_installed_smoke.py`, and `uv run --offline --frozen ty check`. Expected: all exit 0.
- [ ] **Step 5: Review the Task 1 diff and commit only its files** with `git add src/xplane_fdau/contracts/__init__.py src/xplane_fdau/contracts/errors.py src/xplane_fdau/contracts/_json_parse.py tests/test_contract_json_parse.py tests/test_installed_smoke.py` and a scoped `feat: decode canonical JSON strictly` commit. No commit while a red test remains.

### Task 2: Canonical Unicode, containers, integers, and parameter-domain entry point

**Files:** Create `src/xplane_fdau/contracts/canonical_json.py` and `tests/test_canonical_json.py`; modify `src/xplane_fdau/contracts/__init__.py` and `tests/test_installed_smoke.py`; extend `tests/test_contract_json_parse.py` for text validation.

**Interfaces:** Consumes Task 1 `_parse_json_document`, `_NumberToken`, `_materialize_number`, and error types. Produces `canonical_bytes(value: object) -> bytes` (public, object-rooted data-only parameter domain for now) and private `_encode_document(value: object) -> bytes` for parsed or validated future family-shaped trees. `_encode_document` materializes preserved number tokens and permits arbitrary NFC string object keys and the document limits; `canonical_bytes` additionally requires an object root and enforces Identifier keys, NfcText(16384), no `null`/bytes, and parameter depth 32.

- [ ] **Step 1: Write failing `unittest` methods** asserting exact private-document bytes for nested scalar-value key order (U+E000 before U+1F600, unlike UTF-16 order), preserved array order, UTF-8 non-ASCII, short escapes for `\b\t\n\f\r`, lowercase `\u000f`, escaped quote/backslash, unescaped solidus, one final LF, `-9223372036854775808` and `9223372036854775807`, Boolean literals distinct from numbers, and parsed `-0` emitting `0`. Assert public `canonical_bytes({}) == b"{}\n"` and that public scalar/array roots raise `CanonicalJSONError` at the root. Assert `CanonicalJSONError.path` for decomposed NFC text, lone surrogate, non-string object key, `null`, bytes, Int64 overflow, and an invalid parameter Identifier. Assert escaped surrogate-pair input is accepted as one scalar. Update the exact module-set test to include `xplane_fdau.contracts.canonical_json` before creating that module. Include Review Focus depth 32/33 and 64/65 and member-count 65535/65536 boundary tests without allocating an unbounded fixture.
- [ ] **Step 2: Verify RED.** Run `uv run --offline --frozen python -m unittest tests.test_canonical_json tests.test_contract_json_parse tests.test_installed_smoke -v`. Establish the new module/API with an import-surface or exact-module-set assertion if needed, then require a specific canonical-byte or rejection assertion to fail before implementing each behavior. Import errors and missing-symbol exceptions are setup failures, not RED evidence.
- [ ] **Step 3: Implement canonical tree validation and bytes.** Materialize preserved number tokens and validate NFC/surrogates in the encoder stage, after complete syntax and duplicate checks; future family loaders call this stage only after version and shape validation. Encode strings by Unicode scalar with exact project escapes. Sort raw unescaped keys by Unicode code-point sequence at every object; preserve arrays. Serialize Boolean before Int64 checks, use base-10 integer text, reject unsupported objects, and append LF exactly once at the document boundary. Require an object root and validate parameter depth/Identifier/text limits at the public entry; validate document depth/member limits in the private entry. In `contracts.__init__`, export only the C1.1 error classes and `canonical_bytes`; leave `compute_content_hash` and later model exports for their owning children.
- [ ] **Step 4: Verify GREEN and focused static checks.** Run the Task 2 `unittest` command, Ruff check/format for the changed files, and `uv run --offline --frozen ty check`. Expected: all exit 0.
- [ ] **Step 5: Review the Task 2 diff and commit only its files** with a scoped `feat: encode canonical JSON bytes` commit.

### Task 3: Bit-exact ECMAScript binary64 tokens

**Files:** Create `src/xplane_fdau/contracts/_binary64.py`, `tests/test_contract_binary64.py`, and non-packaged `tests/data/c1_1_binary64_oracle.tsv`; modify `src/xplane_fdau/contracts/canonical_json.py`, `tests/test_canonical_json.py`, and `tests/test_installed_smoke.py`.

**Interfaces:** Produces private `_ecmascript_number_token(value: float) -> str`, consumed by Task 2's encoder. The formatter returns the RFC 8785 / ECMAScript token before C1.1's integral-real adaptation; the encoder maps real negative zero to `0.0` and adds `.0` only if the token lacks both `.` and `e`.

- [ ] **Step 1: Write failing literal and independent-oracle tests.** Convert every finite RFC 8785 Appendix B hexadecimal bit pattern with `struct.unpack` into a float and assert its listed ECMAScript token; include explicit C1.1 byte assertions for `1.0 -> b"1.0\n"`, `-0.0 -> b"0.0\n"`, `1e-6 -> b"0.000001\n"`, `1e-7 -> b"1e-7\n"`, `1e20 -> b"100000000000000000000.0\n"`, `1e21 -> b"1e+21\n"`, minimum positive subnormal `5e-324`, maximum finite `1.7976931348623157e+308`, and the Appendix B round-to-even bit pattern `43143ff3c1cb0959 -> 1424953923781206.2`. Freeze at least 4096 unique finite bit-pattern/token pairs in `tests/data/c1_1_binary64_oracle.tsv`: start with 2048 unique finite `random.Random(0xC11).getrandbits(64)` values, then for every finite exponent field `0..2046` add a value with sign `exponent % 2` and a fresh 52-bit fraction from the same RNG; skip duplicates and draw more seeded finite values until the count reaches 4096. Obtain expected tokens from an independent ECMAScript `JSON.stringify(Number)` engine using the exact bits. Put the sampling recipe and engine/version in the fixture header; record the completed fixture's SHA-256 in Task 3 review evidence, outside the hashed file. The `unittest` suite reads the frozen file offline; it never invokes Node/JavaScript or the implementation to calculate expected tokens. Add targeted finite-adjacent and boundary cases. For each of `float("nan")`, `float("inf")`, and `-float("inf")`, assert that `canonical_bytes({"test.x": {"value": number}})` raises `CanonicalJSONError` with `path == "/test.x/value"`; also assert the private formatter rejects each nonfinite value. Expectations must be independent of Python `repr` or `json.dumps`.

  Oracle rows are `16-lowercase-hex-bits<TAB>expected-token<LF>` after `#` provenance comments. The test rejects malformed, duplicate, nonfinite, or fewer than 4096 data rows. It also extracts each row's 11-bit exponent field from the hexadecimal binary64 bits and asserts that every finite exponent field `0..2046` occurs at least once; a 4096-row fixture concentrated in a narrow exponent range must fail. One-time fixture generation may use local Node/V8, but no JavaScript tool is required by CI or the installed package.
- [ ] **Step 2: Verify RED.** Add `xplane_fdau.contracts._binary64` to the exact module-set test, then run `uv run --offline --frozen python -m unittest tests.test_contract_binary64 tests.test_canonical_json tests.test_installed_smoke -v`. Establish the private formatter symbol with an import-surface or exact-module-set assertion if needed, then require literal RFC and frozen-oracle token assertions to fail before implementing formatting. Import errors and missing-symbol exceptions do not count as RED evidence.
- [ ] **Step 3: Implement the formatter without a runtime dependency.** Use the exact binary64 bit pattern and integer/rational interval arithmetic to select the shortest round-tripping decimal with ECMAScript's tie choice, then apply its plain/exponent thresholds and sign rules. Do not delegate output spelling to `json.dumps`, a host locale, or an external executable. The formatter rejects nonfinite values; the encoder performs the spec's integral-real and negative-zero adaptation. Use RFC 8785 §3.2.2.3 and Appendix B as the frozen numeric authority, not full JCS key sorting.
- [ ] **Step 4: Verify GREEN and focused static checks.** Run the Task 3 `unittest` command against every frozen oracle row plus the RFC and project-specific vectors, Ruff check/format, and `uv run --offline --frozen ty check`. Expected: all exit 0 with no skipped oracle rows or JavaScript dependency in the test gate. Record the oracle source and fixture hash for review.
- [ ] **Step 5: Review the Task 3 diff and commit only its files** with a scoped `feat: serialize binary64 canonically` commit.

### Task 4: C1.1 integration, installed proof, and four-gate closeout

**Files:** Modify `tools/installed_smoke.py` and `tests/test_installed_smoke.py`; extend `tests/test_canonical_json.py`; after review, update this plan, `BACKLOG.md` through the guarded adapter, and `.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/` evidence.

**Interfaces:** Consumes `canonical_bytes`, `_parse_json_document`, and `_encode_document`. Produces no C1.2 public model or self-hash function. The installed smoke asserts that the wheel's `xplane_fdau.contracts.canonical_bytes({"test.x": 1.0})` yields `b'{"test.x":1.0}\n'` outside the checkout.

- [ ] **Step 1: Write failing integration tests** for parse-then-canonicalize convergence under changed whitespace/property order, literal SHA-256 `c7a95602104d7db4d2fca0e277f6e064854c886d32328a57cb4d28ab10467424` for `b'{"test.x":1}\n'`, public `contracts.__all__` containing only the seven C1.1 error classes and `canonical_bytes`, and unchanged root `__all__`. For installed smoke, fault-inject an incorrect `xplane_fdau.contracts.canonical_bytes` result and assert `smoke()` raises `SmokeError`; before the new check this must fail as an `assertRaises` assertion, not an import error. Confirm the exact module inventory updated across Tasks 1–3 now includes `xplane_fdau.contracts`, `xplane_fdau.contracts.errors`, `xplane_fdau.contracts._json_parse`, `xplane_fdau.contracts.canonical_json`, and `xplane_fdau.contracts._binary64`, retaining its exact-set assertion so unexpected modules also fail. Check that a duplicate key wins over an out-of-range number in the same document; do not fabricate a family envelope or claim C1.1 proves the later version/shape tiers.

  For the SHA-256 assertion, compute `encoded = canonical_bytes({"test.x": 1})`, assert `encoded == b'{"test.x":1}\n'`, and assert `hashlib.sha256(encoded).hexdigest() == "c7a95602104d7db4d2fca0e277f6e064854c886d32328a57cb4d28ab10467424"`. Hash the encoder's returned bytes, never a standalone literal; the changed-whitespace/property-order inputs must converge to the same bytes and digest.
- [ ] **Step 2: Verify RED.** Run `uv run --offline --frozen python -m unittest tests.test_canonical_json tests.test_installed_smoke tests.test_public_api -v`. Require the faulty-canonical-bytes smoke test to fail at its `assertRaises` assertion before changing the smoke implementation; the exact module inventory is a separate regression assertion, not a manufactured negative control. Import errors and missing-symbol exceptions are not RED evidence.
- [ ] **Step 3: Add the minimal installed-smoke assertion and close integration gaps.** Extend `tools/installed_smoke.py` to import and assert the exact installed `canonical_bytes({"test.x": 1.0})` result; keep the updated exact-module inventory test green and the root namespace unchanged. Do not add family `load_*_v1` functions, `compute_content_hash`, schemas, C4.2 corpus, or a generic reflection serializer. If an existing release validator rejects a correctly built package, first add a focused regression test and fix only the proven validator assumption.
- [ ] **Step 4: Run focused GREEN checks** for all C1.1 test modules, `tests.test_public_api`, `tests.test_runtime_import_boundary`, and `tests.test_installed_smoke`; then Ruff check/format and ty. Expected: all exit 0.
- [ ] **Step 5: Request independent code review** of the bounded C1.1 diff against the four backlog gates, exact spec profile, RFC number vectors, error precedence, runtime/import boundary, and C1.2 exclusions. Resolve Critical/Important findings with focused tests before closeout. Do not mark gates satisfied merely because tests exist.
- [ ] **Step 6: Run one complete stable-candidate gate.** Run `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` on Python 3.12. It supplies the full quality suite, strict docs, offline lock, backlog audit, hooks, and a fresh exact wheel/sdist pair; do not separately rerun `tools/quality.py check` on the unchanged candidate. Record the exact result and artifact hashes/evidence. If it fails, repair and repeat on the changed candidate.
- [ ] **Step 7: Prove the installed wheel on Python 3.12.** Use the following Windows commands from the checkout; on POSIX use `bin/python` instead of `Scripts/python.exe`. Record the external path and artifact hashes; do not delete a failed artifact. No local 3.13/3.14 source matrix is required.

```powershell
$repo = (Get-Location).Path
$version = (uv version --short).Trim()
if ($LASTEXITCODE -ne 0 -or -not $version) { throw "Cannot determine project version" }
$artifactDir = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-c1-1-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $artifactDir | Out-Null
uv build --offline --no-sources --out-dir $artifactDir
if ($LASTEXITCODE -ne 0) { throw "Wheel/sdist build failed" }
$wheel = Join-Path $artifactDir "xplane_fdau-$version-py3-none-any.whl"
$sdist = Join-Path $artifactDir "xplane_fdau-$version.tar.gz"
uv run --offline --frozen twine check --strict $wheel $sdist
if ($LASTEXITCODE -ne 0) { throw "Artifact metadata check failed" }
uv run --offline --frozen python tools/release.py check-dist $artifactDir
if ($LASTEXITCODE -ne 0) { throw "Artifact inventory check failed" }
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
- [ ] **Step 8: Record review and gate evidence only after verification.** Use backlog dry-run then hash-guarded apply for each `record-gate` and lifecycle transition. The four receipts must correspond to exact bytes/Unicode, Int64/Binary64 lexical vectors (including the independent frozen oracle), typed rejection/context, and deterministic bytes/SHA-256. Advance C1.1 to `verified` only with accepted review and all four receipts. Keep G1 waiting and the current project version unreleased.
- [ ] **Step 9: Commit the verified C1.1 evidence and report local integration options.** Do not merge, push, tag, publish, or release without the separately required user decision and checks.
