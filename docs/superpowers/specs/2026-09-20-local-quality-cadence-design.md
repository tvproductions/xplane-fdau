# Local quality cadence design

- **Governance:** historical
- **Status:** completed
- **Disposition:** Approved 2026-09-20 crosscutting correction to T2.1 local-cadence policy; retained as the design authority for the current hook, hygiene, and guidance changes outside roadmap-child delivery state.

## Decision and authority

Jeff requested a fix to the local development cadence after reviewing the
three-stage proposal and clarified that GitHub Actions is separate from the
local bottleneck. This design amends the invocation cadence in the verified
T2.1 local-workflow design. Its historical implementation and evidence remain
historical facts. The complete quality thresholds, release gates, Python
support policy, and CI workflow remain unchanged.

## Problem

The `quality-check` pre-commit hook runs `tools/quality.py check`, including
the full `unittest` suite under coverage. Every commit pays for that gate.
Hygiene runs all pre-commit hooks, so the same quality gate runs again after a
manual closeout check. The local three-version matrix is also too costly for
ordinary feature closeout, although it remains required for version-sensitive
and release-readiness work.

## Local workflow

1. During edits, use focused `unittest` and the relevant Ruff and ty checks.
   Intermediate commits do not trigger the complete quality suite.
2. Pre-commit runs Ruff lint and format checks only for staged Python files,
   plus the existing staged-file detect-secrets hook. Lizard and cohesion
   remain available through `tools/quality.py metrics` as explicit diagnostics.
3. At stable closeout, run the complete active-Python gate exactly once.
   For a change to package layout, shipped resource or schema inventory,
   distribution metadata, lockfiles, build rules, or artifact validation,
   invoke full offline hygiene; hygiene runs `tools/quality.py check` directly
   once, then strict documentation, fast pre-commit hooks, and one fresh
   wheel/sdist inspection. Do not also invoke `quality.py check` separately
   for that same unchanged candidate.
4. For edits to existing source files, invoke
   `uv run python tools/quality.py check` once at closeout without full
   hygiene. Run strict MkDocs for documentation changes and the strict backlog
   audit for governance changes.
5. Run the local Python 3.12-3.14 source/installed-wheel matrix only for
   version-sensitive changes or explicit release readiness. CI continues
   broad compatibility verification.

The full `quality.py check` command and its thresholds are unchanged. Hygiene
continues to fail closed, preserve failed artifacts, and avoid network access
and repository mutation. Pre-commit does not become a release or quality-gate
substitute.

## Surfaces

- `.pre-commit-config.yaml`: replace the full-suite hook with staged-file Ruff
  lint and format hooks; retain staged detect-secrets; remove metrics hooks.
- `.codex/skills/hygiene/scripts/hygiene.py`: call the full quality gate once
  directly before the fast pre-commit pass.
- `AGENTS.md`, project quality/hygiene skills, and `HANDOFF.md`: state the new
  cadence and exact closeout choice.
- Contract tests: verify the hook entries and hygiene command order, including
  exactly one direct full quality invocation.

## Acceptance

- A commit no longer launches coverage or the full `unittest` suite.
- Full hygiene still executes every blocking quality check once and validates
  one fresh exact artifact pair.
- Local closeout instructions never require both standalone full quality and
  full hygiene for one unchanged candidate.
- No GitHub Actions workflow, full-gate threshold, matrix support target,
  release gate, runtime dependency, or publication authority changes.
