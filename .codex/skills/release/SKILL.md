---
name: release
description: Use when validating, preparing, or authorizing an xplane-fdr distribution release, including wheel artifacts, installed smoke tests, release CI, or publication decisions.
---

# xplane-fdr Release

Validate first; publish only after the user explicitly authorizes every external action.

## Local Readiness

Run these from the repository root:

```powershell
uv sync --frozen
uv run python -m unittest discover -v
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run python tools/quality.py check
uv run mkdocs build --strict
uv build --no-sources
uv tool run twine check --strict dist/*
uv run python tools/release.py check-dist dist
```

The validator requires only `xplane_fdr-0.1.0-py3-none-any.whl` and `xplane_fdr-0.1.0.tar.gz`, no runtime requirements, package modules, schema, one license, and no repository/workflow/cache or official-fixture content. Release CI also checks `v0.1.0` with `tools/release.py check-tag`.

## Installed Matrix

For Python 3.12, 3.13, and 3.14, create an isolated environment outside the checkout, install the exact wheel, and run its interpreter on `tools/installed_smoke.py 0.1.0`. It must import outside the checkout, expose `__all__` and the schema, parse minimal v3/v4 fixtures, round-trip canonical v4, and resolve `xplane-fdr` from that environment's scripts directory.

## Authorization Gate

Local validation, hashes, CI success, urgency, and a release tag candidate do **not** authorize a push, tag, PyPI publication, or GitHub release. Stop after reporting immutable artifact names and SHA-256 hashes. Ask for explicit authorization that names each external action before doing any of them.
