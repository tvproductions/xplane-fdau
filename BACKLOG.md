# xplane-fdau Backlog

- **Status:** Active delivery ledger
- **Updated:** 2026-08-09

`ROADMAP.md` defines capability order and release gates. This file tracks each
reviewable delivery slice, its dependencies, governing documents, status, and
measurable acceptance evidence.

## Dashboard

| ID | Outcome | Status | Depends on | Specification | Implementation plan | Verified gates |
| --- | --- | --- | --- | --- | --- | --- |
| `M0` | FDAU identity and native FDR kernel migration | `verified` | — | [Design](docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md) | [Plan](docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md) | 6/6 |
| `C1` | Canonical contract foundation | `designing` | `M0` | [Draft design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/6 |
| `C2` | Measurement and source-binding catalogs | `designing` | `C1` | [Draft design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/6 |
| `C3` | Observation, sample, and frame records | `designing` | `C2` | [Draft design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/6 |
| `C4` | Contract conformance and artifact closure | `designing` | `C3` | [Draft design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/6 |
| `A1` | Acquisition profiles, demand, lifecycle, continuity, and fan-out | `queued` | `C4` | — | — | 0/5 |
| `R1` | Canonical archive, manifest, recovery, and replay | `queued` | `A1` | — | — | 0/5 |
| `P1` | Canonical-to-native-FDR projection with loss reporting | `queued` | `R1` | — | — | 0/5 |
| `G1` | Canonical vertical-slice review and release-readiness decision | `queued` | `P1` | — | — | 0/5 |

Gate counts are derived from the checklists below. A count and its checkbox
evidence must change in the same commit.

## Canonical release boundary

Before any release, separately reviewed increments must implement:

1. measurement, binding, observation, sample, frame, timing, and quality contracts;
2. acquisition profiles, demand resolution, continuity, and generic fan-out;
3. the canonical archive, manifest, recovery, and deterministic replay; and
4. projection from canonical samples to the native FDR sink with explicit loss
   reporting.

The slice IDs and gates below refine this sequence without weakening or
reordering it.

## Active canonical-contract increment

The canonical-contract design is one normative semantic specification with four
separately executable plans. This prevents a single oversized implementation
plan while keeping shared wire decisions coherent.

### C1 — Canonical contract foundation

**Outcome:** Deterministic, language-neutral identity, canonical JSON, shared
value, timing, provenance, validity, and quality primitives.

**Planned plan:**
`docs/superpowers/plans/2026-08-09-xplane-fdau-contract-foundation.md`

Acceptance gates:

- [ ] Exact canonical JSON and SHA-256 golden vectors pass.
- [ ] Identity, definition/record reference, authority, provenance, and producer
      contracts are immutable and strictly validated.
- [ ] Signed 64-bit, finite binary64, Unicode, structured value, and payload
      reference contracts pass boundary tests.
- [ ] UTC, monotonic/source clock, anchor, simulator-time, and acquisition-phase
      contracts preserve distinct semantics.
- [ ] Validity and closed canonical quality vocabularies pass invariant tests.
- [ ] Source, quality, import-boundary, and installed-wheel gates remain green
      with no runtime dependency.

### C2 — Measurement and source-binding catalogs

**Outcome:** Provider-neutral semantic catalogs and exact binding references,
with no shipped provider or aircraft content.

**Planned plan:**
`docs/superpowers/plans/2026-08-09-xplane-fdau-measurement-binding-catalogs.md`

Acceptance gates:

- [ ] Measurement definition/catalog models and version-1 schema pass strict
      construction, load, hash, order, and round-trip tests.
- [ ] Source-binding definition/catalog models and version-1 schema pass the
      same strict gates.
- [ ] Every binding pins one measurement ID, revision, and content hash.
- [ ] Pure cross-catalog validation rejects missing, incompatible, or ambiguous
      references without executing transforms.
- [ ] Catalog schemas and synthetic conformance fixtures are packaged exactly.
- [ ] Artifact inspection proves no stock DataRefs, aircraft catalogs, provider
      adapters, executable expressions, or ARINC constants ship.

### C3 — Observation, sample, and frame records

**Outcome:** Immutable canonical evidence records with exact timing, quality,
ordering, and raw lineage.

**Planned plan:**
`docs/superpowers/plans/2026-08-09-xplane-fdau-observation-sample-frame-contracts.md`

Acceptance gates:

- [ ] Raw-observation model and version-1 schema preserve provider/resource,
      type/shape, value/status, generation, and timing evidence.
- [ ] Measurement-sample model and version-1 schema preserve exact catalog
      references, normalization status, validity, quality, freshness, and raw
      lineage.
- [ ] Measurement-frame model and version-1 schema preserve canonical sample
      ordering and actual observation arrival order.
- [ ] Pure sample/frame validators reject reference, representation, unit,
      range, timing, epoch, order, and lineage conflicts.
- [ ] Failed reads/conversions cannot acquire fabricated values, timestamps, or
      validity.
- [ ] No acquisition engine, transform execution, payload storage, archive, or
      native projection behavior is introduced.

### C4 — Contract conformance and artifact closure

**Outcome:** One independently reviewed, distributable contract kernel whose
schemas, implementation, fixtures, documentation, and artifacts agree.

**Planned plan:**
`docs/superpowers/plans/2026-08-09-xplane-fdau-contract-conformance-closure.md`

Acceptance gates:

- [ ] Accepted/rejected fixture manifest covers every family, boundary, error
      class, property path, canonical byte vector, and expected hash.
- [ ] Packaged schemas and documentation copies are byte-identical and
      independently versioned.
- [ ] Documentation clearly separates measurements/bindings,
      observations/samples, FDAU frames/ARINC frames, and acquisition
      quality/operational evaluation.
- [ ] Complete native FDR and canonical-contract `unittest` suites and all
      repository quality gates pass.
- [ ] Fresh wheel/sdist and installed-wheel smoke tests pass on Python
      3.12–3.14 with exact resources and no runtime dependencies.
- [ ] Independent review finds no unresolved load-bearing defect; version
      `0.1.0` remains unreleased.

## Remaining release-path increments

The exact gates below are architectural exit conditions. Each item receives a
reviewed specification and may be split into smaller executable plans before
implementation.

### A1 — Acquisition profiles, demand, lifecycle, continuity, and fan-out

- [ ] Immutable acquisition profiles and consumer demands are specified.
- [ ] Compatible demand merge and contradictory-demand rejection are proven.
- [ ] Lifecycle/epoch transitions and continuity classification are proven.
- [ ] Generic sink/subscriber fan-out, backpressure, and failure isolation are
      proven without provider imports.
- [ ] Independent review and installed-artifact gates pass.

### R1 — Canonical archive, manifest, recovery, and replay

- [ ] Canonical archive preserves every accepted observation and sample lineage
      within declared retention policy.
- [ ] Manifest hashes, relationships, provenance, and terminal results are
      deterministic and complete.
- [ ] Atomic publication, checkpoint, partial recovery, and no-replace behavior
      are proven under injected failures.
- [ ] Deterministic replay reproduces identities, ordering, timing semantics,
      and declared epoch behavior.
- [ ] Long-session, artifact, independent-review, and installed-wheel gates
      pass.

### P1 — Canonical-to-native-FDR projection

- [ ] Projection maps exact measurement/binding references to every native FDR
      field.
- [ ] Omitted measurements, defaults/placeholders, conversions, rounding,
      precision loss, and v3/v4 limitations are reported.
- [ ] Canonical evidence remains authoritative and is not rewritten through the
      lossy projection.
- [ ] End-to-end canonical-to-sink tests and X-Plane-oriented fixture tests pass.
- [ ] Independent review and installed-artifact gates pass.

### G1 — Canonical vertical-slice review

- [ ] `C1`–`C4`, `A1`, `R1`, and `P1` are verified with durable evidence.
- [ ] Cross-slice identity, timing, quality, lineage, recovery, replay, and loss
      semantics are consistent.
- [ ] Runtime and built artifacts remain standard-library-only and
      provider-neutral.
- [ ] The release candidate passes the complete Python 3.12–3.14 matrix outside
      the checkout.
- [ ] A separate reviewed decision either authorizes release preparation or
      records remaining blockers; this gate itself does not publish anything.

## Later governed work

| ID | Work | Status | Required before design or implementation |
| --- | --- | --- | --- |
| `I1` | q4xpcc Phase 24A integration | `queued` | Verified canonical slice and consumer-owned adapter plan |
| `I2` | xpwebapi corroboration adapter | `queued` | Stable contract kernel and consumer-owned development plan |
| `S1` | Standards baseline/traceability contract | `queued` | Stable contract identities and separate standards specification |
| `S2` | ARINC 717 profile and codec | `blocked` | Licensed edition, scoped profile, FRED relationship, golden vectors |
| `S3` | ARINC 647A/FRED boundary | `blocked` | Licensed edition and redistribution decision |
| `S4` | ARINC 429 profile and codec | `blocked` | Licensed edition and concrete source/target/use case |
| `F1` | FDM analysis | `deferred` | Canonical archive plus separate downstream project specification |
| `F2` | FOQA governance/claims | `deferred` | Organizational approval, governance, validation, and legal review |

Native X-Plane textual `.fdr` v3/v4 remains only a lossy FDAU projection and
sink. ARINC and FDM/FOQA work cannot be pulled into an earlier slice by changing
this backlog alone.

## Backlog maintenance rules

1. The dashboard status must agree with its linked spec, plan, and checklist.
2. A proposed path is not implementation authority.
3. Each implementation plan must produce one independently testable outcome.
4. New requirements enter as a backlog item or an explicit acceptance-gate
   amendment, never as an untracked plan expansion.
5. A checked gate cites committed verification evidence in its plan or handoff.
6. `verified` requires every gate checked and independent review resolved.
7. `released` requires a separate authorized release action; no current item is
   authorized for release.
