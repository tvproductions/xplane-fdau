# xplane-fdau Markdown-Native Backlog Governance Tooling Design

- **Governance:** active
- **Status:** approved
- **Date:** 2026-08-09
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T1`
- **Roadmap children:** `T1.1`, `T1.2`, `T1.3`, `T1.4`, `T1.5`, `T1.6`
- **Approval:** 2026-08-15 — Jeff / tvproductions

## Authority and purpose

`ROADMAP.md` is the node-identity, kind, order, and dependency authority.
`BACKLOG.md` is the only mutable delivery-state authority and the durable
Superpowers entry point. This specification defines repository-local tooling
that measures xplane-fdau delivery from those files, validates governing specs
and plans, recommends the next Superpowers action, and performs explicit guarded
state changes.

The tooling governs only xplane-fdau. It does not manage consumer projects,
coordinate sibling repository state, or become part of the distributed Python
library. q4xpcc and other consumers keep independent backlogs.

Version `0.1.0` remains unreleased. This tooling cannot authorize a Git remote
write, tag, publication, or release.

## Decision summary

The project will add a `backlog-status` skill backed by a modular,
standard-library-only Markdown state engine. Six run-sized children deliver the
capability:

| Child | Outcome |
| --- | --- |
| `T1.1` | Markdown authority contract and explicit inventory normalization |
| `T1.2` | Typed parser, human status report, and versioned JSON |
| `T1.3` | Structural audit and spec/plan adherence |
| `T1.4` | Deterministic next-action selection |
| `T1.5` | Guarded child-state and gate-evidence mutations |
| `T1.6` | Skill, session-entry, hygiene, and artifact closure |

One governing design covers these exact children. Each child receives one
focused implementation plan and one independently reviewable run.

The engine may mature as the repository develops, but new capability must enter
through focused models, rules, fixtures, and tests. Child-specific product
semantics remain in normal repository tests rather than accumulating in the
generic Markdown parser.

## Goals

This epic will:

1. make backlog and resume answers reproducible from repository evidence;
2. inventory every roadmap node without treating every node as local work;
3. enforce one selected local child per run;
4. keep mutable state in exactly one authoritative file;
5. enforce lifecycle prerequisites without inferring completion;
6. detect drift among roadmap, backlog, specs, plans, gates, and evidence;
7. make state changes reviewable as ordinary Markdown diffs;
8. give Superpowers a deterministic next-action recommendation;
9. provide stable human and machine-readable reports; and
10. preserve modular growth boundaries learned from q4xpcc.

## Non-goals

This epic will not:

- change the FDAU runtime architecture or public library API;
- ship governance tooling in the wheel or source distribution;
- manage q4xpcc, Ortho4XP, xpwebapi, or any other repository;
- use conversation history as delivery evidence;
- infer completion from file presence, recent commits, or plan task marks alone;
- execute implementation plans or edit product source;
- stage, commit, fetch, pull, merge, rebase, push, tag, publish, or release;
- create a second handoff database or generated Markdown authority; or
- implement a release transition while the current release prohibition exists.

## Roadmap node taxonomy

The roadmap parser recognizes five nonoverlapping node kinds:

| Kind | Contract | Locally selectable? | Mutable delivery state? |
| --- | --- | --- | --- |
| Milestone | Verified prerequisite such as `M0` | No | No |
| Epic | Ordered group of local children | No | No |
| Local child | Independently planned xplane-fdau outcome | Yes | Yes, in `BACKLOG.md` |
| Release gate | Cross-child reconciliation such as `G1` | No | Derived gate state only |
| External boundary | Consumer/downstream handoff owned elsewhere | No | No |

The report inventories all five kinds. Only local children appear in the
mutable local-child inventory or can be selected and transitioned. Release-gate
readiness is derived from local prerequisites and recorded gate evidence.
External boundaries are report-only architecture context.

## Authority model

### Roadmap authority

`ROADMAP.md` owns:

- exact node identity and kind;
- epic membership and roadmap order;
- local dependency identities;
- external prerequisites and boundary handoff conditions;
- release-path relationships; and
- the allowed local-child lifecycle vocabulary.

Roadmap child tables contain no mutable delivery-state column. Dependency
ranges in authoring prose expand to exact identities before evaluation.

### Backlog authority

`BACKLOG.md` owns:

- the single selected local child or an explicit empty selection;
- every local child's current lifecycle state;
- governing design and implementation-plan links;
- copied local dependencies for drift detection;
- acceptance gates and derived satisfied/total counts;
- blocking/deferred reason and resume state; and
- the current release and publication prohibition.

The backlog remains hand-authored Markdown. It is not generated from JSON and
is not mirrored into another mutable state file.

### Governance artifact authority

`docs/superpowers/specs/` contains governing designs. One design may cover an
ordered, nonempty set of exact local children. `docs/superpowers/plans/`
contains implementation plans. Every active plan covers exactly one local
child and cites one governing design.

Historical artifacts remain preserved. They receive explicit historical
metadata and a disposition instead of being misreported as active orphans.

### Evidence and Git authority

Acceptance evidence is an explicit repository artifact with the metadata
defined below. Git cannot prove semantic success, but it proves whether an
evidence artifact is tracked and whether its indexed or committed bytes match
the link being reviewed. Recent commits and dirty state remain observations;
they never advance lifecycle state implicitly.

`HANDOFF.md` remains a concise pointer required by repository instructions. It
does not duplicate the complete state ledger.

## Managed Markdown contract

### Roadmap structures

The parser recognizes roadmap node kind from its exact containing heading and
table header:

- `Milestones` contains `Milestone | Outcome`;
- local epic sections contain `Child | Outcome | Depends on` tables;
- the standards epic adds `External prerequisite` as a fourth column;
- `Release gates` contains `Gate | Outcome | Depends on`;
- `External consumer and downstream boundaries` contains
  `Boundary | Owner | xplane-fdau handoff condition`; and
- `M0` is the named verified milestone in the release-path section.

Narrative ranges are permitted, but every local child and external boundary
must also have one explicit table row. Duplicate identities across kinds are
invalid.

### Backlog current position

`## Current position` contains exactly one managed selection line:

