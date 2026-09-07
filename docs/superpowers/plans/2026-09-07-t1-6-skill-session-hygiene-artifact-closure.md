# T1.6 Skill, Session-Entry, Hygiene, and Artifact Closure Implementation Plan

- **Governance:** active
- **Status:** completed
- **Date:** 2026-09-07
- **Roadmap child:** `T1.6`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- **Approval:** 2026-09-07 — Jeff / tvproductions
- **Completion evidence:** `.superpowers/sdd/2026-09-07-t1-6-skill-session-hygiene-artifact-closure/completion.md`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the completed backlog engine discoverable and mandatory at the correct repository workflow seams, prove repository-governance content cannot ship, and close T1 without changing runtime behavior or release authority.

**Architecture:** Keep the existing backlog engine and its CLI unchanged. Add a thin project-local skill that routes status and controlled-state requests to that CLI, make session entry and hygiene invoke its read-only audit/next seams, reduce `HANDOFF.md` to a current pointer backed by `BACKLOG.md`, and extend artifact tests around the existing build exclusions and exact release validator.

**Tech Stack:** Markdown skill/instruction surfaces, Python 3.12-compatible standard library, `argparse`, `subprocess`, `tomllib`, `unittest`, uv, Git, MkDocs, wheel/sdist validation, and installed-wheel smoke tests.

