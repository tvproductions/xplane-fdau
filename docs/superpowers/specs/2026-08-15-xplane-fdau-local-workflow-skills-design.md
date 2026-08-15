# xplane-fdau Local Workflow Skills Design

- **Governance:** active
- **Status:** approved
- **Date:** 2026-08-15
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T2`
- **Roadmap children:** `T2.1`, `T3.1`
- **Approval:** 2026-08-15 — Jeff / tvproductions

## Authority and purpose

`ROADMAP.md` owns roadmap identity, order, and dependencies. `BACKLOG.md` is
the only mutable delivery-state authority. The existing
`docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
continues to govern the modular `T1` backlog-status epic.

This specification translates the remaining q4xpcc-local repository workflows
into xplane-fdau-native `repo-hygiene` and `git-sync` skills. It uses q4xpcc as
review input, not as a code source or runtime/tooling dependency. The translated
skills are newly designed around xplane-fdau's distribution artifacts, roadmap,
release prohibition, standard-library boundary, and `unittest` requirement.

The workflow sequence is:

```text
T1.1 -> T1.2 -> T1.3 -> T1.4 -> T1.5 -> T1.6
                                               |
                                               +-> T2.1 repo-hygiene
                                                       |
                                                       +-> T3.1 git-sync
                                                               |
                                                               +-> B1.1
```

Repository governance is completed before the source-layout migration resumes.
Neither this design nor its skills authorize a push, tag, publication, GitHub
release, or PyPI release.

## q4xpcc design-input provenance

The reviewed q4xpcc checkout was clean at commit
`1c9ff89358e22fb3e1a4adbcc23d224f60c3dfdf`. Only its three project-local
skills were considered. Superpowers is an external dependency and is not part
of this translation inventory.

| q4xpcc local skill | SHA-256 of `SKILL.md` | xplane-fdau disposition |
| --- | --- | --- |
| `backlog-status` | `105e6e6c0cb14417b61556136961d6a8c24159ee40db0ebf3df6c5d3e9a6c65a` | Adopted through the existing modular `T1` design. Phase-specific parsing and product-evidence rules are rejected. |
| `repo-hygiene` | `7d9a62122ae9723d2dfa1db28f94934a407c67bca254a7bcd346c0094ef46509` | Translated by `T2.1` from plugin-tree inspection to fresh wheel/sdist verification. |
| `git-sync` | `f2ed129d6e98e888be9b96d04cc88df89d0432a515e88fc5c34fbb3879a24ea5` | Translated by `T3.1` with q4xpcc-style planning/apply behavior and a code-enforced xplane-fdau push prohibition. |

The q4xpcc scripts and tests are not copied. No translated skill reads q4xpcc,
assumes a sibling path, or imports a q4xpcc module.

## Decision summary

The repository will keep three independently governed workflow concerns:

1. `T1` owns backlog authority, typed status, audit, next action, guarded
   backlog mutation, and the `backlog-status` skill.
2. `T2.1` owns the canonical full-strength `repo-hygiene` workflow and replaces
   the current `hygiene` skill without an alias.
3. `T3.1` owns q4xpcc-style guarded Git planning and apply behavior, using
   `repo-hygiene` as its mandatory pre-commit gate.

The existing `code-quality`, `documentation`, and `release` skills remain
focused supporting workflows. They are not aliases for the translated skills.

## Goals

This increment will:

1. onboard every q4xpcc-local skill capability through an explicit
   xplane-fdau owner;
2. preserve the modular T1 design instead of copying q4xpcc's phase-oriented
   backlog implementation;
3. make routine hygiene validate real wheel and source-distribution artifacts;
4. make Git synchronization dry-run-first, script-backed, deterministic, and
   testable against local repositories;
5. mirror q4xpcc's guarded Git state handling while enforcing xplane-fdau's
   current no-push boundary;
6. keep all governance tooling outside built and installed artifacts; and
7. leave `B1.1` ready to resume with consistent status and repository tooling.

## Non-goals

This increment will not:

