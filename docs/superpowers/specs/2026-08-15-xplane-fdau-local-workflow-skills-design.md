# xplane-fdau Local Workflow Skills Design

- **Governance:** active
- **Status:** approved
- **Date:** 2026-08-15
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T2`
- **Roadmap children:** `T2.1`, `T2.2`, `T3.1`
- **Approval:** 2026-08-15 — Jeff / tvproductions; canonical workflow amendment approved 2026-09-05 by Jeff / tvproductions

## Authority and purpose

`ROADMAP.md` owns roadmap identity, order, and dependencies. `BACKLOG.md` is
the only mutable delivery-state authority. The existing
`docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
continues to govern the modular `T1` backlog-status epic.
The repository-owned
[`xplane_fdau_core_scope_amendment.md`](../../architecture/xplane_fdau_core_scope_amendment.md)
governs the Python compatibility and dependency boundaries used here.

This specification translates the remaining q4xpcc-local repository workflows
into future deterministic xplane-fdau project adapters for canonical
`gzs-repository-hygiene`, `gzs-update-dependencies`, and `gzs-git-sync`. Jeff's
2026-09-05 adoption of all eleven `gz-skills` workflows sunsets the proposed
local canonical skill definitions: the pinned `.agents/skills/gzs-*` catalog
and `gz-skills.lock.json` own portable workflow behavior. This design still owns
the project-specific commands, distribution artifacts, roadmap, release
boundary, standard-library boundary, 3.12-3.14 compatibility matrix, and
`unittest` requirement. q4xpcc remains review input, not a code source or
runtime/tooling dependency.

The workflow sequence is:

```text
T1.1 -> T1.2 -> T1.3 -> T1.4 -> T1.5 -> T1.6
                                               |
                                               +-> T2.1 hygiene adapter
                                                       |
                                                       +-> T2.2 dependency adapter ---+
                                                       |                            |
                                                       +-> T3.1 Git-sync adapter -----+-> B1.1
```

Repository governance is completed before the source-layout migration resumes.
Installing the canonical workflows or implementing these adapters does not
execute or authorize a sync. A later explicit Git-sync request authorizes an
ordinary guarded commit and push with final remote-alignment proof. Tags,
package publication, and GitHub releases remain separately gated.
This 2026-09-05 current-policy amendment supersedes older no-push wording only
for explicitly requested ordinary Git synchronization. It does not rewrite or
weaken accepted D1, provenance, implementation, or release evidence.

## q4xpcc design-input provenance

The initial q4xpcc review used clean commit
`1c9ff89358e22fb3e1a4adbcc23d224f60c3dfdf`. The parity update reviewed the
clean q4xpcc commit `a7cc2682ca4289f498fffc409a091e28f528fe9a` on 2026-08-16.
Only project-local skills were considered. The external Superpowers checkout
is explicitly excluded from the comparison, refresh workflow, and translation
inventory.

| q4xpcc local skill | SHA-256 of `SKILL.md` | xplane-fdau disposition |
| --- | --- | --- |
| `backlog-status` | `105e6e6c0cb14417b61556136961d6a8c24159ee40db0ebf3df6c5d3e9a6c65a` | Adopted through the existing modular `T1` design. Phase-specific parsing and product-evidence rules are rejected. |
| `repo-hygiene` | `7d9a62122ae9723d2dfa1db28f94934a407c67bca254a7bcd346c0094ef46509` | Its project-specific artifact checks inform the future `T2.1` adapter beneath `gzs-repository-hygiene`. |
| `refresh-dependencies` | `94141338f038a3d59006bd74e6088aab1b1865f50edc6122b63e003f6cbb4de5` | Its project-specific dependency mechanics inform the future `T2.2` adapter beneath `gzs-update-dependencies`. Superpowers operations are excluded. |
| `git-sync` | `f2ed129d6e98e888be9b96d04cc88df89d0432a515e88fc5c34fbb3879a24ea5` | Its deterministic state observations inform the future `T3.1` adapter beneath `gzs-git-sync`; the canonical portable workflow owns guarded publication behavior. |

The q4xpcc scripts and tests are not copied. No translated skill reads q4xpcc,
assumes a sibling path, or imports a q4xpcc module.

## Decision summary

The repository will keep three independently governed workflow concerns:

1. `T1` owns backlog authority, typed status, audit, next action, guarded
   backlog mutation, and the `backlog-status` skill.
2. `T2.1` owns the future deterministic project hygiene adapter used by
   `gzs-repository-hygiene`; it does not create another canonical skill.
3. `T2.2` owns the future deterministic project dependency adapter used by
   `gzs-update-dependencies`, including the exact repository `uv` pin and
   complete development lock.
4. `T3.1` owns the future deterministic project Git adapter used by
   `gzs-git-sync`, with full project hygiene as its mandatory pre-commit gate.

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
5. mirror q4xpcc's guarded Git state handling while allowing only an explicitly
   authorized ordinary push and requiring final fetch/alignment proof;