```markdown
- Active child: `T1.1`.
```

An empty selection is represented as:

```markdown
- Active child: —.
```

Other current-position prose is preserved and ignored by the selection parser.

### Unified local-child inventory

`T1.1` migrates all local children into one `## Local child inventory` table
with this exact header and column order:

| Child | Outcome | Status | Depends on | Spec | Plan | Gates | Review | Resume | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Rules for cells are:

- `Child` is one exact roadmap local-child ID in roadmap order.
- `Outcome` exactly matches the roadmap outcome after Markdown whitespace
  folding.
- `Status` is one lifecycle token from this specification.
- `Depends on` is an ordered comma-separated list of exact local IDs or `M0`;
  no prose is allowed.
- `Spec` is one repository-relative Markdown link or `—`.
- `Plan` is one repository-relative Markdown link or `—`.
- `Gates` is the derived `<satisfied>/<total>` count or `—` before gates exist.
- `Review` is one accepted child-level review-evidence link for `reviewed` or
  later; otherwise it is `—`.
- `Resume` is required only for `blocked` or `deferred`; otherwise it is `—`.
- `Reason` is required only for `blocked` or `deferred`; otherwise it is `—`.

Every roadmap local child appears exactly once. Milestones, epics, release
gates, and external boundaries never appear in this table.

### Acceptance-gate sections

Each governed local child with defined gates has one exact heading:

```markdown
### T1.1 — Markdown authority contract and explicit inventory normalization
```

Open gates use:

```markdown
- [ ] Gate statement.
```

Satisfied gates use one or more evidence links:

```markdown
- [x] Gate statement. — Evidence: [verification](.superpowers/sdd/example/verification.md)
```

The statement text is immutable after evidence is attached unless the gate is
reopened first. Evidence links are ordered lexically by normalized repository
path. Gate ordinal is its one-based position beneath the child heading. Gate
counts are derived and never edited independently.

Each active design contains one matching `### <child> — <outcome>` subsection
under `## Acceptance criteria`. Backlog gate statements must match those design
criteria exactly after task-list removal and Markdown whitespace folding. Gate
additions or wording changes amend the governing design and backlog together.

### Release-gate dashboard

`## Release-gate dashboard` uses the exact header:

| Gate | Outcome | Gate state | Prerequisites | Evidence |
| --- | --- | --- | --- | --- |

Gate state is `waiting`, `ready`, or `satisfied`. `waiting` and `ready` are
derived from prerequisite state. `satisfied` additionally requires eligible
gate evidence. Release gates are never selected as implementation children.

