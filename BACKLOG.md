# xplane-fdau Backlog

- **Status:** Active delivery ledger and Superpowers entry point
- **Updated:** 2026-09-05

Read `ROADMAP.md` for architecture order and dependencies. Then use this file to
select one primary child slice whose prerequisites are verified. Each child
slice receives one focused plan and one independently reviewable outcome.

## Current position

- `M0` FDAU identity/native-FDR migration: `verified`.
- Governing scope amendment: approved; `xplane-fdau` owns reusable X-Plane
  FDAU, native FDR, ARINC, and FDM/FOQA-support behavior while external clients
  own all simulator I/O.
- Active design: repository-local backlog governance and status reporting.
- Active child: `T1.4`.
- `D1.1`, `D1.2`, and `D1.3` are verified. The statusless external `I1.0`
  handoff condition is eligible for q4xpcc Phase 24A planning reconciliation;
  `T1.3` is verified with 4/4 gates under its approved audit policy
  supplement and completed implementation plan. No local child is selected;
  `T1.4` is implemented under its approved plan and awaits independent review.
- D1 is design-handoff readiness, not implementation or release readiness.
- `B1.1` source-layout migration: `specified` with a draft plan; resumes after
  peer prerequisites `T2.2` and `T3.1` are verified.
- Canonical contract design: approved with accepted independent review; `C1.1`
  through `C4.4` are specified with zero delivery gates satisfied.
- Release, tag, and package publication: prohibited pending their separate
  gates and authorization.
- Ordinary Git synchronization may commit and push only through an explicit
  user request and canonical `gzs-git-sync` safeguards; this adoption does not
  itself authorize or perform a sync.

## Canonical release boundary

Before any release, separately reviewed increments must implement:

1. measurement, binding, observation, sample, frame, timing, and quality contracts;
2. acquisition profiles, demand resolution, continuity, and generic fan-out;
3. the canonical archive, manifest, recovery, and deterministic replay; and
4. projection from canonical samples to the native FDR sink with explicit loss
   reporting.

The child slices below refine this sequence without weakening or reordering it.

## Local child inventory

