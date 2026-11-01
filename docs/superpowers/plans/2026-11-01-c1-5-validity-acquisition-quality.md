# C1.5 Validity States and Acquisition Quality Implementation Plan

- **Governance:** active
- **Status:** completed
- **Date:** 2026-11-01
- **Roadmap child:** `C1.5`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- **Approval:** 2026-11-01 — Jeff / tvproductions; native execution with independent review approved in chat
- **Completion evidence:** `.superpowers/sdd/2026-11-01-c1-5-quality/completion.md`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Deliver the closed validity and acquisition-quality vocabularies and strict quality array-set validation required by C1.5's four gates.

**Architecture:** `measurements.models` owns the two public `StrEnum` classes; a private measurement helper validates explicit validity values and ordered quality collections for future constructors and readers. No sample, catalog, inferred validity, or acquisition evaluator is introduced.

**Tech Stack:** Python 3.12 standard library, unittest, locked all-group uv, Ruff, ty, strict MkDocs, offline hygiene and installed-wheel smoke.

**Spec:** [Approved canonical measurement contract design](../specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md), especially “Contract families and versions,” “Validity and quality,” “Public API and errors,” and C1.5 acceptance criteria; [core scope amendment](../../architecture/xplane_fdau_core_scope_amendment.md).

## Global Constraints

- Implement only C1.5; dependency C1.2 is verified. Preserve C1.1–C1.4 and the native FDR kernel.
- “Named closed vocabularies are `enum.StrEnum` classes and are not dataclasses.”
- “A loader or constructor rejects duplicates and noncanonical order; it never silently sorts or deduplicates.”
- “JSON `null` is prohibited throughout version 1.” Optional properties are omitted when absent.
- “The root `xplane_fdau.__init__` continues to export only `__version__`.”
- Runtime remains pure Python and standard-library-only, supporting `>=3.12,<3.13`. Execute through the exact `.python-version` selection, currently 3.12.16, and locked all-group uv. Use unittest only and preserve mandatory hooks.
- No host/network imports, provider catalogs, transforms, simulator I/O, recording, standards codecs, or operational findings. No public helper, extra model, generic serialization API, schema family, or placeholder for later slices.
- This plan is review material until approved. No lifecycle mutation or task execution before approval. Local implementation commits require execution authorization; remote synchronization and release retain separate gates.

## Review Focus

1. An unrelated string enum can compare equal to a wire string; Task 1 checks exact enum ownership and Task 2 rejects foreign enum members at validation boundaries.
2. A caller's mutable list must not change accepted quality; Task 2 tests a defensive immutable result and unchanged input order on failure.
3. Set iteration or generator consumption can silently manufacture ordering; Task 2 rejects unordered containers and arbitrary iterables rather than sorting them.
4. A malformed later item must outrank an earlier order violation; Task 2 checks complete element shape/domain validation before collection semantics and exact nested paths.
5. Empty quality can be misread as a valid measurement; Tasks 2 and 3 prove no validity default or inferred validity and document producer responsibility.

## Verified planning baseline and scope seams

November 1 entry: clean `main` at `82b1e81a42eab27c47037bc1dc47c4b4378b9476`, matching the local `origin/main` reference. No remote freshness claim is made. Backlog audit passed with no findings; next reports `write_plan C1.5`. C1.5 is `specified`, 0/4 gates, with no active child. Refresh and C1.4 are already integrated; do not repeat their completed work.

Native inventory and actual checkouts agree with the reviewed pins: starter 0.8.0 at `e0b752fcc13b87ec7868fe0b0f85badefdb6bf52`, Superpowers 7.0.1 at `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`, gz-skills 0.8.3 at `d6acc26e28ca1c4f43e5bb46d8973021d7d006c3`. This fresh session discovers the selected entry skills. Heavy is present; Backplane remains disabled. Cognitive acceptance and other recorded STRICT gaps remain open.

Two approved ownership decisions keep the implementation within scope:

