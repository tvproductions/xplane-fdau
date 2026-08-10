# xplane-fdau Markdown-Native Backlog Status Skill Design

- **Status:** Draft for written review
- **Date:** 2026-08-09
- **Decision owner:** Jeff / tvproductions
- **Source roadmap child:** `T1.1` — Markdown-native backlog status and state
  management

## Authority and purpose

`ROADMAP.md` is the architecture-order and dependency authority. `BACKLOG.md`
is the mutable delivery ledger and durable Superpowers entry point. This
specification defines repository-local agent tooling that derives measured
status from those files, checks specification and plan adherence, recommends
the next Superpowers action, and performs explicit guarded state changes.

The tooling governs only xplane-fdau. It does not manage consumer projects,
coordinate sibling repository state, or become part of the distributed Python
library. q4xpcc may consume xplane-fdau through the library's published
contracts, but its own backlog remains independently governed.

Version `0.1.0` remains unreleased. This tooling cannot authorize a push, tag,
publication, or release.

## Decision summary

The project will add a `backlog-status` skill backed by a modular,
standard-library-only Markdown state engine. The engine will:

1. parse the complete roadmap inventory and mutable backlog state;
2. validate identities, dependencies, lifecycle states, acceptance gates, and
   specification/plan adherence;
3. report human-readable and versioned JSON status;
4. recommend the next eligible child and Superpowers workflow stage;
5. apply only explicit, validated, dry-run-first state changes;
6. preserve unrelated Markdown prose and formatting;
7. fail closed on structural or adherence defects; and
8. remain repository-local and absent from distribution artifacts.

The initial engine will be deliberately smaller than q4xpcc's evidence-heavy
backlog implementation. It may mature as this repository develops, but new
capability must enter through focused rules, modules, fixtures, and tests.
Child-specific product evidence belongs in normal repository tests rather than
in generic Markdown parsing code.

## Goals

This increment will:

1. make backlog and resume answers reproducible from repository evidence;
2. inventory every roadmap child rather than only the active release epic;
3. enforce one explicitly selected primary child per run;
4. distinguish architectural order from mutable delivery state;
5. enforce lifecycle prerequisites without inferring completion;
6. detect drift among roadmap, backlog, specs, plans, gates, and evidence;
7. make state changes reviewable as ordinary Markdown diffs;
8. give Superpowers a deterministic next-action recommendation;
9. provide stable output for both agents and repository checks; and
10. establish extension boundaries that prevent a single project-specific
    script from becoming an unstructured monolith.

## Non-goals

This increment will not:

- change the FDAU runtime architecture or public library API;
- ship backlog tooling in the wheel or source distribution;
- manage q4xpcc, Ortho4XP, xpwebapi, or any other repository;
- use conversation history as status evidence;
- infer completion from file presence, recent commits, or checked plan tasks
  alone;
- execute implementation plans or edit product source;
- stage, commit, fetch, pull, merge, rebase, push, tag, publish, or release;
- introduce a second handoff database or generated Markdown authority; or
- freeze the future command surface when repository evidence justifies a
  reviewed extension.

## Authority model

### Roadmap authority

`ROADMAP.md` owns:

- child IDs and human-readable outcomes;
- epic membership and roadmap ordering;
- dependencies and release-path relationships;
- the allowed lifecycle vocabulary; and
- release gates and separately governed tracks.

Every roadmap child must be individually addressable. Ranges may be used in
explanatory prose, but not as substitutes for inventory records.

### Backlog authority

`BACKLOG.md` owns:

- the selected primary child;
- current child state;
- governing spec and plan links;
- dependency presentation copied from the roadmap;
- acceptance-gate counts and evidence links;
- blocked or deferred reasons; and
- the current release and publication prohibition.

The backlog remains hand-authored Markdown. It is neither generated from JSON
nor mirrored into another mutable state file.

### Evidence authority

`docs/superpowers/specs/` and `docs/superpowers/plans/` provide governance
evidence. Repository-relative evidence links attached to gates provide review
and verification evidence. Git status and recent commits provide useful
observations, but they do not change lifecycle state or satisfy gates.

`HANDOFF.md` remains a concise pointer required by repository instructions. It
does not duplicate the complete state ledger.

## Skill contract

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

`SKILL.md` will trigger when a user asks where xplane-fdau stands, what remains,
how to resume, whether Superpowers artifacts cover the backlog, or requests a
controlled backlog state change. It will direct the agent to run the script
instead of answering from memory.

The modules are responsibility boundaries, not a promise that each must begin
large. The CLI remains thin. Markdown parsing, rule evaluation, reporting, and
mutation do not depend on one another's private implementation details.

