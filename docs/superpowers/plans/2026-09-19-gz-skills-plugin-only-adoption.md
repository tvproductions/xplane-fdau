# gz-skills Plugin-Only Adoption Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** The approved 2026-09-19 crosscutting plugin-only policy migration completed and was locally merged into `main`; T2.2 remains draft. Current authority: `docs/architecture/gz_skills_plugin_only_specification.md` and `AGENTS.md`. No Git push, tag, publication, or release occurred.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Make the pinned Codex plugin the only portable gz-skills authority in xplane-fdau.

**Architecture:** Project configuration selects one tagged Git marketplace plugin. Policy tests reject standalone copies and their lock without relying on a developer's Codex install. Current guidance and the T2.2 draft recognize the plugin as a separately managed dependency.

**Tech Stack:** Codex project TOML, Python 3.12 `tomllib` and `unittest`, Git, existing repository checks.

**Spec:** `docs/architecture/gz_skills_plugin_only_specification.md` (approved 2026-09-19).

## Global Constraints

- Keep `xplane-fdau` runtime standard-library-only and use `unittest` only.
- Do not implement T2.2, change backlog state, update plugin version, run Git sync, or release.
- Keep `.agents/superpowers` and its discovery junction ignored and separate.
- Keep historical completed adoption records unchanged; update current guidance only.
- Run one full project quality gate on the final implementation candidate; no standalone hygiene pass.
- The working plan lived in ignored `.superpowers/sdd` during execution and was copied to `docs/superpowers/plans` after the merged implementation was verified; the backlog parser rejects an active plan without a roadmap child.

## Task 1: Configure one plugin source and reject standalone copies

**Files:** Create `.codex/config.toml`; modify `tests/test_project_skills.py`; remove `.agents/skills/gzs-*` and `gz-skills.lock.json`.

**Interface:** `tomllib.loads(Path('.codex/config.toml').read_text(encoding='utf-8'))` exposes `marketplaces.gz-skills` and `plugins.gz-skills@gz-skills`.

- [x] **Step 1: Write the failing policy test.** Replace `test_canonical_gz_skills_installation_matches_locked_catalog` with a `unittest` method that asserts the TOML has exactly one gz-skills marketplace source, its `source_type == 'git'`, `source == 'https://github.com/tvproductions/gz-skills.git'`, and `ref == 'v0.2.0'`; exactly one gz-skills plugin key `gz-skills@gz-skills` is enabled; `gz-skills.lock.json` is absent; and neither `.agents/skills` nor `.codex/skills` has a `gzs-*` entry. Remove the obsolete digest helper, imports, and fixed eleven-skill set.
- [x] **Step 2: Prove red.** Run `uv run --frozen python -m unittest tests.test_project_skills.ProjectSkillTests.test_plugin_only_gz_skills_authority -v`. Expect failure because `.codex/config.toml` is absent or standalone copies remain.
- [x] **Step 3: Add the approved project configuration.** Use the exact TOML block from the approved spec: `[marketplaces.gz-skills]` with `source_type = "git"`, the GitHub source, and `ref = "v0.2.0"`; `[plugins."gz-skills@gz-skills"]` with `enabled = true`.
- [x] **Step 4: Remove the alternative installation.** Use `git rm` on the 23 tracked `.agents/skills/gzs-*` files and `gz-skills.lock.json`, after confirming each target is under this worktree. Preserve `.agents/skills/superpowers` and every project adapter.
- [x] **Step 5: Prove green.** Run the same focused `unittest` method and `git diff --check`; inspect `git status --short` and `git diff --stat` for the exact removed scope.

## Task 2: Reconcile current guidance and generated metadata

**Files:** Modify `AGENTS.md`, `.gitattributes`, `.secrets.baseline`, `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`, `docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`, and `tests/test_project_skills.py`.

**Interface:** The current agent guidance names `gz-skills@gz-skills` and `.codex/config.toml`; a full `gzs-update-dependencies` inventory includes this project pin and uses Codex marketplace to refresh it.

