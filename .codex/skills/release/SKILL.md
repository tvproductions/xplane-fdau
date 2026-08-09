---
name: release
description: Use when validating local readiness for the unreleased xplane-fdau distribution, including wheel artifacts, installed smoke tests, and release-readiness checks.
---

# xplane-fdau Release Readiness

Validate local readiness only; publication is not authorized for this increment.

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

The validator requires only `xplane_fdau-0.1.0-py3-none-any.whl` and `xplane_fdau-0.1.0.tar.gz`, no runtime requirements, package modules, schema, one license, and no repository/workflow/cache or official-fixture content.

## Installed Matrix

For Python 3.12, 3.13, and 3.14, create an isolated environment outside the checkout, install the exact wheel, and run its interpreter on `tools/installed_smoke.py 0.1.0`. It must import `xplane_fdau` outside the checkout, load the nested schema, parse minimal v3/v4 fixtures, round-trip canonical v4, and resolve `xplane-fdau` from that environment's scripts directory.

## Authorization Gate

Stop after reporting local readiness and immutable artifact names and SHA-256 hashes. Do not push, tag, publish to PyPI, or create a GitHub release; the canonical vertical slice must be complete and separately authorized first.