## Initial command model

The initial CLI supports:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
uv run python .codex/skills/backlog-status/scripts/backlog_status.py select T1.1 --expect-current C1.1
uv run python .codex/skills/backlog-status/scripts/backlog_status.py transition T1.1 specified --expect designing
uv run python .codex/skills/backlog-status/scripts/backlog_status.py record-gate T1.1 1 --expect-open --evidence tests/test_backlog_status_skill.py
uv run python .codex/skills/backlog-status/scripts/backlog_status.py reopen-gate T1.1 1 --expect-closed --reason "Evidence contract changed"
```

Mutation commands render a proposed diff and make no change unless `--apply`
is present. Future commands may be added when repository needs justify them.
They must follow the same validation, dry-run, atomicity, and test contracts.

## Parsed model

The internal model uses frozen typed values for:

- roadmap children, epic membership, order, dependencies, and state;
- backlog entries, selected-child identity, links, reasons, and gate totals;
- acceptance gates, ordinal identity, checked state, and evidence links;
- specification and plan records with their declared child and source paths;
- audit findings with severity, rule ID, file, line, child, and message; and
- next-action recommendations with child, lifecycle stage, reason, and command.

IDs are compared exactly. Human text may be normalized only where the format
contract explicitly permits it. Dependency ranges in roadmap prose expand to
exact child identities before evaluation.

## Markdown contract

The parser recognizes named headings and tables rather than arbitrary visual
layout. The implementation plan will migrate the backlog so that every roadmap
child has an explicit row with at least:

| Field | Meaning |
| --- | --- |
| Child | Exact roadmap identity |
| Outcome | Human-readable deliverable |
| Status | Current lifecycle state |
| Depends on | Exact dependency identities or external reason |
| Spec | Governing specification link or em dash |
| Plan | Governing implementation-plan link or em dash |
| Gates | Derived satisfied/total count |

Acceptance gates remain Markdown task-list items beneath an exact child
heading. A satisfied gate includes a repository-relative evidence link on the
same logical item. Gate counts are derived, never independently edited totals.

The parser reports duplicate headings, duplicate rows, missing columns,
unrecognized status values, malformed links, ambiguous ranges, and gate-count
drift. It never silently repairs malformed input during a read-only command.

## Lifecycle and adherence rules

The roadmap lifecycle vocabulary remains authoritative. The engine enforces
these minimum prerequisites:

| State | Required evidence |
| --- | --- |
| `queued` | Roadmap identity and dependencies |
| `designing` | Governing draft specification |
| `specified` | Written specification approval recorded in the spec and backlog |
| `planned` | Approved child-specific implementation plan |
| `in_progress` | Selected child and an open approved plan |
| `implemented` | Completed approved plan with implementation evidence |
| `reviewed` | Independent review with no unresolved load-bearing finding |
| `verified` | Reviewed state plus all gates with committed evidence |
| `blocked` | Explicit blocking reason |
| `deferred` | Explicit governance reason |
| `released` | Verified state plus separately authorized release evidence |

The engine rejects unknown dependencies, cycles, unsatisfied prerequisites,
missing required links, unknown child references, orphan specs/plans, and
claims that exceed their evidence. A queued future child may lack detailed
gates, a spec, and a plan. Once its epic becomes active, the missing governance
becomes blocking according to lifecycle state.

Repository-governance tooling such as `T1.1` can become `verified` but cannot
enter `released`, because it is not part of the distributed product.

Specs and plans must cite an exact source child. Plan links do not prove plan
completion. Checked tasks do not prove independent review or acceptance-gate
closure. Suggested state changes are reported but never applied implicitly.

## Next-action selection

`next` follows this order:

1. Stop and report blocking audit findings.
2. If a primary child is selected, resume it at its current Superpowers stage.
3. If that child is blocked, report the exact reason without selecting another
   child silently.
4. If no child is selected, choose the first dependency-satisfied child in
   roadmap order.
5. Recommend exactly one of: brainstorm/refine the spec, request written spec
   review, write the implementation plan, execute the plan, request review,
   verify gates, or wait for a named prerequisite.

The recommendation contains its evidence and remains informational. It cannot
invoke another workflow or mutate the backlog by itself.

## Mutation safety

State-changing commands:

- require explicit `--apply`;
- require an expected current selection, lifecycle state, or gate state for
  every mutation;
- re-read and revalidate files immediately before publication;
- reject stale input or a changed target hash;
- update only recognized fields or gate items;
- preserve unrelated prose and final-line conventions;
- write a same-directory temporary file and publish atomically;
- validate the complete candidate document before replacement;
- remove an unpublished temporary file after failure where possible; and
- print the resulting diff and audit result.

No command performs a Git write. Agents use the existing guarded local commit
workflow after reviewing the Markdown diff.

## Reporting contract

Human output includes:

- roadmap and backlog paths;
- selected child and lifecycle state;
- dependency readiness;
- spec, plan, gate, and evidence summary;
- blocking findings and warnings;
- next eligible child; and
- recommended Superpowers action.

JSON output begins with `schema_version: 1` and represents the same facts with
stable field names and deterministic ordering. Human wording may improve
without a schema-version change; incompatible JSON shape changes require a new
schema version and compatibility tests.

Exit status is:

- `0` for a valid report, valid dry-run, or successful applied change;
- `1` for audit findings or a refused mutation; and
- `2` for invalid command-line usage.

## Failure handling

Every blocking finding names the rule, file, line when available, child or
gate, and actionable message. Multiple independent findings are reported in a
single audit where safe. Parse failure in an authoritative structure prevents
mutation because the engine cannot prove a safe edit boundary.

An applied mutation is all-or-nothing. Failure before atomic publication leaves
the original bytes unchanged. Failure after publication is reported with the
published path and final audit state so callers do not repeat a successful
change blindly.

## Testing contract

All tests, fixtures, examples, and validation commands use Python's standard
library test framework. This is a hard repository invariant.

Skill implementation follows test-first development. Before adding the skill
or behavior, the implementation plan adds a failing `unittest` that proves the
missing trigger, parse rule, lifecycle rule, report, or mutation behavior.

The test surface includes:

- skill frontmatter and trigger language;
- complete roadmap/backlog inventory and current-repository integration;
- valid and malformed Markdown fixtures;
- duplicate, missing, ranged, unknown, and cyclic identities;
- lifecycle transitions and prerequisites;
- specification and plan adherence;
- gate evidence and derived counts;
- next-action selection for every state;
- human and JSON reports;
- dry-run and apply behavior;
- stale-state refusal, atomic publication, and failure cleanup;
- preservation of unrelated prose and formatting; and
- distribution and runtime-import exclusion.

Temporary-directory fixtures exercise writes without touching the working
backlog. Full repository quality and documentation checks remain required.

## Workflow integration

Repository instructions will require session entry to run `audit` and `next`
after reading the governing documents. Superpowers continues to start from
`BACKLOG.md`. Focused specs and plans cite their exact child, and explicit
transitions record their links.

The full hygiene workflow runs the strict audit. Structural or adherence
defects block the next Superpowers action and the local completion claim.
Informational Git observations remain warnings unless an explicit mutation
safety rule is violated.

`HANDOFF.md` remains a concise pointer to the backlog and current written-review
gate. It does not become a second state system.

## Growth policy

The tool is expected to mature. New commands, evidence adapters, or structural
operations are acceptable when repeated repository work demonstrates the need.
Each extension must:

1. begin with a failing standard-library test;
2. preserve the authority boundaries in this design;
3. add a focused model or rule instead of child-specific branching in the CLI;
4. define human and JSON behavior where relevant;
5. preserve dry-run and atomic-write safety for mutations; and
6. update the skill, fixtures, documentation, and backlog gates together.

When a module becomes difficult to understand independently, it splits by
responsibility before additional evidence families are added.

## Acceptance criteria

`T1.1` is verified only when:

1. the project-local skill triggers for status, resume, adherence, and state
   management requests;
2. the complete roadmap inventory is represented by explicit backlog entries;
3. status, audit, next-action, human, and versioned JSON reports pass;
4. structural and adherence defects return a blocking result with exact
   context;
5. dry-run-first selection, transition, gate-recording, and gate-reopening
   commands pass stale-state and atomic-publication tests;
6. all skill and script tests use the standard-library framework and pass;
7. full hygiene includes the strict backlog audit;
8. built and installed distribution checks prove the tooling is absent from the
   runtime library; and
9. independent review has no unresolved load-bearing finding while release and
   publication remain prohibited.

## Implementation sequence

After written approval of this specification, one focused implementation plan
will execute `T1.1` in this order:

1. failing skill and inventory tests;
2. read-only model, parser, audit, and reports;
3. spec/plan adherence and next-action rules;
4. failing mutation tests followed by dry-run and atomic apply behavior;
5. explicit backlog inventory migration;
6. session-entry and hygiene integration;
7. distribution-boundary and installed-artifact verification; and
8. independent review and closeout.

No implementation begins before this written specification is reviewed.
