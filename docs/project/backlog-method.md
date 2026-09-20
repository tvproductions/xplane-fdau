# The roadmap and evidence-backed backlog

This guide explains the delivery method used by xplane-fdau and the parts another
project could adapt. It describes existing authorities; it does not create a
second backlog or change a release gate. Read the [roadmap](https://github.com/tvproductions/xplane-fdau/blob/main/ROADMAP.md) for
the actual work and dependencies, and the [backlog](https://github.com/tvproductions/xplane-fdau/blob/main/BACKLOG.md) for current
state and acceptance evidence.

For the detailed model, provenance analysis, and separation from release
versions, read the [retrospective specification](backlog-governance-model.md).

## Why this shape exists

The FDAU work spans a reusable core, external simulator clients, and a later
release. A reviewed design can help another project plan before its code is
delivered. A verified local child can still leave the cross-cutting release
gate open. The backlog records those distinctions so status and resumption
come from repository evidence.

The method tracks four separate questions: **scope** (who owns the outcome),
**order** (what must precede it), **maturity** (which lifecycle stage it has
reached), and **proof** (which acceptance gates have evidence). The
[governance design](../superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md)
explains the decision to keep roadmap structure separate from changing
delivery state, select one primary child per run, audit drift, and report a
deterministic next action.

## Read an identifier

The letters are local mnemonics, not a universal alphabet. A whole number
such as C2 names a family; a dotted number such as C2.3 names an outcome.
Numbers are identities, not dates, estimates, or priority scores. **The
roadmap section gives the node kind:** dotted IDs can name local children or
external boundaries.

| Prefix | Meaning here | Example |
| --- | --- | --- |
| M | Milestone | M0 identity and native FDR migration |
| B | Build foundation | B1.1 source-layout isolation |
| C | Canonical contracts | C2.3 source-binding definition |
| A | Acquisition | A1.7 continuity evaluator |
| R | Recording and replay | R1.6 deterministic replay |
| P | Native FDR projection | P1.5 projection-loss report |
| D | Contract-design handoff readiness for q4xpcc | D1.3 reviewed consumer brief |
| G | Release gate | G1 canonical vertical-slice review |
| S | Standards | S2.1 ARINC 717 profile specification |
| F | FDM/FOQA and a related external boundary | F1.1 local analysis; F2.1 external program governance |
| T | Repository tooling | T2.2 dependency refresh |
| I | External consumer or adapter boundary | I1.0 q4xpcc planning reconciliation |

The roadmap does not formally expand the letter I; it uses it for downstream
consumer and adapter boundaries. C1 through C4 are separate canonical-contract
epics. T1, T2, and T3 cover governance, maintenance, and Git synchronization
tooling. Consult [ROADMAP.md](https://github.com/tvproductions/xplane-fdau/blob/main/ROADMAP.md) for each ID's exact outcome.

## Node kinds, state, and evidence

| Kind | Purpose | Mutable local delivery state? |
| --- | --- | --- |
| Milestone | Record a verified prerequisite | No |
| Epic | Group related local outcomes | No |
| Local child | Deliver one independently planned and reviewed outcome | Yes |
| Release gate | Reconcile results across children before a separate release decision | Derived readiness only |
| External boundary | State when another owner may act | No |

Only a local child can be selected as the primary work of a run. One broad
design may govern several exact children, while an implementation plan covers
one child. Plan tasks sit below that child. Explicit dependencies establish
readiness; an earlier-looking ID alone does not.

The [status model](https://github.com/tvproductions/xplane-fdau/blob/main/ROADMAP.md#status-model) distinguishes queued,
designing, specified, planned, in_progress, implemented, reviewed, verified,
blocked, deferred, and released. **Specified** means the design is approved;
**implemented** means plan tasks are complete and review remains open;
**verified** means all acceptance gates have committed evidence and review
findings are resolved. A draft plan does not make a child planned.

The backlog records status, dependencies, spec and plan links, gate count,
review, and any suspension reason. A count such as 0/4 means zero of four
acceptance statements have evidence; it is not a percent-complete estimate.
Release needs a separate review and authorization after child and cross-child
gates pass.

## D1: a consumer contract handoff

Here *handoff* means passing reviewed **contract decisions to another
project**. It is distinct from the session checkpoint in HANDOFF.md and from
the gzs-session-handoff workflow. q4xpcc needed stable interface shapes and
ownership rules to revise four Phase 24A plans. Waiting for the whole FDAU
implementation would have delayed that planning. The
[D1 design](../superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md)
created three local outcomes:

| Child | Verified outcome |
| --- | --- |
| D1.1 | The canonical C1-C4 design was reviewed and approved. |
| D1.2 | Acquisition, recording, projection, deployment, and pinning contracts were designed and reviewed. |
| D1.3 | The decisions were reconciled into a [consumer brief](../architecture/q4xpcc_phase_24a_contract_handoff.md) with an exact repository snapshot and explicit limits. |

Verified D1.3 makes external I1.0 **planning reconciliation** eligible.
Contract models and fixtures wait for C4.4 (I1.1); live XPLM acquisition
adoption waits for A1.9 (I1.2). G1 still waits for the whole canonical vertical
slice. D1 delivered reviewed decisions and a brief, not runtime artifacts.

## Authorities and resumption

ROADMAP.md owns identity, node kind, capability order, dependencies, and
release gates. BACKLOG.md owns mutable local-child state and acceptance
evidence. Specifications define approved behavior; single-child plans define
execution. HANDOFF.md is a concise session checkpoint pointing back to them.

At session entry, run the repository backlog audit and next-action report.
Stop on findings. Otherwise resume or select a dependency-ready local child
and follow its reported lifecycle action. The
[backlog-status adapter](https://github.com/tvproductions/xplane-fdau/blob/main/.codex/skills/backlog-status/SKILL.md) gives the
exact commands. State changes use an inspected dry run and an explicit apply
with the current target hash.

## Adapting the method elsewhere

1. Identify outcomes and owners. Separate local work, milestones, release
   decisions, and external dependencies.
2. Group local outcomes into stable capability or feature families. A family
   identifies an area of responsibility; a child identifies one reviewable
   outcome. Choose letters that fit the project and record the legend.
3. Split families into independently reviewable children with explicit
   dependencies and acceptance statements.
4. Keep structural decisions in one roadmap and changing status in one
   backlog. Link specs, plans, reviews, and evidence rather than duplicating
   them in a session note.
5. Add lifecycle and audit rules to address observed ambiguity or drift.
   Distinguish external planning, adoption of delivered artifacts, and release
   when they have different thresholds.

This degree of governance helps when work spans repositories, agents, long
pauses, or separate design and release decisions. A small single-owner change
may need only a short outcome list with clear acceptance criteria. The portable
idea is **explicit outcomes, dependencies, state, and evidence**; this
repository's letters and gate counts are examples. Candidate use in gzkit
and airlineops should first test whether an outcome keeps its identity
when its target release changes; the
[retrospective specification](backlog-governance-model.md#candidate-pattern-for-gzkit-and-airlineops)
gives an evaluation checklist.
