# Agent Instructions

## Session Entry

- Read `HANDOFF.md` before taking any project action.
- Read `ROADMAP.md` for capability order and release gates, then `BACKLOG.md`
  for the active slice, status, governing documents, and acceptance evidence.
- Read the complete parent architecture at
  `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`.
- Read the completed migration specification at
  `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`
  and its completed plan at
  `docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
- Read the current canonical-contract specification and plan linked from
  `BACKLOG.md` before changing canonical FDAU behavior. A draft specification
  is review material, not implementation authority.
- The next release remains prohibited until a reviewed canonical vertical slice
  is complete. Do not push, tag, publish, or create a release in this increment.

## Testing

- **NO pytest. EVER.** Do not add, suggest, or assume pytest as a testing
  framework.
- Use Python's `unittest` framework.

## Runtime Boundary

- `xplane-fdau` must remain pure Python and standard-library-only at runtime.
- Do not introduce a dependency on `xpwebapi`, XPPython3, XPLM, or any network
  client.

## Superpowers Workflow

- Use `.agents/superpowers` as the governing external Superpowers checkout.
  Keep it ignored and update it from `https://github.com/obra/superpowers.git`;
  do not vendor upstream Superpowers under `.codex`.
- Expose its skills at `.agents/skills/superpowers` using a local directory
  junction to `.agents/superpowers/skills`, matching the q4xpcc discovery
  surface. Keep both the checkout and junction ignored.
- Keep `.codex/skills` limited to xplane-fdau-specific workflow skills and
  repository-local tooling.
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