- The approved public table places `ValidityState` and `QualityFlag` in `measurements.models`. Export only these delivered names there and from `measurements`; later C2.1 extends that table incrementally. Do not create future model shells or move vocabulary into contracts.
- C1.5 supplies private scalar/collection validators to make its ordering gates executable without inventing a public quality container. The complete sample compatibility matrix, normalization reasons, lineage corroboration, and measurement authorization checks remain C2/C3 integration work. Separate scalar and collection validation never purport to validate a complete sample.

| Responsibility | Exact files |
| --- | --- |
| Owned vocabulary and package exports | Create `src/xplane_fdau/measurements/models.py`, `src/xplane_fdau/measurements/__init__.py` |
| Strict private validity/quality boundary | Create `src/xplane_fdau/measurements/_quality.py` |
| Vocabulary, collection, error-context tests | Create `tests/test_measurement_quality.py` |
| Public ownership and import boundary | Modify `tests/test_public_api.py`; exercise `tests/test_runtime_import_boundary.py` |
| Installed module inventory and vocabulary behavior | Modify `tools/installed_smoke.py`, `tests/test_installed_smoke.py` |
| Guidance and rendered API | Create `docs/reference/measurement-quality.md`; modify `mkdocs.yml` |
| Execution/evidence after approval | This plan; guarded `BACKLOG.md`; `.superpowers/sdd/2026-11-01-c1-5-quality/` |

Keep existing contracts, canonical JSON dispatch, import rules, packaging metadata, lockfiles, and release validators unchanged. The artifact inventory derives from shipped source; adjust only the existing installed-smoke expected module set for the three new modules.

## Execution entry — after approval

- [x] Record plan approval and the selected execution method. Recheck handoff authorities, plugin sources, clean status, HEAD, worktrees, and audit/next. Stop on findings or authority drift.
- [x] Resolve the draft's clean baseline without silently stashing, discarding, or committing unrelated work. Use `superpowers:using-git-worktrees` to create a temporary C1.5 branch/worktree; record actual path and base HEAD.
- [x] With approved authority, use the backlog adapter's dry-run and printed target digest to link this plan, select C1.5 and transition `specified` → `planned` → `in_progress`. Inspect each proposed diff/audit before its matching apply. Do not record gates at entry.

## Task 1: Publish the exact owned vocabularies

**Files:** Create `measurements/models.py`, `measurements/__init__.py`, and `tests/test_measurement_quality.py` under the roots above; modify `tests/test_public_api.py`.

**Interfaces:** Consumes `enum.StrEnum`. Produces public `ValidityState` and `QualityFlag`, with uppercase member names corresponding exactly to the wire strings below. Both `__all__` lists are exactly `["ValidityState", "QualityFlag"]` in that order.

- [x] **Step 1: Write failing unittest cases.** `MeasurementQualityVocabularyTests.test_exact_vocabularies` checks `issubclass(..., StrEnum)`, exact member name/value pairs (including `__members__` to detect aliases), and exact enum construction round trips for every spelling. `test_closed_vocabularies` rejects `"VALID"`, `" valid"`, `"within_tolerance"`, `"outside_tolerance"`, `"indeterminate"`, `"warning"`, `"critical"`, and `"finding"` with `ValueError` from direct enum construction. Public API tests assert owning-module/package object identity, exact exports, unchanged root exports, and no measurement re-export from contracts.

Validity values in declaration order:

```text
valid invalid unknown not_applicable
```

Quality values in declaration and lexical order:

```text
conversion_failed discontinuous dropped duplicate orphaned
out_of_declared_range precision_lost provider_degraded read_error
reordered rounded saturated stale type_mismatch unavailable
```

