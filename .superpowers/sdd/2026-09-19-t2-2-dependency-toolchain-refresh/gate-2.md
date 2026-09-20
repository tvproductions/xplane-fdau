# T2.2 gate 2 — Guarded compatible refresh

- **Child:** `T2.2`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** Exact uv and Python policy, complete lock, stale-scope and security fail-closed checks.

The verified newest stable uv and WinGet-owned installed executable were both `0.12.17`; apply made no global tool change and pinned `[tool.uv].required-version = "==0.12.17"`. Existing CI `setup-uv` pins already matched `0.12.17`. `requires-python` changed from `>=3.12` to `>=3.12,<3.15`, with 3.12/3.13/3.14 classifiers retained and development-only `packaging>=25`. Runtime dependencies remain empty. `uv lock --upgrade`, `uv sync --all-groups --locked`, and `uv lock --check` exited 0. The 98-package registry graph changed only `virtualenv` 21.7.16 → 21.9.0.

Apply re-collected official status, compared SHA-256 and exact reviewed Git paths/index bytes, validated all managed edit anchors and uv installer ownership before writing, and blocked unresolved after-refresh yanks/advisories, missing source evidence, and unexplained constraints. Regression cases passed for stale source/lock/branch/review scope, untrusted or malformed official responses, incompatible Python and `uv_build` targets, unknown owner, workflow-anchor mismatch, ordered commands, and post-refresh failure. Five stale versions remained explained by exact [wily](https://pypi.org/pypi/wily/1.25.0/json), [virtualenv](https://pypi.org/pypi/virtualenv/21.9.0/json), and [radon](https://pypi.org/pypi/radon/5.1.0/json) release requirements; the corrected constraint evaluator tests explicit OS/Python markers and candidate `Requires-Python` evidence. No unresolved blocker, yank, or advisory remained.