| Child | Outcome | Status | Depends on | Spec | Plan | Gates | Review | Resume | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `B1.1` | Source-layout migration and installed-import isolation | `specified` | `T2.2`, `T3.1` | [design](docs/superpowers/specs/2026-08-09-src-layout-migration-design.md) | [draft plan](docs/superpowers/plans/2026-08-09-src-layout-migration.md) | 0/5 | — | — | — |
| `C1.1` | Canonical JSON and binary64/integer encoding | `specified` | `B1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.2` | Identity, hashing, references, authority, and provenance | `specified` | `C1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.3` | Typed values and content-addressed payload references | `specified` | `C1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.4` | Clock domains, UTC instants, anchors, and simulator timing | `specified` | `C1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.5` | Validity states and acquisition-quality vocabulary | `specified` | `C1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.1` | Measurement-definition model and semantic invariants | `specified` | `C1.3`, `C1.5` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.2` | Measurement catalog, schema, ordering, and references | `specified` | `C2.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.3` | Source-binding definition and transform references | `specified` | `C2.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.4` | Binding catalog and pure cross-catalog validation | `specified` | `C2.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/5 | — | — | — |
| `C3.1` | Raw-observation record and schema | `specified` | `C1.3`, `C1.4`, `C1.5`, `C2.4` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.2` | Measurement-sample record and schema | `specified` | `C3.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.3` | Raw/sample lineage and cross-contract validation | `specified` | `C3.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.4` | Measurement-frame record and schema | `specified` | `C3.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.5` | Frame closure, canonical ordering, and validation | `specified` | `C3.4` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.1` | Schema resource parity and version inventory | `specified` | `C3.5` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.2` | Accepted, rejected, and canonical conformance corpus | `specified` | `C4.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.3` | Public API and contract documentation closure | `specified` | `C4.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.4` | Built/installed artifact matrix and independent review | `specified` | `C4.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/5 | — | — | — |
| `A1.1` | Acquisition-profile contracts | `queued` | `C4.4` | — | — | — | — | — | — |
| `A1.2` | Consumer demand contracts and lifecycle | `queued` | `A1.1` | — | — | — | — | — | — |
| `A1.3` | Demand compatibility, merge, and generation resolution | `queued` | `A1.2` | — | — | — | — | — | — |
| `A1.4` | Allow-listed transform registry and execution | `queued` | `C2.4`, `A1.3` | — | — | — | — | — | — |
| `A1.5` | Source/session lifecycle and epoch transitions | `queued` | `C3.5`, `A1.3` | — | — | — | — | — | — |
| `A1.6` | Cadence, downsampling, interpolation, and resampling policy | `queued` | `A1.3`, `A1.5` | — | — | — | — | — | — |
| `A1.7` | Continuity evaluator and continuity report | `queued` | `A1.5`, `A1.6` | — | — | — | — | — | — |
| `A1.8` | Generic fan-out, sink isolation, and backpressure evidence | `queued` | `A1.6`, `A1.7` | — | — | — | — | — | — |
| `A1.9` | Acquisition-session orchestration and installed closure | `queued` | `A1.4`, `A1.5`, `A1.6`, `A1.7`, `A1.8` | — | — | — | — | — | — |
| `R1.1` | Recording-session descriptor and artifact identities | `queued` | `A1.9` | — | — | — | — | — | — |
| `R1.2` | Canonical archive logical format and raw-retention model | `queued` | `R1.1` | — | — | — | — | — | — |
| `R1.3` | Checkpointed writer and atomic/no-replace publication | `queued` | `R1.2` | — | — | — | — | — | — |
| `R1.4` | Artifact manifest graph, integrity, and relationships | `queued` | `R1.3` | — | — | — | — | — | — |
| `R1.5` | Partial-artifact recovery and terminal results | `queued` | `R1.3`, `R1.4` | — | — | — | — | — | — |
| `R1.6` | Deterministic replay source and epoch semantics | `queued` | `R1.5` | — | — | — | — | — | — |
| `R1.7` | Long-session, corruption, recovery, and replay closure | `queued` | `R1.6` | — | — | — | — | — | — |
| `P1.1` | Projection-profile and field-mapping contracts | `queued` | `R1.7` | — | — | — | — | — | — |
| `P1.2` | Mandatory native trajectory-spine projection | `queued` | `P1.1` | — | — | — | — | — | — |
| `P1.3` | Version-4 DataRef extension projection | `queued` | `P1.2` | — | — | — | — | — | — |
| `P1.4` | Projection timing and resampling behavior | `queued` | `P1.1`, `A1.6` | — | — | — | — | — | — |
| `P1.5` | Omission, default, conversion, and precision-loss report | `queued` | `P1.2`, `P1.3`, `P1.4` | — | — | — | — | — | — |
| `P1.6` | End-to-end canonical-to-native-sink verification | `queued` | `P1.5` | — | — | — | — | — | — |
| `D1.1` | Canonical C1–C4 design approval | `verified` | `T1.2` | [design](docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md) | [plan](docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md) | 4/4 | [review](.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/review.md) | — | — |
| `D1.2` | Acquisition, recording, projection, and pinning contract design | `verified` | `D1.1` | [design](docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md) | [plan](docs/superpowers/plans/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts.md) | 4/4 | [review](.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/review.md) | — | — |
| `D1.3` | Reviewed q4xpcc Phase 24A handoff | `verified` | `D1.2` | [design](docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md) | [plan](docs/superpowers/plans/2026-09-05-d1-3-q4xpcc-handoff.md) | 4/4 | [review](.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/review.md) | — | — |
| `S1.1` | Edition-pinned standards baseline and traceability contract | `queued` | `C4.4` | — | — | — | — | — | — |
| `S2.1` | ARINC 717 profile specification | `blocked` | `S1.1`, `R1.7` | — | — | — | — | `queued` | Licensed edition-pinned source is unavailable. |
| `S2.2` | ARINC 717 codec and conformance corpus | `blocked` | `S2.1` | — | — | — | — | `queued` | Licensed edition-pinned source is unavailable. |
| `S3.1` | ARINC 647A/FRED configuration boundary | `blocked` | `S1.1` | — | — | — | — | `queued` | Licensed edition-pinned source is unavailable. |
| `S4.1` | ARINC 429 profile for a concrete source or target | `blocked` | `S1.1` | — | — | — | — | `queued` | A licensed source and concrete use case are unavailable. |
| `F1.1` | AC 120-82 terminology, analysis ports, profiles, evidence, and finding contracts | `queued` | `C4.4`, `R1.7` | [architecture](docs/architecture/xplane_fdau_core_scope_amendment.md) | — | 0/4 | — | — | — |
| `F1.2` | Evidence qualification, flight/phase segmentation, and derived-parameter provenance | `queued` | `F1.1`, `A1.7` | [architecture](docs/architecture/xplane_fdau_core_scope_amendment.md) | — | 0/4 | — | — | — |
| `F1.3` | Versioned event sets, prerequisites, detection, and severity | `queued` | `F1.2` | [architecture](docs/architecture/xplane_fdau_core_scope_amendment.md) | — | 0/4 | — | — | — |
| `F1.4` | Candidate/validated finding lifecycle and auditable review records | `queued` | `F1.3` | [architecture](docs/architecture/xplane_fdau_core_scope_amendment.md) | — | 0/4 | — | — | — |
| `F1.5` | Comparable-profile aggregation, trend analysis, and report projections | `queued` | `F1.4` | [architecture](docs/architecture/xplane_fdau_core_scope_amendment.md) | — | 0/4 | — | — | — |
| `F1.6` | De-identification/security/retention policy ports and end-to-end analysis conformance | `queued` | `F1.5` | [architecture](docs/architecture/xplane_fdau_core_scope_amendment.md) | — | 0/4 | — | — | — |
| `T1.1` | Markdown authority contract and explicit inventory normalization | `verified` | `M0` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | [plan](docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md) | 4/4 | [review](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/review.md) | — | — |
| `T1.2` | Typed parser, status report, and versioned JSON | `verified` | `T1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | [plan](docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md) | 4/4 | [review](.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/review.md) | — | — |
| `T1.3` | Structural audit and spec/plan adherence | `verified` | `T1.2` | [design](docs/superpowers/specs/2026-09-05-t1-3-audit-policy-supplement-design.md) | [plan](docs/superpowers/plans/2026-09-05-t1-3-structural-audit.md) | 4/4 | [review](.superpowers/sdd/2026-09-05-t1-3-structural-audit/review.md) | — | — |
| `T1.4` | Deterministic next-action selection | `implemented` | `T1.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | [plan](docs/superpowers/plans/2026-09-06-t1-4-deterministic-next-action-selection.md) | 0/4 | — | — | — |
| `T1.5` | Guarded child-state and gate-evidence mutations | `specified` | `T1.3`, `T1.4` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/5 | — | — | — |
| `T1.6` | Skill, session-entry, hygiene, and artifact closure | `specified` | `T1.5` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/5 | — | — | — |
| `T2.1` | Project repository-hygiene adapter and fresh artifact verification | `specified` | `T1.6` | [design](docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md) | — | 0/5 | — | — | — |
| `T2.2` | Governed dependency and toolchain refresh | `specified` | `T2.1` | [design](docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md) | — | 0/4 | — | — | — |
| `T3.1` | Guarded Git synchronization adapter | `specified` | `T2.1` | [design](docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md) | — | 0/5 | — | — | — |

