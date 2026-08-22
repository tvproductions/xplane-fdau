# q4xpcc Contract-Handoff Readiness Design

- **Governance:** active
- **Status:** approved
- **Date:** 2026-08-22
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `D1`
- **Roadmap children:** `D1.1`, `D1.2`, `D1.3`
- **Approval:** 2026-08-22 — Jeff / tvproductions

## Authority and purpose

`ROADMAP.md` owns roadmap identity, capability order, dependencies, release
gates, and external boundaries. `BACKLOG.md` owns mutable child status, plan
and specification links, acceptance evidence, and the active selection.

The approved repository scope remains
`docs/architecture/xplane_fdau_core_scope_amendment.md`. The draft canonical
contract design remains
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
until `D1.1` reviews and approves it. This design adds an earlier, explicitly
tracked handoff checkpoint for q4xpcc Phase 24A planning. It does not weaken
the later implementation, adoption, release, or publication gates.

q4xpcc does not need the complete FDAU engine or a published wheel to amend
its four Phase 24A Slice 2 plans. It needs approved, stable contract shapes,
ownership boundaries, versioning, deployment, hashing, and conformance
policies. The repository therefore prioritizes those decisions immediately
after the current `T1.2` review rather than making q4xpcc planning wait for
the full canonical implementation through `C4.4`.

## Decision

Add a local `D1 — q4xpcc contract-handoff readiness` epic with three ordered
children:

| Child | Outcome | Depends on |
| --- | --- | --- |
| `D1.1` | Canonical C1–C4 design approval | `T1.2` |
| `D1.2` | Acquisition, recording, projection, and pinning contract design | `D1.1` |
| `D1.3` | Reviewed q4xpcc Phase 24A handoff | `D1.2` |

The active child remains `T1.2` until its independent review closes. Once
`T1.2` is verified, `D1.1` is the next readiness priority before `T1.3` and
the remaining repository-tooling sequence. `T1.3` retains its existing
dependency on `T1.2`; the readiness branch changes priority, not the meaning
or status of the tooling children.

All three D1 children initially become `specified` under this approved
cross-child design, with no implementation plan, review, or completion
evidence and with every acceptance gate unsatisfied. Completing one child
does not silently complete another.

## External handoff boundary

Add a new report-only external boundary:

| Boundary | Outcome | Owner | xplane-fdau handoff condition |
| --- | --- | --- | --- |
| `I1.0` | q4xpcc Phase 24A specification and plan reconciliation | q4xpcc | Phase 24A specification and plan reconciliation may begin after `D1.3`. |

The existing boundaries retain their stronger meanings:

- `I1.1` continues to require `C4.4` before q4xpcc adopts delivered contract
  models, schemas, fixtures, or runtime APIs.
- `I1.2` continues to require `A1.9` before q4xpcc adopts live XPLM
  acquisition behavior.

`I1.0` authorizes planning reconciliation only. It does not claim that the
contract kernel, acquisition engine, recording engine, projection engine,
wheel, or release artifact exists.

## D1.1 — Canonical C1–C4 design approval

`D1.1` reviews and closes the existing canonical measurement-contract design.
The child changes design authority, not runtime behavior.

Its acceptance gates are:

1. the canonical design has approved governance metadata and no unresolved
   placeholder, contradiction, ambiguity, or load-bearing review finding;
2. canonical JSON, hashing, identity, provenance, measurement, binding, raw
   observation, sample, frame, clock/timing, validity, quality, schema, fixture,
   and Python/native conformance decisions are exact and versioned;
3. ownership and dependency direction remain consistent with the approved
   scope amendment and distinguish FDAU acquisition quality from q4xpcc
   operational policy and findings; and
4. the review records that C1–C4 implementation, schemas, fixtures, built
   artifacts, and release claims remain incomplete, leaving all C1–C4 child
   delivery statuses unchanged.

Approval of the design makes it implementation authority. It does not satisfy
any C1–C4 acceptance gate by intent or document presence alone.

## D1.2 — Acquisition, recording, projection, and pinning contract design

`D1.2` creates and approves one cross-epic contract-only design for the q4xpcc
planning surface of A1, R1, and P1. It freezes:

- acquisition profiles, immutable consumer demands, demand identity and
  lifecycle, timing relationships, and compatibility/resolution outcomes;
- continuity inputs, results, classifications, and references to requested
  versus observed evidence;
- acquisition and recording session descriptors and terminal results;
- generic sink and subscriber ports, lifecycle outcomes, criticality,
  backpressure, drop, failure, and isolation evidence;
- artifact identities, roles, relationships, byte lengths, SHA-256 values,
  integrity manifests, and raw-retention dispositions;
- canonical-to-native-X-Plane-FDR projection profiles, field mappings,
  omissions, defaults, conversion, precision loss, and projection reports;
