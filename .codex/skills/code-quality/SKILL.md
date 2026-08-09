---
name: code-quality
description: Use when changing xplane-fdau code or tooling, checking lint, formatting, types, tests, coverage, security, complexity, pre-commit, or CI-equivalent quality gates.
---

# Code Quality

Use the repository gate so local validation has the same order and scope as CI.

Run the blocking gate before a commit, handoff, or non-trivial change:

```powershell
uv run python tools/quality.py check
```

During an edit, run the smallest relevant gate and repair its failure before continuing:

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

`check` runs Ruff, ty, `unittest`, coverage, Bandit, detect-secrets, Interrogate, Vulture, and Xenon. Metrics and history inspection stay explicit and nonblocking:

```powershell
uv run python tools/quality.py metrics
uv run python tools/quality.py wily
```

Use `unittest` only. Keep generated coverage, Wily, Ruff, and ty cache data out of commits. Update `.secrets.baseline` only after reviewing a deliberate scan-setting or finding change.
