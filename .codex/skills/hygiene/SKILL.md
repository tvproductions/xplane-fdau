---
name: hygiene
description: Use when performing xplane-fdau cleanup, maintenance, lockfile checks, dependency chores, artifact-sensitive pre-handoff verification, or an offline repository hygiene pass.
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
checks normal and ignored Git status, `uv lock --check --offline`, and the strict
backlog audit. It runs `mkdocs build --strict` and all-files pre-commit
hooks before invoking `tools/quality.py check` directly exactly once.
Documentation or hook failures therefore stop before coverage.
Use full hygiene at stable closeout when package layout, shipped resource or
schema inventory, distribution metadata, lockfiles, build rules, or artifact
validation changes. It supplies the complete active-Python quality gate, so
do not run that gate separately on the same unchanged candidate. Edits to
existing source files use the standalone quality gate once at closeout.
Documentation changes use a strict MkDocs build; governance changes use the
strict backlog audit as focused checks.

## Focused main verification after an exact fast-forward

Use this only after the user selects local integration and the clean, reviewed
branch has passed its complete gate. Record branch HEAD and the passing result.
On clean main, run `git merge --ff-only <temporary-branch>` without pulling;
confirm main HEAD equals the recorded branch HEAD. Then run these existing
checks on main:

```powershell
uv sync --offline --frozen
uv lock --check --offline
uv run --offline --frozen python .codex/skills/backlog-status/scripts/backlog_status.py audit
uv run --offline --frozen python -m unittest tests.test_backlog_status_cli.BacklogStatusCliTests.test_current_repository_status_reports_human_and_json tests.test_project_metadata.ProjectMetadataTests.test_runtime_package_uses_only_installed_src_layout -q
$artifactDir = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-merge-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $artifactDir | Out-Null
uv build --offline --no-sources --out-dir $artifactDir
uv run --offline --frozen twine check --strict (Join-Path $artifactDir "xplane_fdau-0.1.0-py3-none-any.whl") (Join-Path $artifactDir "xplane_fdau-0.1.0.tar.gz")
uv run --offline --frozen python tools/release.py check-dist $artifactDir
```

Use the version in `pyproject.toml` for the two artifact names. Record the
temporary artifact path and command results. For package or installed-import
changes, use the existing external environment procedure in the release skill
to run `tools/installed_smoke.py` on the newly built wheel. Keep the worktree
and branch until every focused main check passes. If main HEAD differs from
the reviewed branch, the branch gate is stale, the merged tree changed beyond
these focused checks, or a check fails, investigate and run the complete gate
on main. This exact fast-forward exception avoids a duplicate complete suite;
it grants no Git push, tag, publication, or release authority.

The artifact phase creates one fresh external temporary directory. It builds
one wheel and sdist with `uv build --offline --no-sources`, checks both with
`twine check --strict`, and validates exact members and payloads with
`tools/release.py check-dist`. Normal and ignored Git status run again before
cleanup. Successful cleanup checks the created directory and parent identities
immediately before deleting that exact directory. On any artifact or final
status failure, the directory is preserved and its path is reported. The gate
does not format, update, stage, commit, or remove user-authored files.

The local 3.12, 3.13, and 3.14 source and installed-wheel matrix is reserved
for version-sensitive changes and release readiness, outside routine hygiene.
CI supplies broad compatibility coverage. Use the `code-quality`,
`documentation`, and `release` project skills for their focused commands.
Use `unittest` only.

For a specifically requested dependency freshness inquiry, run the explicit
network probe:

```powershell
uv run --frozen python .codex/skills/hygiene/scripts/hygiene.py --dependencies
```

For a complete project-managed dependency refresh, follow
`gzs-update-dependencies`; the opt-in command above is only an inquiry.

The explicit network-aware project refresh adapter is
`tools/dependency_refresh.py`: inspect `status --json`, then run
`apply --plan-sha256 <digest>` only for the reviewed scope under canonical
`gzs-update-dependencies`. Routine hygiene stays offline.

Git sync and release remain governed by their separate authorization and
release gates. Report commands, status, failures, preserved artifacts, skipped
checks, dependency drift, and changed-file scope.
