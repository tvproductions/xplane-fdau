---
name: git-sync
description: Use when staging, committing, pushing, publishing, or synchronizing xplane-fdau changes with Git, including scope review and pre-push validation.
---

# Git Sync

Publish deliberately. Read `AGENTS.md`, inspect scope, validate, stage only intended files, commit, push, and confirm local and remote state.

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
git push origin <branch>
git fetch origin
git status -sb
git log --oneline -3
```

Use `unittest` only. Do not stage unrelated changes, use force push, rebase, merge, or publish after a rejected push without user direction. If a write command needs sandbox approval, request it with the exact command and a concise reason. Report commit SHA, branch, validation, remote, and final synchronization state.
