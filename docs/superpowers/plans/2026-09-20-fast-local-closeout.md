# Fast local closeout implementation plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** Crosscutting `T2.1` local-cadence execution record for the approved design at `docs/superpowers/specs/2026-09-20-fast-local-closeout-design.md`; it does not advance a roadmap child.

**Goal:** Fail before coverage when existing fast checks detect a problem, and document focused verification after an exact local fast-forward.

**Scope:** Reorder existing quality and hygiene steps; add two existing focused tests as a quality preflight; update AGENTS.md, quality and hygiene adapters, and HANDOFF.md. No new verification command.

## Task 1: Quality order

- [ ] In `tests/test_quality_tool.py`, assert security, docs, dead-code, complexity, and a focused preflight precede coverage, while the complete coverage suite runs once. Run the test and record RED.
- [ ] Add the preflight step and reorder `CHECK_STEPS` in `tools/quality.py`, preserving all current commands and thresholds. Run `uv run --offline --frozen python -m unittest tests.test_quality_tool -q`, Ruff check/format for changed Python files, and `uv run --offline --frozen ty check`.
- [ ] Commit `build: run fast quality checks before coverage`.

## Task 2: Hygiene order

- [ ] In `tests/test_hygiene_tool.py` and `tests/test_project_skills.py`, assert strict docs and all-files hooks run before the complete quality gate, and a hook failure stops before quality. Run the focused tests and record RED.
- [ ] Reorder `LOCAL_COMMANDS` in `.codex/skills/hygiene/scripts/hygiene.py` without changing the artifact phase. Repeat the focused tests, Ruff, and ty.
- [ ] Commit `build: fail fast in offline hygiene`.

## Task 3: Guidance and closeout

- [ ] Update `AGENTS.md`, `.codex/skills/code-quality/SKILL.md`, `.codex/skills/hygiene/SKILL.md`, and `HANDOFF.md` with the narrow exact-fast-forward procedure and fallback. Check guidance with `tests.test_project_skills`, strict backlog audit, strict MkDocs, and `git diff --check`.
- [ ] Review the changed diff against the approved design. Run one full offline hygiene gate on the stable branch candidate, recording its result and timing. Later documentation-only edits receive focused checks.
- [ ] Mark plan steps complete and commit the implementation record. After user-selected local integration, confirm exact HEAD equality, run the documented focused main commands, then remove the temporary worktree and branch only after they pass. Do not push, tag, or publish.
