---
name: hygiene
description: Use when performing xplane-fdau cleanup, maintenance, lockfile checks, dependency chores, pre-handoff verification, or an offline repository hygiene pass.
---

# xplane-fdau Hygiene Adapter

`gzs-repository-hygiene` owns the portable repository-hygiene workflow. Inspect
the worktree first, then run the complete local project gate from the checkout
root:

```powershell
git status --short --branch
git diff --stat
git diff --cached --stat
uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py
```

The outer uv invocation and every routine child command run offline. The script
checks normal and ignored Git status, `uv lock --check --offline`, the strict
backlog audit, and `mkdocs build --strict`. It then runs the local pre-commit
hooks once. The `quality-check` hook supplies the single
`tools/quality.py check` invocation; the remaining local hooks also run.

The artifact phase creates one fresh external temporary directory. It builds
one wheel and sdist with `uv build --offline --no-sources`, checks both with
`twine check --strict`, and validates exact members and payloads with
`tools/release.py check-dist`. Normal and ignored Git status run again before
cleanup. Successful cleanup checks the created directory and parent identities
immediately before deleting that exact directory. On any artifact or final
status failure, the directory is preserved and its path is reported. The gate
does not format, update, stage, commit, or remove user-authored files.

The 3.12, 3.13, and 3.14 source and installed-wheel matrix is separate child
closeout evidence, outside routine hygiene. Use the `code-quality`,
`documentation`, and `release` project skills for their focused commands.
Use `unittest` only.

For a specifically requested dependency freshness inquiry, run the explicit
network probe:

```powershell
uv run --frozen python .codex/skills/hygiene/scripts/hygiene.py --dependencies
```

For a complete project-managed dependency refresh, follow
`gzs-update-dependencies`; the opt-in command above is only an inquiry.
Git sync and release remain governed by their separate authorization and
release gates. Report commands, status, failures, preserved artifacts, skipped
checks, dependency drift, and changed-file scope.
