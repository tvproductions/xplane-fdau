# q4xpcc Contract-Handoff Readiness Authority Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** Approved q4xpcc contract-handoff readiness authority registration completed and independently reviewed on the temporary design branch; preserved as the cross-cutting execution record and not a D1 child implementation plan.

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Register the approved D1 contract-handoff readiness branch so q4xpcc planning can be unblocked by reviewed design contracts before full FDAU implementation, without weakening later implementation, adoption, integration, or release gates.

**Architecture:** Keep `ROADMAP.md` authoritative for D1 identity, order, dependencies, and the statusless `I1.0` boundary; keep `BACKLOG.md` authoritative for the three initially `specified` children, zero satisfied gates, and the unchanged `T1.2` active selection. Protect those decisions with exact Markdown governance tests, reflect the prioritized sequence in `HANDOFF.md`, and preserve this plan as a historical cross-cutting execution record rather than misrepresenting it as a D1.1 implementation plan.

**Tech Stack:** Markdown, Python 3.12+ standard library, Python `unittest`, the repository backlog status parser/CLI, `uv`, repository quality tooling, and Git.

**Spec:** `docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`

## Global Constraints

- Read `HANDOFF.md`, `ROADMAP.md`, `BACKLOG.md`, both governing architecture documents, the completed identity/native-FDR migration specification and plan, the draft canonical-contract specification (no canonical-contract implementation plan existed at execution time), and the source specification before editing.
- Use Python's `unittest` framework only. Do not add, invoke, or suggest pytest.
- Change governance documents, their focused tests, and review evidence only; do not change runtime modules, package metadata, schemas, fixtures, adapters, or release artifacts.
- Keep `T1.2` selected and `implemented` pending its independent review. Do not claim D1.1, D1.2, or D1.3 is implemented, reviewed, or verified.
- Register D1.1, D1.2, and D1.3 as `specified`, with the approved design link, no plan, no review, no completion evidence, and `0/4` gates.
- Keep C1-C4, A1, R1, P1, G1, `I1.1`, and `I1.2` status and prerequisites unchanged.
- Treat `I1.0` as a statusless external boundary permitting q4xpcc specification/plan reconciliation only after D1.3.
- Keep native `.fdr` a deliberately lossy format and sink, never the canonical data model.
- Do not push, tag, publish, create a release, or make implementation-completion claims.
- Do not finalize this plan's historical/completed metadata until Tasks 1-3 and independent review have passed.

---

### Task 1: Lock the new authority contract with failing governance tests

**Files:**

- Modify: `tests/test_backlog_governance.py`
- Modify: `docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`

**Interfaces:**

- Consumes: the approved D1 identities, dependencies, outcomes, external boundary, lifecycle state, and governing-spec assignment.
- Produces: exact failing tests for the missing authority plus governance-compatible acceptance headings in the already approved design.

- [x] **Step 1: Extend exact epic and node-kind expectations**

  Add `"D1": ("D1.1", "D1.2", "D1.3")` to `EXPECTED_EPIC_MEMBERS`. Change the expected local-child count from 61 to 64 in both count assertions. Add `I1.0` before `I1.1` in the exact boundary identity list, add `"q4xpcc Phase 24A specification and plan reconciliation"` before the existing boundary outcomes, and add `I1.0` to the non-child exclusion set.

- [x] **Step 2: Assert exact D1 dependencies and readiness-boundary language**

  Extend `test_authoritative_dependency_cells_use_exact_identities` with:

  ```python
  self.assertEqual("`T1.2`", by_child["D1.1"])
  self.assertEqual("`D1.1`", by_child["D1.2"])
  self.assertEqual("`D1.2`", by_child["D1.3"])
  ```

  Add a focused test that locates `I1.0`, `I1.1`, and `I1.2` in the roadmap boundary table and asserts their exact owners and handoff conditions. Assert that the backlog external-boundary table carries the same three distinct conditions, so planning reconciliation cannot be mistaken for delivered-model adoption or live-XPLM adoption.

