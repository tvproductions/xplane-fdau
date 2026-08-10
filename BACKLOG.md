# xplane-fdau Backlog

- **Status:** Active delivery ledger and Superpowers entry point
- **Updated:** 2026-08-09

Read `ROADMAP.md` for architecture order and dependencies. Then use this file to
select one primary child slice whose prerequisites are verified. Each child
slice receives one focused plan and one independently reviewable outcome.

## Current position

- `M0` FDAU identity/native-FDR migration: `verified`.
- Active design: Source-layout migration and installed-import isolation.
- Active child slice: `B1.1` source-layout migration.
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

## Build-foundation child dashboard

The governing [source-layout design](docs/superpowers/specs/2026-08-09-src-layout-migration-design.md)
covers the selected pre-canonical build correction.

| Child | Outcome | Status | Depends on | Spec | Plan | Gates |
| --- | --- | --- | --- | --- | --- | --- |
| `B1.1` | Source-layout migration and installed-import isolation | `designing` | `M0` | [design](docs/superpowers/specs/2026-08-09-src-layout-migration-design.md) | — | 0/5 |

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

## Canonical-contract child dashboard

All canonical child slices are governed by the current draft
[canonical-contract design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md).
`C1.1` remains `designing` while its written review is pending. After written
approval, the covered children become `specified`; each receives its own plan
when it is selected for execution.

| Child | Outcome | Status | Depends on | Plan | Gates |
| --- | --- | --- | --- | --- | --- |
| `C1.1` | Canonical JSON and number encoding | `designing` | `B1.1` | — | 0/4 |
| `C1.2` | Identity, hashes, references, authority, provenance | `queued` | `C1.1` | — | 0/4 |
| `C1.3` | Typed values and payload references | `queued` | `C1.2` | — | 0/4 |
| `C1.4` | Clock domains, UTC, anchors, simulator timing | `queued` | `C1.2` | — | 0/4 |
| `C1.5` | Validity and quality vocabulary | `queued` | `C1.2` | — | 0/4 |
| `C2.1` | Measurement-definition model | `queued` | `C1.3`, `C1.5` | — | 0/4 |
| `C2.2` | Measurement catalog and schema | `queued` | `C2.1` | — | 0/4 |
| `C2.3` | Source-binding definition | `queued` | `C2.2` | — | 0/4 |
| `C2.4` | Binding catalog and cross-validation | `queued` | `C2.3` | — | 0/4 |
| `C3.1` | Raw-observation record and schema | `queued` | `C1.3`–`C1.5`, `C2.4` | — | 0/4 |
| `C3.2` | Measurement-sample record and schema | `queued` | `C3.1` | — | 0/4 |
| `C3.3` | Raw/sample lineage and validation | `queued` | `C3.2` | — | 0/4 |
| `C3.4` | Measurement-frame record and schema | `queued` | `C3.3` | — | 0/4 |
| `C3.5` | Frame closure, ordering, and validation | `queued` | `C3.4` | — | 0/4 |
| `C4.1` | Schema parity and version inventory | `queued` | `C3.5` | — | 0/4 |
| `C4.2` | Cross-language conformance corpus | `queued` | `C4.1` | — | 0/4 |
| `C4.3` | Public APIs and documentation | `queued` | `C4.2` | — | 0/4 |
| `C4.4` | Artifact matrix and independent review | `queued` | `C4.3` | — | 0/5 |

Gate counts are derived from the checklists below and change only with committed
evidence.

## Canonical-contract acceptance gates

### C1.1 — Canonical JSON and number encoding

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

### C1.3 — Typed values and payload references

- [ ] Boolean, integer, real, string, enumeration, vector, array, and byte-only
      representations retain exact type and order.
- [ ] Boolean/numeric coercion, unauthorized nulls, invalid shapes, and invalid
      enum values fail closed.
- [ ] Payload references preserve media type, length, hash, role, and retention
      status without reading storage.
- [ ] Programmatic and loaded validation produce equivalent property paths.

### C1.4 — Clock domains, UTC, anchors, and simulator timing

- [ ] Clock domains/readings preserve unit, resolution, origin, scope, and
      producer identity.
- [ ] UTC instants preserve exact nanosecond text and explicit `Z`.
- [ ] Same-domain comparison succeeds while unrelated-domain comparison fails.
- [ ] Clock anchors, uncertainty, source timing, simulator timing, replay/pause,
      cycle, and acquisition-phase values round-trip without invention.

### C1.5 — Validity and acquisition quality

- [ ] Validity is a closed state independent of quality flags.
- [ ] Quality flags are closed, unique, and lexically ordered.
- [ ] Empty quality flags do not manufacture validity.
- [ ] Operational findings and tolerances cannot enter acquisition quality.

### C2.1 — Measurement-definition model

- [ ] Representation-specific, unit/unitless, frame/datum/axis, precision,
      resolution, range, and enumeration invariants pass.
- [ ] Freshness, interpolation, discontinuity, sensitivity, applicability, and
      provenance fields are explicit.
- [ ] Irrelevant representation fields and semantic revision mismatches fail.
- [ ] Synthetic definitions are immutable, hash-stable, and round-trip.

### C2.2 — Measurement catalog and schema

- [ ] Catalog ID/revision/hash, authority, provenance, scope, and definition
      ordering are exact.
