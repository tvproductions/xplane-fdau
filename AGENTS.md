# Agent Instructions

## Session Entry

- Read `HANDOFF.md` before taking any project action.
- Read `ROADMAP.md` for capability order and release gates, then `BACKLOG.md`
  for the active slice, status, governing documents, and acceptance evidence.
- Read the complete parent architecture at
  `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`.
- Read the repository-owned scope amendment at
  `docs/architecture/xplane_fdau_core_scope_amendment.md`. It governs the
  X-Plane-specific core purpose, external client/adapter boundary, local
  ARINC and FDM/FOQA ownership, and Python compatibility policy where the
  provenance-locked parent architecture differs.
- Read the completed migration specification at
  `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`
  and its completed plan at
  `docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
- Read the current canonical-contract specification and plan linked from
  `BACKLOG.md` before changing canonical FDAU behavior. A draft specification
  is review material, not implementation authority.
- Run the repository backlog workflow after reading those authorities:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  ```

  Stop on an audit finding. Otherwise follow the reported lifecycle action
  for the selected or first dependency-ready local child. Read
  `.codex/skills/backlog-status/SKILL.md` for status, resume, adherence,
  next-action, or controlled state requests.
- The next release remains prohibited until a reviewed canonical vertical slice
  is complete. Tags, package publication, and GitHub releases remain separately
  gated; an explicitly requested ordinary Git sync does not grant release
  authority.

## Testing

- **NO pytest. EVER.** Do not add, suggest, or assume pytest as a testing
  framework.
- Use Python's `unittest` framework.
- During implementation, use focused `unittest`, Ruff lint/format, and ty
  checks for the affected work. Installed pre-commit runs Ruff check,
  Ruff format --check, ty, and the full unittest suite. Do not bypass hooks.
- Run the complete project gate on the active supported Python version once at
  stable closeout for ordinary changes. Edits to existing source files use the
  standalone quality gate. Run full offline hygiene when package layout,
  shipped resources, distribution metadata, lockfiles, build rules, or artifact
  validation changes; hygiene supplies that full gate, so do not run it
  separately on the same unchanged candidate. For documentation or governance
  edits, run their focused checks. Python 3.12 is the sole supported minor
  version for now; use it for source and installed-wheel verification. Reserve
  the local external wheel check for version-sensitive changes and release
  readiness. Do not add unsupported Python minors to routine feature closeout.

### Exact local fast-forward verification

After a reviewed branch passes its complete gate and the user selects local
integration, record its HEAD and passing gate. Check both worktrees are clean,
use `git merge --ff-only` on main without pulling, and confirm main HEAD
equals the recorded branch HEAD. Run the focused offline main checks in the
hygiene skill: frozen sync, lock check, backlog audit, live-state tests, and a
fresh external artifact pair with strict metadata and inventory validation.
For package or installed-import changes, also run external installed-wheel
smoke. This user-approved exact fast-forward path replaces a second complete
gate on an identical merged tree. If HEAD differs, the branch gate is stale,
the tree changed beyond the focused checks, or any check fails, investigate
and run the complete gate on main. Keep the worktree and branch until main
verification passes. This does not authorize remote sync, a tag, or release.

## Runtime Boundary

- `xplane-fdau` must remain pure Python and standard-library-only at runtime.
- Do not introduce a dependency on `xpwebapi`, XPPython3, XPLM, or any network
  client.

## Canonical gz-skills Workflows

- Read `AGENTS.skills-first.md`, `docs/agents/skills-first.md`, and
  `docs/engineering/python.md`. Their applicable starter engineering obligations
  are mandatory. The approved baseline is recorded in `.skills-first/bundle.lock.json`;
  the current refresh evidence is `docs/reviews/2026-11-01-coordinated-refresh.md`.
  The outstanding STRICT adoption evidence remains in
  `docs/reviews/2026-10-25-strict-heavy-starter-adoption.md`.