## Local-child acceptance gates

### B1.1 — Source-layout migration and installed-import isolation

- [ ] The complete runtime package exists only under `src/xplane_fdau` and
      `uv_build` uses `module-root = "src"`.
- [ ] Quality, coverage, import-boundary, documentation, and release tooling
      address the new physical source root without weakening existing checks.
- [ ] Repository-root and installed-wheel tests prove imports resolve through
      the installed project rather than a top-level checkout package.
- [ ] Wheel members and public imports remain unchanged while source-archive
      members use the required `src/xplane_fdau` path.
- [ ] The full quality, strict documentation, distribution, and
      installed-artifact gates pass with no release, tag, or package publication.

### C1.1 — Canonical JSON and binary64/integer encoding

- [ ] Exact UTF-8, Unicode, object-key, array, string-escaping, and final-LF
      vectors pass.
- [ ] Signed 64-bit integer and finite binary64 canonical lexical vectors pass.
- [ ] Duplicate keys, non-NFC/surrogate text, overflow, and non-finite values
      fail with exact error context.
- [ ] Canonical bytes and SHA-256 results are deterministic without relying on
      incidental `json.dumps()` float spelling.

### C1.2 — Identity, hashing, references, authority, and provenance

- [ ] Semantic IDs, revisions, UUIDs, generations, and sequences enforce exact
      syntax and range.
