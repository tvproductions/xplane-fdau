# T2.1 gate 1 — Complete deterministic offline hygiene

- **Child:** `T2.1`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-19
- **Subject:** Ordered full-strength offline repository hygiene gate

Observed reviewed revision: `149392f33b404e13722ada199ab49e52f8c5f792`; implementation ends at `8d291c3`. `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` exited 0 on the corrected tree, with identical tracked/untracked Git status before and after. Its direct command order was normal status, ignored status, `uv lock --check --offline`, strict backlog audit, `mkdocs build --strict`, and `tools/quality.py pre-commit`; the final two status commands ran after artifact validation. `HygieneCommandTests` and `ProjectSkillTests` assert exact order, offline/frozen uv arguments, `UV_OFFLINE=1`, `shell=False`, fail-fast OSError/nonzero handling, and exactly one local `quality-check` hook.

The real run passed strict MkDocs and all four local pre-commit hooks: quality check, detect-secrets baseline, lizard report, and cohesion report. The quality hook ran the complete repository gate once, including Ruff, ty, `unittest` coverage, Bandit, detect-secrets, Interrogate, Vulture, and Xenon. Separate aggregate `uv run python tools/quality.py check` runs before the implemented and reviewed checkpoint commits exited 0. No gate was weakened or skipped. Windows was observed; macOS and Linux were not.