- Use the shared `skills-first-starter` marketplace at its reviewed full starter
  revision, with `superpowers@skills-first-starter` and
  `gz-skills@skills-first-starter`. The latter is the sole portable workflow authority.
  Keep duplicate sources disabled in this project. Verify ID, version, enabled state,
  actual checkout revision and source with
  `codex plugin list --json` and `codex plugin marketplace list --json`.
  Use the native manager for installation and refresh; preserve user defaults and
  unrelated projects. Verify discovery in a fresh session; configured is not discovered.
  Stop the affected workflow if its owning plugin is unavailable. Do not use copied, linked, vendored, or
  standalone `gzs-*` skills under `.agents/skills`, `.codex/skills`, or another
  discovery root, and do not recreate `gz-skills.lock.json`.
- The explicit profile is **heavy**. Backplane remains disabled pending readiness
  and separate adoption authority. FDAU requirements, backlog and release ownership
  remain local. Heavy selection does not establish complete stack readiness.
- A full `gzs-update-dependencies` run inventories the starter, Superpowers,
  Backplane and gz-skills independently alongside Python and managed tools.
  Use the discovered `update-gz-template` skill for released template changes;
  reconcile shared provenance and managed files together, without a private catalog.
  Review at adoption, scoped maintenance, quarterly on demand, and release acceptance.
  Do not create an automatic schedule. Codex owns native plugin updates.
  The T2.2 Python/uv adapter does not mutate the plugin cache. A full refresh
  cannot be reported complete while this project-managed pin is unverified.
- Use `gzs-router` for catalog orientation. Apply the documented automatic
  triggers for `gzs-agent-context-diet`, `gzs-cross-platform-python`,
  `gzs-intent-audit`, `gzs-plan-audit`, `gzs-quality-gate`,
  `gzs-repository-hygiene`, `gzs-tech-debt-review`, and
  `gzs-update-dependencies`.
- `gzs-git-sync` and `gzs-session-handoff` are explicit-only. Invoke Git sync
  only when the user asks to sync, commit and push, publish the current work, or
  create a remote save point. Invoke session handoff only when the user asks to
  hand off, checkpoint, resume, or preserve work. Installing or using any other
  workflow never implies either operation.
- Project adapters under `.codex/skills` provide exact xplane-fdau commands and
  domain boundaries beneath the portable invariants. The quality command is
  `uv run --locked --all-groups python tools/quality.py check`; the hygiene command is
  `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`. Use `unittest`
  only, preserve the standard-library-only runtime, and follow the canonical
  Git-sync safeguards for any explicitly authorized ordinary push.

- For an explicit complete dependency refresh, use canonical
  `gzs-update-dependencies` and the project adapter after reviewing its status
  report. On Windows run
  `.venv/Scripts/python.exe tools/dependency_refresh.py status --json`;
  use `.venv/bin/python` on POSIX. Apply with
  `tools/dependency_refresh.py apply --plan-sha256 <digest>` and one
  `--review-scope <path>` per reviewed dirty path. Keep routine hygiene offline.

## Superpowers Workflow

- Use the selected native Superpowers plugin. Do not create a competing
  `.agents/skills/superpowers` junction or vendor upstream skills. Preserve a
  pre-existing checkout as rollback state; detach only a verified link, never
  recursively delete its target. Main's legacy discovery surface is reconciled
  separately at verified integration.
- Keep `.codex/skills` limited to xplane-fdau-specific adapters, domain
  guidance, and repository-local tooling; do not duplicate a canonical
  `gzs-*` workflow there.
- Follow the upstream Superpowers workflow in order:
  1. `superpowers:brainstorming` before changing behavior, with the reviewed
     design saved under `docs/superpowers/specs/`.
  2. `superpowers:using-git-worktrees` after design approval unless the user
     explicitly directs work in the current checkout or on `main`.
  3. `superpowers:writing-plans` after design approval, with exact files,
     steps, tests, verification commands, and commits recorded under
     `docs/superpowers/plans/`.
  4. `superpowers:subagent-driven-development` for independent plan tasks in
     the current session, or `superpowers:executing-plans` when appropriate.
  5. `superpowers:test-driven-development` during implementation: failing
     `unittest` first, minimal implementation, then green verification.
  6. `superpowers:requesting-code-review` at substantial checkpoints and
     before finishing major feature work; address findings before continuing.
  7. `superpowers:finishing-a-development-branch` after the plan is complete
     and verified.
- A worktree's feature branch is temporary implementation plumbing, not a
  long-lived delivery path.
