# Project Handoff

## Session checkpoint — 2026-09-19

### Current state and last completed action

T2.1 is verified, merged into `main`, and its temporary worktree and branch
are removed. The B1.1 dependency correction is on `main`: B1.1 waits on T2.2
only; T3.1 is independent. No local child is selected. The latest live backlog
`audit` had no findings, and `next` recommended `write_plan T2.2`.

The T2.2 plan is saved at
`docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`.
It is marked **draft** and its own plan audit says **FAIL for execution
readiness**: several test and code steps still lack executable examples. It
has no implementation authority and is linked as a draft plan in
`BACKLOG.md`. Its temporary planning worktree and branch had no unique commits
and were removed after the draft was copied byte-for-byte into `main`.

### Important context and decisions

The release prohibition and standard-library-only runtime boundary below
remain in force. Use `unittest`; never use pytest. Jeff wants Superpowers
execution behavior shaped in the T2.2 plan, without modifying Superpowers.
No Superpowers files were changed. The plan now states its commit, verification,
and hygiene cadence; one full hygiene pass is scoped to T2.2's actual hygiene
gate. Do not add hygiene passes to ordinary governance edits.

For ordinary changes, run the complete project gate on the active supported
Python version; use CI for broad compatibility. Use a local version matrix for
version-sensitive changes or explicit release-readiness work. T2.1's three-
version matrix was a one-time closeout check, not the routine gate.

Jeff's standing choice for completed, reviewed feature branches is local
integration into `main`, merged-result verification, and removal of the
temporary worktree and branch. Do not ask again for that choice. An ordinary
Git sync was explicitly requested for this stopping point. It does not
authorize a tag, package publication, or release.

### Immediate next actions

1. Resume using live Git and backlog state after reading the authorities in
   `AGENTS.md`. Run the backlog audit and next-action command there; stop on a
   finding. Treat this checkpoint as a snapshot.
2. Keep q4xpcc Phase 24A specification and plan reconciliation under I1.0
   high priority, using the reviewed D1.3 handoff. Runtime and fixture adoption
   remain gated by C4.4; live XPLM acquisition remains gated by A1.9.
3. For local T2.2, add executable fixtures and code examples to the remaining
   prose-only test and implementation steps. Re-run the plan audit and review
   the plan with Jeff before approval, lifecycle registration, or execution.
   Preserve its draft status until that review succeeds.

### Pending work and limits

B1.1 and canonical contract implementation remain behind T2.2 in the current
roadmap. T3.1 is an independent specified peer. I1.0 q4xpcc planning can
proceed now. T2.2 has no implementation or completion evidence. No tag,
package publication, or release occurred.

### Verification and evidence

T2.1 passed its five acceptance gates, independent review, the offline hygiene
gate, and a one-time Python 3.12–3.14 source/installed-wheel matrix (467
`unittest` tests per version). The B1.1 dependency amendment passed the
aggregate quality gate and 61 focused governance tests. The aggregate gate
runs hygiene integration tests repeatedly inside its full `unittest` suite;
that accounts for much of its runtime and does not call for a separate hygiene
pass on this docs-only checkpoint.

- T2.1 plan: `docs/superpowers/plans/2026-09-19-t2-1-repository-hygiene-artifact-verification.md`
- T2.1 completion, review, and gates: `.superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/`
- T2.2 draft: `docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`
- q4xpcc brief: `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`

### Suggested skills on resumption

Use `gzs-session-handoff` for resumption, `backlog-status` for live delivery
state, and `gzs-plan-audit` for the remaining T2.2 plan review.

## Session entry

`ROADMAP.md` is the capability-order authority and `BACKLOG.md` is the only
mutable delivery-state authority. Do not infer current state from this file;
after reading the required architecture and governance documents, inspect
`git worktree list --porcelain` and the status and commits of any linked
worktrees before reporting backlog status or selecting another increment.
Report completed but unmerged work explicitly so it is integrated through the
authorized workflow before being mistaken for unfinished work. Then run:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
```

Stop on a finding. Otherwise follow the exact reported local-child lifecycle
action.

## Architecture and release boundary

The parent architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`; the approved
repository amendment is
`docs/architecture/xplane_fdau_core_scope_amendment.md`. `xplane-fdau` is the
X-Plane-specific, transport-free, standard-library-only core. XPLM,
XPPython3, `xpwebapi`, network clients, and simulator I/O remain external.
Use `unittest`, never pytest. Local ARINC and FDM/FOQA-support behavior remains
inside this boundary.

Identity and native-FDR-kernel migration: implemented and verified, but unreleased. Completed implementation plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
The next canonical vertical slice retains measurement, binding, observation, sample, frame, timing, and quality contracts. Version `0.1.0`, tags, package
publication, and GitHub releases remain separately gated. Ordinary Git sync
requires an explicit request and does not grant release authority. `gzs-git-sync`
and `gzs-session-handoff` are explicit-only workflows.

## Current delivery path

T1.6 and T2.1 are verified at 5/5. T2.1 completed the offline project
hygiene gate and fresh wheel/sdist verification; no child is selected.
The live BACKLOG audit/next result recommends `write_plan` for T2.2.
T3.1 remains a separate specified peer; B1.1 depends only on T2.2
before canonical foundation work continues through C4.4. I1.0 q4xpcc
planning reconciliation is eligible and is the cross-repository priority.

## q4xpcc readiness

`D1.1` canonical C1-C4 design approval is verified. `D1.2` acquisition,
recording, projection, and pinning contract design is verified. `D1.3`
reviewed q4xpcc Phase 24A consumer handoff is verified. `I1.0` is eligible as
the next reportable external action for planning reconciliation.

`I1.1` permits delivered contract-model, schema, fixture, and runtime adoption
only after `C4.4`. `I1.2` permits live XPLM acquisition adoption only after
`A1.9`. Do not modify q4xpcc from this repository.

`I1.0` now permits Phase 24A specification and plan reconciliation because
`D1.3` is verified.

## Evidence pointers

- T1 design:
  `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- T1.6 plan:
  `docs/superpowers/plans/2026-09-07-t1-6-skill-session-hygiene-artifact-closure.md`
- q4xpcc brief: `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`
