# Local Quality Cadence Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** Approved 2026-09-20 crosscutting T2.1 local-cadence execution record; it changes repository tooling outside roadmap-child delivery state and leaves CI and release gates intact.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make local commits fast while retaining one complete active-Python quality gate at stable closeout.

**Architecture:** Pre-commit checks staged files with Ruff and detect-secrets. Full offline hygiene invokes the unchanged aggregate quality gate directly once, then its existing docs, hook, and artifact checks. Existing source edits use standalone quality at closeout; package-boundary changes select hygiene without a duplicate gate.

**Tech Stack:** Python 3.12-3.14, standard-library `unittest`, uv, pre-commit, Ruff, ty, MkDocs.

**Spec:** `docs/superpowers/specs/2026-09-20-local-quality-cadence-design.md`

## Global Constraints

- Do not modify `.github/workflows/` or the complete `tools/quality.py check` gate and thresholds.
- Use `unittest` only; runtime stays standard-library-only.
- Preserve offline hygiene, strict backlog audit, exact artifacts, and safe cleanup.
- Keep the local three-version matrix for version-sensitive and release-readiness work.
- Do not tag, publish, release, or push as part of this change.

---

### Task 1: Fast pre-commit with full hygiene gate

**Files:**
- Modify: `.pre-commit-config.yaml`
- Modify: `.codex/skills/hygiene/scripts/hygiene.py`
- Modify: `tests/test_project_skills.py`
- Modify: `tests/test_hygiene_tool.py`

**Interfaces:**
- Consumes: `tools/quality.py check`, `tools/quality.py pre-commit`, and the existing `run_local_hygiene()` contract.
- Produces: staged-file Ruff hooks and exactly one direct full quality invocation per hygiene run.

- [x] **Step 1: Write failing contract tests.** Change the hook test to require IDs `ruff-check`, `ruff-format-check`, and `detect-secrets-baseline`, staged filenames for Ruff, and no full-suite or metrics hook. Change hygiene tests to require `uv run --offline --frozen python tools/quality.py check` once before pre-commit; preserve the existing offline and artifact assertions.
- [x] **Step 2: Prove RED.** Run `uv run python -m unittest tests.test_project_skills tests.test_hygiene_tool -q`; expect the hook and hygiene-order assertions to fail.
- [x] **Step 3: Implement.** Set Ruff entries to `uv run ruff check` and `uv run ruff format --check`, each with `types: [python]`; keep `detect-secrets-baseline`. Insert the direct quality command into `LOCAL_COMMANDS` before strict MkDocs and pre-commit.
- [x] **Step 4: Prove GREEN.** Re-run the two modules. Run `uv run pre-commit run --all-files` to validate the actual hook configuration without launching the full suite.
- [x] **Step 5: Review the diff.** Confirm `.github/workflows/` and `tools/quality.py` are untouched and hygiene still builds one artifact pair.

### Task 2: Reconcile local instructions and closeout evidence

**Files:**
- Modify: `AGENTS.md`
- Modify: `.codex/skills/code-quality/SKILL.md`
- Modify: `.codex/skills/hygiene/SKILL.md`
- Modify: `HANDOFF.md`
- Modify: `tests/test_project_skills.py`

**Interfaces:**
- Consumes: Task 1 hook and hygiene behavior.
- Produces: unambiguous edit, commit, closeout, and matrix cadence guidance.

- [x] **Step 1: Write failing guidance assertions.** Require guidance to state that full quality runs once at stable closeout, hygiene supplies that run when used, and ordinary local work does not run the version matrix.
- [x] **Step 2: Prove RED.** Run `uv run python -m unittest tests.test_project_skills -q`; expect guidance assertions to fail.
- [x] **Step 3: Update instructions.** Remove the before-every-commit full-gate instruction; document focused edit commands, the fast hook, and the single closeout command choice. Update the handoff resume point without changing backlog state.
- [x] **Step 4: Prove GREEN.** Re-run `tests.test_project_skills` and run the backlog audit.
- [x] **Step 5: Verify closeout.** Run the full offline hygiene command once, which supplies the active-version quality gate, strict docs, fast hooks, and fresh artifact validation. Check `git diff --check` and `git status --short`.
