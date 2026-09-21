# Fast Local Closeout Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** Crosscutting execution plan for Jeff's 2026-09-20 approved fast-local-closeout design; implementation is in progress on the temporary fast-local-closeout branch and does not alter roadmap child status.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Surface cheap local failures before coverage and replace a duplicate full suite after an exact local fast-forward with focused, offline merged-checkout verification.

**Architecture:** Reorder the existing blocking quality and hygiene commands without removing checks. Add one standard-library project adapter that validates exact Git evidence and runs focused import, backlog, wheel, sdist, and installed-smoke checks on main. Document the narrow local-merge exception.

**Tech Stack:** Python 3.12-3.14, unittest, uv, Ruff, ty, pre-commit, MkDocs, Git, existing release and installed-smoke tools.

**Spec:** docs/superpowers/specs/2026-09-20-fast-local-closeout-design.md

## Global constraints

- No pytest; use unittest only.
- Preserve standard-library-only runtime and unchanged xplane_fdau distribution.
- Preserve every existing blocking quality check, coverage threshold, offline hygiene artifact inventory, CI workflow, release gate, and Git-sync safeguard.
- Run focused unittest, Ruff, and ty during edits; run full offline hygiene once on the stable feature candidate.
- The merge shortcut applies only after an exact, clean, user-selected local fast-forward with a tracked passing branch receipt.
- No Git push, tag, publication, or release is implied.

## File map

| Responsibility | Exact files |
| --- | --- |
| Quality fail-fast order and contracts | tools/quality.py, tests/test_quality_tool.py |
| Hygiene fail-fast order and contracts | .codex/skills/hygiene/scripts/hygiene.py, tests/test_hygiene_tool.py, tests/test_project_skills.py |
| Focused merge verification | tools/merge_verify.py, tests/test_merge_verify.py |
| Workflow guidance and closure | AGENTS.md, .codex/skills/code-quality/SKILL.md, .codex/skills/hygiene/SKILL.md, HANDOFF.md, tests/test_project_skills.py, this plan |

## Task 1: Put cheap quality checks before coverage

- [ ] Add assertions in tests/test_quality_tool.py that the check sequence is Ruff lint/format, ty, Bandit, detect-secrets hook/report, Interrogate, Vulture, Xenon, focused live-state unittest, then coverage run/report. Require exactly one coverage-backed full suite, one focused preflight, unchanged standalone test command, and no dropped blocking step.
- [ ] Run uv run --offline --frozen python -m unittest tests.test_quality_tool -v and record the expected order failure.
- [ ] In tools/quality.py add a named preflight Step invoking only tests.test_backlog_status_cli.BacklogStatusCliTests.test_current_repository_status_reports_human_and_json and tests.test_project_metadata.ProjectMetadataTests.test_runtime_package_uses_only_installed_src_layout. Reorder CHECK_STEPS as above; leave COMMANDS coverage, security, and thresholds intact.
- [ ] Repeat the focused unittest; run Ruff check/format on the two files and uv run --offline --frozen ty check.
- [ ] Commit as build: run quality preflight before coverage.

## Task 2: Put docs and hooks before the full hygiene gate

- [ ] Update tests/test_hygiene_tool.py and tests/test_project_skills.py command-order expectations: status, ignored status, offline lock, strict backlog audit, strict MkDocs, all-files pre-commit, then exactly one complete quality check, followed by the existing artifact commands and final statuses. Add a negative control that a pre-commit failure stops before quality and artifacts.
- [ ] Run uv run --offline --frozen python -m unittest tests.test_hygiene_tool tests.test_project_skills -q and record the expected order failures.
- [ ] Change LOCAL_COMMANDS in .codex/skills/hygiene/scripts/hygiene.py to the required order without changing artifact_commands, owned-directory checks, or run_command behavior.
- [ ] Repeat the focused unittest; run Ruff check/format on changed Python tests and hygiene script, then ty check.
- [ ] Commit as build: fail fast on hygiene docs and hooks.

## Task 3: Reject unsafe merge shortcuts

- [ ] Add tests/test_merge_verify.py with synthetic temporary Git repositories or injected command results for wrong branch, dirty tracked/untracked checkout, missing or non-passing tracked receipt, wrong expected HEAD, non-ancestor full-gate commit, and any disallowed changed path. Accept Markdown under docs and .superpowers/sdd plus BACKLOG.md and HANDOFF.md. Assert no uv/build invocation occurs on refusal.
- [ ] Run uv run --offline --frozen python -m unittest tests.test_merge_verify -v and record RED.
- [ ] Implement the Git/evidence precheck and CLI in tools/merge_verify.py. Arguments are --expected-head SHA, --full-gate-commit SHA, and --receipt repository-relative path. Require main, exact HEAD, clean porcelain status including untracked files, a tracked passing verification receipt in HEAD, ancestor relation, and allowlisted intervening paths. Use subprocess argument lists and explicit text encoding/error handling; reject links and unsafe paths.
- [ ] Repeat focused unittest, Ruff check/format, and ty check. Commit as build: guard exact local merge verification.

## Task 4: Verify merged artifacts and installed import offline

- [ ] Add positive and failure tests for command ordering: offline frozen sync/lock, strict backlog audit, the two focused live-state unittests, fresh external wheel/sdist build, strict Twine, exact release.py check-dist, isolated wheel install, installed_smoke.py, and import path. Verify failure preserves the exact temp path; success checks ownership and removes only its own temp directory. Verify JSON/report output names commit, Python version, artifact hashes, and import path.
- [ ] Run the focused tests and record RED.
- [ ] Complete tools/merge_verify.py using the existing release and installed-smoke command interfaces. Use one tempfile.mkdtemp under the OS temp parent, record directory and parent identities, reject symlinks/junctions or changed identities before recursive cleanup, and preserve on failure. Do not invoke Git pull/push or any release action.
- [ ] Repeat focused unittest, Ruff check/format, and ty check. Use a synthetic main repository in unittest for the positive proof; the real command requires main and runs only after a user-selected local integration.
- [ ] Commit as build: verify fast-forward artifacts and installed imports.

## Task 5: Guidance, review, and stable closeout

- [ ] In tests/test_project_skills.py assert that AGENTS.md and the project quality/hygiene adapters state the narrow exact-fast-forward exception, preflight-before-coverage order, full-gate fallback, worktree preservation on failure, and no remote/release authority.
- [ ] Run that focused test and record RED; update AGENTS.md, both skill adapters, and HANDOFF.md to match the spec; repeat the focused test and run strict backlog audit.
- [ ] Run an independent implementation review against the spec, plan, and source diff. Address load-bearing findings with focused RED/GREEN checks.
- [ ] Run one full offline hygiene gate on the stable feature candidate. It must run preflight, strict docs, hooks, the complete 521-plus unittest suite under coverage, security/static checks, and exact artifacts once. Record timing and verify that preflight occurs before coverage.
- [ ] Add a tracked passing receipt under .superpowers/sdd/2026-09-20-fast-local-closeout/, with Result: passed, the exact branch full-gate commit, command, and measured timing. Force-add the ignored receipt. The verifier reads this tracked receipt only after local integration; do not invent a passing receipt before the gate.
- [ ] Mark plan steps complete, replace this plan disposition with completed implementation and evidence, run focused documentation checks, backlog audit, git diff --check, and commit closure. Present finishing choices. If Jeff selects local integration, record branch HEAD, fast-forward main without pull, run tools/merge_verify.py with expected HEAD, full-gate commit, and receipt, then remove the worktree and branch only after it passes. No push, tag, publication, or release.