- [ ] Definition and record self-hashes use the specified canonical preimages.
- [ ] Definition/record references pin identity, revision/version, and hash.
- [ ] Authority, provenance, and producer values are immutable and round-trip.

### C1.3 — Typed values and content-addressed payload references

- [ ] Boolean, integer, real, string, enumeration, vector, array, and byte-only
      representations retain exact type and order.
- [ ] Boolean/numeric coercion, unauthorized nulls, invalid shapes, and invalid
      enum values fail closed.
- [ ] Payload references preserve media type, length, hash, role, and retention
      status without reading storage.
- [ ] Programmatic and loaded validation produce equivalent property paths.

### C1.4 — Clock domains, UTC instants, anchors, and simulator timing

- [ ] Clock domains/readings preserve unit, resolution, origin, scope, and
      producer identity.
- [ ] UTC instants preserve exact nanosecond text and explicit `Z`.
- [ ] Same-domain comparison succeeds while unrelated-domain comparison fails.
- [ ] Clock anchors, uncertainty, source timing, simulator timing, replay/pause,
      cycle, and acquisition-phase values round-trip without invention.

### C1.5 — Validity states and acquisition-quality vocabulary

- [ ] Validity is a closed state independent of quality flags.
- [ ] Quality flags are closed, unique, and lexically ordered.
- [ ] Empty quality flags do not manufacture validity.
- [ ] Operational findings and tolerances cannot enter acquisition quality.

### C2.1 — Measurement-definition model and semantic invariants

- [ ] Representation-specific, unit/unitless, frame/datum/axis, precision,
      resolution, range, and enumeration invariants pass.
- [ ] Freshness, interpolation, discontinuity, sensitivity, applicability, and
      provenance fields are explicit.
- [ ] Irrelevant representation fields and semantic revision mismatches fail.
- [ ] Synthetic definitions are immutable, hash-stable, and round-trip.

### C2.2 — Measurement catalog, schema, ordering, and references

- [ ] Catalog ID/revision/hash, authority, provenance, scope, and definition
      ordering are exact.
- [ ] Duplicate or noncanonical definition order fails closed.
- [ ] Version-1 measurement-catalog schema matches runtime shape.
- [ ] No provider resource identity or stock X-Plane catalog content ships.

### C2.3 — Source-binding definition and transform references

- [ ] Each binding pins one exact measurement reference.
- [ ] Provider/adapter, resource, expected/observed shape boundary, native unit,
      applicability, dependencies, companions, phase, and replay policy are
      explicit.
- [ ] Transform/calibration references contain identity and data-only parameters,
      never executable expressions.
- [ ] Failure dispositions and irrelevant fields fail closed.

### C2.4 — Binding catalog and pure cross-catalog validation

- [ ] Binding catalog identity, ordering, uniqueness, schema, and hashes pass.
- [ ] Missing or mismatched measurement references fail.
- [ ] Direct bindings enforce unit/representation/shape/payload/applicability parity.
- [ ] Failure dispositions incompatible with measurement quality or validity
      authorization fail during cross-catalog validation.
- [ ] Transformed bindings validate declarations without executing or claiming algorithm
      conformance.

### C3.1 — Raw-observation record and schema

- [ ] Provider/adapter/resource, generations, type/shape, timing, status, and
      value evidence round-trip exactly.
- [ ] Inline value, payload reference, and absent value are mutually exclusive.
- [ ] Status/value combinations enforce the approved matrix.
- [ ] Receiver timing is never relabeled as source timing.

### C3.2 — Measurement-sample record and schema

- [ ] Sample/session/stream/epoch/sequence and exact definition references pass.
- [ ] Normalized value/unit, applied transforms, validity, quality, and freshness
      obey local invariants.
- [ ] Absent or failed normalization cannot contain a fabricated value.
- [ ] Version-1 sample schema matches runtime shape and canonical hash.

### C3.3 — Raw/sample lineage and cross-contract validation

- [ ] Every sample reaches every consumed observation through a complete record or
      immutable record reference.
- [ ] Ordered derivation algorithm inputs remain intact and cycle-free within the
      supplied validation closure.
- [ ] Catalog-resolved sample representation, unit, payload, range, binding, status, and
      quality validation passes.
