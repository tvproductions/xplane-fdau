# xplane-fdau Roadmap

- **Status:** Active planning authority
- **Updated:** 2026-08-09
- **Decision owner:** Jeff / tvproductions

## Purpose

This roadmap connects the parent FDAU architecture to independently reviewable
delivery slices. It answers what must exist, in what order, and which gates
prevent release. It is not a substitute for a design specification or an
implementation plan.

- `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md` owns the
  cross-project architecture.
- `ROADMAP.md` owns capability order, dependencies, and release gates.
- `BACKLOG.md` owns slice status, links, and measurable acceptance checklists.
- `docs/superpowers/specs/` owns reviewed semantic decisions.
- `docs/superpowers/plans/` owns executable test-first tasks.
- `HANDOFF.md` identifies the current checkpoint and next authorized action.

## Status model

Every backlog slice uses one status:

| Status | Meaning |
| --- | --- |
| `queued` | Ordered work exists, but its specification has not started. |
| `designing` | Requirements and boundaries are being reviewed. |
| `specified` | The written specification is approved. |
| `planned` | An approved executable implementation plan exists. |
| `in_progress` | Plan tasks are being implemented. |
| `verified` | All slice acceptance gates pass with committed evidence. |
| `blocked` | A named external decision or prerequisite prevents progress. |
| `deferred` | Deliberately outside the active release path. |
| `released` | The verified slice is included in a published release. |

Progress is measured by verified acceptance gates and completed slices. The
project does not use speculative hours or story points. A gate count changes
only in the same commit that records its evidence.

## Current release path

```text
M0 Identity and native FDR kernel                                  verified
 |
 +-> C1 Contract foundation
      |
      +-> C2 Measurement and binding catalogs
           |
           +-> C3 Observation, sample, and frame records
                |
                +-> C4 Contract conformance and artifact closure
                     |
                     +-> A1 Acquisition, demand, continuity, and fan-out
                          |
                          +-> R1 Canonical archive, recovery, and replay
                               |
                               +-> P1 Canonical-to-native-FDR projection
                                    |
                                    +-> G1 Canonical vertical-slice review
                                         |
                                         +-> separate 0.1.0 release decision
```

The sequence is dependency order, not a promise that every slice has equal
size. A later slice may be split into additional backlog items when its design
begins. Splitting cannot remove or weaken an upstream gate.

## Release-path stages

| Stage | Backlog IDs | Outcome | Entry condition | Exit condition | Current state |
| --- | --- | --- | --- | --- | --- |
| Identity and native kernel | `M0` | Correct FDAU identity with native FDR isolated as a lossy format and sink | Prior narrow kernel exists | Migration plan and independent review gates pass | `verified` |
| Canonical contract kernel | `C1`–`C4` | Language-neutral definitions and evidence records with deterministic identity | `M0` verified | Schemas, Python contracts, fixtures, artifacts, and independent review pass | `designing` |
| Acquisition core | `A1` | Compatible demand merge, lifecycle, continuity, and generic fan-out | `C4` verified | Reviewed acquisition specification and all continuity/fan-out gates pass | `queued` |
| Canonical recording | `R1` | Recoverable canonical archive, manifest, and deterministic replay | `A1` verified | Long-session, recovery, integrity, and replay gates pass | `queued` |
| Native projection | `P1` | Canonical samples project to native FDR with explicit loss reporting | `R1` verified | End-to-end projection and loss-report gates pass | `queued` |
| Release gate | `G1` | Independently reviewed canonical vertical slice | `P1` verified | All release blockers closed; separate release authorization still required | `queued` |

Current measured position: one release-path slice is verified (`M0`); the
canonical contract kernel is in design; no later release-path slice has begun.
This count is deliberately not expressed as a percentage because slices are
not interchangeable units of effort.

## Version 0.1.0 release gates

Release remains prohibited until every gate below is verified:

- [x] Repository, distribution, package, CLI, documentation, schema, workflow,
      and artifact identity is `xplane-fdau` / `xplane_fdau`.
- [x] Native X-Plane FDR is isolated as a deliberately lossy format and sink.
- [ ] Canonical measurement, binding, observation, sample, frame, timing, and
      quality contracts are implemented and independently reviewed.
- [ ] Acquisition profiles, demand resolution, lifecycle, continuity, and
      generic fan-out are implemented and independently reviewed.
- [ ] Canonical archive, manifest, recovery, and deterministic replay are
      implemented and independently reviewed.
- [ ] Canonical samples project end to end to the native FDR sink with explicit
      omission, conversion, precision, and default-value loss reporting.
- [ ] The complete canonical vertical slice passes source, built-artifact, and
      installed-wheel verification on Python 3.12, 3.13, and 3.14.
- [ ] A separate release review authorizes publication.

The checked identity gates do not authorize a release by themselves.

## Post-0.1.0 integration roadmap

These capabilities depend on the canonical release path but do not block the
initial vertical-slice implementation unless a later reviewed decision changes
that boundary.

| Backlog ID | Capability | Dependency | State |
| --- | --- | --- | --- |
| `I1` | q4xpcc Phase 24A adapter and evidence integration | `G1` and a pinned FDAU artifact | `queued` |
| `I2` | xpwebapi development/corroboration adapter | `C4`, then consumer-owned plan | `queued` |
| `S1` | Edition-pinned standards baseline and traceability contract | `C4` | `queued` |
| `S2` | ARINC 717 recording profile and codec | `S1`, licensed normative source, `R1` | `blocked` |
| `S3` | ARINC 647A/FRED configuration boundary | `S1`, licensed normative source | `blocked` |
| `S4` | ARINC 429 profile/codec for a concrete use case | `S1`, licensed normative source and use case | `blocked` |
| `F1` | Downstream FDM analysis system | `R1` and separate project governance | `deferred` |
| `F2` | FOQA organizational workflow or claims | External organizational approval and governance | `deferred` |

`blocked` for standards work means the exact licensed normative edition and
profile decision are unavailable; it does not invite implementation from public
catalog summaries. FDM/FOQA remains a downstream system, not an FDAU recorder
feature.

## Roadmap maintenance rules

1. Add or split a roadmap slice before beginning a materially new subsystem.
2. Give every active slice one stable backlog ID.
3. Link an approved specification before marking a slice `specified`.
4. Link an approved implementation plan before marking a slice `planned`.
5. Mark a slice `verified` only after every listed acceptance gate has committed
   evidence and independent review findings are resolved.
6. Update `HANDOFF.md` whenever the active slice or next authorized action
   changes.
7. Never use roadmap status to bypass specification, testing, review, or release
   gates.
8. Preserve completed specifications and plans as history; update the backlog
   link and status instead of rewriting their outcome.