- copy q4xpcc skill, script, or test files;
- reproduce q4xpcc phase IDs, product-evidence validators, coordination gates,
  aircraft rules, plugin packaging, native build rules, or sibling paths;
- replace Superpowers or vendor it as a local workflow;
- change the xplane-fdau runtime API or native FDR behavior;
- run the Python 3.12-3.14 installed-wheel matrix during routine hygiene;
- make routine hygiene depend on network access;
- permit a push, tag, publication, GitHub release, or PyPI release; or
- collapse T1, T2.1, T3.1, and B1.1 into one implementation plan.

## T1 boundary

The existing T1 design remains authoritative for:

- Markdown authority and explicit roadmap inventory;
- typed parsing and human/JSON status;
- structural and spec/plan adherence audit;
- deterministic next-action selection;
- dry-run-first state and gate-evidence mutation; and
- `backlog-status` skill/session integration.

Its modular `model`, `parse`, `rules`, `report`, and `edit` boundaries are
retained. Generic typed evidence replaces q4xpcc's product-specific artifact
recognizers. Stable finding codes, deterministic ordering, and explicit
conflict reporting replace conversational inference.

## T2.1 repo-hygiene contract

`T2.1` creates `.codex/skills/repo-hygiene/` and removes the former
`.codex/skills/hygiene/` skill. No compatibility alias remains because these
repository-internal workflows are unreleased.

Every invocation runs the complete workflow:

1. report branch, staged/unstaged scope, and ignored/generated artifacts;
2. verify the lockfile offline;
3. run the T1 backlog audit;
4. run `tools/quality.py check`;
5. run strict MkDocs validation;
6. run every pre-commit hook;
7. build one fresh wheel and sdist in a uniquely named temporary directory
   outside the checkout;
8. run strict metadata validation and `tools/release.py check-dist` against
   that exact pair;
9. verify repository-governance skills and scripts are absent from both
   artifacts; and
10. recheck and report repository state.

The script stops at the first blocking failure and reports the failed command.
Successful temporary artifacts are removed only after their resolved path is
verified as the exact script-created temporary directory. Failed artifacts are
preserved and their exact path is reported for diagnosis.

Routine hygiene does not run the installed Python-version matrix. The
`release` skill and child-slice closeout retain that responsibility. Dependency
freshness remains an explicit opt-in network inquiry. Hygiene never formats,
stages, commits, changes declarations, or deletes repository files.

## T3.1 git-sync contract

`T3.1` replaces the prose-only Git routine with a standard-library script. The
workflow mirrors q4xpcc's guarded state machine while translating its policy to
xplane-fdau.

Dry-run is the default. Human and deterministic JSON output report:

- branch and expected branch;
- remote and remote branch;
- staged, unstaged, and untracked scope;
- ahead, behind, and diverged state;
- merge/conflict/detached state;
- planned and executed actions;
- blockers and warnings; and
- final state after apply.

A fetch with prune refreshes remote observations before planning. Apply mode:

1. revalidates the expected branch, HEAD, worktree state, and remote state;
2. displays the complete auto-add set and refuses unrelated or newly appeared
   paths;
3. stages the reviewed worktree with q4xpcc-style auto-add behavior;
4. runs the full `repo-hygiene` gate;
5. creates an intentional commit;
6. pulls fast-forward when only behind;
7. rebases when local and remote histories diverge;
8. creates a uniquely named backup branch and linearizes a repairable local
   merge-head commit before synchronization; and
9. reruns planning to report the actual resulting state.

Apply refuses detached HEAD, unresolved conflicts, merge-in-progress,
unexpected branch, stale expected HEAD or worktree scope, a missing remote
branch, fetch failure, failed hygiene, or an unrepairable merge head. No force,
`--no-verify`, `--no-hygiene`, or silent safety bypass exists.

Unlike q4xpcc, push is unavailable in both the command-line interface and the
implementation. The script contains no push execution path. An ahead branch is
reported as an expected local state and never treated as authorization for a
remote write. Tags, publication, and releases are also outside the skill.