- [x] **Step 3: Register the approved design in artifact expectations**

  Extend `test_active_design_epic_assignments_match_roadmap_contract` with:

  ```python
  "2026-08-22-q4xpcc-contract-handoff-readiness-design.md": (
      "`D1`",
      EXPECTED_EPIC_MEMBERS["D1"],
  ),
  ```

  Add the same filename to the exact active-spec set in `test_active_artifact_assignments_match_current_roadmap_children`. Do not change the exact active-plan set: this authority-registration plan is a historical cross-cutting record after completion, not a D1 child plan.

- [x] **Step 4: Make the approved design satisfy the existing heading contract without changing its decisions**

  Under the design's final `## Acceptance criteria`, add these exact headings in this exact order:

  ```markdown
  ### D1.1 — Canonical C1–C4 design approval
  ### D1.2 — Acquisition, recording, projection, and pinning contract design
  ### D1.3 — Reviewed q4xpcc Phase 24A handoff
  ```

  Beneath each heading, state that the child is complete only when its four earlier acceptance gates pass. Move the six authority-registration criteria under a separately named `## Authority-registration acceptance criteria` section so the existing active-design parser sees only the three exact local-child headings.

- [x] **Step 5: Run the focused test and confirm the intended RED state**

  Run:

  ```powershell
  uv run python -m unittest tests.test_backlog_governance -v
  ```

  Expected: failures identify missing D1 roadmap/inventory/acceptance headings and missing `I1.0`; no failure should indicate a malformed test or unrelated regression.

---

### Task 2: Register D1 and I1.0 in the roadmap and backlog authorities

**Files:**

- Modify: `ROADMAP.md`
- Modify: `BACKLOG.md`
- Test: `tests/test_backlog_governance.py`

**Interfaces:**

- Consumes: Task 1's exact authority assertions.
- Produces: three ordered local children with honest initial lifecycle state and one statusless external planning boundary.

- [x] **Step 1: Add the readiness branch to `ROADMAP.md`**

  Update the document date to 2026-08-22. In the release-path diagram, show `T1.2` feeding `D1 q4xpcc contract-handoff readiness`, which feeds `I1.0` planning reconciliation, while the existing full implementation path to C1-C4, A1, R1, P1, G1, and the separate release decision remains intact.

  Add `## D1 — q4xpcc contract-handoff readiness epic` after P1 and before release gates, explain that it freezes consumer planning contracts without delivering runtime artifacts, and add this exact table:

  ```markdown
  | Child | Outcome | Depends on |
  | --- | --- | --- |
  | `D1.1` | Canonical C1–C4 design approval | `T1.2` |
  | `D1.2` | Acquisition, recording, projection, and pinning contract design | `D1.1` |
  | `D1.3` | Reviewed q4xpcc Phase 24A handoff | `D1.2` |
  ```

  State that D1 changes readiness priority only: it does not change T1.3's dependency, C/A/R/P delivery order, G1, adoption boundaries, or release gates.

- [x] **Step 2: Add `I1.0` without weakening `I1.1` or `I1.2`**

  Insert this exact first row in the roadmap external-boundary table:

  ```markdown
  | `I1.0` | q4xpcc Phase 24A specification and plan reconciliation | q4xpcc | Phase 24A specification and plan reconciliation may begin after `D1.3`. |
  ```

  Preserve the existing `I1.1`/`C4.4` and `I1.2`/`A1.9` rows byte-for-byte.

