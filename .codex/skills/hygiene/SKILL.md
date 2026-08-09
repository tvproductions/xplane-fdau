---
name: hygiene
description: Use when performing xplane-fdau cleanup, maintenance, lockfile checks, dependency chores, pre-handoff verification, or an offline repository hygiene pass.
---

# Hygiene

Inspect the worktree first, then run the deterministic local workflow:

```powershell
git status --short --branch
git diff --stat
git diff --cached --stat
uv run python .codex/skills/hygiene/scripts/hygiene.py
```

The script checks the lockfile offline, runs `tools/quality.py check`, and runs the repository pre-commit hooks. Do not silently format, update, stage, clean, or delete files.

For a requested dependency freshness check, use the opt-in network command:

```powershell
uv run python .codex/skills/hygiene/scripts/hygiene.py --dependencies
```

If updates are approved, change the declared constraint intentionally, run `uv lock --upgrade-package <name>`, inspect both lockfile and project-file diffs, then rerun hygiene. Use `unittest` only; retain generated caches outside commits. Report commands, status, failures, skipped checks, dependency drift, and changed-file scope.