- [ ] Missing, mismatched, or stale lineage fails with exact context.

### C3.4 — Measurement-frame record and schema

- [ ] Frame identity, acquisition instant, samples, observations, producer, and
      limitations round-trip.
- [ ] Complete raw observations preserve arrival order.
- [ ] Samples preserve canonical semantic order and use frame-local observation
      references.
- [ ] Version-1 frame schema matches runtime shape and canonical hash.

### C3.5 — Frame closure, canonical ordering, and validation

- [ ] Sample and observation identities are unique and reference closure is
      complete.
- [ ] Noncanonical sample order fails rather than being silently rewritten.
- [ ] Frame/session/stream/epoch/timing conflicts fail with exact context.
- [ ] Multiple corroborating bindings for one measurement are accepted.

### C4.1 — Schema resource parity and version inventory

- [ ] All five version-1 schema resources have exact IDs and family mappings.
- [ ] Packaged and documentation schema copies are byte-identical.
- [ ] Schema inventory rejects missing, duplicate, or unrecognized families.
- [ ] Installed resources contain no provider or standards implementation.

### C4.2 — Accepted, rejected, and canonical conformance corpus

- [ ] Manifest covers accepted, rejected, and canonical cases for every family.
- [ ] Rejected cases pin expected error class and JSON property path.
- [ ] Accepted cases pin canonical bytes and SHA-256.
- [ ] Boundary corpus covers numeric, Unicode, timing, ordering, lineage, and
      reference semantics.

### C4.3 — Public API and contract documentation closure

- [ ] Root package remains version-only; semantic packages expose exact owned
      names.
- [ ] Documentation distinguishes measurement/binding, observation/sample,
      FDAU/ARINC frames, and acquisition/operational quality.
- [ ] Native FDR APIs and documentation remain unchanged and green.
- [ ] Runtime import-boundary tests reject providers, hosts, networks, and
      third-party imports.

### C4.4 — Built/installed artifact matrix and independent review

- [ ] Complete `unittest` and repository quality gates pass.
- [ ] Fresh wheel/sdist contain exact schemas, fixtures/resources, and no runtime
      dependency or provider content.
- [ ] Installed-wheel smoke passes on Python 3.12, 3.13, and 3.14 outside the
      checkout.
- [ ] Independent review has no unresolved load-bearing finding.
- [ ] Version `0.1.0` remains unreleased and no release tag or package
      publication occurs; separately authorized routine Git sync does not
      satisfy or violate this release gate.

### D1.1 — Canonical C1–C4 design approval

- [x] the canonical design has approved governance metadata and no unresolved
      placeholder, contradiction, ambiguity, or load-bearing review finding; —
      Evidence: [verification](.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-1.md)
- [x] canonical JSON, hashing, identity, provenance, measurement, binding, raw
      observation, sample, frame, clock/timing, validity, quality, schema, fixture,
      and Python/native conformance decisions are exact and versioned; — Evidence:
      [verification](.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-2.md)
- [x] ownership and dependency direction remain consistent with the approved
      scope amendment and distinguish FDAU acquisition quality from q4xpcc
      operational policy and findings; and — Evidence:
      [verification](.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-3.md)
- [x] the approved design is linked from `C1.1` through `C4.4`, and those children
      advance only to `specified`, with zero delivery gates satisfied and no
      implementation-plan, review, artifact, or release evidence. — Evidence:
      [verification](.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-4.md)

### D1.2 — Acquisition, recording, projection, and pinning contract design

- [x] this one approved design fixes the A1/R1/P1 contract shapes and policies needed by
      all four q4xpcc Phase 24A Slice 2 plans, including acquisition, continuity,
      fan-out, recording, recovery, replay, native-FDR projection, deployment, and
      conformance planning surfaces; — Evidence:
      [verification](.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-1.md)
- [x] every family has an exact identity/version boundary, fields, invariants,
      references, runtime outcomes, error boundary, delivery ownership boundary, and
      future schema/conformance path, with closed failure codes and deterministic
      validation/causal precedence; — Evidence:
      [verification](.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-2.md)
- [x] installed-wheel and reproducibly bundled deployment, independently trusted
      expected version/revision/artifact/conformance pins, mode-specific metadata
      evidence, delivered-file hashes, conformance, and closed-world no-divergent-subset
      proof are explicit without requiring or fabricating a current release; and — Evidence:
      [verification](.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-3.md)
