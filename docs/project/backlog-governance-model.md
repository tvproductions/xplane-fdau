# Retrospective specification: roadmap and backlog model

- **Status:** explanatory analysis, written after the model was adopted
- **Scope:** the xplane-fdau delivery system as it exists on 2026-09-20
- **Authority:** [ROADMAP.md](https://github.com/tvproductions/xplane-fdau/blob/main/ROADMAP.md),
  [BACKLOG.md](https://github.com/tvproductions/xplane-fdau/blob/main/BACKLOG.md),
  approved designs, and repository instructions remain authoritative

This document states the model precisely and explains its design logic. It
does not add a child, change a gate, approve work, or prescribe a universal
alphabet. The [short guide](backlog-method.md) is the starting point for
readers who only need the IDs and the normal workflow.

## The problem it solves

A single numbered list easily mixes five different statements: a capability
is desired, its design is approved, code exists, another project may plan
against it, and a release may ship. Those statements have different owners,
prerequisites, and evidence. This repository spans a reusable FDAU core,
external X-Plane clients, q4xpcc planning, and a separately gated release.
The model makes those claims independently inspectable.

A work item's **stable identity** answers what outcome is being pursued.
Its **kind and owner** answer who may act on it. Dependencies answer when it
is ready. Lifecycle state answers how far execution has advanced. Linked
evidence answers why that state is credible. A release version answers which
public artifact was published and what compatibility it represents. The
model does not make one field answer all six questions.

## What can be established about its origin

The repository history shows a roadmap decomposition on 2026-08-09, followed
that day by a Markdown backlog governance design and refinement. The
[governance design](../superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md)
records Jeff / tvproductions as decision owner and approval on 2026-08-15.
It explicitly names lessons from q4xpcc and integration with Superpowers.
The [parent architecture](../architecture/xplane12_virtual_fdau_ecosystem_design.md)
was imported from q4xpcc, and the
[scope amendment](../architecture/xplane_fdau_core_scope_amendment.md)
determines which work belongs in this repository.

Those records establish a local design and its recorded approval. They do not
identify PMI, NASA, or Kanban as the original sources of the ID scheme. Git
authorship and approval metadata do not independently prove who first invented
each rule or which alternatives were considered. The following comparisons
describe structural kinship, not documented historical borrowing.

| Published concept | Corresponding part here | Limit of the comparison |
| --- | --- | --- |
| [PMI work breakdown structure](https://www.pmi.org/learning/library/developing-elaborating-work-breakdown-structures-7241) | Epics group deliverable-oriented, reviewable children; IDs locate outcomes. Design briefs can be interim deliverables. | This roadmap also contains gates and external boundaries, so the whole document is not a pure WBS. Complete WBS coverage of all future work has not been proven. |
| [Precedence relationships](https://www.pmi.org/learning/library/developing-elaborating-work-breakdown-structures-7241) | Explicit dependencies, rather than numeric order, determine readiness. | The project does not derive a schedule or critical path from them. |
| [Kanban definition of workflow](https://kanbanguides.org/the-kanban-guide/) | Local children have named states, explicit transition policies, and one primary selection per run. | The project does not claim a complete Kanban system or maintain its service-level and flow metrics. |
| [Systems engineering verification](https://www.nasa.gov/reference/5-3-product-verification/) | Acceptance claims link to reviewed, versioned evidence; design, verification, and release are distinct. | The backlog is not a formal requirements verification matrix. |
| [Interface management](https://www.nasa.gov/reference/6-3-interface-management/) | D1 baselines consumer-facing decisions before implementation and separates planning from integration. | D1 proves local readiness to hand off; external acceptance belongs to q4xpcc. |
| [Superpowers](https://github.com/obra/superpowers) | Approved design precedes a focused implementation plan, execution, review, and closeout. | The roadmap taxonomy and Markdown state engine are repository-specific additions. |

## Conceptual data model

The roadmap defines a tagged set of five nonoverlapping node kinds.
[Its node table](https://github.com/tvproductions/xplane-fdau/blob/main/ROADMAP.md#roadmap-node-kinds)
is the source of the actual inventory.

| Kind | Identity and purpose | Can be the selected local work? | Mutable local state? |
| --- | --- | --- | --- |
| Milestone | A verified prerequisite, such as M0 | No | No |
| Epic | A related family of local children, such as C2 | No | No |
| Local child | One independently planned and reviewed outcome, such as C2.3 | Yes | Yes |
| Release gate | Cross-child reconciliation, such as G1 | No | Derived readiness and gate evidence |
| External boundary | When another owner may act, such as I1.0 | No | No |

In conceptual terms, a local child contains a stable ID, epic, outcome,
ordered dependency IDs, lifecycle state, governing specification, one
implementation plan, acceptance statements, gate evidence, review evidence,
and optional suspension reason/resume state. The
[backlog inventory](https://github.com/tvproductions/xplane-fdau/blob/main/BACKLOG.md#local-child-inventory)
is its human-readable record. The parser has typed models and a versioned JSON
report; Markdown remains the editable authority.

The letters are domain mnemonics. C identifies canonical contracts, A
acquisition, R recording and replay, P projection, T tooling, and so on.
C2.3 is a child in the C2 epic; the dot is a hierarchy cue, not a release
number. The containing roadmap section determines kind: dotted I1.0 is an
external boundary, and dotted F2.1 is external program governance. IDs are
not dates, priority ranks, effort points, or SemVer components.

## Core invariants

The current implementation can be summarized by these constraints:

1. Each roadmap ID has exactly one node kind. Every local child has exactly
   one backlog inventory row, in roadmap order; nonlocal nodes have none.
2. Local dependencies name known local children or M0 and form an acyclic
   graph. The backlog repeats dependencies so an audit can detect drift.
3. A child is dependency-ready only when every local predecessor is verified
   or released. Readiness does not itself change its lifecycle state.
4. The satisfied/total gate count is derived from the child acceptance items.
   A checked gate has eligible linked evidence, and its statement agrees with
   the governing design's criterion.
5. Lifecycle state cannot outrun its required design, plan, review, and
   evidence. Verification requires accepted review and every gate supported
   by committed evidence.
6. External boundaries remain report-only. Release gates reconcile multiple
   children; a separate release decision controls publication.

These are the rules that turn a readable backlog into a checkable claim
ledger. Their exact parser and evidence conditions are in the
[governance design](../superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md).

## Authority layers

| Layer | Owns | Does not establish by itself |
| --- | --- | --- |
| Parent architecture and approved scope amendment | System purpose, dependency direction, and ownership boundaries | Local completion |
| ROADMAP.md | Node kind and identity, epic membership, dependencies, order, external conditions, and release gates | Child delivery state |
| BACKLOG.md | One active selection, each local child's state, links, gate counts, review, suspension, and release dashboard | New semantic design authority |
| Approved specification | Behavior, boundaries, and acceptance statements for exact children | Implemented behavior |
| Approved single-child plan | Executable tasks and verification for one child | Completed tasks or passing gates |
| Review and gate artifacts | Evidence for a specific claim | Other children's completion |
| HANDOFF.md | Concise session checkpoint back to the authorities | An independent state ledger |

A design can cover several named children when their semantics must agree.
An execution plan covers exactly one child. Plan tasks remain beneath that
child; new scope needs a child or a gate amendment. Backlog gate statements
match the governing design's acceptance criteria. Evidence is an explicit
artifact, not an inference from a file's existence or recent commit.

## Dependencies, lifecycle, and selection

The dependency graph determines eligibility. A local dependency is satisfied
when it is verified or released; M0 is the verified initial prerequisite.
Local cycles, unknown IDs, and roadmap/backlog dependency drift are audit
errors. A design or plan may be prepared before downstream delivery, but
dependency readiness controls which child can be selected for execution.

The ordinary forward lifecycle is:

    queued -> designing -> specified -> planned -> in_progress
           -> implemented -> reviewed -> verified

Specified requires an approved design. Planned requires an approved,
single-child plan. Implemented requires completed plan evidence. Reviewed
requires accepted independent review. Verified requires every child gate to
have eligible evidence in the committed repository state. An artifact may
temporarily lead its child by one adjacent handoff while a guarded backlog
transition is made; that never advances the child implicitly.

Blocked and deferred retain an explicit reason and exact resume state.
Reopening uses defined backward transitions, not arbitrary status editing.
Released is reserved for a separately authorized publication decision.
[The governance design](../superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md#lifecycle-model)
defines the exact transitions and evidence rules.

The read-only next-action algorithm audits first. If a child is selected, it
returns that child's required lifecycle action (or wait if suspended).
Otherwise it chooses the first dependency-ready local child in roadmap order.
It never selects an epic, milestone, release gate, or external boundary.
Selection itself does not change lifecycle state. At most one local child is
selected at a time.
## The backlog as an evidence ledger

The backlog is more than a queue. Its one local-child inventory row records
the current claim about a child. Its acceptance section records each exact
criterion, checkbox, and evidence link. The displayed satisfied/total count is
derived from those items. Four checked gates do not mean an estimated 100% of
effort; they mean four specified claims have evidence.

The audit cross-checks node identity, kind, membership, dependency graph,
design and plan metadata, gate text, evidence eligibility, and lifecycle
prerequisites. Evidence must match the child and gate, have an eligible kind
and result, and be tracked without unstaged byte changes. Final verification
requires a clean post-commit audit of those evidence bytes in HEAD. Thus a
status word alone cannot manufacture completion.

Mutations are controlled: preview the proposed diff, check the candidate
document, then apply with expected state and a hash of the current backlog.
The writer edits managed Markdown, checks for stale input, and publishes by
atomic replacement. The
[backlog-status adapter](https://github.com/tvproductions/xplane-fdau/blob/main/.codex/skills/backlog-status/SKILL.md)
provides the exact commands. Ordinary source edits, Git sync, external
application writes, tags, publication, and release are separate operations.

A normal run reads the architecture, roadmap, backlog, and governing design;
runs audit and next; selects or resumes one child; follows its design, plan,
implementation, review, and verification stage; records gate evidence; and
leaves a concise session pointer. A handoff can become stale, so the next
session recomputes status from the authorities.

## The D1 example: a design deliverable before runtime delivery

D1 was inserted because q4xpcc could revise its Phase 24A plans using stable
contracts before the complete FDAU engine existed. D1.1 approved canonical
contract semantics. D1.2 approved acquisition, recording, projection, and
deployment/pinning contracts. D1.3 reconciled them into a
[consumer brief](../architecture/q4xpcc_phase_24a_contract_handoff.md).
These were local, independently reviewed design outcomes with their own
evidence. The C, A, R, and P implementation children were not thereby
verified.

The roadmap records three different downstream thresholds:

| Threshold | What becomes eligible | Local prerequisite |
| --- | --- | --- |
| I1.0 | q4xpcc specification and plan reconciliation | D1.3 |
| I1.1 | q4xpcc adoption of delivered contract models and fixtures | C4.4 |
| I1.2 | q4xpcc live XPLM acquisition adoption | A1.9 |

I1.0 through I1.2 are external boundaries, not q4xpcc tasks managed from
this repository. G1 separately reconciles C4.4, A1.9, R1.7, and P1.6 before
a further release decision. Here *consumer handoff* means passing reviewed
contract decisions across a project boundary. It does not mean the session
checkpoint in HANDOFF.md or the gzs-session-handoff workflow.

This is a useful answer to the apparent paradox that D1 is verified while
much of C/A/R/P is queued or specified: D1's deliverable is a reviewed
design-and-brief package. Its acceptance gates ask whether that package
exists and is coherent, not whether the future runtime exists. The
[D1 design](../superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md)
makes that limitation explicit.

## Work IDs and release versions answer different questions

[Semantic Versioning](https://semver.org/) communicates the compatibility
meaning of a released public API: incompatible changes affect major,
compatible additions minor, and compatible fixes patch after 1.0. It also
defines version zero as initial development. SemVer does not specify how to
number future work items or require a feature to be booked into a future
version when its scope is first imagined.

This repository does name an intended 0.1.0 release gate. It does **not**
embed 0.1.0 in child identities. C2.3 remains C2.3 if a gate or schedule
changes. Whether it belongs in a particular release is a separate planning
and authorization statement, with its own evidence. IDs preserve traceability
across design, plan, review, and implementation even if a release boundary is
amended.

A hypothetical version-booked backlog might name a proposed capability
"1.4 feature 7." If it slips to 1.5, either its identity becomes misleading
or references in designs, tests, and reviews must be rewritten. Under this
model, a stable capability ID remains fixed while the proposed release
assignment changes. That is the specific failure mode this separation could
address in gzkit and airlineops, based on the reported version-booking
problem; this document does not assert either project's actual file layout
or workflow.

| Question | Stable child ID | Release version |
| --- | --- | --- |
| What outcome is this? | Yes | No |
| What does it depend on? | Referenced by dependency edges | No |
| What is its design and proof? | Referenced by artifacts | No |
| Which published API and compatibility contract is this? | No | Yes |
| Can release scope change while references remain stable? | Yes | Assignment may change |

A target release may still be recorded for planning, but it should remain a
separate, revisable relationship. Publishing the release then requires the
applicable release gate and its own decision. A version number cannot serve
as completion evidence.

## Candidate pattern for gzkit and airlineops

The transferable classification is by **capability or feature family** and
then by **specific outcome**. A family names a coherent area of product or
repository responsibility; a child names one result that can be specified,
reviewed, and evidenced. A family may include design or tooling outcomes
as well as runtime features. Release assignment is a separate relationship
that can be revised without changing either ID.

The user has identified gzkit and airlineops as candidates because their
current release-booked backlogs cause friction. A read-only inspection of
their ADR taxonomies, templates, roadmaps, and representative records on
2026-09-20 supports that concern. This is a candidate study, not an adoption
decision or a complete audit of either repository. Before changing either
repository, inspect a larger representative sample and ask:

1. When a planned feature moves to another release, which references must
   be renamed or become misleading?
2. Which family labels describe stable domain areas, and which currently
   describe a release, team, or temporary campaign?
3. Can each proposed child be given a clear outcome, owner, dependencies,
   and acceptance criteria independently of its target version?
4. Can a release view select eligible children and enforce a gate without
   becoming the source of their identities or status?
5. How will old version-coded references resolve during migration?

A useful trial is to map a few existing items to stable family/child IDs while
retaining their current version labels as planning metadata. Then move one
hypothetical item to a different release. The trial succeeds if the child's
specification, plan, dependency links, and evidence references remain valid
and only the release assignment changes. Split or merged outcomes need an
explicit identity decision and historical mapping. The exact xplane-fdau
letters, lifecycle depth, Markdown parser, and evidence machinery should be
chosen separately for each repository.

## ADRs, feature records, and releases are different records

An architecture decision record answers **which consequential choice was made,
in what context, against which alternatives, and with what consequences**.
That is the structure in [Nygard's original ADR proposal](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
and the [MADR template](https://adr.github.io/madr/). A decision can govern
several features, remain relevant after many releases, and later be superseded
by another decision. Its decision status (proposed, accepted, superseded, or
rejected) is different from implementation progress.

A **feature record** is the proposed local artifact name for a capability or
reviewable outcome. It answers **what result is wanted, for whom, under which
constraints, with which prerequisites, and what evidence will prove delivery**.
It can link to one or more ADRs. A feature may need no new ADR if existing
decisions already govern it. A feature can be split, deferred, or dropped
without rewriting a decision's history. This artifact name and schema are a
recommendation, not a published ADR standard. The
[Scrum Guide's product backlog](https://scrumguides.org/scrum-guide.html)
supports an emergent, ordered set of work to improve a product; the richer
feature-record fields here are a local traceability choice.

A **release record** selects completed outcomes, checks compatibility and
release gates, and receives a version. [SemVer](https://semver.org/) defines
the meaning of a published version relative to a declared public API,
including the special initial-development meaning of `0.y.z`. It does not
define a work-item namespace, architectural decision taxonomy, or backlog
order. Using SemVer-shaped strings for ADRs or briefs is a project convention,
not a SemVer requirement. A Git commit or tag can still anchor an audit receipt
without making the anchored work item's ID a version.

| Record | Stable identity represents | Own status answers | Typical links |
| --- | --- | --- | --- |
| ADR | One significant choice and its rationale | Is this decision proposed, accepted, or superseded? | Architecture, affected feature records, superseding ADR |
| Feature record | One capability or reviewable outcome in a family | Is this outcome specified, in progress, verified, or released? | ADRs, dependencies, briefs/plans, tests, evidence |
| Release record | One published artifact and compatibility boundary | Is this release candidate ready, authorized, and published? | Included feature records, gate evidence, version/tag |
| Issue | One tracker conversation or defect report | Is the issue open or resolved? | Any of the above; its number need not encode meaning |

The relationships are many-to-many. The same retention-policy ADR may constrain
configuration, rollup, and purge-safety features; a rollup feature may also
depend on a separate storage-interface ADR. The release selects the features
that actually ship. The ADR is referenced in release notes when its choice
matters to users or maintainers, but it is not itself the release unit.

### What the sibling repositories show

The inspected files contain valuable discipline: explicit intent, alternatives,
work decomposition, acceptance, attestation, and audit evidence. The problem
is that a single ADR identity currently carries several distinct meanings:

| Repository evidence (2026-09-20 local snapshot) | What it shows | Consequence of the current binding |
| --- | --- | --- |
| gzkit `docs/user/concepts/adr-taxonomy.md` | `pool` means backlog intent, `foundation` means an invariant, and `feature` means a release-carrying capability. The validator binds foundation to `0.0.x` and feature to non-`0.0.x`; new gzkit foundations are closed, though adopter projects may still author them. | The taxonomy uses “ADR” for both a decision and a backlog/delivery item. Closing the foundation kind may increase pressure to put new significant choices inside feature ADRs; this is an inference, not a proven cause. |
| gzkit `docs/design/roadmap/ROADMAP-GZKIT.md` and root `AGENTS.md` | Roadmap phases map versions to ADRs. The operator later had to enforce ascending SemVer work order after 0.35.0, 0.36.0, and 0.37.0 were simultaneously authored with 25 briefs and no landed work. | Version order became a scheduling rule, while capacity and dependencies remained separate questions. The incident demonstrates real sequencing friction; it does not show that the evidence gates are unnecessary. |
| gzkit `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` | One record contains enduring tombstone/source-of-truth decisions plus ten SemVer-derived OBPI implementation briefs and requirement IDs. | Changing the planned version reaches the ADR ID, directory, brief IDs, REQ IDs, and references, not just release planning. |
| airlineops `docs/governance/GovZero/adr-lifecycle.md` and root `AGENTS.md` | Pool promotion assigns the next version; Accepted leads through implementation to Completed and Validated. A release tag is the highest validated feature-series ADR, with a human bump gate. | Decision acceptance, work completion, validation, and version selection are serialized through one ADR lifecycle. |
| airlineops `docs/design/adr/adr-0.1.x/ADR-0.1.18-bts-tiered-data-lifecycle/ADR-0.1.18-bts-tiered-data-lifecycle.md` | The ADR states a durable hot/warm/cold retention decision and also owns a feature checklist, OBPI breakdown, and completion evidence. It says later ADRs implement rollup and schema. | One architectural policy spans several delivery items and planned versions, exactly where a separate decision record would retain clearer identity. |

The gzkit template under `docs/examples/templates/adr-template.md` already asks
for a decision, consequences, and alternatives. That is a useful ADR core. Its
requirements checklist and parent PRD link support traceability, but when the
same record is also the work order, decision status and delivery status can
no longer change independently. Airlineops has the same overlap in its full
records even though its short `ADR_TEMPLATE.md` is decision-shaped.

### Proposed classification and minimum schemas

Ask two questions at intake. **Would a future maintainer need the reasoning
behind this choice even if the planned feature were cancelled?** If yes,
capture an ADR. **What observable capability or outcome must be delivered?**
If there is an answer, capture a feature record. When both answers apply,
create two linked records. A small implementation choice can stay in the
feature's design notes; not every feature needs an ADR. A pool idea without
a chosen solution belongs in a capability pool, not in an accepted-decision
register.

An ADR minimally needs a stable, release-independent ID; decision status and
date; context and forces; the choice; considered alternatives; consequences;
the affected architecture boundary; links to governed capabilities; and an
explicit supersedes/superseded-by link when doctrine changes. Its acceptance
authorizes the choice. It does not claim that implementation or a release has
completed.

A feature record minimally needs a stable ID under a named capability family;
one-sentence outcome and owner; architecture and governing-ADR links;
dependencies; scope/non-goals; acceptance claims; mutable delivery status;
plan/brief links; and evidence. `candidate_release` is optional, mutable
planning data. `released_in` is historical evidence added after publication.
These are different fields: the former can slip, the latter cannot be revised
merely to replan. Keep issue numbers as aliases or links.

For example, airlineops' hot/warm/cold policy could keep `ADR-0.1.18`
as the historical source while an approved, release-independent ADR records
the current retention decision and explicitly points back to it. Separate
feature records would cover retention configuration, warm rollup, and the
purge interlock, each linking to that decision and to its own proof. In
gzkit, the tombstone algebra in `ADR-0.35.0` is a candidate decision;
corpus landing and the separately reviewable OBPIs are delivery records.
These are classification examples, not an instruction to split or renumber
those repositories now.

### A safe migration test

1. Freeze historical ADR, OBPI, REQ, receipt, and tag identifiers. Record
   aliases from them to new decision and feature IDs; do not rewrite old
   attestation evidence to make history look newly structured.
2. Inventory consumers of version-shaped IDs: validators, templates, ledger
   schemas, links, tests, release commands, and agent instructions. Identify
   which require compatibility reads before changing any authoring rule.
3. Pilot one foundation-like ADR, one feature ADR containing a real decision,
   one feature with no new architectural choice, and one pooled idea. Produce
   separate decision, feature, and release views over those examples.
4. Simulate a feature slipping a release, one decision governing two features,
   and a later decision superseding an earlier one. The pilot passes when
   only the candidate release assignment changes on a slip, feature evidence
   stays linked, and supersession changes decision authority without erasing
   shipped history.
5. Approve the new taxonomy and compatibility path before updating creation,
   audit, promotion, and release tooling. Preserve the current gates unless
   a separate evidence-based review changes them.

This separates the benefits of GovZero's review discipline from the cost of
using a prospective release number as the primary key for every artifact.
## Working with an agent to design a stronger backlog

Two limitations should be examined separately. An opaque issue number is a
useful durable tracker reference, but by itself it does not show which
architectural capability an item belongs to, whether it is a feature or
gate, who owns it, or which prerequisites and evidence matter. Booking a
work item's identity into a future SemVer release adds another problem:
a planning change can make the identity misleading. An improved backlog
can keep the existing issue number while adding architecture-linked
classification and a separate target-release relationship.

A useful engagement with an agent has four reviewable stages:

1. **Map the existing system.** Give the agent the governing architecture,
   product/design documents, current issues, release policy, and a sample of
   completed work. Ask for an authority map and an inventory of roughly a
   dozen varied items: features, defects, design work, tooling, cross-project
   handoffs, and slipped release items. The agent should identify where the
   current record loses architectural context or conflates work with a
   release.
2. **Design the classification together.** Ask the agent to propose two or
   three candidate family schemes grounded in product responsibilities.
   For each family, require a one-sentence scope, examples that belong,
   examples that do not, and its relationship to adjacent families.
   Distinguish a family or epic from a reviewable child, a prerequisite,
   an external owner, and a release gate. Review this map yourself before
   assigning IDs; an issue list cannot decide architecture ownership.
3. **Pilot the backlog model.** Translate a small representative set into
   stable family/child IDs, explicit dependency links, lifecycle states,
   acceptance statements, and optional target releases. Keep the original
   issue numbers as aliases or tracker links. Ask the agent to walk through
   cases where a feature slips a release, a child splits, a shared contract
   precedes two features, a design is approved before code, or another
   project owns adoption. Revise the model where those cases become awkward.
4. **Approve and migrate in stages.** Agree on the taxonomy, state meanings,
   evidence rules, and release-view policy. Have the agent produce a
   crosswalk from old references to stable IDs and identify ambiguous
   mappings for human decision. Only then update a bounded slice of the
   backlog and check every link and dependency. Add parser or mutation
   automation after the human-readable model survives the pilot.

Ask for these concrete review artifacts: a capability map tied to architecture
sections, an ID legend, a typed node inventory, a dependency graph, a sample
backlog with evidence fields, a decision register, a release view, a migration
crosswalk, and a list of unresolved ownership decisions. The crosswalk should
classify each legacy ADR as a decision, feature/work record, or mixed record;
show the proposed decision-to-feature links; and mark ambiguous cases for
human review. Those artifacts make the agent's judgment inspectable before
the entire backlog changes.

A starting prompt for a discovery session is:

> Read the project's architecture, designs, current backlog or issues, and
> release policy. Map the major capability families and ownership boundaries
> before proposing IDs. Show where existing item numbers or version labels
> hide feature relationships, prerequisites, and acceptance evidence.
> Propose two or three small taxonomy options with examples and tradeoffs.
> Keep tracker issue numbers as references. Separate lasting ADR decisions
> from feature outcomes and give each its own status and identity. Treat
> target releases as separate planning metadata. Pilot the preferred model
> on representative items and
> show what happens when one item moves to another release. Identify decisions
> that require my approval before changing the backlog.

For a hypothetical item, issue #314 can remain the tracker key;
MEAS1.3 can identify its measurement capability and reviewable outcome; and
v1.4 can remain a provisional target release. If the target changes to
v1.5, #314 and MEAS1.3 keep their references. The family label alone is
insufficient: the item's outcome, dependency links, state, and acceptance
evidence give it operational meaning.

The adoption test is whether a reader can answer, from the backlog and its
linked authorities: *what architectural capability is this, why is it
needed, what must exist first, who owns it, what proves it complete, and
which release may include it?* Each answer should have its own source.
A simple numeric issue tracker can continue to supply durable URLs; the
backlog supplies the capability structure and evidence relationships.

## Consistency with this project's governing design

The model implements the approved architecture's allocation of reusable FDAU
behavior to this repository and concrete simulator I/O to external clients.
Its local versus external node kinds express that boundary. The scope
amendment maps ARINC and FDM/FOQA mechanics to local work while leaving
consumer adapters and organizational program authority external.

The agent instructions require architecture-first entry, the backlog audit,
a deterministic next action, reviewed design, single-child plan,
implementation, review, and verification. The roadmap and backlog then
express those rules in inspectable data. The complete canonical vertical
slice and G1 remain separate from the 0.1.0 publication decision. D1 changes
the readiness of external planning without claiming runtime or release.
Those relationships are internally coherent; the repository audit checks
many structural and evidence invariants.

Internal coherence is narrower than conformance to an external method.
The repository has not demonstrated a PMI 100% WBS accounting of all possible
future scope, a full Kanban flow measurement system, a NASA requirements
verification matrix, or bilateral acceptance of the D1 brief by q4xpcc.
Those would require separate evidence and, where relevant, the other owner.
The exact Markdown parser, line-sensitive tests, and gate counts are local
engineering choices rather than portable standards. In particular, a recent
two-line roadmap pointer shifted a test's expected line numbers; the pointer
was removed. That brittleness is an implementation cost, not a property that
another project needs to copy.

## A minimal transferable schema

For another project, the smallest useful version is:

1. A stable local outcome ID and mnemonic family, independent of release
   version, plus a one-sentence completion outcome.
2. A node kind and owner: local child, grouping, milestone, cross-child gate,
   or external boundary only where needed.
3. Explicit predecessor IDs; validate that local dependencies exist and have
   no cycles.
4. One mutable status record per local child, with links to its design, plan,
   acceptance criteria, review, and evidence.
5. Explicit rules for each state change and a separate release decision.
6. One canonical backlog, with session handoffs pointing to it rather than
   restating its state as a competing ledger.

A project can begin with a Markdown table and manual review. Typed parsing,
JSON reports, hash-guarded mutation, and strict evidence artifacts should
follow demonstrated need. The first migration step for a version-booked
backlog is to give work stable IDs while retaining existing target-version
labels as optional planning metadata. Existing version commitments can then
be evaluated explicitly as release gates, without renumbering the work.

## Sources and interpretation

The project's
[roadmap](https://github.com/tvproductions/xplane-fdau/blob/main/ROADMAP.md),
[backlog](https://github.com/tvproductions/xplane-fdau/blob/main/BACKLOG.md),
[scope amendment](../architecture/xplane_fdau_core_scope_amendment.md),
[governance design](../superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md),
and [D1 design](../superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md)
support the description of current project behavior. The external links above
support comparisons and the SemVer distinction. Similarity to a published
method is an analytical inference unless the project history records it as
an influence.
