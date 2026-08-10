# xplane-fdau Roadmap

- **Status:** Active planning authority
- **Updated:** 2026-08-09
- **Decision owner:** Jeff / tvproductions

## Purpose

This roadmap connects the parent FDAU architecture to independently reviewable
delivery work. It answers what must exist, in what order, and which gates
prevent release. It is not a substitute for a design specification or an
implementation plan.

- `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md` owns the
  cross-project architecture.
- `ROADMAP.md` owns capability order, dependencies, epics, and release gates.
- `BACKLOG.md` is the durable Superpowers entry point and owns child-slice
  status, plan/spec links, and measurable acceptance gates.
- `docs/superpowers/specs/` owns reviewed semantic decisions.
- `docs/superpowers/plans/` owns executable test-first work for one child slice.
- `HANDOFF.md` remains a concise current-project checkpoint required by this
  repository's agent instructions; it is not a separate workflow system.

## Work hierarchy

The roadmap uses four levels:

| Level | Purpose | Executed directly? |
| --- | --- | --- |
| Architecture | Cross-project boundaries and final system shape | No |
| Epic | Related capability family such as canonical contracts or acquisition | No |
| Child slice | One independently testable, reviewable outcome | Yes—one primary child slice per agent run |
| Plan task | Test-first implementation steps inside one child slice | Yes—within that slice's run |

The former `C1`–`C4`, `A1`, `R1`, and `P1` labels are epics. They are not
implementation-plan units. A child slice receives its own specification link,
plan, status, and acceptance gates in `BACKLOG.md`.

## Status model

| Status | Meaning |
| --- | --- |
| `queued` | Ordered work exists, but its specification is not approved. |
| `designing` | Requirements and boundaries are under review. |
| `specified` | The written specification is approved. |
| `planned` | An approved executable implementation plan exists. |
| `in_progress` | Plan tasks are being implemented. |
| `implemented` | Approved plan tasks are complete, but review is not closed. |
| `reviewed` | Independent review is complete with no unresolved load-bearing finding. |
| `verified` | All child-slice acceptance gates pass with committed evidence. |
| `blocked` | A named external decision or prerequisite prevents progress. |
| `deferred` | Deliberately outside the active release path. |
| `released` | The verified slice is included in a published release. |

Progress is measured by verified gates and child slices, not hours, story
points, or percentage extrapolated from unequal work.

## Release path

```text
M0 Identity and native FDR kernel                                      verified
 |
 +-> C1 Foundation -> C2 Catalogs -> C3 Evidence records -> C4 Closure
      |
      +-> A1 Acquisition, lifecycle, continuity, and fan-out
           |
           +-> R1 Canonical archive, recovery, and replay
                |
                +-> P1 Canonical-to-native-FDR projection
                     |
                     +-> G1 Independent vertical-slice review
                          |
                          +-> separate 0.1.0 release decision
```

Each epic expands into the child slices below.

## C — Canonical semantic contract kernel

### C1 — Contract foundation epic

| Child | Outcome | Depends on | State |
| --- | --- | --- | --- |
| `C1.1` | Canonical JSON and binary64/integer encoding | `M0` | `designing` |
| `C1.2` | Identity, hashing, references, authority, and provenance | `C1.1` | `queued` |
| `C1.3` | Typed values and content-addressed payload references | `C1.2` | `queued` |
| `C1.4` | Clock domains, UTC instants, anchors, and simulator timing | `C1.2` | `queued` |
| `C1.5` | Validity states and acquisition-quality vocabulary | `C1.2` | `queued` |

### C2 — Measurement and binding catalog epic

| Child | Outcome | Depends on | State |
| --- | --- | --- | --- |
| `C2.1` | Measurement-definition model and semantic invariants | `C1.3`, `C1.5` | `queued` |
| `C2.2` | Measurement catalog, schema, ordering, and references | `C2.1` | `queued` |
| `C2.3` | Source-binding definition and transform references | `C2.2` | `queued` |
| `C2.4` | Binding catalog and pure cross-catalog validation | `C2.3` | `queued` |

### C3 — Canonical evidence-record epic

| Child | Outcome | Depends on | State |
| --- | --- | --- | --- |
| `C3.1` | Raw-observation record and schema | `C1.3`–`C1.5`, `C2.4` | `queued` |
| `C3.2` | Measurement-sample record and schema | `C3.1` | `queued` |
| `C3.3` | Raw/sample lineage and cross-contract validation | `C3.2` | `queued` |
| `C3.4` | Measurement-frame record and schema | `C3.3` | `queued` |
| `C3.5` | Frame closure, canonical ordering, and validation | `C3.4` | `queued` |

### C4 — Contract closure epic

| Child | Outcome | Depends on | State |
| --- | --- | --- | --- |
| `C4.1` | Schema resource parity and version inventory | `C3.5` | `queued` |
| `C4.2` | Accepted, rejected, and canonical conformance corpus | `C4.1` | `queued` |
| `C4.3` | Public API and contract documentation closure | `C4.2` | `queued` |
| `C4.4` | Built/installed artifact matrix and independent review | `C4.3` | `queued` |

## A1 — Acquisition core epic