- [x] **Step 1: Add a failing guidance test.** Assert `AGENTS.md` names the plugin ID, project config, sole portable authority, and the full-refresh inventory obligation. Assert the active T2 design points to the new approved spec and the T2.2 draft calls out the plugin pin as a Codex-managed surface, separate from Python/uv mutation. Assert `.gitattributes` has no `gzs-*/**` rule and `.secrets.baseline` has no `gz-skills.lock.json` result.
- [x] **Step 2: Prove red.** Run `uv run --frozen python -m unittest tests.test_project_skills -q`. Expect only the new guidance assertions to fail.
- [x] **Step 3: Update `AGENTS.md`.** Replace the snapshot/lock paragraph with the sole plugin authority, exact project pin and source, installation and local verification commands, forbidden standalone roots/lock, and full dependency refresh obligation. Preserve explicit-only Git sync/handoff, project adapter commands, and Superpowers rules.
- [x] **Step 4: Update live design and draft plan.** Replace the active T2 design's snapshot/lock authority claim with a link to the approved plugin-only specification. In the T2.2 draft, add the project plugin pin to managed-dependency inventory and state that Codex marketplace owns its refresh; keep the Python adapter's scope, draft state, and lifecycle unchanged.
- [x] **Step 5: Remove obsolete metadata.** Delete the two `.gitattributes` snapshot lines. Parse `.secrets.baseline` as JSON and remove only the `results['gz-skills.lock.json']` entry, preserving all other keys and entries.
- [x] **Step 6: Prove green.** Run `uv run --frozen python -m unittest tests.test_project_skills tests.test_documentation -q`, `git diff --check`, and a focused `rg` for live snapshot/lock authority references. Historical documents and negative packaging test fixtures may retain dated references.

## Task 3: Verify, review, and integrate

**Files:** Copy this checked and completed plan to `docs/superpowers/plans/2026-09-19-gz-skills-plugin-only-adoption.md`; no product code edits.

- [x] **Step 1: Audit against the approved spec.** Compare intent, scope, and plan under `gzs-plan-audit`; resolve missing or drifted requirements before final verification. Check the exact `git diff --name-status` for unintended edits.
- [x] **Step 2: Verify local plugin.** From this trusted worktree, run `codex plugin list --json` and `codex plugin marketplace list --json`; record installed/enabled `gz-skills@gz-skills` version `0.2.0`, Git marketplace source, and the resolved `v0.2.0` commit from marketplace metadata or the trusted Git source. Report any mismatch precisely.
- [x] **Step 3: Verify the candidate once.** Run `uv run python tools/quality.py check`, `uv run mkdocs build --strict`, `uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit`, and `git diff --check`. Diagnose any failure; do not count pre-existing warnings as success.
- [x] **Step 4: Review and commit.** Review the full diff under `superpowers:requesting-code-review`, correct findings, and commit the coherent policy migration. After fast-forward integration and cleanup, preserve this plan as a tracked historical record. Do not push.
- [x] **Step 5: Finish the branch.** Use `superpowers:finishing-a-development-branch` and the standing local-integration choice: merge into `main`, verify the merged state, remove the temporary worktree, and delete its branch. Confirm T2.2 remains draft and backlog audit has no findings.

## Plan audit

| Intent to scope | Evidence | Result |
| --- | --- | --- |
| Sole plugin authority; no alternative installation | User-approved intent and `docs/architecture/gz_skills_plugin_only_specification.md:8`, `:91` | Aligned |
| Project-managed plugin in complete dependency updates | User-approved intent and `docs/architecture/gz_skills_plugin_only_specification.md:110` | Aligned |

| Scope to plan | Evidence | Result |
| --- | --- | --- |
| Pin/configuration and copied-catalog removal | Spec `:36`, `:91`; Task 1 | Aligned |
| Current guidance, T2.2 draft inventory, obsolete metadata | Spec `:110`, `:161`; Task 2 | Aligned |
| Plugin, quality, documentation, backlog, and integration evidence | Spec `:202`; Task 3 | Aligned |

Verdict: **PASS**. No missing or drifted requirement remains. The T2.2 draft
still requires its own executable plan audit before approval.

## Completion evidence

- The plugin policy test first failed because `.codex/config.toml` was absent,
  then passed after configuration and standalone-catalog removal. The guidance
  test likewise failed before and passed after reconciliation.
- `codex plugin list --json` reported one installed, enabled
  `gz-skills@gz-skills` at version `0.2.0`, from the expected Git marketplace.
  The local marketplace `v0.2.0` tag and HEAD both resolved to
  `21579a545b3bf05339a017c82290ddcea8e9beec`. The repository had zero
  standalone `gzs-*` copies in its known discovery roots.
- The final `uv run python tools/quality.py check` passed. Its first attempt
  stopped at Ruff formatting in the changed test; formatting was corrected
  before the passing run. `uv run mkdocs build --strict` passed after a
  pre-existing T2.2 draft cross-reference warning was corrected in the draft.
- Independent diff review found no Critical or Important issue. Its one minor
  duplicate-plugin test gap was corrected before the passing full gate.
- Fast-forward merge placed implementation commit `bd3656e` on `main`.
  Merged-tree focused policy/documentation tests passed (24 tests), strict
  MkDocs passed, and the backlog audit reported no findings. The temporary
  worktree and branch were removed. T2.2 remains draft; the next backlog action
  is to finish its implementation plan.
