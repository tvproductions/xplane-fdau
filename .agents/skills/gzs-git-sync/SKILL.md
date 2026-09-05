---
name: gzs-git-sync
description: Create and publish a guarded Git save point after reviewing scope and passing the repository's own quality gates. Use only when the user explicitly asks to git sync, commit and push, publish the current work, or create a remote save point.
compatibility: Requires Git, a configured repository remote, and permission to commit and push.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Git Sync

Own the complete save-point ritual: review the work, validate it through the
repository's declared gates, commit the intended unit, reconcile safely with the
remote, push, and prove local and remote are aligned.

The user's explicit invocation authorizes the ordinary commit and push steps for
the current repository. It does not authorize destructive history changes,
unrelated cleanup, or bypassing repository safeguards.

## Workflow

1. Read the repository's applicable agent guidance and inspect the current
   branch, remote tracking branch, complete worktree status, staged diff, and
   unstaged diff. Completion means every changed path is understood.
2. Decide whether the changed paths form one truthful save point. Preserve
   unrelated user work. If the tree contains changes that cannot truthfully ship
   together and the intended subset cannot be established from context, stop
   and name the boundary.
3. Discover the repository's canonical sync command. Prefer, in order:

   - A repo-local `gzs-git-sync` or `git-sync` skill with a deterministic helper.
   - A documented `gz git-sync` or equivalent project command.
   - The repository's documented quality commands followed by ordinary Git.

   Treat the portable skill as the invariant and the project surface as the
   adapter. Do not substitute remembered commands for documented ones.
4. Preview mutations when the selected adapter supports a dry run. Fetch current
   remote state before trusting ahead/behind counts. Completion means the plan
   identifies the branch, remote, changed-file scope, validation, commit, remote
   reconciliation, and push.
5. Run every quality gate required for the changed scope. Keep commit hooks
   enabled. Fix an in-scope failure and rerun its owning gate; stop on a failure
   that cannot be resolved within the requested work.
6. Stage only the intended save point and inspect the staged diff. Compose a
   concise commit message that describes the whole staged unit. Do not commit an
   empty or misleading unit.
7. Commit, fetch, and reconcile without rewriting published history. Use a
   fast-forward when available. Rebase only unpublished local commits when the
   repository permits it. Stop on conflicts or ambiguous divergence.
8. Push the current branch to its configured remote. When the remote branch does
   not exist, create it with upstream tracking if repository policy permits.
9. Fetch once more and verify the final state. Completion requires the intended
   commit to exist locally and remotely, `ahead=0`, `behind=0`, and no unintended
   staged or unstaged changes.

## Safety invariants

- Preserve published history: no force push or destructive reset.
- Preserve hooks and gates: no `--no-verify` or equivalent bypass.
- Preserve user work: no automatic clean, stash deletion, branch deletion, or
  unrelated file edits.
- Treat failed fetches, unresolved conflicts, detached HEAD, and unexplained
  divergence as blockers.
- Never claim synchronization from a successful push alone; prove final remote
  alignment.

## Evidence

Report the branch, remote, changed-file scope, validation commands and results,
commit SHA and message, reconciliation performed, push result, and final
ahead/behind and worktree state. Name any skipped gate or unresolved warning.
