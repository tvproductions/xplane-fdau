# T2.1 gate 4 — Offline scope and supporting skills

- **Child:** `T2.1`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-19
- **Subject:** Offline routine without implicit dependency inquiry, mutation, or matrix

Observed reviewed revision: `149392f33b404e13722ada199ab49e52f8c5f792`. The public project command in both `AGENTS.md` and `.codex/skills/hygiene/SKILL.md` is `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py`. Every direct routine subprocess gets `UV_OFFLINE=1`, `shell=False`, and the checkout root; local pre-commit hooks use `uv run` and inherit the offline environment. The real run left tracked/untracked Git status identical. It did not query outdated dependencies, update packages, stage, commit, sync, or run a Python-version matrix.

The network-capable dependency probe remains opt-in behind `--dependencies`, and complete upgrades route to `gzs-update-dependencies`. `gzs-repository-hygiene` remains the portable owner; `code-quality`, `documentation`, and `release` remain focused project skills. The 3.12–3.14 matrix was executed separately only for this child closeout. The changed implementation range contains no `xplane_fdau/` runtime file, and `pyproject.toml` still has `dependencies = []`. Git sync, tags, publication, and release authorization did not change.
