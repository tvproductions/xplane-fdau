# T1.4 Deterministic Next-Action Selection Implementation Plan

- **Governance:** active
- **Status:** in_progress
- **Date:** 2026-09-06
- **Roadmap child:** `T1.4`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- **Approval:** 2026-09-06 — Jeff / tvproductions
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repository-local backlog tool deterministically recommend the exact next Superpowers lifecycle action for a selected child or the first dependency-ready unfinished local child.

**Architecture:** Add one pure recommendation-policy module over the already-audited, dependency-annotated repository snapshot. Compose that policy into the existing schema-version-1 report and expose the read-only `next` CLI alongside `status` and `audit`; no selector mutates Markdown or invokes another workflow.

**Tech Stack:** Python 3.12-compatible standard library, frozen dataclasses, `argparse`, `unittest`, uv, Ruff, ty, Git, and MkDocs.

**Spec:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`.

## Global Constraints

- `ROADMAP.md` remains the exact node-kind and roadmap-order authority; `BACKLOG.md` remains the only mutable delivery-state authority.
- Implement only child `T1.4`; T1.5 mutations and T1.6 skill/session/hygiene integration remain out of scope.
- Use Python's standard-library `unittest` framework exclusively; never add or invoke pytest.
- Keep all production implementation under `.codex/skills/backlog-status/scripts`; do not edit `xplane_fdau`, package dependencies, canonical FDAU contracts, q4xpcc, or any external client.
- Preserve schema version 1, its exact keys and key order, UTF-8 output, two-space JSON indentation, null optionals, and one final LF.
- `next`, `status`, and `audit` are read-only: no Markdown edit, Git write, workflow invocation, network access, state transition, release, tag, publication, or push.
- Any audit error blocks actionable work. A selected `blocked` or `deferred` child returns `wait` with its recorded reason and is never replaced silently.
- Only a roadmap `local_child` may be recommended. Milestones, epics, release gates, and external boundaries remain report-only.
- Version `0.1.0` remains unreleased and the runtime remains standard-library-only.

## File Responsibilities

| File | Responsibility |
| --- | --- |
| `.codex/skills/backlog-status/scripts/backlog/next_action.py` (new) | Pure lifecycle-to-action policy, roadmap-order choice, blocking behavior, reasons, and suggested workflow commands |
| `.codex/skills/backlog-status/scripts/backlog/report.py` | Compose one recommendation into every status report without changing schema shape |
| `.codex/skills/backlog-status/scripts/backlog_status.py` | Parse and render the read-only `next` command |
| `tests/test_backlog_status_next_action.py` (new) | Exhaustive selector policy, lifecycle, suspension, finding, and node-kind tests |
| `tests/test_backlog_status_report.py` | Human/JSON recommendation rendering and exact schema compatibility |
| `tests/test_backlog_status_cli.py` | CLI usage, read-only behavior, and real-repository recommendation integration |
| `tests/test_backlog_governance.py` | Current selection grammar and exact active-plan inventory during lifecycle migration |
| `BACKLOG.md` | Selected child, approved plan link, lifecycle state, gate evidence, review link, and final selection |
| `HANDOFF.md` | Concise T1.4 closure and next dependency-ready child pointer |
| `.superpowers/sdd/2026-09-06-t1-4-deterministic-next-action-selection/*.md` | Completion, independent review, and four committed acceptance-gate records |

### Task 1: Pure recommendation policy

**Files:** Create `.codex/skills/backlog-status/scripts/backlog/next_action.py` and `tests/test_backlog_status_next_action.py`.

**Interfaces:** Produce `recommend_next(snapshot: RepositorySnapshot, findings: tuple[Finding, ...]) -> Recommendation`. The caller supplies `with_dependency_readiness(...)` output. The function reads only frozen values and returns one frozen `Recommendation`; it performs no I/O.

- [x] **Step 1: Write the failing lifecycle matrix tests**

  Parse the valid fixture and use `dataclasses.replace` to select `T1.2`. For each effective status assert this exact action mapping:

  ```python
  expected = {
      "queued": "refine_spec",
      "designing": "request_spec_review",
      "specified": "write_plan",
      "planned": "execute_plan",
      "in_progress": "execute_plan",
      "implemented": "request_review",
      "reviewed": "verify",
      "verified": "wait",
      "released": "wait",
  }
  ```

  Assert every non-wait result names `T1.2`, gives a nonempty reason, and supplies a command that names the governing workflow (`superpowers:brainstorming`, `superpowers:requesting-code-review`, `superpowers:writing-plans`, `superpowers:subagent-driven-development`/`superpowers:executing-plans`, or `gzs-quality-gate`). Assert terminal `wait` results have no command.

- [x] **Step 2: Write failing order, kind, and blocking tests**

  Cover all of these cases:

  ```python
  recommendation = recommend_next(with_dependency_readiness(snapshot), ())
  self.assertEqual(("write_plan", "T1.2"), (recommendation.action, recommendation.child))
  ```

  - verified/released earlier children are skipped;
  - the first dependency-ready unfinished child is chosen by `roadmap.local_children` order even if backlog tuple order is replaced;
  - a dependency-unready child is skipped;
  - milestone `M0`, epic `T1`, release gate `G1`, and external boundary `I1.1` can never occupy `Recommendation.child`;
  - no eligible unfinished local child returns `wait`, `child=None`, and `command=None`;
  - any error finding returns `wait` before selection with the audit command;
  - warning-only findings do not block;
  - selected `blocked` and `deferred` children return `wait` with the exact recorded reason and no fallback child.

- [x] **Step 3: Run RED**

  Run:

  ```powershell
  uv run python -m unittest tests.test_backlog_status_next_action -v
  ```

  Expected: FAIL because `backlog.next_action` does not exist.

- [x] **Step 4: Implement the minimal pure selector**

  Use an explicit status-to-action table and a single helper that turns a child into a recommendation. Evaluate in the specification's order: errors, selected suspension, selected child, then first dependency-ready unfinished roadmap local child. Look up backlog children by ID while iterating `snapshot.roadmap.local_children`; skip only terminal `verified`/`released` children during unselected discovery. Return `wait` when no unfinished dependency-ready local child exists.

  Suggested command strings are informational sentences and never shell execution. Use the exact repository entry point for the audit blocker:

  ```python
  "uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit"
  ```

- [x] **Step 5: Run GREEN and quality checks**

  Run:

  ```powershell
  uv run python -m unittest tests.test_backlog_status_next_action -v
  uv run ruff check .codex/skills/backlog-status/scripts/backlog/next_action.py tests/test_backlog_status_next_action.py
  uv run ty check
  ```

  Expected: all pass.

- [x] **Step 6: Commit the independently testable policy**

  ```powershell
  git add .codex/skills/backlog-status/scripts/backlog/next_action.py tests/test_backlog_status_next_action.py
  git commit -m "feat: select deterministic backlog next actions"
  ```

### Task 2: Report and `next` CLI composition

**Files:** Modify `.codex/skills/backlog-status/scripts/backlog/report.py`, `.codex/skills/backlog-status/scripts/backlog_status.py`, `tests/test_backlog_status_report.py`, and `tests/test_backlog_status_cli.py`.

**Interfaces:** `build_report(...)` continues returning the existing `StatusReport` schema version 1 but populates `recommendation` via `recommend_next`. CLI `next` accepts no options, renders the same complete human report as `status`/`audit`, and returns `0` only when the report has no audit error.

- [x] **Step 1: Write failing report tests**

  Replace the historical `Recommendation: unavailable until T1.4` assertion with exact human fields for the fixture's `T1.2`/`write_plan` recommendation. Assert `report_dict` and `render_json` retain the exact top-level and recommendation key order while changing the valid fixture's recommendation from null to:

  ```python
  {
      "action": "write_plan",
      "child": "T1.2",
      "reason": "T1.2 is specified and requires an approved single-child implementation plan.",
      "command": "Use superpowers:writing-plans to create the single-child implementation plan.",
  }
  ```

  Retain the existing synthetic-null-optionals serialization test by constructing its report with `dataclasses.replace`.

- [x] **Step 2: Write failing CLI tests**

  Add `next` to valid executable/mtime-read-only command loops. Assert `next` equals human `status` for the same committed fixture, returns `0`, writes nothing to stderr, and contains `action=write_plan child=T1.2`. Remove `next` from invalid-future-command coverage, and assert `next --json` and `next --apply` return usage status `2`.

  For an audit-error fixture, assert `next` returns `1` and renders `action=wait` with the audit command. For the real repository integration at implementation time, assert the selected T1.4 lifecycle yields `execute_plan`; after Task 3 closure, update that assertion to the first dependency-ready unfinished child `T1.5` with `write_plan`.

- [x] **Step 3: Run RED**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_report tests.test_backlog_status_cli -v
  ```

  Expected: failures because reports still force `recommendation=None` and `next` is not parsed.

- [x] **Step 4: Compose selector and CLI**

  Import `recommend_next` in `report.py` and set `recommendation=recommend_next(snapshot, sorted_findings)` while preserving `valid` and finding order. Remove the temporary unavailable wording from human rendering. Add `commands.add_parser("next", help="recommend the next Superpowers lifecycle action")`; render JSON only for `status --json`, otherwise preserve the human report.

- [x] **Step 5: Run GREEN and focused regression**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_next_action tests.test_backlog_status_report tests.test_backlog_status_cli -v
  uv run ruff check .codex/skills/backlog-status/scripts tests/test_backlog_status_next_action.py tests/test_backlog_status_report.py tests/test_backlog_status_cli.py
  uv run ty check
  ```

  Expected: all pass and schema version remains 1.

- [x] **Step 6: Commit report/CLI composition**

  ```powershell
  git add .codex/skills/backlog-status/scripts/backlog/report.py .codex/skills/backlog-status/scripts/backlog_status.py tests/test_backlog_status_report.py tests/test_backlog_status_cli.py
  git commit -m "feat: expose backlog next-action reporting"
  ```

### Task 3: T1.4 lifecycle, independent review, and acceptance evidence

**Files:** Modify `BACKLOG.md`, `HANDOFF.md`, this plan, `tests/test_backlog_governance.py`, and the final real-repository assertions in `tests/test_backlog_status_cli.py`; create `.superpowers/sdd/2026-09-06-t1-4-deterministic-next-action-selection/completion.md`, `review.md`, and `gate-1.md` through `gate-4.md`.

**Interfaces:** The committed final `next` result is `T1.5`/`write_plan`, because T1.4 becomes verified and unselected. No C, A, R, P, release-gate, or external-boundary state changes.

- [ ] **Step 1: Register and execute the approved plan lifecycle**

  Before implementation commits, update only T1.4's inventory row and active selection: link this plan, move `specified -> planned -> in_progress` as work starts, and set this plan status to `in_progress`. Run `audit` after each lifecycle edit. Do not use or implement T1.5 mutation commands.

- [ ] **Step 2: Run full implementation verification**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_next_action tests.test_backlog_status_report tests.test_backlog_status_cli -v
  uv run python -m unittest discover -v
  uv run python tools/quality.py check
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  git diff --check
  ```

  Record exact command results, test counts, coverage, branch, and revision in `completion.md`; mark the plan `completed` with that completion-evidence path and T1.4 `implemented`.

- [ ] **Step 3: Request independent review and address every finding**

  Use `superpowers:requesting-code-review` against the exact implementation revision and review the complete T1.4 diff against the governing design and this plan. Record Critical, Important, and Minor findings in `review.md`. Fix all load-bearing findings test-first, rerun affected verification, and request rereview until no unresolved finding remains; then link accepted review and move T1.4 to `reviewed`.

- [ ] **Step 4: Create four exact gate records**

  Create evidence using the approved metadata contract:

  ```markdown
  # Verification Evidence

  - **Child:** `T1.4`
  - **Gate:** `1`
  - **Kind:** verification
  - **Result:** passed
  - **Date:** 2026-09-06
  - **Subject:** Selected-child lifecycle recommendation
  ```

  Gate 1 proves every selected lifecycle state and selected suspension. Gate 2 proves first dependency-ready unfinished local-child selection in roadmap order. Gate 3 proves audit errors and suspension block substitution. Gate 4 proves only local children can be recommended and `next` is read-only. Each record cites exact tests/commands and the reviewed revision.

- [ ] **Step 5: Commit evidence with the corresponding backlog gates**

  In one commit, link `gate-1.md` through `gate-4.md`, check all four T1.4 boxes, set its gate count to `4/4`, preserve T1.4 as `reviewed`, and stage every evidence file. Run audit against the staged candidate before committing. After commit, rerun audit so evidence is proven in `HEAD`, then set T1.4 to `verified`, clear the active selection, and update the final real-repository CLI assertion to exact `T1.5`/`write_plan`.

- [ ] **Step 6: Update handoff without overstating consumer readiness**

  Record the exact T1.4 reviewed/verified revisions, commands, test count, coverage, and next recommendation. State explicitly that C1.1-C4.4 remain unimplemented, I1.1 is not eligible, and A1.9/I1.2 remain unready; the dependency path continues through T1.5, T1.6, T2.1, T2.2/T3.1, and B1.1 before C1.1.

- [ ] **Step 7: Run final clean-state verification and commit closeout**

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  uv run python tools/quality.py check
  uv run mkdocs build --strict
  git diff --check
  git status --short --branch
  ```

  Expected: no findings; T1.4 verified at 4/4 and unselected; recommendation `write_plan` for T1.5; 0.1.0 remains unreleased; no push, tag, publication, or q4xpcc modification.

## Self-Review

- **Spec coverage:** Task 1 covers all four T1.4 acceptance criteria and the exact seven-action vocabulary; Task 2 delivers the `next` command and schema-compatible report composition; Task 3 covers review, committed evidence, final backlog/handoff state, and full verification.
- **Scope:** No task edits runtime code, canonical contract children, external repositories, mutation commands, skill/session integration, dependencies, or release machinery.
- **Type consistency:** `recommend_next(RepositorySnapshot, tuple[Finding, ...]) -> Recommendation` is the sole new production interface and matches the existing frozen model types.
- **Placeholder scan:** The plan contains no deferred implementation placeholder; later-child boundaries are explicit exclusions.