- [x] **Step 2: Verify RED.** Run `uv run --locked --all-groups python -m unittest tests.test_measurement_quality tests.test_public_api -v`; require the expected missing measurement-module/name failure before implementation. Investigate unrelated failures.
- [x] **Step 3: Implement the two enums and explicit re-exports.** Use uppercase names such as `NOT_APPLICABLE` and `OUT_OF_DECLARED_RANGE`; no aliases, generated registries, inference, or extra public types. Enum constructors themselves retain standard-library exception behavior; contextual contract errors belong to Task 2.
- [x] **Step 4: Verify GREEN.** Repeat Step 2, then run the focused static checks below. Expect all commands to exit zero.
- [x] **Step 5: Commit the exact Task 1 files** with `feat: add closed measurement validity and quality vocabularies`, after execution authorization and mandatory hooks.

## Task 2: Enforce immutable, ordered acquisition-quality inputs

**Files:** Create `src/xplane_fdau/measurements/_quality.py`; extend `tests/test_measurement_quality.py`.

**Interfaces:** Consumes Task 1 enums and existing `contracts.errors`. Produces only these private functions:

```python
_validity_state(value: object, *, path: str = "/validity") -> ValidityState
_quality_flags(value: object, *, path: str = "/quality") -> tuple[QualityFlag, ...]
```

Accept exact strings or the corresponding owned enum members. `_quality_flags` accepts only actual list/tuple containers and returns a new immutable tuple of owned members. It rejects strings, bytes, sets, mappings, generators and foreign enum classes. These private adapters will be called by future strict constructors/readers; no model or loader is added here.

- [x] **Step 1: Write failing unittest cases.** `MeasurementQualityInputTests.test_scalar_and_collection_conversion` checks all four scalar states, all 15 flags, mixed owned-enum/string entries, and exact returned types. `test_empty_flags_do_not_infer_validity` checks `_quality_flags([]) == ()`, all four explicit scalar states remain distinct, and calling `_validity_state()` without a value raises `TypeError`. No combined sample validator or default-valid parameter exists.
- [x] **Step 2: Add array-set and boundary tests.** `test_duplicate_and_reverse_order_are_rejected` checks duplicate `stale` at `/quality/1`, reversed `("stale", "rounded")` at `/quality/1`, unchanged caller input after failure, and all 105 distinct reversed flag pairs. Both violations raise `ContractValidationError`. `test_defensive_copy` mutates a valid input list after conversion and checks its returned tuple is unchanged. `test_foreign_types_and_operational_terms` rejects every Task 1 operational term and a foreign `StrEnum` whose value is `stale`, with `ContractShapeError` at the item's path. Non-list/tuple containers fail with `ContractShapeError` at the collection path; null collection/scalar/items fail with `CanonicalJSONError` at their exact paths. Wrong element types, unknown spellings, and foreign enums raise `ContractShapeError`. These expectations follow existing closed-vocabulary validation behavior.
- [x] **Step 3: Add precedence/context tests.** `test_shape_precedes_collection_semantics` supplies `["stale", "rounded", 7]` and expects `ContractShapeError` at `/quality/2`, rather than an order error at index 1. With `["stale", "rounded", None]`, require `CanonicalJSONError` at index 2. `test_nested_paths_and_context` passes `path="/samples/2/quality"`, checks its item pointer, `<memory>` source, and absent line/column. All 15 permitted unique flags pass together. `test_sixteen_flags_rejects_duplicate_at_index_15` supplies `tuple(flag.value for flag in QualityFlag) + ("unavailable",)` (the 15 exact flags in Task 1 order followed by a second `unavailable`) and requires `ContractValidationError` with `path == "/quality/15"`; the validator must not truncate or silently deduplicate the input. The finite vocabulary naturally limits successful arrays to 15 entries.
- [x] **Step 4: Verify RED.** Run `uv run --locked --all-groups python -m unittest tests.test_measurement_quality -v`; require the expected absent-helper failure.
- [x] **Step 5: Implement the two private functions.** Validate container and all element shapes first, canonical null prohibition next, then uniqueness and strict lexical order. Compare `.value` strings, return owned enum members, and report the first offending element within the applicable tier. Reject arbitrary iterables without consuming them. Preserve the supplied RFC 6901 pointer prefix; invent no parser locations or family identity. Do not sort or mutate input and do not infer validity from flags.
- [x] **Step 6: Verify GREEN.** Repeat Step 4, then run focused static checks. No full family JSON reader exists yet; future readers must reuse these helpers after their normal envelope/shape/domain stages to preserve constructor/loaded parity.
- [x] **Step 7: Commit the exact Task 2 files** with `feat: validate canonical acquisition quality array sets`, retaining mandatory hooks.