## Error handling and exit status

Both scripts fail closed:

- exit `0` for a successful report, dry-run, or completed permitted action;
- exit `1` for repository, policy, validation, or hygiene blockers; and
- exit `2` for invalid command usage or malformed machine input.

Dry-run performs no worktree, index, commit, branch, or history mutation.
Fetch may update remote-tracking observations and is reported explicitly.
Apply pins the state observed during planning and refuses stale execution.
Primary failures remain distinguishable from cleanup failures.

## Testing strategy

All tests use `unittest`. Every behavior begins with a failing test.

### T1

The existing T1 test contract remains: strict Markdown fixtures, lifecycle
rules, typed evidence, deterministic human/JSON output, stable findings,
next-action selection, dry-run/apply mutation, stale hashes, and atomic
publication.

### T2.1

Unit tests inject command runners and temporary directories to prove command
order, immediate failure propagation, offline behavior, safe cleanup, failure
preservation, and reporting. Integration tests build fresh artifacts and prove
exact validation plus governance-tool exclusion.

### T3.1

Tests create temporary working repositories and local bare remotes. They cover
clean, dirty, ahead, behind, diverged, detached, conflicting, missing-remote,
stale-state, hygiene-failure, repairable-merge, and unrepairable-merge states.
They prove reviewed auto-add, commit, fast-forward pull, rebase, backup-branch
linearization, dry-run immutability, deterministic JSON, and the absence of any
push option or execution path. Tests never use the real repository or network.

### Repository closure

Complete verification runs the repository quality gate, strict documentation,
pre-commit, fresh artifact validation, and independent review. The installed
Python 3.12-3.14 matrix runs at the applicable child closeout, not inside every
routine hygiene invocation.

## Documentation and session integration

After the implementation children are verified:

- `AGENTS.md` invokes `backlog-status` for status/resume/adherence questions;
- `AGENTS.md` invokes `repo-hygiene` for every full hygiene and pre-handoff
  request;
- `AGENTS.md` invokes `git-sync` for guarded synchronization requests;
- `HANDOFF.md` points to the backlog and exact resume child;
- the old `hygiene` trigger is absent; and
- build/release documentation states that repository-governance tooling never
  ships.

## Acceptance criteria

### T2.1 — Canonical repo-hygiene and fresh artifact verification

- The canonical `repo-hygiene` skill replaces `hygiene` and runs status,
  offline lock, backlog audit, quality, strict documentation, and pre-commit
  gates at full strength.
- Every run builds one fresh wheel/sdist pair outside the checkout and validates
  exact metadata, members, payload bytes, and repository-governance exclusion.
- Successful temporary artifacts are safely removed while failed artifacts are
  preserved at a reported exact path for diagnosis.
- Routine hygiene performs no implicit network inquiry, repository mutation, or
  installed Python-version matrix and retains focused supporting skills.
- All standard-library tests, current-repository integration, artifact checks,
  and independent review pass without changing release authorization.

### T3.1 — Guarded local Git synchronization with push disabled

- Dry-run and JSON reports deterministically expose branch, remote, scope,
  ahead/behind/divergence, actions, warnings, blockers, and expected state.
- Apply revalidates pinned state, performs reviewed auto-add, full hygiene,
  intentional commit, fast-forward pull or rebase, and repairable merge-head
  backup/linearization with final verification.
- Detached, conflicting, stale, unexpected, missing-remote, failed-fetch,
  failed-hygiene, and unrepairable-merge states fail closed without partial
  unsafe continuation.
- Push is absent from both CLI and implementation, and no tag, publication,
  release, force, or verification-bypass path exists.
- Temporary-repository tests, current-repository dry-run, complete quality
  gates, and independent review pass without changing release authorization.

## Delivery boundary

This design covers exactly `T2.1` and `T3.1`. Each child receives one focused
implementation plan after written approval. `T1.1` through `T1.6` remain under
their existing design and execute first. `B1.1` remains specified with a draft
plan and resumes only after `T3.1` is verified.
