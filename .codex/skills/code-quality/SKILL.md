---
name: code-quality
description: Use when changing xplane-fdau code or tooling, checking lint, formatting, types, tests, coverage, security, complexity, pre-commit, or CI-equivalent quality gates.
---

# xplane-fdau Quality Adapter

`gzs-quality-gate` owns the portable complete-verification workflow. This
project adapter supplies xplane-fdau's exact aggregate and focused commands so
local validation has the same order and scope as CI.

During an edit, run focused `unittest`, Ruff, and ty checks for the affected
work. Pre-commit checks staged Python files and secrets without launching the
full suite. Repair a focused failure before continuing:

```powershell
uv run python -m unittest tests.test_fdr_reader -q
uv run ruff check xplane_fdau tests tools
uv run ruff format --check xplane_fdau tests tools
uv run ty check
```

At stable closeout, run the complete active-Python gate exactly once:

```powershell
uv run python tools/quality.py check
```

Edits to existing source files use the standalone command at stable closeout.
When package layout, shipped resources, metadata, lockfiles, build rules, or
artifact validation changes, full offline hygiene invokes this gate directly
once; do not also run the standalone command on the same unchanged candidate.
Use the smallest relevant standalone gate when diagnosing a failure:

```powershell
uv run python tools/quality.py lint
uv run python tools/quality.py format-check
uv run python tools/quality.py format
uv run python tools/quality.py typecheck
uv run python tools/quality.py test
uv run python tools/quality.py coverage
uv run python tools/quality.py security
uv run python tools/quality.py docs
uv run python tools/quality.py dead-code
uv run python tools/quality.py complexity
```

`check` runs Ruff, ty, the full `unittest` suite once under coverage, Bandit,
detect-secrets, Interrogate, Vulture, and Xenon. `test` remains a focused
standalone command. Metrics and history inspection stay explicit and
nonblocking:

```powershell
uv run python tools/quality.py metrics
uv run python tools/quality.py wily
```

Use `unittest` only. Keep generated coverage, Wily, Ruff, and ty cache data out of commits. Update `.secrets.baseline` only after reviewing a deliberate scan-setting or finding change.