**Spec:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`.

## Global Constraints

- `ROADMAP.md` remains the node identity, kind, order, and dependency authority; `BACKLOG.md` remains the only mutable delivery-state authority.
- Implement only child `T1.6`; T2.1/T2.2/T3.1, B1.1, canonical FDAU runtime work, external-client work, and q4xpcc changes remain out of scope.
- Do not change the behavior, grammar, JSON schema, or mutation safety of `.codex/skills/backlog-status/scripts`.
- Use Python's standard-library `unittest` framework exclusively; never add, invoke, or suggest pytest.
- Keep every runtime module standard-library-only and do not edit `xplane_fdau` product behavior.
- The project-local skill is an adapter to repository-owned commands. It does not duplicate a canonical `gzs-*` or Superpowers workflow.
- Every controlled state change remains dry-run-first, requires explicit `--apply`, and edits only `BACKLOG.md`; no skill or hygiene command stages, commits, fetches, pulls, pushes, tags, publishes, or releases.
- `HANDOFF.md` is a concise, current pointer. It may repeat immediate guardrails and external readiness boundaries, but it must not become a second delivery ledger or preserve stale branch state.
- Hygiene remains deterministic and offline by default. The strict backlog audit runs before the expensive quality and pre-commit gates and stops the sequence on failure.
- Wheel and sdist contents remain exact. `.codex`, `.agents`, `.superpowers`, `docs/superpowers`, `ROADMAP.md`, `BACKLOG.md`, `HANDOFF.md`, governance evidence, and caches must not ship.
- Version `0.1.0` remains unreleased. No push, tag, PyPI publication, GitHub release, or q4xpcc mutation is authorized.

## File Responsibilities

| File | Responsibility |
| --- | --- |
| `.codex/skills/backlog-status/SKILL.md` (new) | Project-local discovery triggers, read-only commands, and dry-run/apply mutation safeguards |
| `AGENTS.md` | Mandatory session-entry audit/next sequence and pointer to the local skill |
| `HANDOFF.md` | Concise current checkpoint, external readiness boundaries, and exact authority/command pointers |
| `.codex/skills/hygiene/scripts/hygiene.py` | Deterministic local command order including strict backlog audit |
| `.codex/skills/hygiene/SKILL.md` | User-facing description of the strengthened offline hygiene sequence |
| `tests/test_project_skills.py` | Skill discovery/content, session-entry, hygiene ordering/fail-fast, and build-exclusion contracts |
| `tests/test_backlog_governance.py` | Handoff authority and q4xpcc readiness assertions without stale delivery state |
| `tests/test_release_tool.py` | Explicit rejection of repository-governance files from wheel and sdist candidates |
| `tests/test_backlog_status_cli.py` | Current-repository lifecycle/recommendation assertions during final closeout |
| `BACKLOG.md` | T1.6 plan link, selected lifecycle, review, five gate links, and final cleared selection |
| `.superpowers/sdd/2026-09-07-t1-6-skill-session-hygiene-artifact-closure/*.md` | Completion, independent review, and five committed gate records |

### Task 1: Discoverable backlog-status skill adapter

**Files:** Create `.codex/skills/backlog-status/SKILL.md`; modify `tests/test_project_skills.py`.

**Interfaces:** Produce a discoverable `backlog-status` skill that routes read-only requests to `status`, `audit`, and `next`, and routes controlled state requests to the existing dry-run-first mutation CLI without adding another state engine.

- [ ] **Step 1: Write the failing discovery test and run baseline skill evaluations**

  Set the discovered skill set to all project skill directories:

  ```python
  DISCOVERABLE_PROJECT_SKILLS = PROJECT_SKILL_DIRECTORIES
  ```

  Before creating `SKILL.md`, the controller dispatches three fresh-context
  reference-skill evaluations without the skill: status/resume routing,
  roadmap/backlog/spec/plan adherence routing, and a pressured controlled-state
  request. Evaluators must not mutate the checkout. Record their command choices
  and omissions verbatim in the plan workspace as the RED baseline. The intended
  behaviors are audit-before-next for status/resume, strict `audit` for adherence,
  and dry-run followed by the printed `--target-sha256` plus explicit `--apply`
  for controlled mutations.

- [ ] **Step 2: Run RED**

  ```powershell
  uv run python -m unittest tests.test_project_skills.ProjectSkillTests.test_project_skills_are_scoped_to_unreleased_xplane_fdau -v
  ```

  Expected: FAIL because `.codex/skills/backlog-status/SKILL.md` does not exist
  and `backlog-status` is no longer excluded from discovery assertions. The
  fresh-context evaluations provide the behavioral RED evidence for the new
  reference skill; do not replace them with assertions that grep prose.

- [ ] **Step 3: Create the thin skill adapter**

  Create this exact frontmatter and routing structure:

  ````markdown
  ---
  name: backlog-status
  description: Use when reporting or resuming xplane-fdau delivery status, checking roadmap/backlog/spec/plan adherence, asking for the next local action, or performing controlled child selection, lifecycle, suspension, or gate-evidence changes.
  ---

  # xplane-fdau Backlog Status Adapter

  `ROADMAP.md` owns node identity, kind, order, and dependencies. `BACKLOG.md`
  is the only mutable delivery-state authority.

  For status or resume work, run the strict audit and deterministic next action:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  ```

  Use these additional read-only reports when needed:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  ```

  Controlled state commands are `select`, `transition`, `record-gate`,
  `reopen-gate`, `suspend`, and `resume`. Run the complete command without
  `--apply` first. Inspect its dry-run diff and audit. Apply only by repeating
  the same command with the printed `--target-sha256` value and explicit
  `--apply`.

  The adapter and script may edit only `BACKLOG.md`. They do not change a plan,
  specification, evidence file, Git state, remote, tag, package, publication,
  release, or another repository. Use `unittest` only and preserve the
  standard-library-only runtime boundary.
  ````

- [ ] **Step 4: Run GREEN and repeat the skill evaluations**

  ```powershell
  uv run python -m unittest tests.test_project_skills -v
  uv run ruff check tests/test_project_skills.py
  uv run ruff format --check tests/test_project_skills.py
  ```

  Then the controller repeats all three fresh-context evaluations with the new
  skill explicitly available. Each evaluator must choose the intended repository
  command sequence and preserve the no-mutation/no-release boundary. Record the
  responses beside the baseline evidence. Expected: automated checks pass, all
  five project skill directories are discoverable, and the evaluations show that
  the backlog skill is usable as a command adapter rather than another engine.

- [ ] **Step 5: Commit skill discovery**

  ```powershell
  git add .codex/skills/backlog-status/SKILL.md tests/test_project_skills.py
  git commit -m "feat: expose backlog status workflow"
  ```

### Task 2: Session entry and concise handoff authority

**Files:** Modify `AGENTS.md`, `HANDOFF.md`, `tests/test_project_skills.py`, and `tests/test_backlog_governance.py`.

**Interfaces:** Session entry runs the strict audit and deterministic next-action report after reading the required authorities. `HANDOFF.md` retains immediate constraints and q4xpcc boundaries but explicitly delegates all mutable delivery state to `BACKLOG.md`.

- [ ] **Step 1: Measure the current instruction surfaces**

  ```powershell
  Get-Item AGENTS.md,HANDOFF.md | Select-Object Name,Length
  Get-Content AGENTS.md,HANDOFF.md | Measure-Object -Line
  ```

  Confirm `AGENTS.md` and `HANDOFF.md` are authored sources with no generated
  instruction mirror. Record each file's byte and line count in the T1.6
  completion evidence. Inventory the retained hard guardrails: required
  authorities, `unittest`, standard-library-only runtime, external adapter
  boundary, explicit-only Git sync/session handoff, Superpowers order, release
  prohibition, q4xpcc readiness thresholds, and the local dependency path.

- [ ] **Step 2: Run a failing session-entry evaluation and preserve existing contracts**

  Before editing `AGENTS.md`, dispatch one fresh-context evaluator asked to resume
  repository work from the current checkout without naming the backlog commands.
  It must remain read-only and report the actions it would take. Record the RED
  response in the plan workspace; the expected gap is failure to run strict
  `audit` followed by deterministic `next` and stop on an audit finding.

  Do not add tests that merely grep instructions or human prose. Preserve the
  existing backlog-governance and documentation contract tests, including D1.1 ->
  D1.2 -> D1.3 -> I1.0 ordering and the migration/release-boundary strings. Update
  the active-plan governance assertion for the committed T1.6 plan and its current
  lifecycle state.

- [ ] **Step 3: Confirm RED evidence**

  Expected: the evaluator omits at least one required session-entry behavior and
  the measured handoff still reports the removed T1.5 branch as unmerged. If the
  evaluator already complies, strengthen the scenario around resumption pressure;
  do not manufacture a source-text failure.

- [ ] **Step 4: Add the mandatory session-entry commands**

  After the authority-reading bullets in `AGENTS.md`, add:

  ````markdown
  - Run the repository backlog workflow after reading those authorities:

    ```powershell
    uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
    uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
    ```

    Stop on an audit finding. Otherwise follow the reported lifecycle action
    for the selected or first dependency-ready local child. Read
    `.codex/skills/backlog-status/SKILL.md` for status, resume, adherence,
    next-action, or controlled state requests.
  ````

  Preserve every existing testing, runtime, portable-workflow, Superpowers, worktree, integration, Git-sync, and release guardrail.

- [ ] **Step 5: Replace stale handoff history with a concise current pointer**

  Rewrite `HANDOFF.md` to fewer than 120 lines with these sections and meanings:

  ````markdown
  # Project Handoff

  ## Session entry

  `ROADMAP.md` is the capability-order authority and `BACKLOG.md` is the only
  mutable delivery-state authority. Do not infer current state from this file;
  after reading the required architecture and governance documents, run:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  ```

  Stop on a finding. Otherwise follow the exact reported local-child lifecycle
  action.

  ## Architecture and release boundary

  The parent architecture is
  `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`; the approved
  repository amendment is
  `docs/architecture/xplane_fdau_core_scope_amendment.md`. `xplane-fdau` is the
  X-Plane-specific, transport-free, standard-library-only core. XPLM,
  XPPython3, `xpwebapi`, network clients, and simulator I/O remain external.
  Use `unittest`, never pytest.

  Identity and native-FDR-kernel migration: implemented and verified, but
  unreleased. Version `0.1.0`, tags, package publication, and GitHub releases
  remain separately gated. Ordinary Git sync requires an explicit request and
  does not grant release authority.

  ## Current delivery path

  T1.5 is verified and integrated. T1.6 closes skill discovery, session entry,
  hygiene audit integration, and artifact exclusion. The governed path remains
  `T1.6 -> T2.1 -> T2.2/T3.1 -> B1.1 -> C1.1` and then through `C4.4`.

  ## q4xpcc readiness

  `D1.1` canonical C1-C4 design approval is verified. `D1.2` acquisition,
  recording, projection, and pinning contract design is verified. `D1.3`
  reviewed q4xpcc Phase 24A consumer handoff is verified. `I1.0` is eligible as
  the next reportable external action for planning reconciliation.

  `I1.1` permits delivered contract-model, schema, fixture, and runtime adoption
  only after `C4.4`. `I1.2` permits live XPLM acquisition adoption only after
  `A1.9`. Do not modify q4xpcc from this repository.

  `I1.0` now permits Phase 24A specification and plan reconciliation because
  `D1.3` is verified.

  ## Evidence pointers

  - T1 design:
    `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
  - T1.6 plan:
    `docs/superpowers/plans/2026-09-07-t1-6-skill-session-hygiene-artifact-closure.md`
  - q4xpcc brief: `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`
  ````

  Keep the exact migration-boundary strings required by `tests/test_documentation.py`. Do not copy the child inventory, gate dashboard, historical commit narrative, or active branch status into the handoff.

- [ ] **Step 6: Run GREEN, repeat the evaluator, and measure context**

  ```powershell
  uv run python -m unittest tests.test_project_skills tests.test_backlog_governance tests.test_documentation -v
  uv run mkdocs build --strict
  Get-Item AGENTS.md,HANDOFF.md | Select-Object Name,Length
  Get-Content AGENTS.md,HANDOFF.md | Measure-Object -Line
  git diff --check
  ```

  Repeat the same fresh-context session-entry evaluation with the amended
  instructions and record the response. Expected: it chooses strict audit before
  next, stops on findings, and otherwise follows the reported lifecycle action;
  all commands pass, every binding rule remains reachable, `HANDOFF.md` is below
  120 lines, and its byte/line reduction is recorded.

- [ ] **Step 7: Commit session-entry closure**

  ```powershell
  git add AGENTS.md HANDOFF.md tests/test_project_skills.py tests/test_backlog_governance.py
  git commit -m "docs: route session entry through backlog status"
  ```

### Task 3: Strict backlog audit in offline hygiene

**Files:** Modify `.codex/skills/hygiene/scripts/hygiene.py`, `.codex/skills/hygiene/SKILL.md`, and `tests/test_project_skills.py`.

**Interfaces:** `run_local_hygiene(runner: Runner = subprocess.run) -> int` runs the existing fail-fast sequence with the strict backlog audit inserted after the offline lock check and before full quality.

- [ ] **Step 1: Write failing command-order and fail-fast tests**

  Replace the containment assertion with this exact order:

  ```python
  expected = (
      ("git", "status", "--short", "--branch"),
      ("uv", "lock", "--check", "--offline"),
      ("uv", "run", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit"),
      ("uv", "run", "python", "tools/quality.py", "check"),
      ("uv", "run", "python", "tools/quality.py", "pre-commit"),
  )
  self.assertEqual(expected, module.LOCAL_COMMANDS)
  ```

  Add a fake runner that returns `CompletedProcess(command, 7)` for the audit
  and zero otherwise. Assert `run_local_hygiene(runner)` returns `7` and the
  fake sees only the first three commands. These runner assertions are the
  behavior contract; do not add a source-text assertion for
  `.codex/skills/hygiene/SKILL.md`, which remains a concise reference to the
  tested script.

- [ ] **Step 2: Run RED**

  ```powershell
  uv run python -m unittest tests.test_project_skills.ProjectSkillTests.test_hygiene_script_runs_strict_backlog_audit_before_quality tests.test_project_skills.ProjectSkillTests.test_hygiene_stops_when_backlog_audit_fails -v
  ```

  Expected: FAIL because the audit command is absent from `LOCAL_COMMANDS`.

- [ ] **Step 3: Insert the existing strict audit command**

  Change only `LOCAL_COMMANDS`:

  ```python
  LOCAL_COMMANDS = (
      ("git", "status", "--short", "--branch"),
      ("uv", "lock", "--check", "--offline"),
      ("uv", "run", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit"),
      ("uv", "run", "python", "tools/quality.py", "check"),
      ("uv", "run", "python", "tools/quality.py", "pre-commit"),
  )
  ```

  Do not catch or translate the audit exit status. Existing fail-fast behavior returns it unchanged.

- [ ] **Step 4: Update the hygiene adapter description**

  State that the offline sequence checks Git status, the lock offline, strict backlog audit, complete quality, and pre-commit in that order. State that a failed audit stops before quality and that hygiene never mutates backlog state.

- [ ] **Step 5: Run GREEN and focused quality**

  ```powershell
  uv run python -m unittest tests.test_project_skills -v
  uv run ruff check .codex/skills/hygiene/scripts/hygiene.py tests/test_project_skills.py
  uv run ruff format --check .codex/skills/hygiene/scripts/hygiene.py tests/test_project_skills.py
  uv run ty check
  ```

  Expected: all pass and no runtime package file changes.

- [ ] **Step 6: Commit hygiene integration**

  ```powershell
  git add .codex/skills/hygiene/scripts/hygiene.py .codex/skills/hygiene/SKILL.md tests/test_project_skills.py
  git commit -m "build: audit backlog during repository hygiene"
  ```

### Task 4: Explicit repository-governance artifact exclusion

**Files:** Modify `tests/test_project_skills.py` and `tests/test_release_tool.py`.

**Interfaces:** Preserve the existing `uv_build` `source-exclude` configuration and exact `tools.release.check_dist()` validator while adding direct regression coverage for every repository-governance family introduced by T1.

- [ ] **Step 1: Write build-policy and artifact-rejection regression tests**

  Add `test_repository_governance_is_excluded_from_source_builds`:

  ```python
  project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
  excluded = set(project["tool"]["uv"]["build-backend"]["source-exclude"])
  self.assertTrue(
      {".codex/**", ".git/**", ".superpowers/**", "docs/superpowers/**"}.issubset(excluded)
  )
  ```

  Add `test_check_dist_rejects_every_repository_governance_family` with these wheel candidates:

  ```python
  wheel_cases = {
      "skill": {".codex/skills/backlog-status/SKILL.md": b"governance\n"},
      "portable-skill": {".agents/skills/gzs-router/SKILL.md": b"governance\n"},
      "evidence": {".superpowers/sdd/t1-6/gate-1.md": b"governance\n"},
      "backlog": {"BACKLOG.md": b"governance\n"},
      "roadmap": {"ROADMAP.md": b"governance\n"},
      "handoff": {"HANDOFF.md": b"governance\n"},
  }
  ```

  and these sdist candidates under `xplane_fdau-0.1.0/`:

  ```python
  sdist_cases = {
      "skill": {f"{root}/.codex/skills/backlog-status/SKILL.md": b"governance\n"},
      "portable-skill": {f"{root}/.agents/skills/gzs-router/SKILL.md": b"governance\n"},
      "evidence": {f"{root}/.superpowers/sdd/t1-6/gate-1.md": b"governance\n"},
      "plan": {f"{root}/docs/superpowers/plans/t1-6.md": b"governance\n"},
      "backlog": {f"{root}/BACKLOG.md": b"governance\n"},
      "roadmap": {f"{root}/ROADMAP.md": b"governance\n"},
      "handoff": {f"{root}/HANDOFF.md": b"governance\n"},
  }
  ```

  For every candidate, rebuild the synthetic archive and assert
  `release.check_dist()` raises `ReleaseError`. These are characterization tests
  for an already-shipped exact validator, not a production behavior change; they
  may pass on their first execution. Verify their value with the mutation check:
  removing any corresponding rejection from the validator would fail at least one
  literal case.

- [ ] **Step 2: Run the characterization tests**

  ```powershell
  uv run python -m unittest tests.test_project_skills.ProjectSkillTests.test_repository_governance_is_excluded_from_source_builds tests.test_release_tool.ReleaseToolTests.test_check_dist_rejects_every_repository_governance_family -v
  ```

  Expected after adding the tests: PASS against the current exact validator. Do
  not fabricate a failing production state merely to obtain RED evidence for a
  test-only strengthening task.

- [ ] **Step 3: Add the exact regression coverage**

  Import `tomllib` in `tests/test_project_skills.py`, add the build-policy assertion, and add the table-driven wheel/sdist cases to `tests/test_release_tool.py`. Do not widen the allowed artifact set or change product package contents.

- [ ] **Step 4: Run GREEN against synthetic and fresh real artifacts**

  ```powershell
  uv run python -m unittest tests.test_project_skills tests.test_release_tool tests.test_installed_smoke -v
  $artifactDir = Join-Path ([System.IO.Path]::GetTempPath()) ("xplane-fdau-t1-6-" + [guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Path $artifactDir | Out-Null
  uv build --no-sources --out-dir $artifactDir
  uv tool run twine check --strict "$artifactDir\xplane_fdau-0.1.0-py3-none-any.whl" "$artifactDir\xplane_fdau-0.1.0.tar.gz"
  uv run python tools/release.py check-dist $artifactDir
  ```

  Expected: all pass; the validator reports the exact wheel/sdist pair and hashes. Preserve `$artifactDir` for the final installed smoke matrix; do not publish it.

- [ ] **Step 5: Commit artifact-exclusion evidence in code**

  ```powershell
  git add tests/test_project_skills.py tests/test_release_tool.py
  git commit -m "test: prove governance tooling stays out of artifacts"
  ```

### Task 5: T1.6 lifecycle, independent review, evidence, and closeout

Tasks 1-4 are implemented. Completion metadata records the Step 2
implementation handoff; Steps 3-8 remain the subsequent independent-review,
acceptance-evidence, installed-artifact, and verified-state closeout work.

**Files:** Modify this plan, `BACKLOG.md`, `HANDOFF.md`, `tests/test_backlog_governance.py`, and `tests/test_backlog_status_cli.py`; create `.superpowers/sdd/2026-09-07-t1-6-skill-session-hygiene-artifact-closure/completion.md`, `review.md`, and `gate-1.md` through `gate-5.md`.

**Interfaces:** The committed final backlog has T1.6 `verified` at 5/5, no selected child, and deterministic recommendation `T2.1`/`write_plan`. Runtime, external boundaries, G1, release, tag, and publication state remain unchanged.

- [x] **Step 1: Establish coherent planned and in-progress states with the guarded CLI**

  With this approved plan present, run:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py transition T1.6 planned --expect specified --plan docs/superpowers/plans/2026-09-07-t1-6-skill-session-hygiene-artifact-closure.md
  ```

  Inspect the diff and candidate audit, then repeat the exact command with its printed `--target-sha256` and `--apply`. Next dry-run/apply `select T1.6 --expect-current none`. Change this plan's status to `in_progress`; then dry-run/apply `transition T1.6 in_progress --expect planned`. Run `audit`, JSON `status`, and `next` after every applied change. Commit the plan and coherent in-progress state before implementation commits.

- [x] **Step 2: Complete implementation and record completion evidence**

  After Tasks 1-4 pass, run:

  ```powershell
  uv run python -m unittest tests.test_project_skills tests.test_backlog_governance tests.test_backlog_status_cli tests.test_release_tool tests.test_installed_smoke tests.test_documentation -v
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python tools/quality.py check
  uv run mkdocs build --strict
  git diff --check
  ```

  Create `completion.md` with child-level evidence metadata, exact commands/counts/coverage, instruction measurements, artifact paths/hashes, implemented commit range, and confirmation that no runtime, remote, release, or q4xpcc surface changed. Mark this plan `completed` with that exact completion path. Stage both files, dry-run/apply `transition T1.6 implemented --expect in_progress`, audit, and commit the completion transition.

- [ ] **Step 3: Request independent review and resolve all findings**

  Use `superpowers:requesting-code-review` over the merge-base-to-implementation revision. Review against the T1 design, this plan, the authority model, dry-run/apply boundary, context-diet invariant inventory, hygiene fail-fast behavior, artifact exclusion, runtime boundary, and release prohibition. Record Critical, Important, and Minor findings in `review.md`.

  Apply accepted corrections with `superpowers:receiving-code-review`, `superpowers:systematic-debugging` for failures, and a failing `unittest` first. Rerun affected verification and request rereview until no unresolved finding remains. Stage the accepted review, dry-run/apply `transition T1.6 reviewed --expect implemented --review .superpowers/sdd/2026-09-07-t1-6-skill-session-hygiene-artifact-closure/review.md`, audit, and commit review plus state together.

- [ ] **Step 4: Create five exact gate records**

  Use the approved evidence metadata contract with these subjects and proof:

  | Gate | Subject | Required proof |
  | --- | --- | --- |
  | 1 | Project-local backlog skill triggers | Discoverable frontmatter, status/resume/adherence/next/controlled-state routing, and exact dry-run/apply safeguards |
  | 2 | Session entry and concise handoff authority | Mandatory audit-before-next sequence, stale T1.5 removal, context measurements, and preserved binding invariants |
  | 3 | Strict backlog audit in hygiene | Exact offline command order, audit fail-fast test, complete hygiene execution, and no mutation |
  | 4 | Governance artifact exclusion | Build configuration, malicious synthetic members, fresh wheel/sdist validation, and installed smoke outside the checkout |
  | 5 | Standard-library tests and independent review | Full quality/documentation/hygiene results, accepted review, unchanged runtime/release boundaries, and no external repository action |

  Each evidence file names exact tests, commands, revision, artifact hashes, and any platform dimension not directly observed. Stage all five before linking them.

- [ ] **Step 5: Record gate evidence with the guarded CLI**

  For ordinals 1 through 5, run `record-gate T1.6 <ordinal> --expect-open --evidence <gate-path>` without `--apply`, inspect the diff/audit, then repeat with its printed `--target-sha256` and `--apply`. Confirm the inventory row becomes `5/5` and all evidence is eligible from the Git index. Audit and commit evidence plus corresponding backlog changes together.

- [ ] **Step 6: Run final artifact and installed-version verification**

  Build a new immutable pair in a new temporary directory and run `twine check` plus `tools/release.py check-dist`. For each version in `3.12`, `3.13`, and `3.14`, create a uniquely named temporary venv outside the checkout, install the exact wheel, change location outside the checkout, and run that interpreter on `tools/installed_smoke.py 0.1.0`. Record artifact SHA-256 values and all three results. Do not reuse a candidate artifact from Task 4 and do not publish.

- [ ] **Step 7: Verify from HEAD, close selection, and update the handoff**

  With completion, review, and all five gate records committed in `HEAD`, dry-run/apply `transition T1.6 verified --expect reviewed`, then dry-run/apply `select none --expect-current T1.6`. Update the current-repository CLI assertion to expect `T2.1` with `write_plan`. Update `HANDOFF.md` so the current path says T1.6 is verified and `T2.1` is the next dependency-ready child, while keeping `BACKLOG.md` authoritative and all q4xpcc/release boundaries exact.

- [ ] **Step 8: Run the final clean-state gate and commit closeout**

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  uv run python tools/quality.py check
  uv run mkdocs build --strict
  uv run python .codex/skills/hygiene/scripts/hygiene.py
  git diff --check
  git status --short --branch
  ```

  Expected: no findings; T1.6 verified at 5/5 and unselected; recommendation `write_plan` for T2.1; all 3.12-3.14 installed smokes pass; the worktree is clean after the closeout commit; version `0.1.0` remains unreleased; and no push, tag, publication, GitHub release, or q4xpcc change occurred.

  Then use `superpowers:verification-before-completion` and `superpowers:finishing-a-development-branch`. Local integration, merged-result verification, worktree removal, and temporary-branch deletion occur only after the user selects the finishing action.

## Self-Review

- **Spec coverage:** Task 1 covers project-local skill triggers; Task 2 covers session entry and a nonauthoritative concise handoff; Task 3 makes hygiene run the strict audit; Task 4 proves built/installed artifact exclusion; Task 5 supplies full tests, independent review, five committed gates, and final lifecycle closure.
- **Scope:** Only repository workflow adapters, instructions, tests, T1.6 governance state, and evidence change. Backlog engine behavior, runtime code, dependencies, T2/T3/B1/C/A/R/P/S/F1 work, external repositories, and release surfaces remain excluded.
- **Authority:** `ROADMAP.md` and `BACKLOG.md` retain their exact ownership. The skill, AGENTS, HANDOFF, and hygiene surfaces point to the existing engine and do not cache mutable delivery state.
- **Context diet:** Immediate actions and hard guardrails stay in AGENTS/HANDOFF; historical narrative and duplicated dashboards leave the handoff because durable specs, plans, evidence, Git, and backlog already own them.
- **TDD:** Every implementation task starts with a focused failing `unittest`, adds only the minimum adapter/documentation change, and returns to green before commit.
- **Artifact safety:** Existing exact artifact validation remains authoritative; new tests prove every T1 governance family is rejected without widening production artifacts.
- **Placeholder scan:** The plan contains no TBD, TODO, deferred code step, ambiguous error-handling instruction, or undefined production interface.