6. keep the exact `uv` pin current through newest-stable discovery and review,
   while ordinary development dependencies use compatible declarations plus a
   complete reproducible lock;
7. keep all governance tooling outside built and installed artifacts; and
8. leave `B1.1` ready to resume with consistent status and repository tooling.

## Non-goals

This increment will not:

- copy q4xpcc skill, script, or test files;
- reproduce q4xpcc phase IDs, product-evidence validators, coordination gates,
  aircraft rules, plugin packaging, native build rules, or sibling paths;
- replace Superpowers or vendor it as a local workflow;
- inspect, compare, update, or otherwise manage the external Superpowers
  checkout through the dependency adapter or `gzs-update-dependencies`;
- change the xplane-fdau runtime API or native FDR behavior;
- run the Python 3.12-3.14 installed-wheel matrix during routine hygiene;
- make routine hygiene depend on network access;
- infer Git-sync permission from implementation, installation, handoff, or any
  request other than explicit synchronization; permit a tag, package
  publication, GitHub release, or PyPI release; or
- collapse T1, T2.1, T2.2, T3.1, and B1.1 into one implementation plan.

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

## T2.1 project repository-hygiene adapter contract

`T2.1` supplies a deterministic project-owned command adapter for canonical
`gzs-repository-hygiene`. It may replace the current provisional hygiene script
and guidance when implemented, but it does not create or rename a competing
canonical/local workflow skill.

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

## T2.2 dependency-update adapter contract

`T2.2` supplies the deterministic project-owned command adapter used by
canonical `gzs-update-dependencies` to inquire about and update repository
dependency declarations, the lock, and the pinned `uv` tool version. It is
explicit and network-aware; routine hygiene remains offline. It does not create
a competing canonical/local workflow skill.

Every invocation begins read-only and reports human and deterministic JSON
status for:

- the installed `uv` executable and repository `required-version`;
- the newest stable `uv` release available from an official source;
- the supported Python range `>=3.12,<3.15` and required 3.12, 3.13, and 3.14
  verification matrix;
- direct development constraints, locked direct and transitive versions,
  outdated classifications, yanked releases, and published vulnerability
  findings; and
- the exact files and commands an apply would change or run.

The live report, not a version captured while designing the skill, supplies the
candidate `uv` target. Stable releases are preferred so the exact pin follows
new releases without silently accepting prereleases. If the newest stable
release is incompatible with the repository, the workflow retains the current
verified pin and reports a blocker with evidence; it never weakens gates merely
to advance the version.

Apply mode requires a clean or fully scope-reviewed dependency surface and
revalidates the status immediately before mutation. It then:

1. verifies or updates the executable through its owning package manager;
2. sets the project `uv.required-version` to the exact verified stable version;
3. aligns `requires-python` to `>=3.12,<3.15`, the 3.12-3.14 classifiers, and
   the required source/installed-wheel matrix;
4. keeps ordinary development declarations compatible rather than exact-pins
   every package, unless a documented incompatibility requires a bound;
5. upgrades the complete lock across all development groups;
6. synchronizes and checks the selected environment;
7. reports unresolved outdated, yanked, vulnerability, and constraint findings;
8. runs targeted dependency-policy and skill tests using `unittest`;
9. runs full `repo-hygiene` and the 3.12-3.14 source/installed-wheel matrix; and
10. proves dependency and refresh tooling is absent from wheel and sdist
   runtime payloads.

The workflow uses only official package metadata and advisory sources for
version and vulnerability decisions. Network, parsing, resolver, policy,
verification, or artifact failures are blockers. It never updates Python past
the reviewed compatibility range, touches the external Superpowers checkout,
deploys to X-Plane, stages, commits, pushes, tags, publishes, or releases.

## T3.1 guarded Git synchronization adapter contract

`T3.1` supplies a standard-library project adapter beneath canonical
`gzs-git-sync`. It mirrors q4xpcc's useful guarded observations while preserving
the portable workflow's authority and does not create a competing
canonical/local workflow skill.

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
7. rebases only unpublished local commits when local and remote histories
   diverge and project policy permits it;
8. pushes only under the user's explicit Git-sync authorization; and
9. fetches again and proves the final local/remote state is `ahead=0`,
   `behind=0` with no unintended worktree changes.

Apply refuses detached HEAD, unresolved conflicts, merge-in-progress,
unexpected branch, stale expected HEAD or worktree scope, a missing remote
branch, fetch failure, failed hygiene, ambiguous divergence, published-history
rewrite, or unresolved merge head. The portable skill does not require automatic
merge-head rewriting or linearization; the adapter stops rather than inventing
that behavior. No force, destructive reset, `--no-verify`, `--no-hygiene`, or
silent safety bypass exists. An ahead branch is incomplete until an explicitly
authorized push and fresh alignment proof succeed. Tags, publication, and
releases remain outside the adapter.

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