## Governance artifact metadata

### Active design metadata

An active design begins with this exact metadata family after its title:

```markdown
- **Governance:** active
- **Status:** draft
- **Date:** 2026-08-09
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T1`
- **Roadmap children:** `T1.1`, `T1.2`
- **Approval:** —
```

Design status is `draft`, `approved`, `implemented`, or `superseded`.
`approved` or later requires `Approval` in the form
`YYYY-MM-DD — <decision owner>`. Covered children are exact, unique, in roadmap
order, and may span only the named epic unless the roadmap explicitly declares
a cross-epic design.

### Active implementation-plan metadata

An active plan begins with:

```markdown
- **Governance:** active
- **Status:** draft
- **Date:** 2026-08-09
- **Roadmap child:** `T1.1`
- **Source specification:** `docs/superpowers/specs/example-design.md`
- **Approval:** —
- **Completion evidence:** —
```

Plan status is `draft`, `approved`, `in_progress`, `completed`, or
`superseded`. `approved` or later requires an approval value. `completed`
requires a repository-relative completion-evidence value. When that evidence
lives outside MkDocs' docs tree, its value is an inline-code repository-relative
path, not a Markdown link; it remains inside the repository and resolves to a
regular file. This representation preserves strict not-found link validation.
A plan covers exactly one local child, and that child must be covered by the
cited approved design.

### Historical metadata

A preserved pre-governance artifact begins with:

```markdown
- **Governance:** historical
- **Status:** completed
- **Disposition:** Completed under `M0`.
```

Historical status is `completed` or `superseded`. Disposition is required and
must name the completed milestone, replacement artifact, or replacement child.
Historical artifacts are reported but do not compete for selection or next
action. `T1.1` migrates all existing specs and plans to one of these exact
contracts.

## Evidence artifact contract

Each evidence link resolves to a repository-relative regular Markdown file
whose metadata is:

```markdown
# Verification Evidence

- **Child:** `T1.1`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-09
- **Subject:** Local-child inventory contract
```

`Kind` is `verification`, `review`, `artifact`, or `approval`. `Result` is
`passed` for verification/artifact evidence and `accepted` for review/approval
evidence. `Gate` is a positive integer for gate evidence and `—` for
child-level plan-completion or review evidence. Child and gate must match the
referring gate or child-level field. Subject is nonempty.
The body records the relevant commands, inspected artifacts, findings, or
decision without a prescribed prose template.

Eligible evidence:

- parses under the exact metadata contract;
- is inside the repository without absolute or parent traversal;
- is present in the Git index;
- has no unstaged byte changes;
- matches the referring child and gate or child-level field; and
- has an eligible kind/result for the gate requirement.

Index presence establishes that backlog and evidence can land together. Final
`verified` state additionally requires a clean post-commit audit proving the
same evidence bytes are in `HEAD`. The engine never treats an arbitrary source
file or test file as gate evidence.

## Lifecycle model

Local-child status is one of:

`queued`, `designing`, `specified`, `planned`, `in_progress`, `implemented`,
`reviewed`, `verified`, `blocked`, `deferred`, or `released`.

Minimum evidence is:

| Status | Required evidence |
| --- | --- |
| `queued` | Roadmap identity and dependencies |
| `designing` | Linked active draft design covering the child |
| `specified` | Linked approved design covering the child |
| `planned` | Approved design and linked approved single-child plan |
| `in_progress` | Selected child and linked plan marked `in_progress` |
| `implemented` | Plan marked `completed` with eligible child-level completion evidence |
| `reviewed` | Implemented state plus accepted evidence linked from `Review` |
| `verified` | Reviewed state plus every gate satisfied by eligible `HEAD` evidence |
| `blocked` | Required resume state and explicit blocking reason |
| `deferred` | Required resume state and explicit governance reason |
| `released` | Outside T1 mutation scope while release remains prohibited |

### Closed transition graph

The allowed forward path is:

```text
queued -> designing -> specified -> planned -> in_progress
       -> implemented -> reviewed -> verified