- package version and source revision identity;
- installed-wheel versus reproducibly bundled deployment policy;
- release-artifact and delivered-package-file hash recording;
- the shared conformance entry-point contract; and
- proof that a consumer contains no separately edited or divergent local FDAU
  subset.

The design preserves the approved boundary: XPPython3/XPLM, xpwebapi,
aircraft-specific, concrete replay-host integration, and application adapters
remain consumer owned. Deterministic replay contracts, source behavior, and
core semantics remain FDAU owned. q4xpcc retains cards, missions, their
application-orchestration sessions, BIT policy, procedures, guidance, action
authorization, and q4xpcc operational findings. Native `.fdr` remains a
deliberately lossy format and sink rather than the canonical model.

The child explicitly excludes engine implementation, simulator integration,
schema or fixture delivery, built artifacts, tags, releases, PyPI publication,
and implementation-completion claims. Those remain governed by A1, R1, P1,
C4.4, G1, and the separate release decision.

Its acceptance gates are:

1. one approved design fixes every A1/R1/P1 contract shape and policy needed
   by the four q4xpcc Phase 24A Slice 2 plans;
2. every family has an exact identity/version boundary, owned fields,
   invariants, references, error outcomes, and intended future schema/fixture
   path;
3. deployment, revision pinning, release-artifact hashes, delivered-file
   hashes, conformance, and no-divergent-subset proof are explicit without
   requiring a current release artifact; and
4. independent review finds no unresolved load-bearing ambiguity and confirms
   that no A1, R1, P1, C4.4, G1, or release gate was claimed complete.

## D1.3 — Reviewed q4xpcc Phase 24A handoff

`D1.3` reconciles the approved D1.1 and D1.2 specifications into a concise
consumer brief. `HANDOFF.md` remains the repository-owned current checkpoint;
no competing handoff workflow or mutable status authority is created.

The brief supplied to q4xpcc names:

- the exact clean local xplane-fdau commit used for the handoff;
- authoritative specification paths and approval states;
- repository, distribution, import, and package version identity;
- intended contract, schema, fixture, and conformance paths;
- the simulator/adapter and q4xpcc ownership boundaries;
- installed-versus-bundled deployment and hash policies;
- native FDR's lossy projection boundary; and
- exact implementation, artifact, release, and publication limitations.

Its acceptance gates are:

1. D1.1 and D1.2 are verified with committed review evidence and no unresolved
   load-bearing finding;
2. `HANDOFF.md` and the concise q4xpcc brief agree with the approved designs
   and distinguish design readiness from implementation and adoption;
3. the brief is emitted from a clean committed state and identifies its exact
   local HEAD revision; and
4. `I1.0` becomes satisfied without changing `I1.1`, `I1.2`, G1, release,
   push, tag, or publication authorization.

The user coordinates the brief with the q4xpcc agent or project. The repository
does not require a push merely to establish D1 readiness.

## Repository authority changes

Implementation of this design changes only governance surfaces:

- `ROADMAP.md` adds D1, its dependency order, the readiness branch in the
  release-path overview, and external boundary `I1.0`;
- `BACKLOG.md` adds the three specified inventory rows, their acceptance gates,
  and `I1.0`, while retaining `T1.2` as the active child and naming D1.1 as the
  next readiness priority;
- `HANDOFF.md` records the prioritized readiness sequence and the distinction
  among planning reconciliation, contract adoption, live acquisition adoption,
  and release; and
- `tests/test_backlog_governance.py` enforces exact D1 identity, membership,
  dependencies, order, and external-boundary conditions.

Status-report fixtures or tests change only if D1 or `I1.0` exposes an existing
parser assumption. `AGENTS.md`, runtime modules, package metadata, release
gates, and publication instructions remain unchanged.

## Verification

The backlog authority change must pass:

```powershell
uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli -v
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
uv run python -m unittest discover -v
uv run python tools/quality.py check
git diff --check
```

Verification must prove:

- the roadmap and backlog contain each D1 child exactly once and in the same
  order;
- every D1 outcome, dependency, status, spec link, gate count, and acceptance
  heading is exact;
- `I1.0` is report-only and does not appear as a local child;
- `I1.1`, `I1.2`, G1, C1–C4, A1, R1, P1, and release status are unchanged;
- the human and JSON status reports distinguish D1 readiness from delivery;
  and
- no runtime or distribution file changes.

## Acceptance criteria

This backlog-prioritization design is implemented when:

1. D1.1–D1.3 are exact local children with the approved dependencies and
   acceptance gates;
2. `T1.2` remains active and D1.1 is explicitly the next readiness priority
   after its review;
3. `I1.0` permits q4xpcc planning reconciliation only after D1.3;
4. implementation, adoption, live-integration, release, tag, push, and
   publication gates are not weakened;
5. all repository governance and complete `unittest`/quality checks pass; and
6. independent review finds no unresolved load-bearing issue in the authority
   change.