- After the user selects local integration, merge back to `main`, verify the
  merged result, remove the worktree, and delete its temporary branch.
- Superpowers review and subagent checkpoints are authorized when their
  workflow calls for them, unless the current user message says otherwise.

## Release planning and version advancement

PRDs guide major releases; selected work and requirements drive minor releases;
fixes drive patch releases. Follow the canonical starter policy at
https://github.com/tvproductions/gz-skills-first-starter/blob/main/docs/versioning.md#plan-releases-from-their-governing-work
and this project binding. Every major, including 1.0.0, requires a newly written
PRD defining that major's outcomes, requirements and acceptance criteria.

Before implementation planning, identify the release scope served by the work.
Keep a current release-scope record in this project's existing backlog, roadmap
or release authority: actual last published version/tag/revision (or evidence of
no prior release), proposed next version, governing PRD/requirements/fixes,
included completed and remaining work, deferred work, compatibility impact and
acceptance gates. Reconcile completed changes into that record before closeout.
Missing scope/version evidence blocks release-preparation acceptance. Do not
silently shrink approved scope or include the entire future backlog in one release.

Apply SemVer to the complete selected scope since the published baseline.
After 1.0, incompatible contracts require major, compatible requirements/capability
or public deprecations require minor, and compatible fixes require patch. During
0.x, requirements/capability and incompatible changes require minor; compatible
fixes require patch. Multiple tasks in one release share its pending version.
An initial unpublished 0.1.0 may cover an explicitly selected first-release scope;
review scope growth instead of using unpublished status to avoid release accounting.
Keep metadata/runtime mirrors, affected lock metadata and changelog aligned when
the pending version is selected. Preserve published versions/tags, independent
product/template/plugin versions and existing release gates. These instructions
do not authorize publication or enable deferred Backplane.

### Required version decision checks

At requirements intake, planning and closeout, agents MUST derive the pending
target from the actual published baseline and the complete pending scope.
Identify the new major PRD, selected minor requirements or commitment corrected
by a patch. A ticket labeled fix cannot turn new requirements into patch work.
Use the highest required increment and reset lower components: 1.4.2 becomes
1.4.3 for fixes, 1.5.0 for compatible requirements, or 2.0.0 for a breaking
major guided by a newly written PRD. During 0.x, requirements drive 0.4.2 to
0.5.0; compatible fixes drive 0.4.3. Reuse an adequate pending target rather
than incrementing once per task. Reconcile version mirrors and changelog in
the same authorized change; do not ask the maintainer to choose routine numbers.

Require a finite release outcome, included requirements, exclusions and an
acceptance gate, including for the initial 0.1.0. Assign future requirements
to later minor bundles. Preserve approved scope; ask only for unresolved
product decisions. Missing required PRD, scope or consistent version evidence
blocks the applicable planning and closeout claims as well as release preparation.
Report published baseline -> pending target, governing source, compatibility,
version agreement, completed/remaining/deferred work and publication status.
A selected target does not assert readiness or authorize publication. Use the
canonical policy's required-version-decision-procedure; keep the record in
existing project authorities rather than creating another tracker.

### November 1, 2026 local release-accounting review

Development 0.1.0 remains unpublished: no local release tags or GitHub releases
were found on 2026-11-01. ROADMAP.md and BACKLOG.md explicitly gate the first
release on the canonical vertical slice and G1. Retain that gate and selected
first-release requirements; completed children are implementation increments, not
automatic minor releases. Record the remaining selected scope and later/deferred
work in those existing authorities. Any proposed earlier release requires an
explicit scope decision; this policy correction does not select or transition a
child, amend an approved plan or change release readiness.

Reviewed source: starter base commit
`8d090f88bf45b9a755808a62c1445beeb005daff` plus the authorized, uncommitted
0.8.1 clarification. This is development guidance, not a published template
upgrade. Reviewed `docs/versioning.md` SHA-256:
`960cc4052cb87696980be23a393553079f254ac8105240dbcbac5244a52c4460`;
`templates/AGENTS.skills-first.md` SHA-256:
`0383bc3330756600b2d9e0ae2393af0143836b7e6bc3b5b8d407e39f361b51b4`.
No adoption lock, component pin, plugin activation or product version is changed.