```

Explicit reopening moves are:

```text
specified -> designing
planned -> specified
in_progress -> planned
implemented -> in_progress
reviewed -> implemented
verified -> reviewed
```

Any nonreleased state may move to `blocked` or `deferred`. The mutation stores
the prior state in `Resume`. A blocked/deferred child may return only to that
exact resume state after an explicit reason-bearing command. Direct skips,
arbitrary regressions, and any transition to `released` are rejected by T1.

Only `in_progress` requires the child to be selected. Selecting a child does not
change its lifecycle state. At most one local child is selected.

## Structural and adherence audit

The audit rejects:

- unknown, duplicate, missing, or cross-kind identities;
- local dependency cycles, unknown dependencies, or unsatisfied transitions;
- roadmap/backlog dependency or outcome drift;
- missing or duplicate local inventory rows;
- a selected nonlocal or unknown node;
- malformed status, resume, reason, link, or gate-count cells;
- malformed governance metadata;
- active designs with unknown, unordered, or duplicate children;
- active plans with zero or multiple children or an invalid source design;
- active artifacts without required approval/completion metadata;
- historical artifacts without an explicit disposition;
- malformed, ineligible, mismatched, or dirty evidence;
- lifecycle claims beyond their evidence; and
- release-state or release-authorization changes prohibited by this design.

Findings have severity `error` or `warning`. Every error blocks `next`, mutation,
and completion claims. Codes are stable lowercase dotted identifiers such as
`roadmap.duplicate-id`, `backlog.dependency-drift`,
`artifact.plan.multiple-children`, or `evidence.gate-mismatch`. A finding
contains code, severity, repository-relative path, one-based line when known,
node ID when relevant, gate ordinal when relevant, and actionable message.

Findings sort by severity (`error` first), path, line with missing lines last,
code, node, and gate. The audit reports independent findings in one pass where
safe; an authoritative parse failure stops dependent rules for that file.

## Skill and module contract

The project-local skill will live at:

```text
.codex/skills/backlog-status/
├── SKILL.md
└── scripts/
    ├── backlog_status.py
    └── backlog/
        ├── __init__.py
        ├── edit.py
        ├── model.py
        ├── parse.py
        ├── report.py
        └── rules.py
```

`SKILL.md` triggers for status, remaining work, resume, coverage/adherence,
next-action, and controlled state requests. It directs the agent to run the
script instead of answering from memory.

The CLI remains thin. Model, parsing, rules, reporting, and mutation expose
focused public functions and do not depend on one another's private details.

## Command delivery by child

`T1.1` establishes and migrates the Markdown contracts without activating a
repository audit command.

`T1.2` adds:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
```

`T1.3` adds:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
```

`T1.4` adds:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
```

