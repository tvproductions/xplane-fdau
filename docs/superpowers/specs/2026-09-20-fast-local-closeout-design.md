# Fast local closeout design

- **Governance:** historical
- **Status:** completed
- **Disposition:** Approved 2026-09-20 crosscutting amendment to `T2.1` local quality cadence, following B1.1 gate timing. It does not change roadmap child state or release authority.

## Decision

B1.1's full suites took 314.236 seconds on its branch and 292.904 seconds after local integration. Jeff approved a smaller local-workflow change: surface cheap failures before coverage and use focused verification after an exact local fast-forward of a branch that already passed its complete gate. Keep existing tools and thresholds; add no merge-verification command.

## Branch closeout

- Continue focused `unittest`, Ruff, and ty checks during edits. Run one complete quality gate on the stable branch candidate, or full offline hygiene when packaging or artifact surfaces change.
- In `tools/quality.py check`, run Ruff, ty, security, documentation, dead-code, and complexity checks before coverage. Add a focused live-state preflight with the existing current-backlog-status and repository-root import-layout tests before coverage. Retain the complete coverage-backed suite and its 40% minimum.
- In offline hygiene, run lock and backlog checks, strict MkDocs, and all-files pre-commit before the complete quality gate. Retain one quality invocation and the existing external wheel/sdist validation after it.

## Exact local fast-forward

After the user selects local integration, record the reviewed branch HEAD and its passing full-gate result. Check that both worktrees are clean, then fast-forward main without a pull. Confirm main HEAD exactly equals that branch HEAD. On main, use existing commands for offline frozen sync, lock consistency, backlog audit, the two live-state tests, and a fresh external wheel/sdist build with strict metadata and exact inventory checks. For package or installed-import changes, run the existing installed-wheel smoke from an external environment. Record the commands and result in the completion evidence.

If the merge is not an exact fast-forward, the branch gate did not pass, the tree changed after that gate in a way the focused checks do not cover, or a focused main check fails, investigate and run the complete gate on the resulting main candidate. Keep the worktree and branch until main verification passes. The user-approved focused main check is the narrow exception to the upstream finishing instruction to rerun the full suite after local integration.

## Limits and acceptance

No CI, release, remote sync, runtime dependency, quality threshold, or compatibility-matrix policy changes. Existing project scripts perform all checks; no new tool or dependency is added. A docs, hook, live-state, or secrets-baseline failure must stop before coverage. The branch still receives one complete gate; an exact fast-forward receives focused main verification with identical HEAD and a fresh artifact check. A differing tree requires the full gate.