## Task 3: Verify installed ownership and document semantics

**Files:** Modify `tools/installed_smoke.py`, `tests/test_installed_smoke.py`, `mkdocs.yml`; create `docs/reference/measurement-quality.md`.

**Interfaces:** Consumes Tasks 1–2. Produces private `tools.installed_smoke._measurement_quality_smoke() -> None`, invoked by the existing installed verification flow. It raises existing `SmokeError` when required vocabulary/ordering checks fail. No new runtime API.

- [x] **Step 1: Write failing smoke tests.** Add the three measurement modules to `test_all_installed_runtime_modules_are_discovered_and_imported`'s expected set. Add `test_measurement_quality_smoke_detects_reordered_acceptance`: patch the private helper to accept reversed flags and require `SmokeError`. Add `test_measurement_quality_smoke_passes` for real behavior. Run `uv run --locked --all-groups python -m unittest tests.test_installed_smoke -v` and observe the expected new-module/helper failure.
- [x] **Step 2: Implement the smoke check and call it from the existing flow.** Check public package/module identity, exact four and 15 wire values, preservation of explicit `UNKNOWN` with empty quality, and rejection of reversed/duplicate flags through the private helper. Translate an unexpectedly accepted invalid input into `SmokeError`. Import from the installed package, using the existing source-independent smoke procedure.
- [x] **Step 3: Write the guide and add its MkDocs reference entry.** Include all exact flag meanings from the approved design, a short ordered tuple example, producer-asserted validity, and empty-quality semantics. State that operational evaluation stays separate and that complete sample compatibility and corroboration arrive in C3. Include MkDocstrings for only the delivered public enums. Do not claim standalone enums are canonical contract documents or add JSON/schema loaders. Review examples against the source and tests; add no phrase-presence snapshot tests.
- [x] **Step 4: Verify focused GREEN.** Run `uv run --locked --all-groups python -m unittest tests.test_measurement_quality tests.test_public_api tests.test_installed_smoke tests.test_runtime_import_boundary tests.test_documentation -v`, focused static checks, then `uv run --locked --all-groups mkdocs build --strict`. Expect zero failures and no import boundary changes.
- [x] **Step 5: Commit the exact Task 3 files** with `docs: expose and verify measurement quality semantics`, preserving hooks.

## Focused static checks

After each task's GREEN tests, run:

```powershell
uv run --locked --all-groups ruff check src/xplane_fdau/measurements tests/test_measurement_quality.py tests/test_public_api.py tests/test_installed_smoke.py tools/installed_smoke.py
uv run --locked --all-groups ruff format --check src/xplane_fdau/measurements tests/test_measurement_quality.py tests/test_public_api.py tests/test_installed_smoke.py tools/installed_smoke.py
uv run --locked --all-groups ty check
```

## Stable closeout and gate evidence

- [x] Perform independent review through `superpowers:requesting-code-review`; resolve findings and record exact candidate identity. Jeff selected native execution with independent whole-branch review on November 1.
- [x] Use canonical `gzs-quality-gate`/`gzs-repository-hygiene` with the project adapter. Adding a shipped semantic package changes package layout, so run the full offline hygiene command once at stable closeout:

```powershell
uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py
```

This supplies the complete active-Python gate, docs, hooks and fresh strict artifact pair; do not additionally run the standalone full gate on the unchanged candidate. Mandatory commit hooks remain mandatory.