### T2.2

Tests inject official-source responses, command runners, and temporary project
surfaces. They cover current, newer-stable, prerelease-only, incompatible,
yanked, vulnerable, constrained, dirty, stale-plan, resolver-failure, and
artifact-leak cases. They prove dry-run immutability, deterministic JSON, exact
`uv` pinning, compatible ordinary declarations, full-lock refresh, 3.12-3.14
verification, and the absence of any Superpowers or release mutation path.

### T3.1

Tests create temporary working repositories and local bare remotes. They cover
clean, dirty, ahead, behind, diverged, detached, conflicting, missing-remote,
stale-state, hygiene-failure, published-history, merge-head, push-failure, and
final-alignment-failure states. They prove reviewed auto-add, commit,
fast-forward pull, rebase of unpublished commits only, explicit-authorized
push, post-push fetch/alignment, dry-run immutability, and deterministic JSON.
Tests never use the real repository or network.

### Repository closure

Complete verification runs the repository quality gate, strict documentation,
pre-commit, fresh artifact validation, and independent review. The installed
Python 3.12-3.14 matrix runs at the applicable child closeout, not inside every
routine hygiene invocation.

## Documentation and session integration

After the implementation children are verified:

- `AGENTS.md` invokes `backlog-status` for status/resume/adherence questions;
- `AGENTS.md` routes full hygiene to `gzs-repository-hygiene` and the project
  hygiene command adapter;
- `AGENTS.md` routes dependency, Python-compatibility, `uv`, lock-freshness,
  and vulnerability work to `gzs-update-dependencies` and the future project
  dependency adapter;
- `AGENTS.md` invokes explicit-only `gzs-git-sync` for guarded synchronization
  requests and uses the future project Git adapter when available;
- `HANDOFF.md` points to the backlog and exact resume child;
- no project helper claims canonical portable-workflow ownership; and
- build/release documentation states that repository-governance tooling never
  ships.

## Acceptance criteria

### T2.1 — Project repository-hygiene adapter and fresh artifact verification

- A deterministic project hygiene adapter supplies xplane-fdau commands to
  canonical `gzs-repository-hygiene` and runs status, offline lock, backlog
  audit, quality, strict documentation, and pre-commit gates at full strength.
- Every run builds one fresh wheel/sdist pair outside the checkout and validates
  exact metadata, members, payload bytes, and repository-governance exclusion.
- Successful temporary artifacts are safely removed while failed artifacts are
  preserved at a reported exact path for diagnosis.
- Routine hygiene performs no implicit network inquiry, repository mutation, or
  installed Python-version matrix and retains focused supporting skills.
- All standard-library tests, current-repository integration, artifact checks,
  and independent review pass without changing release authorization.

### T2.2 — Governed dependency and toolchain refresh

- Read-only human and JSON status discover the newest stable `uv`, supported
  Python matrix, locked graph, outdated releases, yanks, vulnerabilities, and
  constraints from official sources without mutation.
- Apply pins the exact verified stable `uv`, aligns package metadata to
  `>=3.12,<3.15`, retains compatible ordinary development constraints,
  refreshes the complete lock, and fails closed on stale scope, incompatible
  resolution, or unexplained security findings.
- Targeted `unittest`, full repo hygiene, Python 3.12-3.14 source and
  installed-wheel verification, and exact wheel/sdist inventory all pass.
- Superpowers, X-Plane deployment, staging, commit, push, tag, publication, and
  release behavior is absent from the skill and implementation.

### T3.1 — Guarded Git synchronization adapter

- Dry-run and JSON reports deterministically expose branch, remote, scope,
  ahead/behind/divergence, actions, warnings, blockers, and expected state.
- Apply revalidates pinned state, performs reviewed auto-add, full hygiene,
  intentional commit, fast-forward pull or rebase of unpublished commits, an
  explicitly authorized ordinary push, and a fresh final fetch/alignment check.
- Detached, conflicting, stale, unexpected, missing-remote, failed-fetch,
  failed-hygiene, merge-head, published-history-rewrite, failed-push, and
  failed-alignment states fail closed without partial unsafe continuation.
- An explicitly authorized ordinary push finishes only after proof that local
  and remote are `ahead=0`, `behind=0`; no tag, publication, release, force,
  destructive-reset, or verification-bypass path exists.
- Temporary-repository tests, current-repository dry-run, complete quality
  gates, and independent review pass without changing release authorization.

## Delivery boundary

This design covers exactly `T2.1`, `T2.2`, and `T3.1`. Each child receives one
focused implementation plan after written approval. `T1.1` through `T1.6`
remain under their existing design and execute first. After `T2.1`, `T2.2` and
`T3.1` may proceed as peers. `B1.1` remains specified with a draft plan and
resumes only after both `T2.2` and `T3.1` are verified.
