# xplane-fdau Backlog

- **Status:** Active delivery ledger and Superpowers entry point
- **Updated:** 2026-08-15

Read `ROADMAP.md` for architecture order and dependencies. Then use this file to
select one primary child slice whose prerequisites are verified. Each child
slice receives one focused plan and one independently reviewable outcome.

## Current position

- `M0` FDAU identity/native-FDR migration: `verified`.
- Active design: Repository backlog-governance tooling.
- Active child: `T1.1`.
- `B1.1` source-layout migration: `specified` with a draft plan; resumes after
  `T3.1` is verified.
- Canonical contract design: written review remains pending for `C1.1`.
- Release: prohibited.
- Push/tag/publication: prohibited.

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
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `B1.1` | Source-layout migration and installed-import isolation | `specified` | `T3.1` | [design](docs/superpowers/specs/2026-08-09-src-layout-migration-design.md) | [draft plan](docs/superpowers/plans/2026-08-09-src-layout-migration.md) | 0/5 | — | — | — |
| `C1.1` | Canonical JSON and binary64/integer encoding | `designing` | `B1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.2` | Identity, hashing, references, authority, and provenance | `queued` | `C1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.3` | Typed values and content-addressed payload references | `queued` | `C1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.4` | Clock domains, UTC instants, anchors, and simulator timing | `queued` | `C1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C1.5` | Validity states and acquisition-quality vocabulary | `queued` | `C1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.1` | Measurement-definition model and semantic invariants | `queued` | `C1.3`, `C1.5` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.2` | Measurement catalog, schema, ordering, and references | `queued` | `C2.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.3` | Source-binding definition and transform references | `queued` | `C2.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C2.4` | Binding catalog and pure cross-catalog validation | `queued` | `C2.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.1` | Raw-observation record and schema | `queued` | `C1.3`, `C1.4`, `C1.5`, `C2.4` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.2` | Measurement-sample record and schema | `queued` | `C3.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.3` | Raw/sample lineage and cross-contract validation | `queued` | `C3.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.4` | Measurement-frame record and schema | `queued` | `C3.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C3.5` | Frame closure, canonical ordering, and validation | `queued` | `C3.4` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.1` | Schema resource parity and version inventory | `queued` | `C3.5` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.2` | Accepted, rejected, and canonical conformance corpus | `queued` | `C4.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.3` | Public API and contract documentation closure | `queued` | `C4.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/4 | — | — | — |
| `C4.4` | Built/installed artifact matrix and independent review | `queued` | `C4.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | — | 0/5 | — | — | — |
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
| `S1.1` | Edition-pinned standards baseline and traceability contract | `queued` | `C4.4` | — | — | — | — | — | — |
| `S2.1` | ARINC 717 profile specification | `blocked` | `S1.1`, `R1.7` | — | — | — | — | `queued` | Licensed edition-pinned source is unavailable. |
| `S2.2` | ARINC 717 codec and conformance corpus | `blocked` | `S2.1` | — | — | — | — | `queued` | Licensed edition-pinned source is unavailable. |
| `S3.1` | ARINC 647A/FRED configuration boundary | `blocked` | `S1.1` | — | — | — | — | `queued` | Licensed edition-pinned source is unavailable. |
| `S4.1` | ARINC 429 profile for a concrete source or target | `blocked` | `S1.1` | — | — | — | — | `queued` | A licensed source and concrete use case are unavailable. |
| `T1.1` | Markdown authority contract and explicit inventory normalization | `reviewed` | `M0` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | [plan](docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md) | 4/4 | [review](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/review.md) | — | — |
| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/4 | — | — | — |
| `T1.3` | Structural audit and spec/plan adherence | `specified` | `T1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/4 | — | — | — |
| `T1.4` | Deterministic next-action selection | `specified` | `T1.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/4 | — | — | — |
| `T1.5` | Guarded child-state and gate-evidence mutations | `specified` | `T1.3`, `T1.4` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/5 | — | — | — |
| `T1.6` | Skill, session-entry, hygiene, and artifact closure | `specified` | `T1.5` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/5 | — | — | — |
| `T2.1` | Canonical repo-hygiene and fresh artifact verification | `specified` | `T1.6` | [design](docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md) | — | 0/5 | — | — | — |
| `T3.1` | Guarded local Git synchronization with push disabled | `specified` | `T2.1` | [design](docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md) | — | 0/5 | — | — | — |

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
- [ ] Direct bindings enforce unit/representation/shape/applicability parity.
- [ ] Transformed bindings validate declarations without executing or claiming
      algorithm conformance.

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

