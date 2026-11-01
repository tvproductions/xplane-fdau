# C2.1 independent whole-branch review

## Reviewed candidate and scope

- Base: `0019d129b5eb20922d39709b7443a171139e59b6`.
- Candidate: `5ab8530a5f088044eb94257a23d1e25ea2db6490`.
- Branch/worktree: `feature/c2-1-measurement-definition`, `C:/Users/Jeff/.codex/worktrees/cfdf/xplane-fdau`.
- Scope: C2.1's four gates, governed by the approved November 1 measurement-definition plan, its canonical specification, the supplied exact authority excerpts and global constraints.
- Procedure: the selected Superpowers `requesting-code-review/code-reviewer.md` and `gzs-change-review`; independent report-only review, without subagents.

Reviewed the supplied six-commit `review-0019d12..5ab8530.diff` in segments. The runtime, tests, smoke, documentation, exports, navigation and execution-state changes were inspected. The plan's approved deferral of shared convenience APIs is respected; this review does not reopen that decision or certify the broader C4.3 architecture question as resolved. Controller-owned Task 4 checkboxes and final acceptance receipts remain pending closeout records, not missing implementation.

## Strengths

- `src/xplane_fdau/measurements/models.py:239` provides the required keyword-only, frozen, slotted definition, with required fields before optional numeric/enumeration arguments. Validation uses the independent semantic field inventory. Its cached private non-init/non-comparing hash slot and read-only property avoid an instance dictionary and exclude caller-supplied identity.
- `src/xplane_fdau/measurements/_definition_validation.py:349` validates complete plain projections in shape/domain/semantic passes. Representation-dependent numeric requirements, units, vector axes, enumeration metadata, explicit policies and ordered collections are enforced without executing acquisition or sample behavior. Accepted sequence inputs are copied, and owned nested values remain immutable.
- `src/xplane_fdau/measurements/_definition_io.py:156` through the entry stages separates preserved lexical shape, domain materialization, hash verification, local semantics and final construction. Its literal family-bound hash preimage reuses the unchanged contracts helper without passing a malformed declared hash into that helper. Error context is attached once, including pointer prefix, source, family and bounded identity.
- The independent literal entry/preimage fixture in `tests/test_measurement_definition_io.py:26`, competing-error build barriers, exact binary64 matrix, mutation and cached-hash checks provide substantial behavioral coverage. The 600/1600-level regressions cover the previously discovered recursion failure without prematurely imposing the canonical depth tier.
- `tools/installed_smoke.py:269` independently checks installed ownership, bytes and hash, round trips and meaningful rejection behavior. Its negative controls test the smoke itself. The guide's executable example and representation/coordinate matrices accurately describe the delivered public models and defer catalogs, schemas, sample evaluation and shared convenience operations explicitly.
- No changed contracts/native FDR implementation, runtime dependency, simulator/network access, catalog shell or dynamic dispatch mechanism appears in the reviewed change. The Python 3.12-compatible frozen/slotted dataclass and explicit cached-slot choices fit the approved version decision; no newer-minor feature is introduced.

## Issues

### Critical (Must Fix)

None found.

### Important (Should Fix)

**I1. Null resolution incorrectly selects the integer domain and masks the canonical-null failure.**

- Location: `src/xplane_fdau/measurements/_definition_validation.py:109`, especially line 110; public constructor at `src/xplane_fdau/measurements/models.py:165`.
- Trigger: `NumericSpec(storage_precision_bits=64, resolution=None, minimum=1.0)`, or the same call with `maximum=1.0`.
- Observed result: the constructor raises `ContractShapeError` at `/minimum` or `/maximum`. The same numeric fields in a structurally valid real definition entry raise `CanonicalJSONError` at `/numeric/resolution` before hash verification.
- Cause: every resolution whose exact type is not `float` is treated as selecting the integer domain. The shape pass permits `None` for later canonical-null rejection, but that same null then causes an otherwise valid binary64 bound to fail an invented integer-domain requirement.
- Consequence: the only intrinsically invalid value in these examples is resolution, yet callers receive the wrong error tier and a pointer to valid bound data. This violates canonical-null handling and constructor/reader validator-path parity; it also gives callers the wrong field to repair. This is a bounded error-contract defect, not acceptance of invalid numeric data.
- Fix direction: do not infer an integer domain from null. Preserve whole-object shape-before-domain validation and genuinely invalid bound-type rejection, while deferring null resolution to the canonical-domain phase. Keep actual mixed integer/binary64 triples rejected. Add focused constructor and real-entry parity regressions for both optional bounds, plus a competing true shape error to prove tier ordering remains intact.

**I2. Cyclic raw dictionary/array input never terminates during private reader preprocessing.**