- [x] **Step 3: Add the exact initial D1 inventory state to `BACKLOG.md`**

  In `## Current position`, retain `- Active child: `T1.2`.` and add that after T1.2 review the next readiness priority is D1.1 before T1.3. Clarify that D1 is design-handoff readiness, not implementation or release readiness.

  Insert these rows after P1.6, matching roadmap order:

  ```markdown
  | `D1.1` | Canonical C1–C4 design approval | `specified` | `T1.2` | [design](docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md) | — | 0/4 | — | — | — |
  | `D1.2` | Acquisition, recording, projection, and pinning contract design | `specified` | `D1.1` | [design](docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md) | — | 0/4 | — | — | — |
  | `D1.3` | Reviewed q4xpcc Phase 24A handoff | `specified` | `D1.2` | [design](docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md) | — | 0/4 | — | — | — |
  ```

- [x] **Step 4: Add the twelve unchecked D1 acceptance gates**

  Add exact D1.1, D1.2, and D1.3 acceptance headings in roadmap order after P1.6 and before S1.1. Copy each child's four approved acceptance gates from the source design as unchecked Markdown items. Do not attach evidence or change any existing checkbox.

- [x] **Step 5: Add the concise backlog boundary row**

  Insert this first row in `## External consumer and downstream boundaries`:

  ```markdown
  | `I1.0` | q4xpcc | Phase 24A specification and plan reconciliation may begin after `D1.3`. |
  ```

  Preserve the existing `I1.1`, `I1.2`, `I2.1`, and `F2.1` rows and conditions.

- [x] **Step 6: Run focused governance, parser, report, and CLI tests**

  Run:

  ```powershell
  uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli -v
  ```

  Expected: all focused tests pass. When D1 changed the current repository inventory from 61 to 64, `tests/test_backlog_status_cli.py` was the exact fixture update required; update only that expectation and rerun this command. Do not change production semantics to hide D1 or `I1.0`.

- [x] **Step 7: Inspect the human and JSON status surfaces**

  Run:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  ```

  Expected: 64 local children are represented; `T1.2` remains the sole active child; D1.1-D1.3 appear as `specified` with zero satisfied gates; `I1.0` is not a selectable local child; no output claims implementation or release readiness.

- [x] **Step 8: Commit the authority registration**

  ```powershell
  git add ROADMAP.md BACKLOG.md tests/test_backlog_governance.py docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md
  git commit -m "docs: prioritize q4xpcc contract readiness"
  ```

---

### Task 3: Align the sole handoff checkpoint and verify the repository

**Files:**

- Modify: `HANDOFF.md`
- Test: `tests/test_backlog_governance.py`
- Verify: complete repository

**Interfaces:**

- Consumes: the registered D1 and I1.0 authorities.
- Produces: one current checkpoint that tells the next agent exactly what remains, without issuing the future q4xpcc brief prematurely.

- [x] **Step 1: Update `HANDOFF.md` with the prioritized sequence**

  Link the approved D1 design. State the exact sequence: independently review T1.2; execute D1.1 canonical-design approval; execute D1.2 contract-only A1/R1/P1 design; execute D1.3 reviewed consumer brief; then report the met `I1.0` condition so the user can reconcile q4xpcc's Phase 24A spec and plans.

  Distinguish all three external thresholds:

  - `I1.0`: Phase 24A specification/plan reconciliation after D1.3;
  - `I1.1`: delivered model/schema/fixture/runtime adoption after C4.4; and
  - `I1.2`: live XPLM acquisition adoption after A1.9.

  Preserve the release, push, tag, GitHub release, and PyPI prohibitions. Do not emit the D1.3 brief, invent a pin, or claim any D1 child complete.

- [x] **Step 2: Run repository-native status reporting**

  Run:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  ```

  Expected: both commands succeed and preserve T1.2 as the active child while showing the new D1 work as specified, unsatisfied work.

- [x] **Step 3: Run the complete verification suite**

  Run:

  ```powershell
  uv run python -m unittest discover -v
  uv run python tools/quality.py check
  git diff --check
  ```

  Expected: every command exits 0. Confirm the test count is at least the 268-test baseline plus the new focused boundary test. Confirm the actual `2064b8c..39ba4a8` range contains exactly `ROADMAP.md`, `BACKLOG.md`, `HANDOFF.md`, `docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`, `tests/test_backlog_governance.py`, and `tests/test_backlog_status_cli.py`. This plan was deliberately staged outside the governed plans directory during Tasks 1–3 under the bootstrap ruling; it entered the tracked range only in Task 4, after truthful historical/completed metadata existed.

