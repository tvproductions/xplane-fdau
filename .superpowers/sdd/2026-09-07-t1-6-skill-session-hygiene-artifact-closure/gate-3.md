# T1.6 gate 3

- **Child:** `T1.6`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-07
- **Subject:** Strict backlog audit in hygiene

Observed revision: `3a274fdd5c83954c9b5ecc8ddab6b5e588baec8d`, including
the one-command hygiene insertion `7e6be087527394ba472410a9d0221f904f097bd7`.

```powershell
uv run python .codex/skills/hygiene/scripts/hygiene.py
```

The entire command exited 0 on the clean reviewed worktree. Its exact offline
order was observed without dependency-registry inquiry or mutation:

```powershell
git status --short --branch
uv lock --check --offline
uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
uv run python tools/quality.py check
uv run python tools/quality.py pre-commit
```

Git status reported only the branch; lock validation resolved 81 packages;
audit found no findings, selected T1.6 reviewed, next verify. Full quality
passed 452 discovery tests in 331.583s and 452 coverage tests in 337.252s,
coverage 94% (1,527 statements, 98 missed), Interrogate 43.6%, and every
configured analyzer. Pre-commit invoked `uv run pre-commit run --all-files`:
quality check, detect-secrets baseline, lizard report, and cohesion report
all printed Passed. The quality hook repeats the complete quality command;
its successful verbose test output is suppressed by pre-commit, so no
separate hook timing or count is invented here.

Exact standard-library regression tests, included in the passing full suite:

```powershell
uv run python -m unittest tests.test_project_skills.ProjectSkillTests.test_hygiene_script_runs_strict_backlog_audit_before_quality tests.test_project_skills.ProjectSkillTests.test_hygiene_stops_when_backlog_audit_fails -v
```

Task 3 used these tests for RED/GREEN. The order test asserts the exact
five-command tuple. The fail-fast test returns audit exit 7, asserts unchanged
exit 7, and proves no quality/pre-commit call follows the third command.
The runner and default offline behavior are otherwise unchanged. The
repository remained tracked-clean throughout this full hygiene run; only
ignored, unlinked evidence drafting occurred. No auto-fix, state transition,
dependency refresh, or external repository operation was performed by hygiene.

Final fresh artifact hashes: wheel
`25ac6660fa3b4b1bfd5e431d0a3d7126a126012ad998509639d3f18465802afb`;
sdist `5429361eb3d1569cba926bcc0f95c72dda41caa2069bb30f2ed924f6ec52bce6`.
Gate-4.md records exact paths and Windows Python 3.12.13/3.13.14/3.14.4
installed smokes. Linux/macOS were not directly run. Runtime and release
boundaries remain unchanged; offline hygiene does not grant publication.