- [ ] Every sample reaches one complete observation or immutable record reference.
- [ ] Ordered derivation-parent references remain intact and cycle-free within
      the supplied validation closure.
- [ ] Catalog-resolved sample representation, unit, range, binding, status, and
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
- [ ] Version `0.1.0` remains unreleased and no push/tag/publication occurs.

### T1.1 — Markdown authority contract and explicit inventory normalization

- [x] Roadmap milestones, epics, local children, release gates, and external
      boundaries have exact nonoverlapping contracts. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-1.md)
- [x] `BACKLOG.md` is the only mutable delivery-state authority. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-2.md)
- [x] Every local child has one explicit inventory row; external boundaries
      have no local delivery status. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-3.md)
- [x] Existing specs and plans have valid governance metadata or an explicit
      historical disposition. — Evidence: [verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-4.md)

### T1.2 — Typed parser, status report, and versioned JSON

- [ ] Frozen typed models and the strict Markdown parser pass valid and
      malformed fixture cases.
- [ ] Human status reports the complete roadmap inventory and local delivery
      state without inferring completion.
- [ ] JSON schema version 1 matches the exact documented shape and ordering.
- [ ] The migrated current repository parses and reports without a structural
      finding.

### T1.3 — Structural audit and spec/plan adherence

- [ ] Identity, kind, dependency, cycle, lifecycle, gate-count, and link rules
      fail closed with stable finding codes.
- [ ] Multi-child governing designs, single-child plans, and historical
      artifacts follow the exact metadata contract.
- [ ] Lifecycle prerequisites and eligible evidence are validated without
      treating presence as proof.
- [ ] Audit reports all independent findings with file, line, node, and exact
      context and returns a blocking result when required.

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

### T2.1 — Canonical repo-hygiene and fresh artifact verification

- [ ] The canonical `repo-hygiene` skill replaces `hygiene` and runs status,
      offline lock, backlog audit, quality, strict documentation, and pre-commit
      gates at full strength.
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

### T3.1 — Guarded local Git synchronization with push disabled

- [ ] Dry-run and JSON reports deterministically expose branch, remote, scope,
      ahead/behind/divergence, actions, warnings, blockers, and expected state.
- [ ] Apply revalidates pinned state, performs reviewed auto-add, full hygiene,
      intentional commit, fast-forward pull or rebase, and repairable merge-head
      backup/linearization with final verification.
- [ ] Detached, conflicting, stale, unexpected, missing-remote, failed-fetch,
      failed-hygiene, and unrepairable-merge states fail closed without partial
      unsafe continuation.
- [ ] Push is absent from both CLI and implementation, and no tag, publication,
      release, force, or verification-bypass path exists.
- [ ] Temporary-repository tests, current-repository dry-run, complete quality
      gates, and independent review pass without changing release
      authorization.

## Release-gate dashboard

Release-gate readiness is derived from its prerequisites and evidence. A gate
is not a selectable implementation child.

| Gate | Outcome | Gate state | Prerequisites | Evidence |
| --- | --- | --- | --- | --- |
| `G1` | Canonical vertical-slice reconciliation | `waiting` | `C4.4`, `A1.9`, `R1.7`, `P1.6` | — |

## External consumer and downstream boundaries

FDM/FOQA work remains downstream and separately governed; it is not part of the
canonical runtime or release gate.

These boundaries are report-only. They have no local delivery status and cannot
be selected or mutated by xplane-fdau tooling.

| Boundary | Owner | xplane-fdau handoff condition |
| --- | --- | --- |
| `I1.1` | q4xpcc | Contract/fixture adoption may begin after `C4.4`. |
| `I1.2` | q4xpcc | Live XPLM acquisition adoption may begin after `A1.9`. |
| `I2.1` | xpwebapi adapter owner | Corroboration-adapter work may begin after `C4.4`. |
| `F1.1` | Separate FDM project | Canonical archive consumption may begin after `R1.7`. |
| `F2.1` | External FOQA governance | Workflow and claims require separate organizational approval. |

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
