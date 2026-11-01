# Coordinated refresh implementation plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** User-authorized November 1 crosscutting T2.1/T2.2 refresh completed under `docs/superpowers/specs/2026-11-01-coordinated-refresh-design.md`, with results in `docs/reviews/2026-11-01-coordinated-refresh.md`. This execution record does not advance or replace a roadmap child or close STRICT adoption acceptance.

> **For agentic workers:** Use superpowers:executing-plans for this sequential maintenance change; request one independent whole-change review at closeout.

**Goal:** Reconcile the reviewed starter, native project configuration and locked development toolchain.

**Architecture:** Project configuration selects immutable shared upstream sources. The existing dependency adapter owns guarded resolution and verification. Runtime code and public behavior remain unchanged.

**Tech Stack:** Python 3.12.16, uv/uv_build 0.13.6, Ruff, ty, unittest, native Codex plugins.

**Spec:** `docs/superpowers/specs/2026-11-01-coordinated-refresh-design.md`.

## Global constraints

Preserve stdlib-only runtime, `>=3.12,<3.13`, unittest-only tests, all hooks,
heavy selection and disabled Backplane. No global activation, cache edits,
automatic merge/push/release or unrelated dependency worktree changes.

## Review focus

- Required uv version and backend/CI must agree; no stale parser assumptions.
- Native cache contents do not establish project activation or fresh discovery.
- Starter exceptions never waive FDAU's unresolved STRICT evidence.
- Major transitive upgrades require consumer compatibility evidence.
- Generated locks and artifacts must come from their owning tools.

### Task 1: Reconcile managed starter content

Files: `.skills-first/bundle.lock.json`, `.codex/config.toml`,
`AGENTS.skills-first.md`, `.agents/skills/update-gz-template/SKILL.md`,
`AGENTS.md`, `docs/agents/skills-first.md`, dated review evidence.

- [x] Capture rollback and user/native state; generate old and target candidates.
- [x] Review three-way differences; reconcile only managed content and applicable local policy references.
- [x] Preview and apply project-local activation repair; compare outside-project/user controls.
- [x] Execute helper status and native verification. Helper status has an upstream Windows separator false positive; released-byte equality, actual sources and fresh discovery passed independently. Full template/STRICT acceptance is not claimed.

### Task 2: Refresh the resolver and Python dependency graph

Files: `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`,
`.github/workflows/release-readiness.yml`, `docs/engineering/python.md`;
only necessary adapter/tests if actual compatibility failures require them.

- [x] Bootstrap reviewed exact uv/backend/Ruff/ty pins and CI action; regenerate lock with uv.
- [x] Inspect `.venv/Scripts/python.exe tools/dependency_refresh.py status --json`.
- [x] Apply its digest with one `--review-scope` per reviewed dirty path.
- [x] Confirm retained parent constraints, advisories, focused checks, complete offline hygiene and external source/installed wheel verification. Original failed adapter attempts are preserved; the final owning gates passed independently on the frozen candidate.
- [x] Demonstrate failing metadata regression unittest before the minimal parser correction, then pass focused checks.

### Task 3: Close review and evidence

Files: `docs/reviews/2026-11-01-coordinated-refresh.md`, this plan and local
`.superpowers/sdd/coordinated-refresh-2026-11-01/` receipts.

- [x] Inspect complete diffs and obtain independent scoped review.
- [x] Resolve the specification-heading failure and rerun affected verification; independent review found no actionable defects.
- [x] Record final hashes/results and remaining acceptance gaps; retain the reviewable worktree without implying local integration or Git sync.

Commit boundary: one coherent maintenance save point only if requested or needed
by the documented branch-finishing workflow, with mandatory hooks intact.