`T1.5` adds dry-run-first mutation commands:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py select T1.2 --expect-current T1.1
uv run python .codex/skills/backlog-status/scripts/backlog_status.py transition T1.2 specified --expect designing
uv run python .codex/skills/backlog-status/scripts/backlog_status.py record-gate T1.2 1 --expect-open --evidence .superpowers/sdd/t1.2/gate-1.md
uv run python .codex/skills/backlog-status/scripts/backlog_status.py reopen-gate T1.2 1 --expect-closed --reason "Evidence contract changed"
uv run python .codex/skills/backlog-status/scripts/backlog_status.py suspend T1.2 blocked --expect in_progress --reason "Named prerequisite unavailable"
uv run python .codex/skills/backlog-status/scripts/backlog_status.py resume T1.2 --expect blocked --resume in_progress --reason "Prerequisite restored"
```

Mutation commands render a proposed diff and make no change unless `--apply`
is present. `--target-sha256` may pin the current backlog bytes explicitly; when
omitted, the command pins the hash read at process start and verifies it again
before publication.

## Next-action contract

`next` follows this exact order:

1. Stop on any audit error.
2. If a local child is selected and suspended, return `wait` with its reason.
3. If a local child is selected, recommend its required lifecycle action.
4. If no child is selected, choose the first dependency-ready local child in
   roadmap order.
5. Never recommend a milestone, epic, release gate, or external boundary as an
   implementation child.

Action is one of:

`refine_spec`, `request_spec_review`, `write_plan`, `execute_plan`,
`request_review`, `verify`, or `wait`.

The recommendation contains its evidence and suggested command but remains
informational. It cannot invoke another workflow or mutate state.

## Mutation safety

Every state-changing command:

- requires explicit `--apply` to publish;
- requires expected current selection, lifecycle state, or gate state;
- re-reads and hashes authoritative files before publication;
- validates the complete candidate document before replacement;
- updates only exact managed cells or gate items;
- preserves unrelated prose, encoding, newline style, and final-line state;
- writes a same-directory uniquely named temporary file;
- publishes with atomic replacement;
- removes an unpublished temporary file after failure where possible; and
- prints the resulting unified diff and post-change audit.

Failure before replacement leaves original bytes unchanged. A post-replacement
failure names the published path and final audit so callers do not repeat a
successful change blindly. No mutation command performs a Git write.

## Reporting and JSON schema version 1

Human status includes authority paths, selected child, lifecycle state,
dependency readiness, governing artifacts, gates/evidence, findings, roadmap
node summaries, Git observations, and recommendation.

JSON output has this exact top-level shape and no additional keys:

```json
{
  "schema_version": 1,
  "repository": "xplane-fdau",
  "valid": true,
  "roadmap": {
    "milestones": [],
    "epics": [],
    "local_children": [],
    "release_gates": [],
    "external_boundaries": []
  },
  "backlog": {
    "active_child": null,
    "children": [],
    "release_gates": []
  },
  "artifacts": {
    "specifications": [],
    "plans": [],
    "historical": []
  },
  "findings": [],
  "recommendation": null,
  "git": {
    "branch": "main",
    "dirty": false,
    "recent_commits": []
  }
}
```

Arrays use roadmap order except findings, artifacts, and recent commits.
Artifacts sort by repository path; recent commits retain newest-first Git order.
Object shapes and exact key order are:

| Object | Keys in order |
| --- | --- |
| Milestone | `id`, `kind`, `title` |
| Epic | `id`, `kind`, `title`, `children` |
| Local roadmap child | `id`, `kind`, `epic`, `title`, `dependencies`, `external_prerequisite` |
| Release gate | `id`, `kind`, `title`, `dependencies` |
| External boundary | `id`, `kind`, `title`, `owner`, `handoff_condition` |
| Backlog child | `id`, `status`, `dependencies`, `specification`, `plan`, `gates`, `review_evidence`, `resume_state`, `reason`, `dependency_ready` |
| Gate summary | `satisfied`, `total`, `items` |
| Gate item | `ordinal`, `statement`, `satisfied`, `evidence` |
| Backlog release gate | `id`, `state`, `evidence` |
| Active specification | `path`, `governance`, `status`, `epic`, `children`, `approval` |
| Active plan | `path`, `governance`, `status`, `child`, `source_specification`, `approval`, `completion_evidence` |
| Historical artifact | `path`, `governance`, `status`, `disposition` |
| Finding | `code`, `severity`, `path`, `line`, `node`, `gate`, `message` |
| Recommendation | `action`, `child`, `reason`, `command` |
| Recent commit | `sha`, `subject` |

IDs, titles, paths, statuses, actions, reasons, commands, subjects, and evidence
links are strings. `children`, `dependencies`, `items`, `evidence`, and
`recent_commits` are arrays. `ordinal`, `satisfied`, and `total` are integers;
booleans are used only for `valid`, `dirty`, `dependency_ready`, and gate-item
`satisfied`. Optional scalar values are JSON `null`; keys are never omitted.
Repository paths always use `/` separators.

Output uses UTF-8, two-space indentation, the displayed object-key order, and
one final LF. It contains no timestamps. Incompatible field or semantic changes
require a new schema version and compatibility fixtures.

Exit status is `0` for a valid report/dry-run/applied change, `1` for audit
errors or refused mutation, and `2` for invalid command usage. Warnings alone
do not change exit status.

## Testing contract

All tests, fixtures, examples, and validation commands use Python's standard
library test framework. This is a hard repository invariant.

Every behavior begins with a failing `unittest` proving the missing trigger,
parse rule, audit rule, report, recommendation, or mutation. Tests include:

- exact skill trigger and frontmatter behavior;
- node-kind, inventory, metadata, lifecycle, evidence, and JSON fixtures;
- duplicates, omissions, ranges, unknowns, cycles, and cross-kind conflicts;
- multi-child designs, single-child plans, and historical dispositions;
- every forward, reopen, suspend, resume, and refused transition;
- finding codes, severity, ordering, paths, lines, and gate context;
- next action for every lifecycle and suspension state;
- dry-run/apply, stale hashes, atomic publication, and cleanup failures;
- Markdown byte preservation outside managed structures;
- current-repository integration after each migration gate; and
- source and installed distribution exclusion.

Temporary-directory fixtures exercise writes without touching the working
backlog. Full repository quality and documentation checks remain required.

## Workflow integration

`T1.6` updates repository instructions to run `audit` and `next` at session
entry after reading governing documents. Superpowers continues to start from
`BACKLOG.md`. The full hygiene workflow runs the strict audit only after `T1.1`
through `T1.5` are migrated and verified, avoiding a permanently failing
bootstrap gate.

Focused plans cite one exact child. Explicit transitions record approved spec
and plan links. `HANDOFF.md` remains a concise pointer to the backlog and
written-review gate rather than a second state system.

## Growth policy

New commands, evidence adapters, or structural operations are allowed when
repeated repository work proves the need. Each extension must:

1. enter the roadmap/backlog as a run-sized child or gate amendment;
2. begin with a failing standard-library test;
3. preserve the authority and node-kind boundaries;
4. add a focused model or rule rather than child-specific CLI branching;
5. define human and JSON behavior where relevant;
6. preserve dry-run and atomic-write safety for mutations; and
7. update skill guidance, fixtures, and governance documentation together.

When a module becomes difficult to understand independently, it splits by
responsibility before more evidence families are added.

## Acceptance criteria

### T1.1 — Markdown authority contract and explicit inventory normalization

- Roadmap milestones, epics, local children, release gates, and external
  boundaries have exact nonoverlapping contracts.
- `BACKLOG.md` is the only mutable delivery-state authority.
- Every local child has one explicit inventory row; external boundaries have no
  local delivery status.
- Existing specs and plans have valid governance metadata or an explicit
  historical disposition.

### T1.2 — Typed parser, status report, and versioned JSON

- Frozen typed models and the strict Markdown parser pass valid and malformed
  fixture cases.
- Human status reports the complete roadmap inventory and local delivery state
  without inferring completion.
- JSON schema version 1 matches the exact documented shape and ordering.
- The migrated current repository parses and reports without a structural
  finding.

### T1.3 — Structural audit and spec/plan adherence

- Identity, kind, dependency, cycle, lifecycle, gate-count, and link rules fail
  closed with stable finding codes.
- Multi-child governing designs, single-child plans, and historical artifacts
  follow the exact metadata contract.
- Lifecycle prerequisites and eligible evidence are validated without treating
  presence as proof.
- Audit reports all independent findings with file, line, node, and exact
  context and returns a blocking result when required.

### T1.4 — Deterministic next-action selection

- A selected local child resumes at its exact Superpowers lifecycle stage.
- With no selection, the first dependency-ready local child is recommended in
  roadmap order.
- Blocking findings or a blocked selected child stop recommendation without
  silent substitution.
- Milestones, epics, release gates, and external boundaries are never
  recommended as implementation children.

### T1.5 — Guarded child-state and gate-evidence mutations

- Every mutation is dry-run-first and requires explicit apply authority.
- Expected selection/state/gate values and target hashes reject stale changes.
- Selection and lifecycle transitions enforce the exact transition graph and
  prerequisites.
- Gate recording and reopening enforce the typed evidence contract.
- Candidate validation, atomic publication, failure cleanup, and unrelated
  Markdown preservation pass.

### T1.6 — Skill, session-entry, hygiene, and artifact closure

- Project-local skill triggers for status, resume, adherence, next action, and
  controlled state requests.
- Session instructions and the concise handoff pointer invoke the backlog
  workflow without creating another state authority.
- Full hygiene runs the strict backlog audit.
- Built and installed artifacts exclude all repository-governance tooling.
- All standard-library tests and independent review pass without changing
  release or publication authorization.

## Implementation sequence

After written approval, implementation proceeds one child and one plan per run:

1. `T1.1` normalizes Markdown authority and existing artifact metadata.
2. `T1.2` implements typed parsing and reports.
3. `T1.3` implements audit and adherence.
4. `T1.4` implements next-action selection.
5. `T1.5` implements guarded mutations.
6. `T1.6` integrates the skill, session entry, hygiene, and artifact closure.

No implementation begins before this amended written specification is reviewed.

After `T1.6` is verified, repository-workflow onboarding continues through
`T2.1` canonical `repo-hygiene` and `T3.1` guarded Git synchronization as
specified by
`docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`.
Those children translate the remaining q4xpcc-local workflow capabilities and
remain outside this T1 implementation boundary. `B1.1` resumes only after
`T3.1` is verified.