| Child | Outcome | Depends on | State |
| --- | --- | --- | --- |
| `A1.1` | Acquisition-profile contracts | `C4.4` | `queued` |
| `A1.2` | Consumer demand contracts and lifecycle | `A1.1` | `queued` |
| `A1.3` | Demand compatibility, merge, and generation resolution | `A1.2` | `queued` |
| `A1.4` | Allow-listed transform registry and execution | `C2.4`, `A1.3` | `queued` |
| `A1.5` | Source/session lifecycle and epoch transitions | `C3.5`, `A1.3` | `queued` |
| `A1.6` | Cadence, downsampling, interpolation, and resampling policy | `A1.3`, `A1.5` | `queued` |
| `A1.7` | Continuity evaluator and continuity report | `A1.5`, `A1.6` | `queued` |
| `A1.8` | Generic fan-out, sink isolation, and backpressure evidence | `A1.6`, `A1.7` | `queued` |
| `A1.9` | Acquisition-session orchestration and installed closure | `A1.4`–`A1.8` | `queued` |

## R1 — Canonical recording and replay epic

| Child | Outcome | Depends on | State |
| --- | --- | --- | --- |
| `R1.1` | Recording-session descriptor and artifact identities | `A1.9` | `queued` |
| `R1.2` | Canonical archive logical format and raw-retention model | `R1.1` | `queued` |
| `R1.3` | Checkpointed writer and atomic/no-replace publication | `R1.2` | `queued` |
| `R1.4` | Artifact manifest graph, integrity, and relationships | `R1.3` | `queued` |
| `R1.5` | Partial-artifact recovery and terminal results | `R1.3`, `R1.4` | `queued` |
| `R1.6` | Deterministic replay source and epoch semantics | `R1.5` | `queued` |
| `R1.7` | Long-session, corruption, recovery, and replay closure | `R1.6` | `queued` |

## P1 — Native X-Plane FDR projection epic

| Child | Outcome | Depends on | State |
| --- | --- | --- | --- |
| `P1.1` | Projection-profile and field-mapping contracts | `R1.7` | `queued` |
| `P1.2` | Mandatory native trajectory-spine projection | `P1.1` | `queued` |
| `P1.3` | Version-4 DataRef extension projection | `P1.2` | `queued` |
| `P1.4` | Projection timing and resampling behavior | `P1.1`, `A1.6` | `queued` |
| `P1.5` | Omission, default, conversion, and precision-loss report | `P1.2`–`P1.4` | `queued` |
| `P1.6` | End-to-end canonical-to-native-sink verification | `P1.5` | `queued` |

## G1 — Canonical vertical-slice review

`G1` is a release gate, not an implementation epic. It begins only after
`C4.4`, `A1.9`, `R1.7`, and `P1.6` are verified. It reconciles identity,
timing, quality, lineage, continuity, recovery, replay, projection loss, source
artifacts, and installed artifacts before a separate release decision.

## Parallel integration and standards tracks

These tracks do not weaken the release path and may proceed only after their
named prerequisites:

| Child | Outcome | Dependency | State |
| --- | --- | --- | --- |
| `I1.1` | q4xpcc contract-model and fixture integration | `C4.4` | `queued` |
| `I1.2` | q4xpcc live XPLM acquisition integration | `A1.9`, consumer-owned plan | `queued` |
| `I2.1` | xpwebapi development/corroboration adapter | `C4.4`, consumer-owned plan | `queued` |
| `S1.1` | Edition-pinned standards baseline and traceability contract | `C4.4` | `queued` |
| `S2.1` | ARINC 717 profile specification | `S1.1`, licensed source, `R1.7` | `blocked` |
| `S2.2` | ARINC 717 codec and conformance corpus | `S2.1` | `blocked` |
| `S3.1` | ARINC 647A/FRED configuration boundary | `S1.1`, licensed source | `blocked` |
| `S4.1` | ARINC 429 profile for a concrete source or target | `S1.1`, licensed source/use case | `blocked` |
| `F1.1` | Separate downstream FDM project specification | `R1.7` | `deferred` |
| `F2.1` | FOQA organizational workflow or claims | External governance and approval | `deferred` |

Contract integration can begin after `C4.4`; it does not wait for `G1`. Live
q4xpcc acquisition depends on the completed acquisition epic. ARINC codec work
waits for licensed, edition-pinned normative sources and the relevant canonical
recording boundary.

## T1 — Repository governance tooling epic

This track governs agent-harness delivery tooling. It is independent of the
runtime architecture and never ships in the xplane-fdau distribution.

| Child | Outcome | Dependency | State |
| --- | --- | --- | --- |
| `T1.1` | Markdown-native backlog status and state management | `M0` | `designing` |

## Version 0.1.0 release gates

- [x] Correct repository, distribution, package, CLI, documentation, schema,
      workflow, and artifact identity.
- [x] Native X-Plane FDR isolated as a deliberately lossy format and sink.
- [ ] `C1.1` through `C4.4` verified and independently reviewed.
- [ ] `A1.1` through `A1.9` verified and independently reviewed.
- [ ] `R1.1` through `R1.7` verified and independently reviewed.
- [ ] `P1.1` through `P1.6` verified and independently reviewed.
- [ ] `G1` reconciles the complete canonical vertical slice.
- [ ] Source and installed-wheel verification passes on Python 3.12–3.14.
- [ ] A separate release review authorizes publication.

No checked gate authorizes release by itself.

## Maintenance rules

1. Point Superpowers to `BACKLOG.md` at the start of a run.
2. Select one primary child slice whose prerequisites are satisfied.
3. Link an approved specification before marking that child `specified`.
4. Link an approved implementation plan before marking it `planned`.
5. Mark it `verified` only after every gate has committed evidence and review
   findings are resolved.
6. A run may update cross-cutting roadmap, backlog, documentation, or handoff
   pointers, but it may not silently claim a second child slice complete.
7. Preserve completed specs and plans as history; update status and links rather
   than rewriting their result.
8. Never use roadmap status to bypass specification, testing, review, or release
   gates.
