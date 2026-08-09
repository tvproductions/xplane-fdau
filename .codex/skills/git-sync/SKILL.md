---
name: git-sync
description: Use when staging, committing, or inspecting synchronization state for xplane-fdau changes, including scope review and local validation.
---

# Git Sync

Prepare local changes deliberately. Read `AGENTS.md`, inspect scope, validate,
stage only intended files, commit, and confirm local state.

This project is unreleased and its canonical vertical slice is incomplete. Do not push.
A future push requires both completion of that vertical slice and a
separate request in which the user separately authorizes it; this skill grants
neither condition.

```powershell
git status -sb
git diff --stat
git diff --cached --stat
uv run python -m unittest discover -v
uv run ruff check xplane_fdau tests tools
uv run ruff format --check xplane_fdau tests tools
```

If unrelated changes are mixed in, ask which paths belong to the requested publish. Otherwise stage the scoped paths, inspect the staged diff, and use a concise imperative commit subject.

```powershell
git add -- <paths>
git diff --cached --check
git diff --cached
git commit -m "<subject>"
git status -sb
git log --oneline -3
```

Use `unittest` only. Do not stage unrelated changes, force push, rebase, merge,
tag, publish, or create a release. If a write command needs sandbox approval,
request it with the exact command and a concise reason. Report commit SHA,
branch, validation, and final local state.