- [x] **Step 4: Commit the handoff alignment**

  ```powershell
  git add HANDOFF.md
  git commit -m "docs: align the q4xpcc readiness handoff"
  ```

---

### Task 4: Obtain independent review and close the bootstrap execution record

**Files:**

- Create: `.superpowers/sdd/2026-08-22-q4xpcc-contract-handoff-readiness/review.md`
- Modify: files identified by accepted review findings, if any
- Modify: `docs/superpowers/plans/2026-08-22-q4xpcc-contract-handoff-readiness-authority.md`

**Interfaces:**

- Consumes: committed Tasks 1-3 and their fresh verification output.
- Produces: independent review evidence and an accurate historical disposition for this cross-cutting bootstrap plan.

- [x] **Step 1: Request independent review**

  Use `superpowers:requesting-code-review`. Review the complete diff from `2064b8c` through current HEAD against the approved D1 design. Require the reviewer to check exact authority parity, lifecycle honesty, ownership boundaries, distinct I1.0/I1.1/I1.2 conditions, unchanged implementation/release gates, and absence of runtime/distribution changes.

- [x] **Step 2: Record review evidence**

  Create `.superpowers/sdd/2026-08-22-q4xpcc-contract-handoff-readiness/review.md` with the repository's exact evidence metadata family:

  ```markdown
  # q4xpcc Contract-Handoff Readiness Authority Review

  - **Child:** —
  - **Gate:** —
  - **Kind:** review
  - **Result:** accepted
  - **Date:** 2026-08-22
  - **Subject:** Independent q4xpcc contract-handoff readiness authority review
  ```

  Summarize the reviewed range, commands/evidence inspected, findings, and resolution. Record `Result: accepted` only when no unresolved load-bearing finding remains. If review finds a defect, use `superpowers:receiving-code-review`, add a failing `unittest` where applicable, implement the smallest correction, rerun Task 3 verification, and request re-review before continuing.

- [x] **Step 3: Finalize this plan's truthful historical metadata**

  Replace the bootstrap note above with:

  ```markdown
  - **Governance:** historical
  - **Status:** completed
  - **Disposition:** Approved q4xpcc contract-handoff readiness authority registration completed and independently reviewed on the temporary design branch; preserved as the cross-cutting execution record and not a D1 child implementation plan.
  ```

  Keep the remainder of the plan as the executed record. Check every completed step checkbox only after its command or evidence exists.

- [x] **Step 4: Run final verification from the exact final worktree state**

  Use `superpowers:verification-before-completion`, then run:

  ```powershell
  uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli -v
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
  uv run python -m unittest discover -v
  uv run python tools/quality.py check
  git diff --check
  git status --short
  ```

  Expected: tests and quality checks exit 0; status reports T1.2 active and D1 specified; whitespace check is clean; only the plan and review evidence remain uncommitted before the closing commit.

- [x] **Step 5: Commit the reviewed execution record**

  ```powershell
  git add docs/superpowers/plans/2026-08-22-q4xpcc-contract-handoff-readiness-authority.md .superpowers/sdd/2026-08-22-q4xpcc-contract-handoff-readiness/review.md
  git commit -m "docs: record q4xpcc readiness authority review"
  ```

- [x] **Step 6: Verify the clean committed state without publishing**

  Run:

  ```powershell
  git status --short
  git log -6 --oneline
  ```

  Expected: the worktree is clean and the five execution commits are visible:
  Task 1, Task 2, Task 3, the review-correction wave, and this closing record.
  Do not push, tag, publish, create a release, mark D1.1-D1.3 complete, or send
  a q4xpcc readiness brief.
