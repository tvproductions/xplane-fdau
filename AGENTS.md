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
  checks for the affected work. Pre-commit runs fast staged-file checks; it
  does not run the complete suite on each intermediate commit.
- Run the complete project gate on the active supported Python version once at
  stable closeout for ordinary changes. Edits to existing source files use the
  standalone quality gate. Run full offline hygiene when package layout,
  shipped resources, distribution metadata, lockfiles, build rules, or artifact
  validation changes; hygiene supplies that full gate, so do not run it
  separately on the same unchanged candidate. For documentation or governance
  edits, run their focused checks. Do not add a full 3.12–3.14 source and
  installed-wheel matrix to routine feature closeout. Use CI for broad
  compatibility coverage; run a local version matrix only for
  version-sensitive changes or an explicit release-readiness requirement.

## Runtime Boundary

- `xplane-fdau` must remain pure Python and standard-library-only at runtime.
- Do not introduce a dependency on `xpwebapi`, XPPython3, XPLM, or any network
  client.

## Canonical gz-skills Workflows

- The `gz-skills@gz-skills` Codex plugin is the sole portable workflow authority.
  The trusted project `.codex/config.toml` pins marketplace `gz-skills` to
  `https://github.com/tvproductions/gz-skills.git` at reviewed tag `v0.3.2`
  and enables the plugin. Install through `codex plugin add gz-skills@gz-skills`
  if absent; verify ID, version, enabled state, and source with
  `codex plugin list --json` and `codex plugin marketplace list --json`.
  Stop if the plugin is unavailable. Do not use copied, linked, vendored, or
  standalone `gzs-*` skills under `.agents/skills`, `.codex/skills`, or another
  discovery root, and do not recreate `gz-skills.lock.json`.
- A full `gzs-update-dependencies` run inventories the project-pinned plugin
  alongside Python and other managed dependencies. Review a new release before
  changing `.codex/config.toml`; Codex marketplace owns the plugin update.
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
  `uv run python tools/quality.py check`; the current hygiene command is
  `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py`. Use `unittest`
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

- Use `.agents/superpowers` as the governing external Superpowers checkout.
  Keep it ignored and update it from `https://github.com/obra/superpowers.git`;
  do not vendor upstream Superpowers under `.codex`.
- Expose its skills at `.agents/skills/superpowers` using a local directory
  junction to `.agents/superpowers/skills`, matching the q4xpcc discovery
  surface. Keep both the checkout and junction ignored.
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