- [x] independent review reports no unresolved load-bearing ambiguity; native FDR,
      ARINC, FDM/FOQA, q4xpcc, and external-client boundaries remain consistent with the
      approved scope amendment; the approved contract-only design is recorded as binding
      input for later A1/R1/P1 specifications; and every implementation, schema,
      fixture, artifact, adoption, release, push, tag, and publication gate remains
      unsatisfied without advancing any A1, R1, P1, S, or F1 child. — Evidence:
      [verification](.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-4.md)

### D1.3 — Reviewed q4xpcc Phase 24A handoff

- [x] D1.1 and D1.2 are verified with committed review evidence and no unresolved
      load-bearing finding; — Evidence:
      [verification](.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/gate-1.md)
- [x] `HANDOFF.md` and the concise q4xpcc brief agree with the approved designs
      and distinguish design readiness from implementation and adoption; — Evidence:
      [verification](.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/gate-2.md)
- [x] the brief is emitted from a clean committed state and identifies its exact
      local HEAD revision; and — Evidence:
      [verification](.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/gate-3.md)
- [x] successful D1.3 verification makes the statusless `I1.0` handoff condition
      eligible to be reported as the next action without changing `I1.1`, `I1.2`,
      G1, release, push, tag, or publication authorization. — Evidence:
      [verification](.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/gate-4.md)

### F1.1 — AC 120-82 terminology, analysis ports, profiles, evidence, and finding contracts

- [ ] A reviewed local specification maps FAA AC 120-82 technical concepts to
      X-Plane-specific core contracts without claiming an approved FOQA
      program.
- [ ] Standard-library-only input/output ports define canonical evidence,
      versioned analysis profiles, candidate findings, and validated findings.
- [ ] Acquisition quality and operational findings are distinct types with
      explicit provenance and no simulator or host imports.
- [ ] Schema, API, fixture, installed-wheel, and independent-review evidence
      passes on Python 3.12, 3.13, and 3.14.

### F1.2 — Evidence qualification, flight/phase segmentation, and derived-parameter provenance

- [ ] Evidence qualification consumes canonical validity, timing, continuity,
      and lineage without silently accepting incomplete input.
- [ ] Flight and phase segmentation is deterministic under an explicit,
      versioned profile and preserves boundary rationale.
- [ ] Every derived parameter records its algorithm identity, inputs, units,
      version, and loss/quality disposition.
- [ ] Accepted/rejected fixtures, replay equivalence, installed-wheel tests,
      and independent review pass without transport dependencies.

### F1.3 — Versioned event sets, prerequisites, detection, and severity

- [ ] Event definitions declare required measurements, units, sampling and
      continuity assumptions, aircraft/profile context, and source authority.
- [ ] Event-set and rule versions are immutable identities and historical
      results retain the version that produced them.
- [ ] Detection and severity classification are deterministic for live-fed and
      replayed canonical evidence with identical inputs.
- [ ] Boundary, missing-evidence, derived-value, and conformance fixtures plus
      independent review pass across Python 3.12-3.14.

### F1.4 — Candidate/validated finding lifecycle and auditable review records

- [ ] Threshold detection produces a candidate finding and never silently
      equates it with a validated operational event.
- [ ] Review records preserve reviewer role, disposition, rationale, evidence
      references, timestamps, and prior state without owning identity custody.
- [ ] Invalid, duplicate, stale-profile, and conflicting-review transitions
      fail closed with typed errors and retained audit context.
- [ ] Deterministic lifecycle fixtures, installed-wheel tests, and independent
      review pass without embedding organizational authorization policy.

### F1.5 — Comparable-profile aggregation, trend analysis, and report projections

- [ ] Aggregation groups findings by explicit dimensions and retains counts,
      denominators, profile versions, and evidence-quality exclusions.
- [ ] Trend comparisons reject incompatible definitions or normalize them
      through an explicit, provenance-bearing policy.
- [ ] Reports are deterministic projections from preserved findings and
      aggregates rather than the system of record.
- [ ] Statistical boundary fixtures, replay equivalence, installed-wheel
      verification, and independent review pass using only the standard library.

### F1.6 — De-identification/security/retention policy ports and end-to-end analysis conformance