- [ ] Duplicate or noncanonical definition order fails closed.
- [ ] Version-1 measurement-catalog schema matches runtime shape.
- [ ] No provider resource identity or stock X-Plane catalog content ships.

### C2.3 — Source-binding definition

- [ ] Each binding pins one exact measurement reference.
- [ ] Provider/adapter, resource, expected/observed shape boundary, native unit,
      applicability, dependencies, companions, phase, and replay policy are
      explicit.
- [ ] Transform/calibration references contain identity and data-only parameters,
      never executable expressions.
- [ ] Failure dispositions and irrelevant fields fail closed.

### C2.4 — Binding catalog and cross-validation

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

### C3.3 — Raw/sample lineage and validation

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

### C3.5 — Frame closure, ordering, and validation

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

### C4.2 — Cross-language conformance corpus

- [ ] Manifest covers accepted, rejected, and canonical cases for every family.
- [ ] Rejected cases pin expected error class and JSON property path.
- [ ] Accepted cases pin canonical bytes and SHA-256.
- [ ] Boundary corpus covers numeric, Unicode, timing, ordering, lineage, and
      reference semantics.

### C4.3 — Public API and documentation

- [ ] Root package remains version-only; semantic packages expose exact owned
      names.
- [ ] Documentation distinguishes measurement/binding, observation/sample,
      FDAU/ARINC frames, and acquisition/operational quality.
- [ ] Native FDR APIs and documentation remain unchanged and green.
- [ ] Runtime import-boundary tests reject providers, hosts, networks, and
      third-party imports.

### C4.4 — Artifact matrix and independent review

- [ ] Complete `unittest` and repository quality gates pass.
- [ ] Fresh wheel/sdist contain exact schemas, fixtures/resources, and no runtime
      dependency or provider content.
- [ ] Installed-wheel smoke passes on Python 3.12, 3.13, and 3.14 outside the
      checkout.
- [ ] Independent review has no unresolved load-bearing finding.
- [ ] Version `0.1.0` remains unreleased and no push/tag/publication occurs.

## Future release-path child dashboard

These child boundaries are architectural backlog. Their acceptance gates become
measurable when each governing specification is reviewed; none is implementation
authority yet.

| Child range | Epic outcome | Status | Entry dependency |
| --- | --- | --- | --- |
| `A1.1`–`A1.9` | Profiles, demand, transforms, lifecycle, cadence, continuity, fan-out, acquisition session | `queued` | `C4.4` |
| `R1.1`–`R1.7` | Descriptor, archive, writer, manifest, recovery, replay, long-session closure | `queued` | `A1.9` |
| `P1.1`–`P1.6` | Profiles, native spine/DREF projection, timing, loss report, sink closure | `queued` | `R1.7` |
Exact child names and dependencies are defined in `ROADMAP.md`. Do not merge an
epic back into one plan when its design begins.

## Release-gate dashboard

Release-gate readiness is derived from its prerequisites and evidence. A gate
is not a selectable implementation child.

| Gate | Outcome | Gate state | Prerequisites | Evidence |
| --- | --- | --- | --- | --- |
| `G1` | Independent canonical vertical-slice reconciliation | `waiting` | `C4.4`, `A1.9`, `R1.7`, `P1.6` | — |

## Standards child dashboard

These are local xplane-fdau children. External licensed-source requirements are
recorded as blocking reasons rather than invented local dependencies.

| Child | Work | Status | Depends on | External prerequisite | Spec | Plan | Gates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `S1.1` | Standards baseline and traceability contract | `queued` | `C4.4` | — | — | — | — |
| `S2.1` | ARINC 717 profile specification | `blocked` | `S1.1`, `R1.7` | Licensed edition-pinned source | — | — | — |
| `S2.2` | ARINC 717 codec and conformance corpus | `blocked` | `S2.1` | Licensed edition-pinned source | — | — | — |
| `S3.1` | ARINC 647A/FRED configuration boundary | `blocked` | `S1.1` | Licensed edition-pinned source | — | — | — |
| `S4.1` | ARINC 429 concrete profile | `blocked` | `S1.1` | Licensed source and concrete use case | — | — | — |

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

## Repository governance tooling

The governing [T1 design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md)
covers the six run-sized tooling children below. Each child receives its own
implementation plan when selected.

| Child | Work | Status | Depends on | Spec | Plan | Gates |
| --- | --- | --- | --- | --- | --- | --- |
| `T1.1` | Markdown authority contract and inventory normalization | `designing` | `M0` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/4 |
| `T1.2` | Typed parser, status report, and versioned JSON | `queued` | `T1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/4 |
| `T1.3` | Structural audit and spec/plan adherence | `queued` | `T1.2` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/4 |
| `T1.4` | Deterministic next-action selection | `queued` | `T1.3` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/4 |
| `T1.5` | Guarded child-state and gate-evidence mutations | `queued` | `T1.3`, `T1.4` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/5 |
| `T1.6` | Skill, session-entry, hygiene, and artifact closure | `queued` | `T1.5` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | — | 0/5 |

### T1.1 — Markdown authority contract and inventory normalization

- [ ] Roadmap milestones, epics, local children, release gates, and external
      boundaries have exact nonoverlapping contracts.
- [ ] `BACKLOG.md` is the only mutable delivery-state authority.
- [ ] Every local child has one explicit inventory row; external boundaries
      have no local delivery status.
- [ ] Existing specs and plans have valid governance metadata or an explicit
      historical disposition.

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