- [x] Run the existing release-skill external Python 3.12 installed-wheel smoke procedure on that exact wheel because this slice adds installed imports. Record artifact path, hashes, interpreter and import origin. Do not rerun a broad interpreter matrix or claim release readiness.
- [x] Record four gate receipts under `.superpowers/sdd/2026-11-01-c1-5-quality/`: gate 1 exact closed validity/independence (Tasks 1–2); gate 2 closed unique ordered flags (Tasks 1–2); gate 3 empty flags/no inferred validity (Tasks 2–3); gate 4 operational vocabulary exclusion (Tasks 1–3). Bind focused tests, complete hygiene, artifact smoke and independent review to the actual candidate. Preserve failed attempts honestly.
- [x] Through dry-run/digest/apply backlog operations, advance only C1.5 through implemented/reviewed/verified when requirements and committed evidence actually justify each state. Record completion and update plan checkboxes; no gate closes merely because the plan was written.
- [x] Use `superpowers:finishing-a-development-branch`. Jeff selected local integration on November 1. Main fast-forwarded exactly to `227756a4ace67d7b5bee7849b0e92469f94c6837`; frozen sync/lock, both live-state tests, fresh strict artifacts, external wheel smoke and the full offline hygiene fallback passed. The temporary worktree and branch were removed after verification. The integration receipt is `.superpowers/sdd/2026-11-01-c1-5-quality/integration.md`. Remote sync, tags and publication retain separate authority.

## Planning audit

Intent: approved design's separate evidence axes and exact public ownership. Scope: BACKLOG C1.5's four gates. The tables record planning alignment; the completion receipt owns execution evidence.

| Intent → scope | Classification | Evidence |
| --- | --- | --- |
| Closed producer-asserted validity separate from acquisition degradation | Aligned | Spec “Validity and quality”; BACKLOG C1.5 gates 1 and 3 |
| Exact flag vocabulary, lexical array-set order, operational exclusion | Aligned | Same spec section; BACKLOG C1.5 gates 2 and 4 |
| Runtime and package boundaries | Aligned | Spec “Package and dependency boundaries” and “Public API and errors”; scope amendment |
| Complete sample matrix, lineage and catalog authorization | Not Applicable to C1.5 delivery | Spec “Measurement sample”; BACKLOG C2.1/C2.4/C3.2/C3.3 |

| Scope → plan | Classification | Evidence |
| --- | --- | --- |
| Gate 1: closed independent validity | Aligned | Task 1 exact enum membership; Task 2 separate scalar interface |
| Gate 2: unique ordered closed quality | Aligned | Tasks 1–2 exact vocabulary and rejection tests |
| Gate 3: empty quality cannot create validity | Aligned | Task 2 explicit-input tests; Task 3 installed smoke and guidance |
| Gate 4: no operational findings/tolerances | Aligned | Task 1 rejected vocabulary; Task 2 contextual rejection; Task 3 guide |
| Error context, installed surface and required verification | Aligned | Task 2 precedence/path cases; Task 3 smoke; stable closeout |

**Planning audit verdict:** PASS for scoped planning alignment; no missing or drifted scoped requirement identified. The private helper boundary was approved as an implementation choice, not a specification amendment. Approval and completed task steps are recorded above; the completion receipt records review and verification. Managed lifecycle closure is complete: C1.5 is verified with 4/4 gates and its selection is cleared. Jeff selected local integration; main verification and temporary worktree/branch cleanup are complete.

## Execution rulings

- Installed module inventory updates moved to the module-producing tasks so every intermediate commit can pass mandatory full-suite hooks.
- Task 1 also updates the wheel/sdist directory lists in `tests/test_release_tool.py`; their hard-coded fixture inventory lacked the new measurements directory. The runtime release validator stays unchanged.
- Native checkout CRLF-only differences were restored to exact indexed bytes, preserving all intentional byte fixtures and provenance hashes. This changes no committed baseline content.
- The exact sixteen-item test input uses equivalent tuple unpacking to satisfy Ruff; it still requires `ContractValidationError` at `/quality/15`.

- Integration verification found a raw-byte mismatch in `mkdocs.yml` only: one branch CRLF was normalized to LF in main, with identical Git content. The required full offline hygiene fallback passed on main; no check was relabeled or omitted. All runtime artifact hashes match the reviewed branch.