- [ ] De-identification is an explicit, testable, provenance-bearing
      transformation and never an undocumented field deletion.
- [ ] Classification, access, retention, correction, and feedback metadata use
      ports that leave enforcement and organizational authority to clients.
- [ ] End-to-end canonical evidence through findings, review, aggregation, and
      reports is deterministic and preserves all version boundaries.
- [ ] Security, privacy, artifact-exclusion, Python 3.12-3.14, documentation,
      and independent-review gates pass without regulatory claims.

### T1.1 — Markdown authority contract and explicit inventory normalization

- [x] Roadmap milestones, epics, local children, release gates, and external
      boundaries have exact nonoverlapping contracts. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-1.md)
- [x] `BACKLOG.md` is the only mutable delivery-state authority. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-2.md)
- [x] Every local child has one explicit inventory row; external boundaries
      have no local delivery status. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-3.md)
- [x] Existing specs and plans have valid governance metadata or an explicit
      historical disposition. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-4.md)

### T1.2 — Typed parser, status report, and versioned JSON

- [x] Frozen typed models and the strict Markdown parser pass valid and
      malformed fixture cases. — Evidence: [verification](.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-1.md)
- [x] Human status reports the complete roadmap inventory and local delivery
      state without inferring completion. — Evidence: [verification](.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-2.md)
- [x] JSON schema version 1 matches the exact documented shape and ordering. — Evidence: [verification](.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-3.md)
- [x] The migrated current repository parses and reports without a structural
      finding. — Evidence: [verification](.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-4.md)

### T1.3 — Structural audit and spec/plan adherence

- [x] Identity, kind, dependency, cycle, lifecycle, gate-count, and link rules
      fail closed with stable finding codes. — Evidence: [verification](.superpowers/sdd/2026-09-05-t1-3-structural-audit/gate-1.md)
- [x] Multi-child governing designs, single-child plans, and historical
      artifacts follow the exact metadata contract. — Evidence: [verification](.superpowers/sdd/2026-09-05-t1-3-structural-audit/gate-2.md)
- [x] Lifecycle prerequisites and eligible evidence are validated without
      treating presence as proof. — Evidence: [verification](.superpowers/sdd/2026-09-05-t1-3-structural-audit/gate-3.md)
- [x] Audit reports all independent findings with file, line, node, and exact
      context and returns a blocking result when required. — Evidence: [verification](.superpowers/sdd/2026-09-05-t1-3-structural-audit/gate-4.md)

### T1.4 — Deterministic next-action selection

- [ ] A selected local child resumes at its exact Superpowers lifecycle stage.
- [ ] With no selection, the first dependency-ready local child is recommended
      in roadmap order.
- [ ] Blocking findings or a blocked selected child stop recommendation without
      silent substitution.
- [ ] Milestones, epics, release gates, and external boundaries are never
      recommended as implementation children.

### T1.5 — Guarded child-state and gate-evidence mutations

- [ ] Every mutation is dry-run-first and requires explicit apply authority.
- [ ] Expected selection/state/gate values and target hashes reject stale
      changes.
- [ ] Selection and lifecycle transitions enforce the exact transition graph
      and prerequisites.
- [ ] Gate recording and reopening enforce the typed evidence contract.
- [ ] Candidate validation, atomic publication, failure cleanup, and unrelated
      Markdown preservation pass.

### T1.6 — Skill, session-entry, hygiene, and artifact closure

- [ ] Project-local skill triggers for status, resume, adherence, next action,
      and controlled state requests.
- [ ] Session instructions and the concise handoff pointer invoke the backlog
      workflow without creating another state authority.
- [ ] Full hygiene runs the strict backlog audit.
- [ ] Built and installed artifacts exclude all repository-governance tooling.
- [ ] All standard-library tests and independent review pass without changing
      release or publication authorization.

### T2.1 — Project repository-hygiene adapter and fresh artifact verification

- [ ] A deterministic project hygiene adapter supplies xplane-fdau commands to
      canonical `gzs-repository-hygiene` and runs status, offline lock, backlog
      audit, quality, strict documentation, and pre-commit gates at full
      strength.
- [ ] Every run builds one fresh wheel/sdist pair outside the checkout and
      validates exact metadata, members, payload bytes, and
      repository-governance exclusion.
