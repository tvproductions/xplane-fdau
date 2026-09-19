# Single-Pass Verification Correction Implementation Plan

This is a standalone maintenance execution record, not a governed child plan.
`T2.1` remains specified; its full artifact-hygiene adapter is not delivered here.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each aggregate quality or hygiene invocation execute the full `unittest` suite only once while preserving every blocking analyzer and pre-commit hook.

**Architecture:** Keep `quality.py test` as a focused standalone command, but let `quality.py check` take its sole full-suite run from `coverage`. The provisional hygiene command runs the offline lock check and then pre-commit, whose existing `quality-check` hook owns the aggregate quality call. Release-readiness CI calls only the aggregate quality command. This is a correction to existing tooling, not delivery of the full T2.1 artifact hygiene adapter.

**Tech Stack:** Python 3.12–3.14, standard-library `unittest`, `uv`, coverage, pre-commit, GitHub Actions YAML.

**Spec:** `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md` (2026-09-19 single-pass amendment).

## Global Constraints

- `unittest` only; never pytest.
- Runtime remains standard-library-only and transport-free.
- No release, tag, package publication, Git sync, or T2.1 completion claim.
- Preserve every existing quality analyzer, pre-commit hook, and coverage threshold.
- Do not overwrite the dependency-refresh edits in the primary checkout.

---

### Task 1: One full-suite execution in the aggregate quality command

**Files:** Modify `tests/test_quality_tool.py`, `tools/quality.py`, `.codex/skills/code-quality/SKILL.md`.

**Interfaces:** `quality.COMMANDS["test"]` remains the standalone `unittest` command; `quality.CHECK_STEPS` retains all blocking steps except standalone `test`; `quality.run_steps` still stops on first failure.

- [ ] Add a `unittest` test invoking `quality.run_steps(quality.CHECK_STEPS, runner)` with a deterministic subprocess boundary; assert one `unittest` execution, via `coverage run`, and successful execution of the remaining blocking steps. Assert `quality.COMMANDS["test"]` still invokes standalone `unittest`.
- [ ] Run `uv run python -m unittest tests.test_quality_tool -v`; the new count assertion fails because the aggregate command currently contains two suite runs.
- [ ] Remove `*COMMANDS["test"]` from `CHECK_STEPS`; update the quality adapter's wording to say the aggregate runs tests once under coverage.
- [ ] Rerun `uv run python -m unittest tests.test_quality_tool -v`; expect green.

### Task 2: One quality invocation from routine hygiene

**Files:** Modify `tests/test_project_skills.py`, `.codex/skills/hygiene/scripts/hygiene.py`, `.codex/skills/hygiene/SKILL.md`.

**Interfaces:** `run_local_hygiene(runner)` retains status, offline lock and failure propagation; pre-commit runs all hooks, including the unchanged `quality-check` hook.

- [ ] Replace the existing hygiene topology assertion with a runner-injected `unittest` test that checks the executed commands are status, offline lock, and `quality.py pre-commit`, with no direct `quality.py check`. Keep a failure case showing the first failed command stops the sequence.
- [ ] Run `uv run python -m unittest tests.test_project_skills -v`; expect failure from the extra direct quality command.
- [ ] Remove that command from `LOCAL_COMMANDS`; update the hygiene adapter to explain that pre-commit supplies the single aggregate quality invocation.
- [ ] Rerun the focused project-skill tests; expect green.

### Task 3: One release-readiness source gate and final verification

**Files:** Modify `tests/test_release_workflows.py`, `.github/workflows/release-readiness.yml`, `.codex/skills/release/SKILL.md`.

**Interfaces:** Release-readiness still installs Python 3.14, runs `quality.py check`, strict MkDocs, fresh artifact validation, and the installed-wheel matrix.

- [ ] Add a workflow test proving the `validate-release` job has one aggregate quality step and no preceding standalone full-suite step.
- [ ] Run `uv run python -m unittest tests.test_release_workflows -v`; expect failure on the existing standalone step.
- [ ] Remove only the redundant `python -m unittest discover -v` step from release-readiness; preserve all other workflow steps. Remove the separate unittest, Ruff, and ty calls from local release guidance because the aggregate quality command already owns them.
- [ ] Rerun focused tests and `git diff --check`; expect green.
- [ ] Run the final single full verification through `uv run python .codex/skills/hygiene/scripts/hygiene.py`; record its exit status, test count, coverage, and all hook results. Do not invoke a separate full `quality.py check` before or after it.
- [ ] Request review of the scoped diff, address any findings test-first, and rerun only affected checks plus the final gate if the candidate changes. Leave the branch uncommitted for an explicit integration decision.