- Location: `src/xplane_fdau/measurements/_definition_io.py:300`, especially lines 304-314; the same missing cycle defense exists in `_plain` at lines 109-145.
- Trigger: `value = {}; value['title'] = value; _measurement_definition_from_wire(value)`. Exact dictionaries are an explicitly supported private entry input, and lists/tuples are recursively traversed. A self-referential list in a field has the same structural problem.
- Observed result: an isolated Python 3.12.16 child printed `entered`, then failed to return within a two-second timeout; the probe killed and reaped that child. Code inspection shows an unconditional loop: `_duplicates` keeps pushing the same container with an ever-growing path, so it cannot reach the missing-identity shape check or the domain-depth guard. `_plain` would also keep scheduling the cycle if duplicate traversal alone were changed.
- Consequence: a malformed programmatic mapping can hang the internal validation operation and grow resource use instead of returning a bounded contract rejection. This is not a network or public-loader exploit claim: JSON text cannot contain a cycle, and the API is intentionally private. It is a concrete robustness defect in the raw-dictionary integration seam this change explicitly implements.
- Fix direction: make both preprocessing traversals cycle-aware, with a bounded contract rejection and preserved ordinary duplicate/shape/domain precedence. Distinguish an ancestor cycle from repeated acyclic aliases so legitimate repeated data is not rejected merely for sharing a Python container. Cover self-referential dict/list input under a bounded regression and retain the existing deep finite-input/duplicate-priority regressions. Do not solve this by imposing the depth tier before ordinary shape validation.

### Minor (Nice to Have)

No new C2.1 minor issue retained. The successful strict MkDocs log carries the existing Material end-of-life advisory (`task-4-mkdocs.log:2`). It is a tooling-maintenance observation, not a defect in these documentation changes. No dependency upgrade, warning suppression or C2.1 scope expansion is warranted here.

## Checks and evidence

- Read the supplied diff and approved plan/authority package, ledger, task reports and relevant review/fix records. The ledger's numeric concern was independently assessed against the implementation rather than accepted on the author's rationale.
- Named unchanged-code inspection: numeric tier and lexical integration (`contracts/values.py` scalar/container/tag helpers); family/version and self-hash preimage integrity (`contracts/_content_hash.py`). These checks established how the new code uses the existing contracts primitives; they were not a broad re-audit of C1.
- Read the final task hook log: Ruff check, Ruff format check, ty and unittest all report Passed for `5ab8530`. Read the strict MkDocs log's successful result and advisory. Earlier task reports record focused RED/GREEN/static/hook evidence and the two approved fixes; this review did not rerun those suites.
- Independently executed only the two named unresolved behavioral probes, using the existing worktree `.venv/Scripts/python.exe -B`. Interpreter identified itself as Python 3.12.16. Exact numeric output:

```text
minimum constructor ContractShapeError /minimum
minimum reader CanonicalJSONError /numeric/resolution
maximum constructor ContractShapeError /maximum
maximum reader CanonicalJSONError /numeric/resolution
cyclic dict exceeded 2-second timeout; subprocess killed and reaped; entered
```

- `git rev-parse HEAD` matched the assigned candidate; `git status --short` was empty before report creation. No source, index, HEAD, branch or dependency/cache mutation was performed. Only this authorized ignored report was written.
- Final full offline hygiene and fresh external installed-wheel execution have not yet run for whole-branch acceptance. Source-tree smoke tests and prior task hooks do not establish those pending results.

## Declined to judge

- Shared `canonical_bytes` model dispatch, `compute_content_hash`, `definition_ref` and their architecture reconciliation: explicitly deferred by the approved C2.1 plan to C4.3; the current change preserves that boundary.
- MeasurementCatalog schema/resources, public family loaders, envelope-version rejection and catalog-wide error staging/cross-references: C2.2 or later scope; an entry reader cannot prove document-wide behavior.
- Normalized enumeration/sample authorization, freshness/age classification, interpolation execution, acquisition, recording, ARINC and FDM execution: this child supplies semantic metadata only; the guide states these limits accurately.
- Detecting reuse of a historical revision for changed semantics: a stateless constructor has no publication history; the author revision obligation is documented and no historical-policing facility is promised here.
- Existing parser behavior beyond the entry seam, adversarial mutation through `object.__setattr__`, and later unimplemented consumers: no broadened audit or speculative compatibility finding is claimed. The concrete cyclic exact-dictionary input is retained above because it is within the explicitly implemented seam.
- Material lifecycle/dependency migration: pre-existing tool advisory; no dependency refresh is authorized or required for C2.1.
- Final artifact/inventory and external wheel acceptance, final gate receipts/lifecycle state and integration readiness: still assigned controller closeout work, not claimed passed by review.
- macOS/Linux execution and embedded simulator behavior: only Windows Python 3.12.16 probes were executed; no host-specific runtime code was added and no cross-platform execution claim is made.

## Recommendations

Resolve I1 and I2 with focused regressions and independent fix review. Then perform the already planned single stable full offline hygiene pass and exact external Python 3.12 wheel proof on the resulting candidate, complete the closeout records, and retain the existing C2.2/C4.3 deferrals. No broader redesign or dependency work is needed for these findings.

## Assessment

**Ready to merge? No.**

The implementation substantially satisfies C2.1 and has strong staged validation, identity, mutation and smoke coverage, but the demonstrated numeric error-contract mismatch and nonterminating raw-input traversal need correction. Whole-branch artifact and installed-wheel acceptance also remain pending controller work; passing task hooks do not replace them.