- [ ] Successful temporary artifacts are safely removed while failed artifacts
      are preserved at a reported exact path for diagnosis.
- [ ] Routine hygiene performs no implicit network inquiry, repository
      mutation, or installed Python-version matrix and retains focused
      supporting skills.
- [ ] All standard-library tests, current-repository integration, artifact
      checks, and independent review pass without changing release
      authorization.

### T2.2 — Governed dependency and toolchain refresh

- [ ] Read-only human and JSON status discover the newest stable `uv`, supported Python
      matrix, locked graph, outdated releases, yanks, vulnerabilities, and constraints
      from official sources without mutation.
- [ ] Apply pins the exact verified stable `uv`, aligns package metadata to
      `>=3.12,<3.15`, retains compatible ordinary development constraints, refreshes the
      complete lock, and fails closed on stale scope, incompatible resolution, or
      unexplained security findings.
- [ ] Targeted `unittest`, full repo hygiene, Python 3.12-3.14 source and
      installed-wheel verification, and exact wheel/sdist inventory all pass.
- [ ] Superpowers, X-Plane deployment, staging, commit, push, tag, publication, and
      release behavior is absent from the skill and implementation.

### T3.1 — Guarded Git synchronization adapter

- [ ] Dry-run and JSON reports deterministically expose branch, remote, scope,
      ahead/behind/divergence, actions, warnings, blockers, and expected state.
- [ ] Apply revalidates pinned state, performs reviewed auto-add, full hygiene,
      intentional commit, fast-forward pull or rebase of unpublished commits, an
      explicitly authorized ordinary push, and a fresh final fetch/alignment check.
- [ ] Detached, conflicting, stale, unexpected, missing-remote, failed-fetch,
      failed-hygiene, merge-head, published-history-rewrite, failed-push, and
      failed-alignment states fail closed without partial unsafe continuation.
- [ ] An explicitly authorized ordinary push finishes only after proof that local and
      remote are `ahead=0`, `behind=0`; no tag, publication, release, force,
      destructive-reset, or verification-bypass path exists.
- [ ] Temporary-repository tests, current-repository dry-run, complete quality gates,
      and independent review pass without changing release authorization.

## Release-gate dashboard

Release-gate readiness is derived from its prerequisites and evidence. A gate
is not a selectable implementation child.

| Gate | Outcome | Gate state | Prerequisites | Evidence |
| --- | --- | --- | --- | --- |
| `G1` | Canonical vertical-slice reconciliation | `waiting` | `C4.4`, `A1.9`, `R1.7`, `P1.6` | — |

## External consumer and downstream boundaries

Reusable FDM/FOQA mechanics are local `F1` work. Approved-program governance,
identity custody, corrective-action authority, protections, and regulatory
claims remain external and separately authorized; neither local analysis work
nor release gate `G1` confers them.

These boundaries are report-only. They have no local delivery status and cannot
be selected or mutated by xplane-fdau tooling.

| Boundary | Owner | xplane-fdau handoff condition |
| --- | --- | --- |
| `I1.0` | q4xpcc | Phase 24A specification and plan reconciliation may begin after `D1.3`. |
| `I1.1` | q4xpcc | Contract/fixture adoption may begin after `C4.4`. |
| `I1.2` | q4xpcc | Live XPLM acquisition adoption may begin after `A1.9`. |
| `I2.1` | xpwebapi adapter owner | Corroboration-adapter work may begin after `C4.4`. |
| `F2.1` | Authorized external organization | Program approval, identity custody, corrective-action authority, protections, and regulatory claims require separate organizational authority. |

## Backlog rules

1. Point Superpowers to this file at the start of a run.
2. Select one primary child slice with satisfied prerequisites.
3. A governing design may cover an ordered set of exact children; an
   implementation plan covers exactly one child.
4. A child needs an approved spec before `specified` and an approved plan before
   `planned`.
5. Plan tasks remain beneath the child; they do not become competing backlog
   items.
6. New requirements enter as a child or an explicit gate amendment, never an
   untracked plan expansion.
7. Gate counts and checkboxes change in the same commit as their evidence.
8. `verified` requires every child gate and independent review to pass.
9. Cross-cutting documentation may change during a run, but only the selected
   child may be claimed complete.
10. `released` requires separate authorization; no current item is authorized
   for release.
