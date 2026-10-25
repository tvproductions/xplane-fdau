---
name: release
description: Use when validating local readiness for the unreleased xplane-fdau distribution, including wheel artifacts, installed smoke tests, and release-readiness checks.
---

# xplane-fdau Release Readiness

Validate local readiness only; release publication is not authorized by this
workflow and it does not sync Git. A separately and explicitly requested
`gzs-git-sync` may perform an
ordinary guarded commit and push without granting tag, package-publication, or
GitHub-release authority.

## Local Readiness

Run these from the repository root:

```powershell
uv sync --locked --all-groups
uv run --locked --all-groups python tools/quality.py check
uv run --locked --all-groups mkdocs build --strict
uv build --no-sources
uv run --locked --all-groups twine check --strict dist/*
uv run --locked --all-groups python tools/release.py check-dist dist
```

The validator requires only `xplane_fdau-0.1.0-py3-none-any.whl` and `xplane_fdau-0.1.0.tar.gz`, no runtime requirements, package modules, schema, one license, and no repository/workflow/cache or official-fixture content.

Use the exact selected Python patch in `.python-version`. Also execute the
applicable deeper analysis, source-independent sdist-to-wheel build and A01–A18
proof in `docs/engineering/python.md` on the actual candidate. Required failed,
unknown or stale evidence blocks STRICT acceptance. Product SemVer is separate
from the template; every major, including 1.0.0, requires its newly reviewed PRD.
G1 and canonical vertical-slice prerequisites remain binding.

## Installed Matrix

For Python 3.12, create an isolated environment outside the checkout, install the exact wheel, and run its interpreter on `tools/installed_smoke.py 0.1.0`. It must import `xplane_fdau` outside the checkout, load the nested schema, parse minimal v3/v4 fixtures, round-trip canonical v4, and resolve `xplane-fdau` from that environment's scripts directory.

## Authorization Gate

Stop after reporting local readiness and immutable artifact names and SHA-256
hashes. Do not tag, publish to PyPI, or create a GitHub release; the canonical
vertical slice must be complete and release publication must be separately
authorized first.
